#!/usr/bin/evn python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
from loguru import logger
from sys import stdout


class LoguruHandler(logging.Handler):

    def __init__(self, name_list=None):
        self.name_list = name_list or []
        logging.Handler.__init__(self)

    def emit(self, record):
        if record.name not in self.name_list:
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class LoggerInit:

    def __init__(self, app):
        self.app = app

    def init(self):
        """ 日志的配置类 """
        # 这句话很关键避免多次的写入我们的日志
        logger.configure(
            handlers=[
                {
                    'sink': stdout,
                    'format': "<g>{time:YYYY-MM-DD HH:mm:ss}</g>  <level>[{level}]</level>    (<b><y>{file}</y><y>:</y><y>{line}</y></b>)<b>{module}.<e>{function}</e></b>  <level>{message}</level>"
                }
            ],
        )
        logging.basicConfig(
            handlers=[LoguruHandler(["tortoise", "tortoise.db_client"])],
            level=0, format="%(asctime)s %(filename)s %(levelname)s %(message)s ",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

