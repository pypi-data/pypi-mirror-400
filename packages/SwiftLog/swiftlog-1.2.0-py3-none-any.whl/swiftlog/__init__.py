import os
from datetime import datetime

from .Logger import Logger

_logger: Logger = Logger("general")


def log(level_name: str, message: str):
    _logger.log(level_name, message)


def INFO(message: str):
    _logger.INFO(message)


def WARNING(message: str):
    _logger.WARNING(message)


def ERROR(message: str):
    _logger.ERROR(message)


def CRITICAL(message: str):
    _logger.CRITICAL(message)
