from __future__ import annotations
import ast
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import Series
from threading import local

_thread_local = local()
_thread_local.accessed_cols = []

_dataframes = []  # pipe里全部mydataframe实例列表，暂未完全使用

# K2Pipe提供的内置函数，用于解决暂时无法通过eval()实现的常用操作，如时间操作
def time_shift(self: Series, *args, **kwargs):
    return self + pd.to_timedelta(*args, **kwargs)
pd.Series.time_shift = time_shift


# 修改pd.concat()方法
_original_concat = pd.concat
def my_concat(objs, axis=0, **kwargs):
    result = _original_concat(objs, axis=axis, **kwargs)

    if isinstance(result, pd.DataFrame):
        result = MyDataFrame(result)

    if axis == 0:
        # 纵向拼接的情况
        result.attrs['op'] = 'concat'
        for col in objs[0].columns:
            result.actual_mappings[col] = col
    elif axis == 1:
        # 横向拼接的情况
        result.attrs['op'] = 'concat(1)'

        all_features = []
        for obj in objs:
            if isinstance(obj, pd.Series):
                all_features.append(obj.name)
            elif isinstance(obj, pd.DataFrame):
                # merge的实现会调用concat(axis=1)
                # 虽然pandas的concat支持两个df有同名列，但结果格式复杂容易出错，这里禁止这种情况
                if bool(set(all_features) & set(obj.columns.values)):
                    raise ValueError(f'横向拼接的DataFrame不能有同名列：{all_features}  -- {obj.columns.values}')
                all_features.extend(obj.columns)
            else:
                raise ValueError('暂不支持非Series类型的拼接')
        for col in all_features:
            result.actual_mappings[col] = col

    # 建立连接关系
    for obj in objs:
        if isinstance(obj, pd.Series):
            df = MyDataFrame(obj)
            df.attrs['name'] = 'Series'
            result.input_dfs.append(df)
        elif isinstance(obj, pd.DataFrame):
            result.input_dfs.append(obj)
            obj.output_df = result

    # 加入到processors列表
    _dataframes.append(result)
    return result
# merge也会调用自定义concat()方法，若覆盖会报错：
# AttributeError: 'Series' object has no attribute 'columns'
# 暂时不覆盖原生concat
pd.concat = my_concat


_original_read_csv = pd.read_csv
def my_read_csv(filepath_or_buffer, *args, **kwargs):
    df = _original_read_csv(filepath_or_buffer, *args, **kwargs)
    if isinstance(filepath_or_buffer, (str, Path)):
        filename = Path(filepath_or_buffer).name
        df = MyDataFrame(df)
        df.attrs['name'] = filename
    return df

# 替换 pandas 的 read_csv
pd.read_csv = my_read_csv

