import os

from .csv_handler import CsvHandler
from .excel_handler import ExcelHandler
from .json_handler import JsonHandler
from .jsonl_handler import JsonlHandler
from .txt_handler import TxtHandler


class DataHandlerFactory:
    _handler_map = {
        "xlsx": ExcelHandler,
        "xls": ExcelHandler,
        "json": JsonHandler,
        "jsonl": JsonlHandler,
        "txt": TxtHandler,
        "csv": CsvHandler,
    }

    @staticmethod
    def get_handler(file_path):
        """根据文件后缀返回对应的处理器实例"""
        ext = os.path.splitext(file_path)[1][1:].lower()  # 提取后缀并转为小写
        handler_class = DataHandlerFactory._handler_map.get(ext)

        if not handler_class:
            raise ValueError(f"Unsupported file type: {ext}")

        return handler_class(file_path)