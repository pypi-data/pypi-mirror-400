# -*- coding: utf-8 -*-
# Copyright (C) 2023 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.deimport logging

import logging

from .config import LOG_LEVEL

log = logging.getLogger(__name__)

log_config = dict(
    level=LOG_LEVEL,
    format="%(asctime)s %(name)-10s %(levelname)-4s %(message)s",
)

logging.basicConfig(**log_config)
logging.getLogger("").setLevel(LOG_LEVEL)