class MyDataFrame(pd.DataFrame):
    _metadata = ['actual_mappings','input_dfs','output_df']

    def __init__(self, *args, actual_mappings=None, input_dfs=None, output_df=None,  **kwargs):
        super().__init__(*args, **kwargs)
        self.actual_mappings = actual_mappings  # 实际发生的计算关系（例如 * 已经展开）
        self.input_dfs = input_dfs
        self.output_df = output_df
        if self.input_dfs is None:
            self.input_dfs = []
        if self.actual_mappings is None:
            self.actual_mappings = {}
        self.attrs['name'] = 'DataFrame'  # default name

    @property
    def _constructor(self):
        # 确保在 df 操作（如 df.head(), df.copy()）后仍返回 MyDataFrame 类型
        return MyDataFrame


    def merge(self, right, on=None, **kwargs):
        # 目前不支持自动加_x、_y的处理
        # 如果两个df有同名列（on内除外），则抛出异常
        if on is None:
            raise ValueError("strict_merge 要求必须显式指定 `on` 参数。")
        # 标准化 on 为集合
        if isinstance(on, str):
            on_cols = {on}
        else:
            on_cols = set(on)
        # 检查 on 列是否都存在于两个 DataFrame 中
        missing_in_left = on_cols - set(self.columns)
        missing_in_right = on_cols - set(right.columns)
        if missing_in_left or missing_in_right:
            raise KeyError(
                f"连接键缺失：left 缺少 {missing_in_left}，right 缺少 {missing_in_right}"
            )
        common_cols = set(self.columns) & set(right.columns)
        extra_common = common_cols - on_cols
        if extra_common:
            raise ValueError(
                f"发现非连接键的同名列（除 `on={on}` 外）: {sorted(extra_common)}。"
                "请重命名列或移除重复列后再合并。"
            )

        # 原始merge结果
        result =  MyDataFrame(super().merge(right=right, **kwargs))

        # FIXME: 重名带有后缀的情况还没有处理
        result.attrs['op'] = 'merge'
        for col in self.columns:
            result.actual_mappings[col] = col
        for col in right.columns:
            result.actual_mappings[col] = col

        # 建立连接关系
        result.input_dfs = [self,right]
        self.output_df = result
        right.output_df = result

        # 加入到processors列表
        _dataframes.append(result)
        return result


    # 覆盖pd.DataFrame的rename方法
    def rename(self, inplace = None, *args, **kwargs):
        if inplace:
            raise ValueError("mydataframe.rename 暂不支持 inplace=True 参数") # TODO
        result = MyDataFrame(super().rename(*args, **kwargs))
        result.attrs['op'] = 'rename'
        for old, new in zip(list(self.columns), list(result.columns)):
            result.actual_mappings[new] = old
        # 建立连接关系
        result.input_dfs = [self]
        self.output_df = result
        _dataframes.append(result)
        return result


    # 覆盖pd.DataFrame的fitler方法
    def filter(self, *args, **kwargs) -> MyDataFrame:
        result = MyDataFrame(super().filter(*args, **kwargs))
        result.attrs['op'] = 'filter'
        columns = _all_columns(result)
        for col in columns:
            result.actual_mappings[col] = col
        # 建立连接关系
        result.input_dfs = [self]
        self.output_df = result
        _dataframes.append(result)
        return result

    # 追溯 df[['col1','col2']] 这类filter操作
    def __getitem__(self, key):
        if isinstance(key, tuple):
            key = list(key)

        if isinstance(key, list):
            result = self.filter(key)
            result.attrs['op'] = 'getitem'
            return result

        # 为__setitem__时获取使用记录做准备
        if isinstance(key, str):
            _thread_local.accessed_cols.append(key)

        # 其他key情况直接返回原始结果，不追溯：
        # slice类型：merge里会使用到此形式 left = self.left[:]
        # Series类型：drop_duplicate里使用
        # str类型：过于常用，例如df['k_ts'] = pd.to_datetime(df['k_ts'])
        # 可能还有其他类型
        return  super().__getitem__(key)


    # 追溯 df['new_col'] = df['col1'] + df['col2'] 这类操作
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        # 清除__getitem__里记录的访问列的全局记录
        accessed = getattr(_thread_local, 'accessed_cols', [])
        _thread_local.accessed_cols = []

        # 避免过于频繁的追溯记录
        if not isinstance(key, str):
            return
        if not (isinstance(value, Series) or isinstance(value, int) or isinstance(value, str)\
                or isinstance(value, float)):  # FIXME: 对于 df['f1'] = 100 这类应记录到expression
            return
        if key in ['k_ts', 'k_device']:
            return
        if accessed == []:
            return

        # FIXME: 列类型转换astype()也会被记录，追溯的意义不大
        # if key=='jiuxy':
        #     print()

        # 流程图里不能新建df节点
        expression = '+'.join(accessed)
        self.actual_mappings[key] = expression

        # # FIXME: 无法创建新的MyDataFrame实例，仅用名称提示存在setitem操作
        # if self.name is None or 'set(' in self.name:
        #     return
        # self.name = self.name +f'\nset({key})'


    # 追溯 df = df.assign(new_col = df['col1'] + df['col2'])
    def assign(self, **kwargs):
        result = MyDataFrame(super().assign(**kwargs))

        result.attrs['op'] = 'assign'
        for col in self.columns:
            result.actual_mappings[col] = col
        for key, value in kwargs.items():
            # FIXME: 无法获取到assign里的原始表达式
            # assign会触发__setitem__，需要消除影响（self对象的actual_mappings）
            result.actual_mappings[key] = self.actual_mappings[key]
            self.actual_mappings.pop(key)

        # 建立连接关系
        result.input_dfs = [self]
        self.output_df = result
        # 加入到processors列表
        _dataframes.append(result)
        return result


    # 覆盖pd.DataFrame的query方法
    def query(self, *args, **kwargs):
        result = MyDataFrame(super().query(*args, **kwargs))
        # actual_mappings
        result.attrs['op'] = 'query'
        for col in result.columns:
            result.actual_mappings[col] = col
        # 建立连接关系
        result.input_dfs = [self]
        self.output_df = result
        # 加入到processors列表
        _dataframes.append(result)
        return result


    # mypipe内部应使用原始drop，以免产生多余的追溯
    def drop_old(self, *args, **kwargs):
        return super().drop(*args, **kwargs)


    # 覆盖pd.DataFrame的drop方法
    def drop(self, *args, **kwargs):
        result = MyDataFrame(super().drop(*args, **kwargs))
        result.attrs['op'] = 'drop'
        for col in result.columns:
            result.actual_mappings[col] = col
        # 建立连接关系
        result.input_dfs = [self]
        self.output_df = result
        # 加入到processors列表
        _dataframes.append(result)
        return result

    # 根据配置的映射信息进行批量化的列级操作，例如重命名、特征提取等
    def extract_features(self, config: pd.DataFrame | str | Path, step_name: str = None) -> MyDataFrame:
        # 如果 config 是路径（Path 或 str），则读取为 DataFrame
        if isinstance(config, (str, Path)):
            config = pd.read_csv(config)
        elif not isinstance(config, pd.DataFrame):
            raise TypeError("config must be a pandas DataFrame, a string path, or a pathlib.Path object.")

        result = MyDataFrame(self) # 不能用copy()创建新实例，会将actual_mappings等属性复制过来
        if step_name:
            result.attrs['name'] = step_name
        result.columns = result.columns.str.strip()  # 防止列名前后有空格造成难以排查的错误

        # 展开第一个 * 为所有列名，并放在最前面
        if '*' in config['feature'].values:
            config.drop(config[config['feature'] == '*'].index, inplace=True)
            new_df = pd.DataFrame(columns=config.columns)
            for col in list(self.columns):
                new_df.loc[len(new_df)] = {'feature':col, 'expression':col, 'comment':'*'}
            for idx, row in config.iterrows():
                new_df.loc[len(new_df)] = row
            config = new_df

        for _, row in config.iterrows():
            # 忽略注释行
            if row[0].startswith('#'):
                continue

            feature_name = row['feature']
            if not pd.isna(feature_name):
                feature_name = feature_name.strip()
            else:
                raise ValueError(f"特征名称不能为空 {row}, line: {_}")

            _validate_var_name(feature_name)

            expression = row['expression']
            if not pd.isna(expression):
                expression = expression.strip()
            else:
                result[feature_name] = np.nan
                continue

            # 非数值类型用eval容易报错，这种情况直接赋值
            if feature_name == expression:
                result[feature_name] = result[expression]
            else :
                result[feature_name] = _eval(result, expression)

            # 记录实际生成的列
            expression_values = {}
            cols = _extract_column_names(expression)
            for col in cols:
                expression_values[col] = result[col]
            result.actual_mappings[feature_name] = expression

        _dataframes.append(result)

        # 删除self中存在但config中没有定义的列
        config_columns = set(config['feature'].dropna())
        original_columns = set(self.columns)
        columns_to_drop = original_columns - config_columns
        result = result.drop_old(columns=columns_to_drop, errors='ignore')

        result = _sort_columns(result)

        self.output_df = result
        result.input_dfs = [self]

        return result


    # 向前追踪指定df的指定列的计算逻辑
    # @Deprecated 此方法已被generate_dataflow()替代，后者输出更易读的图形化结果
    # def trace_column(self, feature_to_trace:str):
    #     assert isinstance(feature_to_trace, str)
    #
    #     # start_line: 倒序处理的开始行号（若为None则处理所有行）
    #     def _build_pipe_tree_recursive(df, feature, depth=0, start_line:int=None):
    #         if df.input_dfs is None:
    #             return None
    #
    #         if start_line is None:
    #             start_line  = len(df.actual_mappings)
    #
    #         # 倒序遍历
    #         # 获取 actual_mappings 的键值对列表
    #         mappings_list = list(df.actual_mappings.items())
    #         for idx in range(start_line - 1, -1, -1):  # 从 start_line-1 到 0
    #             mapped_feature, expr = mappings_list[idx]
    #             if mapped_feature == feature :
    #                 # 避免无限递归（同一个配置文件内部递归查找时）
    #                 # if df is self and feature == expr:
    #                 #     continue
    #                 input_names = _extract_column_names(expr)
    #
    #                 children = []
    #                 for name in input_names:
    #
    #                     # 同一个配置文件内部的递归匹配
    #                     # 从当前行的上一行继续倒序匹配
    #                     if idx > 1: # FIXME： 改为>0?
    #                         child_ast_self = _build_pipe_tree_recursive(df, name, depth + 1, idx -1)
    #                         if child_ast_self:
    #                             children.append(child_ast_self)
    #
    #                     # 前一个配置文件内的递归匹配
    #                     for input_df in df.input_dfs:
    #                         child_ast_prev = _build_pipe_tree_recursive(input_df, name, depth + 1)
    #                         if child_ast_prev:
    #                             children.append(child_ast_prev)
    #
    #                 return {
    #                     "feature": feature,
    #                     "df": df.copy(),
    #                     "mapping": {"feature": mapped_feature, "expression": expr},
    #                     "expression": expr,
    #                     "children": children,
    #                     "depth": depth
    #                 }
    #
    #     def _print_pipe_tree(ast_node, indent=0):
    #         if ast_node is None:
    #             print("└── (empty)")
    #             return
    #         spaces = "  " * indent
    #         expr = ast_node["expression"]
    #         feature = ast_node['feature']
    #         df = ast_node["df"]
    #         print(f"{spaces}└── [{df.attrs['name']}] {feature} = {expr} ")
    #         for child in ast_node["children"]:
    #             _print_pipe_tree(child, indent + 1)
    #
    #     tree = _build_pipe_tree_recursive(self, feature_to_trace)
    #     _print_pipe_tree(tree)
    #     return tree
    #
    #
    # # 向前追溯多个列
    # # @Deprecated 此方法已被generate_dataflow()替代，后者输出更易读的图形化结果
    # def trace_columns(self, features_to_trace:list):
    #     for feature in features_to_trace:
    #         print(feature)
    #         self.trace_column(feature)
    #         print()


    # 宽表转长表，例如：
    # k_ts, f1_mean_3D, f1_slope_3D, f2_mean_3D, f2_slope_3D
    # 2025 - 01 - 01, 1, 2, 3, 4
    # 2025 - 01 - 02, 5, 6, 7, 8
    # 转为：
    # k_ts, feature, measure, period, value
    # 2025 - 01 - 01, f1, mean, 3D, 1
    # 2025 - 01 - 01, f1, slope, 3D, 2
    # 2025 - 01 - 01, f2, mean, 3D, 3
    # 2025 - 01 - 01, f2, slope, 3D, 4
    # 2025 - 01 - 02, f1, mean, 3D, 5
    # 2025 - 01 - 02, f1, slope, 3D, 6
    # 2025 - 01 - 02, f2, mean, 3D, 7
    # 2025 - 01 - 02, f2, slope, 3D, 8
    def wide_to_long(self) -> MyDataFrame:
        id_vars = ['k_ts','k_device']
        value_vars = [col for col in self.columns if col != 'k_ts' and col != 'k_device']
        df_melted = self.melt(id_vars=id_vars, value_vars=value_vars, var_name='feature_measure_period',
                            value_name='value')
        split_cols = df_melted['feature_measure_period'].str.rsplit('_', n=2, expand=True)
        df_melted[['feature', 'measure', 'period']] = split_cols
        result = df_melted[['k_ts', 'k_device', 'feature', 'measure', 'period', 'value']]
        result = result.sort_values(['k_ts', 'feature', 'measure']).reset_index(drop=True)
        return result


    # 长表转宽表
    def long_to_wide(self) -> MyDataFrame:
        required_cols = ['k_ts', 'k_device', 'feature', 'measure', 'period', 'value']
        missing_cols = [col for col in required_cols if col not in self.columns]
        if missing_cols:
            raise ValueError(f"缺少必需的列: {missing_cols}")
        wide_df = self.copy()
        wide_df['new_col'] = wide_df['feature'] + '_' + wide_df['measure'] + '_' + wide_df['period']
        wide_df = MyDataFrame(wide_df.pivot(index=['k_ts', 'k_device'], columns='new_col', values='value'))
        wide_df = wide_df.reset_index()
        wide_df.columns.name = None
        return wide_df


    # 生成数据流图
    # show_value: 是否显示此列数据值（第一行）
    # highlight_useless_column：是否高亮显示无输出edge的列（无用列）
    def generate_dataflow(self, filename: Path = None, show_value=False, highlight_useless_column=True):
        # graphviz需要本地安装应用（仅pip install graphviz不够），比较麻烦
        # 所以开发者可能本地没有生成数据流图的条件
        # 此时仅警告不实际生成图（不抛出异常以免影响测试用例的完成）
        try:
            import os
            import graphviz
            from graphviz import ExecutableNotFound
        except ImportError as e:
            print(f"警告: 未安装graphviz，请先安装graphviz应用，然后 pip install graphviz  {e}")
            return None

        if filename.suffix.lower() != '.svg':
            raise ValueError(f"仅支持 .svg 格式: {filename.suffix}")

        dot = graphviz.Digraph(comment='DataFlow Graph', format='svg')
        # ranksep: df矩形之间的横向距离（英寸）
        # nodesep: 列矩形之间的纵向距离（英寸）
        dot.attr(rankdir='LR', splines='spline', ranksep='1', nodesep='0.12', compound='true')
        # 设置中文字体，优先使用系统中存在的字体
        dot.attr('graph', fontname='SimHei,SimSun,Microsoft YaHei,DejaVu Sans,Arial,sans-serif', fontsize='12')
        dot.attr('node', fontname='SimHei,SimSun,Microsoft YaHei,DejaVu Sans,Arial,sans-serif',
                 shape='box', style='filled', fillcolor='white', fontsize='10', height='0.3')
        dot.attr('edge', fontname='SimHei,SimSun,Microsoft YaHei,DejaVu Sans,Arial,sans-serif')

        # 使用集合记录已访问的节点，避免重复处理
        visited_dfs = set()
        visited_edges = set()
        all_col_nodes = set()  # 记录所有列节点ID
        output_sources = set()  # 记录有出边的源节点ID

        def add_dataframe_node(df):
            """添加DataFrame节点到图中"""
            if id(df) in visited_dfs:
                return
            visited_dfs.add(id(df))

            # 创建子图表示DataFrame，使用cluster前缀使graphviz将其渲染为带边框的组
            with dot.subgraph(name=f'cluster_{id(df)}') as c:
                label = df.attrs["name"]
                if "op" in df.attrs:
                    label = f'{label}\\n({df.attrs["op"]})'
                label = "\\n".join(textwrap.wrap(label, width=20)) # 长文本加换行
                c.attr(label=label,
                       fontname='SimHei,SimSun,Microsoft YaHei,DejaVu Sans,Arial,sans-serif')
                c.attr(style='filled', color='lightgrey')
                c.attr(rankdir='TB')

                # 添加列节点 - 强制垂直排列在同一列
                prev_col_node_id = None
                columns = _all_columns(df)
                for i, col in enumerate(columns):
                    col_node_id = f'col_{id(df)}_{i}_{col}'
                    label = f'{col} ({df.iloc[0][col]})' if show_value else col
                    c.node(col_node_id, label=label)
                    all_col_nodes.add(col_node_id)

                    # 强制垂直排列：避免同一df里两个列出现左右排列的情况，导致连线难以看清
                    # if prev_col_node_id:
                    #     c.edge(prev_col_node_id, col_node_id, style='invis')
                    # prev_col_node_id = col_node_id

                # 强制垂直排列：避免同一df里两个列出现左右排列的情况，导致连线难以看清
                if len(columns) > 1:
                    with c.subgraph() as s:
                        s.attr(rank='same')
                        for i, col in enumerate(columns):
                            col_node_id = f'col_{id(df)}_{i}_{col}'
                            s.node(col_node_id)

        def build_graph_recursive(current_df):
            """递归构建图"""
            # 添加当前DataFrame节点
            add_dataframe_node(current_df)

            # 处理上游节点
            for input_df in current_df.input_dfs:
                build_graph_recursive(input_df)

                # 根据actual_mappings创建列之间的连接
                # 注意：current_df内部不会有同名列，input_dfs之间不会有同名列；但current_df与input_dfs之间可能有同名列
                for feature, expression in current_df.actual_mappings.items():
                    create_edges_from_mapping(feature, expression, input_df, current_df)

            # 处理本节点内部连接
            for feature, expression in current_df.actual_mappings.items():
                create_edges_from_mapping(feature, expression, current_df, current_df)

        # 根据feature mapping信息创建连接线
        def create_edges_from_mapping(feature, expression, input_df, current_df):
            target_feature = feature

            # 提取表达式中的输入列
            input_cols = _extract_column_names(expression)

            # 在上游DataFrame中找到对应的列并创建连接
            for input_col in input_cols:
                # 避免current_df列自身的连接
                if current_df is input_df and target_feature == input_col:
                    continue
                if input_col in _all_columns(input_df):
                    if "op" in current_df.attrs and current_df.attrs['op'] == 'concat':
                        # 如果是纵向concat操作则创建cluster间的连接，而非col之间的连接，以减少图中的连线数量
                        cluster_edge_key = (id(input_df), id(current_df))
                        if cluster_edge_key not in visited_edges:
                            input_cols_list = list(_all_columns(input_df))
                            output_cols_list = list(_all_columns(current_df))
                            if input_cols_list and output_cols_list:
                                representative_input = f'col_{id(input_df)}_0_{input_cols_list[0]}'
                                representative_output = f'col_{id(current_df)}_0_{output_cols_list[0]}'
                                # 参数ltail和lhead要求compound=true才有效
                                dot.edge(
                                    representative_input,
                                    representative_output,
                                    ltail=f'cluster_{id(input_df)}',
                                    lhead=f'cluster_{id(current_df)}'
                                )

                            visited_edges.add(cluster_edge_key)
                            for col_idx, col in enumerate(_all_columns(input_df)):
                                source_node_id = f'col_{id(input_df)}_{col_idx}_{col}'
                                output_sources.add(source_node_id)
                    else:
                        target_idx = list(_all_columns(current_df)).index(target_feature)
                        target_node_id = f'col_{id(current_df)}_{target_idx}_{target_feature}'

                        # 找到上游DataFrame中的源列节点ID
                        source_idx = list(_all_columns(input_df)).index(input_col)
                        source_node_id = f'col_{id(input_df)}_{source_idx}_{input_col}'

                        # 创建连接，避免重复边
                        edge_key = (source_node_id, target_node_id)
                        if edge_key not in visited_edges:
                            if input_df is current_df:
                                dot.edge(source_node_id, target_node_id, color='gray') # 同一个DataFrame内部的连接用灰色
                            else:
                                dot.edge(source_node_id, target_node_id)
                            visited_edges.add(edge_key)
                            output_sources.add(source_node_id)


        # 从当前DataFrame开始构建图
        build_graph_recursive(self)

        # 如果启用了 highlight_useless_column，则将没有输出边的列高亮
        if highlight_useless_column:
            no_output_nodes = all_col_nodes - output_sources
            for node_id in no_output_nodes:
                dot.node(node_id, fillcolor='yellow')

        try:
            # 渲染图片，render里的filename参数不要带扩展名
            dot.render(os.path.splitext(filename)[0], cleanup=True)  # cleanup=True删除临时文件
            print(f"数据流图已保存到: {filename}")
            return dot
        except ExecutableNotFound as e:
            print(f"警告: 未安装graphviz应用，请先下载安装。 {e}")
            return None


    # 确保DataFrame的时间戳和设备列的类型，时间戳作为索引
    # 将object类型的列转为string类型，前者不支持eval()
    def format_columns(self) -> MyDataFrame:
        result = MyDataFrame(self)
        result.attrs['name'] = self.attrs['name']
        if 'k_ts' in result.columns:
            result['k_ts'] = pd.to_datetime(result['k_ts'])
            # 若k_ts同时作为索引和普通列，对merge操作会报错（'k_ts' is both an index level and a column label, which is ambiguous.）
            # 若k_ts仅作为索引，df['k_ts']会报错 （KeyError)
            # result = result.set_index(['k_ts'], drop=True)
        if 'k_device' in result.columns:
            result['k_device'] = result['k_device'].astype(str)

        # 将object类型的列转为string类型，避免eval()里报错
        object_cols = result.select_dtypes(include=['object']).columns
        result[object_cols] = result[object_cols].astype('string')

        # 列名去掉首尾空格，防止难以察觉的错误
        result.columns = result.columns.str.strip()

        # 列名排序，方便调试对比
        result = _sort_columns(result)

        return result


