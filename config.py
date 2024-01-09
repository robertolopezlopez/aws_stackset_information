import configparser
import os
import logging

# Setup logging for config module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def load_config():
    conf = configparser.ConfigParser()
    config_path = 'setup.conf'

    if not os.path.exists(config_path):
        logger.error(f"The configuration file '{config_path}' does not exist.")
        raise FileNotFoundError(f"The configuration file '{config_path}' does not exist.")

    conf.read(config_path)
    logger.info({section: dict(conf[section]) for section in conf.sections()})
    return conf
