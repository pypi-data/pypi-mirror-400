"""
框架级日志配置工具

这是一个**工具模块**，提供便捷的日志配置函数。
使用者可以选择使用，也可以自己配置 Python logging。

使用示例：
    from skill_scheduler.logging_config import configure_logging

    # 简单配置（输出到控制台）
    configure_logging()

    # 自定义配置
    configure_logging(
        level=logging.INFO,
        format='json',  # or 'text'
        output_file='app.log'  # 可选，相对路径
    )

    # 获取 logger
    logger = logging.getLogger(__name__)
"""
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union


class JSONFormatter(logging.Formatter):
    """JSON 格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, 'skill_name'):
            log_data["skill_name"] = record.skill_name
        if hasattr(record, 'execution_time'):
            log_data["execution_time"] = record.execution_time
        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """文本格式化器（带颜色）"""

    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
        'RESET': '\033[0m',      # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # 基本格式
        formatted = f"{level_color}[{record.levelname}]{reset} "
        formatted += f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} "
        formatted += f"{record.name}:{record.funcName}:{record.lineno} "
        formatted += f"- {record.getMessage()}"

        # 添加上下文信息
        if hasattr(record, 'skill_name'):
            formatted += f" (skill={record.skill_name})"
        if hasattr(record, 'execution_time'):
            formatted += f" (took={record.execution_time:.2f}s)"

        return formatted


def configure_logging(
    level: Union[int, str] = logging.INFO,
    format_type: str = 'text',  # 'text' or 'json'
    output_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    配置日志系统（工具函数）

    这是便捷函数，使用者也可以直接使用 Python logging 配置。

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 日志格式 ('text' 或 'json')
        output_file: 输出文件路径（可选，默认输出到 stdout）
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的备份文件数量
    """
    # 获取根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除已有的 handlers
    root_logger.handlers.clear()

    # 选择格式化器
    if format_type == 'json':
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # 添加控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # 添加文件 handler（如果指定）
    if output_file:
        from logging.handlers import RotatingFileHandler

        # 确保目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            output_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取一个命名 logger

    Args:
        name: logger 名称（通常使用 __name__）

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


# 兼容性别名
setup_logging = configure_logging  # 向后兼容


def configure_debug_logging():
    """配置调试级别日志（便捷函数）"""
    configure_logging(level=logging.DEBUG, format_type='text')


def configure_json_logging(output_file: str = 'app.log'):
    """
    配置 JSON 格式日志（便捷函数）

    Args:
        output_file: 日志文件路径（可以是相对路径）
    """
    configure_logging(
        level=logging.INFO,
        format_type='json',
        output_file=output_file
    )


# 向后兼容的别名
setup_debug_logging = configure_debug_logging
setup_production_logging = configure_json_logging
