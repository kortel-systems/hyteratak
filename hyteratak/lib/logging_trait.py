#!/usr/bin/env python3
import logging


class LoggingTrait:
    def get_logger(self) -> logging.Logger:
        return logging.getLogger(type(self).__name__)

    def log_debug(self, msg: str):
        self.get_logger().debug(msg)

    def log_info(self, msg: str):
        self.get_logger().info(msg)

    def log_warning(self, msg: str):
        self.get_logger().warning(msg)

    def log_error(self, msg: str):
        self.get_logger().error(msg)

    def log_exception(self, exc):
        self.get_logger().exception(exc)

__author__ = "Kortel <hytera@kortel.systems>"
__copyright__ = "Copyright 2022 Kortel"
__license__ = "Apache License, Version 2.0"
