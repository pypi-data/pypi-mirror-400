""" """

import logging
import os
import time
from logging import Logger

from totp.config import LOG_DIR, LOG_LEVEL


def get_logger(name: str) -> Logger:
    t = time.localtime()
    os.makedirs(LOG_DIR, exist_ok=True)
    file = os.path.join(LOG_DIR, f"totp_{t.tm_year}{t.tm_mon}{t.tm_mday}.txt")

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(filename)s:%(lineno)s - %(message)s",
        datefmt="%Y-%m-%d_%H-%M-%S",
        filename=file,
        encoding="utf-8",
    )

    return logger
