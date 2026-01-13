import pandas as pd
from pathlib import Path
from .base import DataProcessor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class TxtHandler(DataProcessor):
    def __init__(self, file_path: str, sep: str = '\t', encoding: str = 'utf-8'):
        # 检查文件扩展名
        if not str(file_path).lower().endswith('.txt'):
            raise ValueError(f"File {file_path} is not a valid TXT file.")
        super().__init__(file_path)
        self.sep = sep
        self.encoding = encoding

    def read(self) -> pd.DataFrame:
        try:
            logger.info(f"Reading TXT file: {self.file_path}")
            df = pd.read_csv(self.file_path, sep=self.sep, encoding=self.encoding)
            self.processed_records = len(df)
            self.log_processing_summary(logger)
            return df
        except Exception as e:
            logger.error(f"Error reading TXT file: {str(e)}", exc_info=True)
            raise

    def write(self, df: pd.DataFrame):
        try:
            logger.info(f"Writing TXT file: {self.file_path}")
            output_file = Path(self.file_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.file_path, sep=self.sep, index=False, encoding=self.encoding)
            self.processed_records = len(df)
            logger.info(f"Successfully wrote {len(df)} records to {self.file_path}")
        except Exception as e:
            logger.error(f"TXT write failed: {str(e)}", exc_info=True)
            raise