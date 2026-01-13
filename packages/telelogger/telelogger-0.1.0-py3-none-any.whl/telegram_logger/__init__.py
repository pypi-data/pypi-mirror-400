from .telelog import TelegramLogHandler
from .exceptions import *

__version__ = "0.1.0"

__all__ = ["TelegramLogHandler"] + [name for name in dir() if name.endswith("Error")]
