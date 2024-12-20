import sys
import urllib3

from utils.loguru_logger import logger


def setup():
    level = "INFO"

    urllib3.disable_warnings()
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        colorize=True,
        format="<light-cyan>{time:HH:mm:ss}</light-cyan> | <level> {level: <8}</level> | - <white>{"
        "message}</white>",
    )
    logger.add("./logs/logs.log", rotation="1 day", retention="7 days")


