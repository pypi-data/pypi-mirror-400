import yaml
import pandas as pd

from ..evaluators.base import BaseProcessor
from ..utils.extra_yaml import YamlVariableExtractor


class Evaluator:
    def __init__(self, yaml_path):
        # print(yaml_path)
        self._load_prompts(yaml_path)

    def _load_prompts(self, yaml_path):
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
            self.user_prompt = self.prompts.get("USER_PROMPT_TEMPLATE")
            self.relevance = self.prompts.get("relevance")
            self.accuracy = self.prompts.get("accuracy")
            self.directness = self.prompts.get("directness")
            self.comprehensiveness = self.prompts.get("comprehensiveness")
        except FileNotFoundError:
            raise ValueError(f"YAML配置文件 {yaml_path} 未找到")
        except KeyError as e:
            raise KeyError(f"YAML文件中缺少必要字段: {e}")

    def format(self, question, reference, answer1, answer2):
        params = {
            "relevance": self.relevance,
            "accuracy": self.accuracy,
            "directness": self.directness,
            "comprehensiveness": self.comprehensiveness,
            "question": question,
            "reference": reference,
            "answer1": answer1,
            "answer2": answer2
        }
        return self.user_prompt.format(**params)


class RewardEvalProcessor(BaseProcessor):
    """答案评估处理器"""

    def __init__(self, yaml_path='prompt/reward_prompt.yaml', required_columns=None):
        self.evaluator = Evaluator(yaml_path)
        extractor = YamlVariableExtractor(yaml_path)
        self.var_list = extractor.extract_variables()  # required_columns顺序和var_list一致
        if required_columns is None:
            required_columns = ['问题', '上下文', '答案1', '答案2']
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

    def user_format(self, question, reference, answer1, answer2):
        try:
            return self.evaluator.format(question, reference, answer1, answer2)
        except KeyError as e:
            raise ValueError(f"模板参数缺失: {e}")
