import importlib.metadata
import logging

VERSION = importlib.metadata.version("teklia-toolbox")

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO
)
