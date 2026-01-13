import pandas as pd
from pathlib import Path
from .base import DataProcessor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class JsonHandler(DataProcessor):
    def __init__(self, file_path: str, orient: str = 'records', lines: bool = False):
        # 检查文件扩展名
        if not str(file_path).lower().endswith('.json'):
            raise ValueError(f"File {file_path} is not a valid JSON file.")
        super().__init__(file_path)
        self.orient = orient
        self.lines = lines

    def read(self) -> pd.DataFrame:
        try:
            logger.info(f"Reading JSON file: {self.file_path}")
            df = pd.read_json(self.file_path, orient=self.orient, lines=self.lines)
            self.processed_records = len(df)
            self.log_processing_summary(logger)
            return df
        except Exception as e:
            logger.error(f"Error reading JSON file: {str(e)}", exc_info=True)
            raise

    def write(self, df: pd.DataFrame):
        try:
            logger.info(f"Writing JSON file: {self.file_path}")
            output_file = Path(self.file_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_json(self.file_path, orient=self.orient, force_ascii=False, lines=self.lines)
            self.processed_records = len(df)
            logger.info(f"Successfully wrote {len(df)} records to {self.file_path}")
        except Exception as e:
            logger.error(f"JSON write failed: {str(e)}", exc_info=True)
            raise