import uuid
import sys
from loguru import logger

import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def instance_id():
    return uuid.uuid4().hex

log_fmt = (
    "<red>[kmviz:" + instance_id() + "]</red> ~ "
    "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> ~ "
    "<level>{level: <4}</level> ~ "
    "<white><bold>{message}</bold></white>"
)

def setup_logger(log_level: str="DEBUG", log_directory: str=None, with_stderr: bool=True) -> None:
    log_level = log_level.upper()
    logger.remove()

    if with_stderr:
        logger.add(sys.stderr, format=log_fmt, colorize=True, level=log_level, backtrace=False, diagnose=False)

    if log_directory:
        logger.add(f"{log_directory}/kmviz-{instance_id()}-{{time:YYYY-MM-DD_HH:mm}}", rotation="1H", format=log_fmt)

def kmv_ex(exp) -> None:
    logger.exception(exp)

def kmv_debug(*args, **kwargs) -> None:
    logger.opt(depth=1).debug(*args, **kwargs)

def kmv_info(*args, **kwargs) -> None:
    logger.opt(depth=1).info(*args, **kwargs)

def kmv_warn(*args, **kwargs) -> None:
    logger.opt(depth=1).warning(*args, **kwargs)

def kmv_error(*args, **kwargs) -> None:
    logger.opt(depth=1).error(*args, **kwargs)

