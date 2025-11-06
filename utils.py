"""
module provide utility function
"""
import logging
import os
import sys
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError
sys.path.append(os.path.join(os.path.dirname(__file__),'./.venv/ib/python3.13/site-packages/'))


def log_it(level='info', src_name=None, text=None):
    """
    Logger function
    :param level: String specifying the log level
    :param src_name: String containing the name of the logging module
    :param text: A string containing the log message
    :return: void
    """
    logging.basicConfig(level=logging.DEBUG)
    logger_name = src_name if src_name else __name__
    log_writer = logging.getLogger(logger_name)

    do_log = {
        "info": log_writer.info,
        "error": log_writer.error,
        "warning": log_writer.warning,
    }

    do_log.get(level, log_writer.debug)(text)


def read_yaml(f_path):
    """
    Read YAML file and return contents as a dict
    :param f_path: Path to file to read
    :return: File content as a dict
    """
    f_contents = {}
    yaml = YAML()

    try:
        with open(f_path, encoding="UTF-8") as f_yml:
            f_contents = yaml.load(f_yml)
    except ScannerError as e:  # NOQA
        log_it("debug", __name__, f"Bad yaml in {f_path}: {e}")
    except ParserError as e:  # NOQA
        log_it("debug", __name__, f"Bad yaml in {f_path}: {e}")

    return f_contents
