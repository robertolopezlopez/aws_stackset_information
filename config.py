import configparser
import os


def load_config():
    conf = configparser.ConfigParser()
    config_path = 'setup.conf'

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"The configuration file '{config_path}' does not exist.")

    conf.read(config_path)
    print({section: dict(conf[section]) for section in conf.sections()})
    return conf
