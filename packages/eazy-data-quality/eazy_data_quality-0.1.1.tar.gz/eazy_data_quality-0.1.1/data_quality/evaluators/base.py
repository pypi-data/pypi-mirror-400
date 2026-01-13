import yaml
import pandas as pd
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """评估处理器基类，负责加载YAML配置和通用字段校验"""

    def __init__(self, yaml_path, required_columns):
        self.yaml_path = yaml_path
        self.REQUIRED_COLUMNS = list(required_columns)
        self._load_prompts()

    def _load_prompts(self):
        """从YAML文件加载提示模板"""
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
            # 统一在基类赋值
            self.system_prompt = self.prompts.get("SYSTEM_PROMPT_TEMPLATE")
            self.user_prompt = self.prompts.get("USER_PROMPT_TEMPLATE")
        except FileNotFoundError:
            raise ValueError(f"YAML配置文件 {self.yaml_path} 未找到")
        except KeyError as e:
            raise KeyError(f"YAML文件中缺少必要字段: {e}")

    def _validate_row(self, row, row_index=None):
        """验证单行是否包含所有必要字段"""
        missing = set(self.REQUIRED_COLUMNS) - set(row.index)
        if missing:
            raise ValueError(f"字段缺失: {missing} (行号: {row_index if row_index is not None else '未知'})")

    @abstractmethod
    def process(self, input_data: pd.DataFrame):
        """处理输入数据"""
        pass