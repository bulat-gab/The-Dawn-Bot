import sys
from loguru import logger


logger.remove()
level = "INFO"

logger.add(sink=sys.stdout, level=level, colorize=True)