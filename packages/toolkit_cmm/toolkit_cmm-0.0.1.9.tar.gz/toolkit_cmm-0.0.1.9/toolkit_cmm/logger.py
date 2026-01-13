import logging


def create_file_std_logger(name: str, path: str, level=logging.INFO) -> logging.Logger:
    """
    Usage::

      logger = create_file_std_logger(__name__, '/tmp/main.log')
      logger.info('hello world')
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] - %(levelname)s: %(message)s"
        )
    )
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(
        logging.Formatter(
            fmt="[%(asctime)s - %(name)s - %(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(ch)
    return logger
