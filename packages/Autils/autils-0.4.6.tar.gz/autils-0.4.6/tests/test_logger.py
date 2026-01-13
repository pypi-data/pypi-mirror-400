from autils import Logger
import logging


logger = Logger("test.log", level=logging.DEBUG, when='d').logger

logger.debug("debug")
logger.info("info")
logger.error("error")
logger.warn("warn")
