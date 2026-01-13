import logging

logging.basicConfig(
    format="%(name)s-%(levelname)s|%(lineno)d:  %(message)s", level=logging.INFO
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
