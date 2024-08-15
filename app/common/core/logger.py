import logging
from logging.handlers import TimedRotatingFileHandler
from app.common.core.config import config
# import requests
import json
import time
import socket
import os
import threading
import concurrent.futures

# 如果 config.FEISHU_WEBHOOK_URL 存在则为error 增加处理器
# class FeishuReporterHandler(logging.Handler):
#     def __init__(self, *args, **kwargs):
#         # 初始化父类
#         super().__init__(*args, **kwargs)
#         self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        
#     def emit(self, record):
#         if record.levelno == logging.ERROR:
#             self.executor.submit(self.post_to_feishu,record)

#     def post_to_feishu(self, record):
#         # print(record.levelname)
#         if record.levelno == logging.ERROR:
#             error_message = record.getMessage()
#             url = config.FEISHU_WEBHOOK_URL
#             headers = {
#                 "Content-Type": "application/json; charset=utf-8",
#             }
#             readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
#             host_name = socket.gethostname()
#             payload_message = {
#                 "msg_type": "interactive",
#                 "card": {
#                     "header": {
#                         "template": "purple",
#                         "title": {
#                             "content": "📋 日志通知",
#                             "tag": "plain_text"
#                         }
#                     },
#                     "config": {
#                         "wide_screen_mode": True
#                     },
#                     "elements": [
#                         {
#                             "content": f"{error_message}",
#                             "tag": "markdown"
#                         },
#                         {
#                             "tag": "hr"
#                         },
#                         {
#                             "content":f"**🅰︎ 等级：** {record.levelname} \n**📦 包名：** {record.name} \n**🔢 函数名：**{record.funcName} \n**🧳 行数：**{record.lineno} \n**🤖 服务器：** {host_name}",
#                             "tag": "markdown"
#                         },
#                         {
#                             "tag": "hr"
#                         },
#                         {
#                             "elements": [
#                                 {
#                                     "content": f"时间：{readable_time}",
#                                     "tag": "plain_text"
#                                 }
#                             ],
#                             "tag": "note"
#                         }
#                     ],
#                 }
#             }
#             response = requests.post(url=url, data=json.dumps(payload_message), headers=headers, timeout=5)

def __setup_logging():
    if not hasattr(logging.root, "configured") or not logging.root.configured:
        NOTICE_LEVEL = logging.INFO + 5
        logging.addLevelName(NOTICE_LEVEL, 'NOTICE')

        def notice(self, message, *args, **kws):
            if self.isEnabledFor(NOTICE_LEVEL):
                self._log(NOTICE_LEVEL, message, args, **kws)

        logging.Logger.notice = notice

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.getLevelName(config.LOG_LEVEL))
        root_formatter = logging.Formatter(config.LOG_FORMAT)

        error_handler = TimedRotatingFileHandler(
            config.ERROR_LOG_FILE, when='H', interval=1,
            backupCount=config.LOG_BACKUP_DAYS * 24)
        error_handler.setFormatter(root_formatter)
        error_handler.addFilter(lambda record: record.levelno != NOTICE_LEVEL)
        
        root_logger.addHandler(error_handler)
        # if config.FEISHU_WEBHOOK_URL != "":
        #     root_logger.addHandler(FeishuReporterHandler())


        notice_handler = TimedRotatingFileHandler(
            config.NOTICE_LOG_FILE, when='H', interval=1,
            backupCount=config.LOG_BACKUP_DAYS * 24)
        notice_handler.setLevel(NOTICE_LEVEL)
        notice_handler.setFormatter(root_formatter)
        notice_handler.addFilter(lambda record: record.levelno == NOTICE_LEVEL)
        root_logger.addHandler(notice_handler)

        logging.root.configured = True


__setup_logging()


def get_logger(name):
    return logging.getLogger(name)
