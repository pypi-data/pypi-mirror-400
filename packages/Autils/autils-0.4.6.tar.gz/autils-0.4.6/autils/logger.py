import logging
import logging.handlers


class Logger:
    """
    日志工具类
    参数:
        filename: 日志文件路径
        level: 日志级别
        fmt：日期格式
        datefmt: 时间格式
        when: 日志文件的划分间隔 默认h 每小时
    """

    def __init__(self, filename, level=logging.INFO, fmt="%(asctime)s %(levelname)s %(filename)s %(lineno)d: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", when='h'):
        self._logger = logging.getLogger()
        self._logger.setLevel(level)
        ft = logging.Formatter(fmt, datefmt)
        sh = logging.StreamHandler()
        sh.setFormatter(ft)
        tm = logging.handlers.TimedRotatingFileHandler(filename, when=when)
        tm.setLevel(level)
        tm.setFormatter(ft)
        self._logger.addHandler(tm)
        self._logger.addHandler(sh)

    @property
    def logger(self):
        return self._logger
