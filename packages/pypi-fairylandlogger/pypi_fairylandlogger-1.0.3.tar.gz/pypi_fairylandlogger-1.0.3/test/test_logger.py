# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-11-29 17:41:08 UTC+08:00
"""

import os
import unittest
from pathlib import Path

from fairylandlogger import LogManager


class TestFairylandLogger(unittest.TestCase):

    def setUp(self):
        LogManager.reset()

        # print(__banner__)

    def tearDown(self):
        LogManager.reset()

    def test_logger(self):
        print(os.getcwd())
        logger = LogManager.get_logger(__name__)  # test.test_logger

        class A:

            def __init__(self):
                logger.info("Info message from A")

        A()

        logger1 = LogManager.get_logger()

        logger.info("Info message", depth=1)
        logger.debug("Debug message")
        logger.error("Error message")
        logger.warning("Warning message")
        logger.success("Success message")
        logger.critical("Critical message")

        logger1.info("Info message from another logger")
        logger1.debug("Debug message from another logger")


if __name__ == "__main__":
    unittest.main()
