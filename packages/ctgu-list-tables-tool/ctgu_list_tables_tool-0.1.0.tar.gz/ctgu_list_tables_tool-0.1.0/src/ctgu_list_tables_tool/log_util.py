import os
from loguru import logger

#获取当前项目的绝对路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir,"logs")                #存放项目日志目录的绝对路径

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

LOG_FILE = "translation.log"

# 打印错误日志的工具类
class MyLogger:
    def __init__(self):
        self.logger = logger
        self.logger.remove()
        log_file_path = os.path.join(log_dir,LOG_FILE)
        self.logger.add(log_file_path,
                        level="DEBUG",
                        encoding = 'UTF-8',
                        format="{time:YYYYMMDD HH:mm:ss}-{process.name} | {thread.name} | {module}.{function}:{line}-{level}-{message}",
                        rotation='10 MB',
                        retention=20
                        )

    def get_logger(self):
        return self.logger


log = MyLogger().get_logger()