# 检验列名是否合法
def _validate_var_name(var_name: str):
    forbidden_chars = {'.', '[', ']', '-', '+', '*', '/', '\\', '%', '&'}
    if any(char in forbidden_chars for char in var_name):
        raise ValueError(f"变量名 '{var_name}' 包含非法字符")


# 先使用numexpr解析，若失败再尝试python解析
def _eval(df: pd.DataFrame, expression: str):
    result = None

    # dataframe的eval()方法不支持where表达式，自己实现
    if expression.startswith('where'):
        args = _parse_where_args(expression)
        if len(args) == 3:
            return np.where(_eval(df, args[0]), _eval(df, args[1]), _eval(df, args[2]))
        else:
            raise ValueError(f"无效的where表达式格式: {expression}")

    try:
        result = df.eval(expression, engine='numexpr')
    except Exception as e:
        # numexpr不支持字符串等操作，此时尝试降级到python解释器（性能较低）
        # 典型错误信息：'unknown type object'、'unknown type datetimedelta64[ns]'
        try:
            result = df.eval(expression, engine='python')
        except Exception as e:
            # 如果python解析器也失败，报错
            cols = _extract_column_names( expression)
            print('\n表达式执行失败相关输入数据：')
            print(df[cols])
            raise Exception(f'表达式 {expression} 执行失败(python)： {e}')
    return result


