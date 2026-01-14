# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

import os
import shutil

from flask import Blueprint, render_template, request, send_file, session
from flask_json import json_response

from io import BytesIO

from tgp_backend.config import PATH_DATA
from tgp_backend.nextcloud import Nextcloud
from tgp_backend.project import Project
from tgp_backend.session_manager import SessionManagerNextcloud

log = logging.getLogger(__name__)

data_routes = Blueprint("data", __name__)


# ***TABS***
# **********
@data_routes.route("/tab-import-data/<string:projectname>", methods=["GET"])
def tab_import_data(projectname=None, project=None, error_message=None):
    if not project:
        if not projectname:
            raise ValueError("Project name must be provided.")
        else:
            project = Project(projectname)
    return render_template(
        "tabs/import_data.html",
        project=project,
        error_message=error_message,
    )


# ***DIRECT UPLOAD***
# *******************
@data_routes.route("/upload_files/<string:projectname>", methods=["POST"])
def upload_files(projectname=None):
    project = Project(projectname)
    project.file_upload(request.files.getlist("files"))

    return tab_import_data(project=project)


# ***GITHUB***
# ************
@data_routes.route("/modal/github/<projectname>", methods=["GET", "POST"])
def modal_github(projectname):
    """
    Render the Github modal.
    """
    project = Project(projectname)
    return render_template(
        "modal/github_modal.html",
        project=project,
    )


@data_routes.route("/clone_git_project/<string:projectname>", methods=["POST"])
def clone_git_project(projectname=None):
    project = Project(projectname)
    project.clone_git_project(request.form.get("github_repo"))

    return tab_import_data(project=project)


# ***NEXTCLOUD***
# ***************


def render_nextcloud_tree(projectname, items):
    """
    Render the Nextcloud tree view.
    """
    # items = items or nc.nxc_list_files_and_folders()
    project = Project(projectname)
    return render_template(
        "modal/file_explorer_nextcloud.html",
        project=project,
        items=items,
        show_checkbox=True,
        show_all_folders=True,
    )


def render_nextcloud_login(projectname, message=None):
    """
    Render the Nextcloud login form.
    """
    return render_template(
        "modal/nextcloud_login.html", projectname=projectname, message=message
    )


@data_routes.route("/modal/nextcloud/<projectname>", methods=["GET", "POST"])
@data_routes.route(
    "/modal/nextcloud/<projectname>/<logout>", methods=["GET", "POST"]
)
def modal_nextcloud(projectname, form_type=None, logout=False):

    nxc_session_manager = SessionManagerNextcloud(session)

    if logout:
        # If the user wants to log out, delete the session credentials
        nxc_session_manager.delete_nextcloud_credentials()
        return render_nextcloud_login(projectname, message="You logged out.")

    nc = Nextcloud(**nxc_session_manager.get_credentials())
    if nc.test_connection():
        # An active Nextcloud session exists, so we can use it to render
        # the tree view
        return render_nextcloud_tree(
            projectname, nc.nxc_list_files_and_folders()
        )
    elif nxc_session_manager.request_has_valid_credentials(request):
        # If credentials are provided,
        # Recreate a Nextcloud instance and test the connection
        nxc_session_manager.save_credentials(request.form)
        nc = Nextcloud(**nxc_session_manager.get_credentials())
        if nc.test_connection():
            return render_nextcloud_tree(
                projectname, nc.nxc_list_files_and_folders()
            )

        else:
            return render_nextcloud_login(
                projectname,
                message="Login failed. Please check your credentials.",
            )
    else:
        # If no valid credentials are provided, render the login form
        log.info("No valid Nextcloud credentials found, showing login form.")
        # This will clear any previous session data
        nxc_session_manager.delete_nextcloud_credentials()
        return render_nextcloud_login(projectname)


@data_routes.route("/download_nextcloud/<projectname>", methods=["POST"])
def download_nextcloud(projectname):

    nxc_session_manager = SessionManagerNextcloud(session)

    selected_option = request.form.getlist("selected_folder")

    if selected_option:
        nc = Nextcloud(**nxc_session_manager.get_credentials())
        nc.download_nxc_files(selected_option, projectname=projectname)

        return json_response(
            status=200,
            message="Downloaded.",
        )
    else:
        return json_response(
            status=400, message="No folder selected for download."
        )


# ***OTHER***
# *******************
@data_routes.route("/image/<path:filepath>")
def serve_image(filepath):
    filepath = "/" + filepath
    if os.path.isfile(filepath):
        return send_file(filepath)
    return "", 404


@data_routes.route("/file/<path:filepath>")
def serve_file(filepath):

    filepath = "/" + filepath

    if os.path.isfile(filepath):
        with open(filepath, "rb") as file:
            file_content = BytesIO(file.read())

        return send_file(
            file_content,
            download_name=os.path.basename(filepath),
            as_attachment=True,
        )


@data_routes.route("/api/delete-folder", methods=["DELETE"])
def delete_folder():
    error_message = None  # Variable für die Fehlermeldung
    try:
        path = request.form.get("path")
        projectname = request.form.get("projectname")

        if not path:
            error_message = "No path specified"
        elif not path.startswith(PATH_DATA):
            # Security check to ensure path is within allowed directory
            error_message = "Invalid path"
        elif not os.path.exists(path):
            # Check if path exists
            error_message = "Path not found"
        else:
            # Check if the path is a file or a folder
            if os.path.isfile(path):
                # Delete the file
                os.remove(path)
                log.info(f"File deleted: {path}")
            elif os.path.isdir(path):
                # Delete the folder and its contents
                shutil.rmtree(path)
                log.info(f"Folder deleted: {path}")
            else:
                error_message = "Path is neither a file nor a folder"

    except Exception as e:
        log.error(f"Error deleting path: {e}")
        error_message = f"An error occurred: {str(e)}"

    # Am Ende einmal `tab_import_data` aufrufen
    return tab_import_data(
        projectname=projectname,
        error_message=error_message,
    )
