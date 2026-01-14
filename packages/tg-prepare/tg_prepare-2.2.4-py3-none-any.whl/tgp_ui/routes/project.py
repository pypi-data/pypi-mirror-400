# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

import os
import shutil

from flask import Blueprint, redirect, render_template, request
from flask import url_for as default_url_for
from flask_json import json_response


from tgp_backend.config import PATH_PROJECTS
from tgp_backend.project import Project

from .views import overview

log = logging.getLogger(__name__)

project_routes = Blueprint("project", __name__)


def get_prefix():
    return request.headers.get(
        "X-Forwarded-Prefix", request.headers.get("X-Script-Name", "")
    )


def url_for(*args, **kwargs):
    """Overrides Flask's url_for globally to include the prefix"""
    return get_prefix() + default_url_for(*args, **kwargs)


@project_routes.route("/new_project", methods=["POST"])
def new_project():
    project = Project(request.form.get("projectname"))
    project.create()
    return redirect(url_for("views.project_view", projectname=project.path))


@project_routes.route("/delete_project/<string:projectname>", methods=["POST"])
def delete_project(projectname):

    # projectname = request.form.get("projectname")
    fullpath = f"{PATH_PROJECTS}/{projectname}"

    # Delete the project
    if fullpath.strip("/") == PATH_PROJECTS.strip("/"):
        log.error(f"Cannot delete main path ({PATH_PROJECTS})!")
    elif os.path.exists(fullpath):
        shutil.rmtree(fullpath)
    else:
        log.warning("Project does not exist!")

    return overview()


@project_routes.route(
    "/modal_delete_project/<string:projectname>", methods=["POST"]
)
def modal_delete_project(projectname):
    return render_template(
        "modal/delete_project.html",
        projectname=projectname,
    )


@project_routes.route(
    "/tab-edit-project/<string:projectname>", methods=["GET", "POST"]
)
def tab_edit_project(projectname):
    project = Project(projectname)
    if request.method == "POST":
        collectors = []
        for name, url in zip(
            request.form.getlist("collector_name"),
            request.form.getlist("collector_url"),
        ):
            collectors.append({"name": name, "url": url})

        project.update(
            title=request.form["title"],
            description=request.form["description"],
            collectors=collectors,
            avatar=request.files["avatar"],
            xslt=request.files.get("xslt"),
        )
    return render_template(
        "tabs/edit_project.html",
        project=project,
    )


@project_routes.route("/delete-xslt/<string:projectname>", methods=["DELETE"])
def delete_xslt(projectname):
    project = Project(projectname)
    log.debug(f"Deleting XSLT for project {projectname}")
    project.clear_xslt()
    return json_response("OK")
