# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import logging

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("Ausonia")
        self.logger.setLevel(logging.INFO)

        # Check if the logger already has handlers to avoid duplicates
        if not self.logger.hasHandlers():
            self.formatter = logging.Formatter(
                "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S"
            )
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setLevel(logging.INFO)
            self.stream_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.stream_handler)

    def info(self, message: str):
        self.logger.info(message)

    def warn(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
