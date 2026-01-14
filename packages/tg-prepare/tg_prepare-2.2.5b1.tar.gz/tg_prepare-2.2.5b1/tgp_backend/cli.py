# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

import click
from .util import cli_startup

log = logging.getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", "-d", is_flag=True, default=False)
@click.option("--login", default="rk")
@click.pass_context
def main(ctx, debug, login):
    cli_startup(log_level=debug and logging.DEBUG or logging.INFO)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["login"] = login
