import pandas as pd
from pathlib import Path
from .base import DataProcessor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class JsonlHandler(DataProcessor):
    def __init__(self, file_path: str):
        if not str(file_path).lower().endswith('.jsonl'):
            raise ValueError(f"File {file_path} is not a valid JSONL file.")
        super().__init__(file_path)

    def read(self) -> pd.DataFrame:
        try:
            logger.info(f"Reading JSONL file: {self.file_path}")
            df = pd.read_json(self.file_path, orient='records', lines=True)
            self.processed_records = len(df)
            self.log_processing_summary(logger)
            return df
        except Exception as e:
            logger.error(f"Error reading JSONL file: {str(e)}", exc_info=True)
            raise

    def write(self, df: pd.DataFrame):
        try:
            logger.info(f"Writing JSONL file: {self.file_path}")
            output_file = Path(self.file_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_json(self.file_path, orient='records', force_ascii=False, lines=True)
            self.processed_records = len(df)
            logger.info(f"Successfully wrote {len(df)} records to {self.file_path}")
        except Exception as e:
            logger.error(f"JSONL write failed: {str(e)}", exc_info=True)
            raise