from pathlib import Path
from loguru import logger
from config import log_path


def is_file_exists(file_path: str) -> bool:
    """
    检测文件是否存在

    :param file_path: 文件路径
    :return bool: 如果文件存在，则返回 True；否则返回 False。
    """
    return Path(file_path).is_file()


def ensure_directory_exists_for_file(file_path: str) -> None:
    """确保文件所在目录存在，不存在则创建"""
    # 获取文件路径的目录
    directory = Path(file_path).parent
    # 确保目录存在
    directory.mkdir(parents=True, exist_ok=True)


def get_configured_logger(log_folder=log_path, log_file_prefix="log"):
    # 确保日志文件夹存在
    log_folder_path = Path(log_folder)
    log_folder_path.mkdir(parents=True, exist_ok=True)

    # 创建日志文件路径，使用每日轮转
    log_file = log_folder_path / f"{log_file_prefix}_{{time:YYYY_MM_DD}}.log"

    # 配置日志记录器
    logger.add(log_file, rotation="00:00", retention=None)

    return logger


if __name__ == '__main__':
    config_file_path = './config.py'
    if is_file_exists(config_file_path):
        print(f"文件 {config_file_path} 存在")
    else:
        print(f"文件 {config_file_path} 不存在")

    log_file_path = './log/2021-09-01.log'
    ensure_directory_exists_for_file(log_file_path)
    if is_file_exists(log_file_path):
        print(f"文件 {log_file_path} 存在")
    else:
        print(f"文件 {log_file_path} 不存在")

    log = get_configured_logger()
    log.debug(f"{log_path}")
