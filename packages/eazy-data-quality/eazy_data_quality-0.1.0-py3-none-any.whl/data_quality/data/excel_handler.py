# data/excel_handler.py
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from .base import DataProcessor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ExcelHandler(DataProcessor):
    def __init__(
            self,
            file_path: str,
            na_values: Optional[List[str]] = None,
            keep_default_na: bool = False
    ):
        """
        Excel 数据处理器

        :param file_path: Excel文件路径
        :param na_values: 识别为缺失值的字符串列表
        :param keep_default_na: 是否保留pandas默认的NA识别
        """
        super().__init__(file_path)
        self.na_values = na_values if na_values is not None else ['', 'NA', 'N/A']
        self.keep_default_na = keep_default_na

    def read(self) -> pd.DataFrame:
        """
        读取 Excel 文件所有工作表，合并为一个 DataFrame，增加 _source_sheet 字段
        """
        try:
            logger.info(f"Starting Excel processing: {Path(self.file_path).name}")

            dfs = pd.read_excel(
                self.file_path,
                sheet_name=None,
                na_values=self.na_values,
                keep_default_na=self.keep_default_na
            )

            all_data = []
            for sheet_name, df in dfs.items():
                if df.empty:
                    continue
                df = df.dropna(how='all')  # 删除全空行
                df['_source_sheet'] = sheet_name
                all_data.append(df)

            if all_data:
                result_df = pd.concat(all_data, ignore_index=True)
            else:
                result_df = pd.DataFrame()

            self.processed_records = len(result_df)
            self.log_processing_summary(logger)
            return result_df

        except pd.errors.EmptyDataError:
            logger.warning(f"Empty Excel file: {self.file_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}", exc_info=True)
            raise

    def write(self, df: pd.DataFrame):
        """
        将 DataFrame 写入 Excel 文件。
        如果包含 '_source_sheet' 字段，则按 sheet 拆分写入；否则写入一个 sheet。
        """
        try:
            logger.info(f"Starting Excel write to: {self.file_path}")

            output_file = Path(self.file_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if df.empty:
                logger.warning("Input DataFrame is empty. No data will be written.")
                # 仍然创建一个空Excel文件
                pd.DataFrame().to_excel(self.file_path, index=False)
                return

            # 若有 _source_sheet 字段，按 sheet 拆分写入
            if '_source_sheet' in df.columns:
                grouped = df.groupby('_source_sheet', sort=False)
                with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                    for sheet_name, group_df in grouped:
                        # 排除 _source_sheet 字段
                        group_df = group_df.drop(columns=['_source_sheet'], errors='ignore')
                        group_df.to_excel(writer, sheet_name=str(sheet_name), index=False)
                        logger.debug(f"Wrote sheet [{sheet_name}]: {len(group_df)} rows")
            else:
                # 没有 _source_sheet 字段，直接写入单一sheet
                df.to_excel(self.file_path, index=False)
                logger.debug(f"Wrote single sheet: {len(df)} rows")

            self.processed_records = len(df)
            logger.info(f"Successfully wrote {len(df)} records to {self.file_path}")

        except Exception as e:
            logger.error(f"Excel write failed: {str(e)}", exc_info=True)
            raise

    def read_group(self):
        """
        读取并返回 groupby(['问题', '参考信息'])对象，兼容老代码。
        """
        df = self.read()
        if df.empty:
            logger.warning(f"No valid data in Excel file: {self.file_path}")
            self.processed_records = 0
            self.log_processing_summary(logger)
            return None
        grouped = df.groupby(['问题', '参考信息'])
        self.processed_records = len(df)
        self.log_processing_summary(logger)
        return grouped