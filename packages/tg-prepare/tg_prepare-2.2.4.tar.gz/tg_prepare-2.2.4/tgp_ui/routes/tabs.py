# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

from flask import Blueprint, session
from flask_json import json_response

log = logging.getLogger(__name__)

tab_manager = Blueprint("tab_manager", __name__)


@tab_manager.route("/get_last_tab/<string:projectname>", methods=["GET"])
def get_last_tab(projectname):

    tabname = session.get(f"last_tab_{projectname}", None)

    return json_response(status=200, initial_tab=tabname or "tab-edit-project")


@tab_manager.route(
    "/set_last_tab/<string:projectname>/<string:tabname>", methods=["POST"]
)
def set_last_tab(projectname, tabname):

    if tabname:
        session[f"last_tab_{projectname}"] = tabname
        return json_response(
            response="OK",
            message=f"Last tab for project '{projectname}' set to '{tabname}'",
        )
