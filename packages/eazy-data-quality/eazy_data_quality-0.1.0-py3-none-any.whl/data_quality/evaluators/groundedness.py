import yaml
import pandas as pd

from ..evaluators.base import BaseProcessor
from ..utils.extra_yaml import YamlVariableExtractor


class GroundednessEvalProcessor(BaseProcessor):
    """三元组评估处理器"""

    def __init__(self, yaml_path='prompt/groundedness_prompt.yaml', required_columns=None):
        extractor = YamlVariableExtractor(yaml_path)
        self.var_list = extractor.extract_variables()  # required_columns顺序和var_list一致
        if required_columns is None:
            required_columns = ['正确上下文', '标准答案']
        super().__init__(yaml_path, required_columns)

    def process(self, input_data: pd.DataFrame):
        """处理输入数据并生成提示模板列表"""
        if not isinstance(input_data, pd.DataFrame):
            raise TypeError("input_data必须为pandas.DataFrame")

        results = []
        for idx, row in input_data.iterrows():
            self._validate_row(row, idx)

            params = {var: row[col] for var, col in zip(self.var_list, self.REQUIRED_COLUMNS)}

            try:
                user_prompt = self.user_prompt.format(**params)
            except KeyError as e:
                raise ValueError(f"模板参数缺失: {e} (行号: {idx})")

            results.append((
                self.system_prompt,
                user_prompt
            ))
        return results