import logging

LOGFILE = "./logs.log"
LOGLEVEL = "DEBUG"
FMT = "[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s] %(message)s"

# Instantiate a logger
logger = logging.getLogger("root")

# Instatiate the file handler
fh = logging.FileHandler(filename=LOGFILE, mode="a", encoding="utf-8")

# Instantiate the formatter
fmt = logging.Formatter(FMT)

# Add all this to the logger
fh.setFormatter(fmt)
logger.addHandler(fh)
logger.setLevel(getattr(logging, LOGLEVEL.upper()))


def get_logger():
    return logging.getLogger(f"root.{__file__}")
