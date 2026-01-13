# -*- coding: utf-8 -*-
#
# Copyright 2021-2023, 2025 NXP
#
# SPDX-License-Identifier: MIT


import logging
import os
import time
from contextlib import suppress

# pylint: disable=too-few-public-methods


class Logger:
    @staticmethod
    def init(
        logger_name, log_name="run.log", log_type="both", log_file_permission=None
    ):
        log_path = os.path.expanduser(os.environ.get("FC_LOG_PATH", "~/.fc/log"))
        log_file = os.path.join(log_path, log_name)

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # set the global time converter to UTC
        logging.Formatter.converter = time.gmtime

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        s_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file)
        if log_file_permission:
            with suppress(Exception):
                os.chmod(log_file, log_file_permission)

        s_format = logging.Formatter(
            fmt="%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%SZ",
        )
        f_format = logging.Formatter(
            fmt="%(asctime)s %(message)s - [%(name)s:%(filename)s:%(lineno)d]",
            datefmt="%Y-%m-%d %H:%M:%SZ",
        )

        s_handler.setFormatter(s_format)
        f_handler.setFormatter(f_format)

        if log_type == "both":
            logger.addHandler(s_handler)
            logger.addHandler(f_handler)
        elif log_type == "stream_only":
            logger.addHandler(s_handler)
        elif log_type == "file_only":
            logger.addHandler(f_handler)
