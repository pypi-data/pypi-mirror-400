import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.WARNING,  # Default level for root logger
    format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path("/tmp/optexity.log")),
    ],
)
current_module = __name__.split(".")[0]  # top-level module/package
logging.getLogger(current_module).setLevel(logging.DEBUG)
