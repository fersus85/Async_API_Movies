import json
import pathlib
import logging.config


def setup_logging():
    config_file = pathlib.Path(__file__).resolve().parent / 'log_config.json'

    with open(config_file) as f_in:
        config = json.load(f_in)
        logging.config.dictConfig(config)
