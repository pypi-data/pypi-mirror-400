#logging_hj3415/__init__.py
from loguru import logger  # re-export for easy usage
from ._setup import setup_logging

__all__ = ["logger", "setup_logging"]