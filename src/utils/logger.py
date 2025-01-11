import logging
import logging.config
import yaml
import os

def setup_logging(default_path='config/logging.yaml', default_level=logging.INFO):
    if os.path.exists(default_path):
        with open(default_path, 'r') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

logger = logging.getLogger(__name__)
