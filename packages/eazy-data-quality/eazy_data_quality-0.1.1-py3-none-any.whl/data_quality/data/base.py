# data/base.py
from abc import ABC, abstractmethod
import os
import pandas as pd


class DataProcessor(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.processed_records = 0

    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        读取文件内容，返回 pandas.DataFrame
        """
        pass

    @abstractmethod
    def write(self, df: pd.DataFrame):
        """
        接收 pandas.DataFrame，写入到文件
        """
        pass

    def log_processing_summary(self, logger):
        """记录处理摘要的通用方法"""
        logger.info(f"Successfully processed {self.processed_records} records from {self.file_path}")