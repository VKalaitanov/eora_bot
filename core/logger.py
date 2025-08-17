import logging
from typing import Optional

logger: Optional[logging.Logger] = None

def setup_logger(name: str) -> logging.Logger:
    """
    Настройка логгера с потоковым выводом в консоль.

    Args:
        name (str): Имя логгера.

    Returns:
        logging.Logger: Настроенный объект логгера.
    """
    global logger
    if logger is None:
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
