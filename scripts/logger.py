import logging
import sys

_logger = logging.getLogger("pipeline")
_logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

if not _logger.handlers:
    _logger.addHandler(handler)

_logger.propagate = False
