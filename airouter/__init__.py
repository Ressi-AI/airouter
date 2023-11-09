import logging
from airouter.utils.logs import get_logger

logger = get_logger("airouter", level=logging.DEBUG)

from .streamed_completion import StreamedCompletion