# 为解决嵌套where()的情况，将原来的正则表达式方案改为手动解析方案
def _parse_where_args(s):
    if not s.startswith('where(') or not s.endswith(')'):
        raise ValueError("Not a where expression")
    # 去掉 'where(' 和最后的 ')'
    inner = s[6:-1]
    args = []
    paren_level = 0
    current = []
    for char in inner:
        if char == ',' and paren_level == 0:
            args.append(''.join(current).strip())
            current = []
        else:
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            current.append(char)
    args.append(''.join(current).strip())  # 最后一个参数
    return args


def _extract_column_names(expr: str):
    if expr.startswith('where'):
        args = _parse_where_args(expr)
        # FIXME: 根据实际情况，选择arg[1]或arg[2]
        return [] # FIXME

    # FIXME：带有@pd的表达式无法解析（如 @pd.shape[0]) ）
    if '@' in expr:
        return [] # FIXME

    tree = ast.parse(expr, mode='eval')
    names = set()

    class NameVisitor(ast.NodeVisitor):
        def visit_Name(self, node):
            names.add(node.id)
            self.generic_visit(node)

    NameVisitor().visit(tree)
    return sorted(names)  # 或直接返回 names（set）


# 列按字母顺序排序
def _sort_columns(df: pd.DataFrame):
    cols = sorted(df.columns)
    if 'k_device' in cols:
        cols = ['k_device'] + [col for col in cols if col != 'k_device']
    if 'k_ts' in cols:
        cols = ['k_ts'] + [col for col in cols if col != 'k_ts']
    # 不使用df[cols]的写法，避免产生追溯记录
    return df.reindex(columns=cols)


# 当df仅有默认索引时，直接返回不包含索引的列
# 若df有k_ts等命名索引时，返回包含这些索引的所有列
def _all_columns(df: pd.DataFrame):
    if any(name is not None for name in df.index.names):
        df_for_iter = df.reset_index()
    else:
        df_for_iter = df
    return df_for_iter.columns