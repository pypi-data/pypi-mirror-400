import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional


def setup_logger(name: str, log_level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    配置并返回一个日志记录器

    参数:
        name: 日志记录器的名称
        log_level: 日志级别 (默认为 INFO)
        log_file: 日志文件路径 (如果不提供则只输出到控制台)

    返回:
        配置好的日志记录器对象
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 避免重复添加handler
    if logger.hasHandlers():
        return logger

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 如果需要写入文件
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 文件处理器 - 按大小轮转，最多保留5个备份，每个最大10MB
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger