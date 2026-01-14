# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

from flask import Blueprint, render_template, request, session  # type: ignore

# from flask_login import login_required  # type: ignore

from tgp_backend.project import Project

log = logging.getLogger(__name__)

main_views = Blueprint("views", __name__)


# favored route
@main_views.route("/overview", methods=["GET", "POST"])
# additional routes for compatibility
@main_views.route("/", methods=["GET"])
@main_views.route("/project", methods=["GET", "POST"])
@main_views.route("/projects", methods=["GET", "POST"])
def overview():
    return render_template("projects_main.html", sub_title="Projects Overview")


@main_views.route("/project/<string:projectname>", methods=["GET", "POST"])
def project_view(projectname=None):
    return render_template(
        "project_main.html",
        user=session.get("user", "-"),
        current_project=projectname,
        project=Project(projectname),
        tab=request.args.get("tab"),
    )


@main_views.route("/modal/container", methods=["GET"])
def modal_container():
    """
    Render a modal spinner template.
    This is used to show a loading spinner while processing requests.
    """
    return render_template("modal/empty_container.html")


@main_views.route("/tabs/container", methods=["GET"])
def tab_container():
    """
    Render a tab spinner template.
    This is used to show a loading spinner while processing requests.
    """
    return render_template("tabs/empty_container.html")


@main_views.route("/details/container", methods=["GET"])
def details_container():
    """
    Render a details spinner template.
    This is used to show a loading spinner while processing requests.
    """
    return render_template("details/empty_container.html", show_spinner=True)
