# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

from flask import Blueprint, render_template, request

from tgp_backend.project import Project

log = logging.getLogger(__name__)

publication_routes = Blueprint("publication", __name__)


@publication_routes.route(
    "/tab-prepare-upload/<string:projectname>", methods=["GET"]
)
def tab_upload(projectname):
    project = Project(projectname)
    return render_template(
        "tabs/upload.html",
        project=project,
    )


@publication_routes.route(
    "/tab-check-result/<string:projectname>", methods=["GET"]
)
def tab_check_result(projectname):
    project = Project(projectname)

    images = [
        {
            "filename": "01_title.png",
            "alt": "Confirm Title",
            "caption": "Confirm your project's title and short description",
            "icon": "bi-card-heading text-primary",
        },
        {
            "filename": "02_avatar.png",
            "alt": "Check Avatar Image",
            "caption": "Check that your avatar image looks correct.",
            "icon": "bi-person-circle text-secondary",
        },
        {
            "filename": "03_readme.png",
            "alt": "Check README.md",
            "caption": "Check your README.md at your landing page.",
            "icon": "bi-file-earmark-text text-success",
        },
        {
            "filename": "04_count_objects.png",
            "alt": "Check Number of Imported Objects",
            "caption": "Confirm that the number of imported objects — especially XML files and collections — is correct.",
            "icon": "bi-123 text-info",
        },
        {
            "filename": "05_facets.png",
            "alt": "Check Facets and Metadata",
            "caption": "Ensure that all facets and metadata are displayed correctly.",
            "icon": "bi-ui-checks-grid text-warning",
        },
        {
            "filename": "06_transformation.png",
            "alt": "Check TEI to HTML Transformation",
            "caption": "Check that some of your TEI files are being correctly transformed into HTML.",
            "icon": "bi-filetype-html text-danger",
        },
        # {"filename": "", "alt": "", "caption": ""},
    ]

    return render_template(
        "tabs/check_upload.html",
        project=project,
        images=images,
    )


@publication_routes.route(
    "/tab-publication/<string:projectname>", methods=["GET"]
)
def tab_publication(projectname):
    project = Project(projectname)
    return render_template(
        "tabs/publication.html",
        project=project,
    )


class TGProjectHandler:
    def __init__(self, projectname, instance, action="upload"):
        self.project = Project(projectname)
        self.tg_project = self.project.get_tgp(instance)
        self.instance = instance
        self.action = action

    def _render_template(self, action="upload", **kwargs):
        return render_template(
            f"includes/{self.action}_form.html",
            project=self.project,
            tg_project=self.tg_project,
            instance=self.instance,
        )

    def save_session_id(self, session_id):
        self.tg_project.tg_session_id = session_id
        return self._render_template()

    def save_tg_project_id(self, tg_project_id):
        self.tg_project.tg_project_id = tg_project_id
        return self._render_template()

    def delete_tg_project(self, tg_project_id):
        self.tg_project.delete_tg_project(tg_project_id)
        return self._render_template()

    def clear_tg_project(self, tg_project_id):
        self.tg_project.clear_tg_project(tg_project_id)
        return self._render_template()

    def create_tg_project(self, tg_projectname):
        self.tg_project.create_tg_project(tg_projectname)
        return self._render_template()

    def upload_tg_project(self):
        self.tg_project.upload_tg_project()
        return self._render_template()

    def upload_collection(self, collection_name):
        self.tg_project.upload_collection(collection_name=collection_name)
        return self._render_template()

    def upload_other_files(self):
        self.tg_project.upload_other_files()
        return self._render_template()

    def publish_project(self):
        self.tg_project.publish_project()
        return self._render_template()


@publication_routes.route(
    "/save_session_id/<string:projectname>/<string:instance>/<string:action>",
    methods=["POST"],
)
def save_session_id(projectname, instance, action):
    return TGProjectHandler(projectname, instance, action).save_session_id(
        request.form.get("tg_auth_session_id")
    )


@publication_routes.route(
    "/save_tg_project_id/<string:projectname>/<string:instance>/<string:tg_project_id>/<string:action>",
    methods=["POST"],
)
def save_tg_project_id(projectname, instance, tg_project_id, action):
    return TGProjectHandler(projectname, instance, action).save_tg_project_id(
        tg_project_id
    )


@publication_routes.route(
    "/delete_tg_project_id/<string:projectname>/<string:instance>/<string:tg_project_id>/<string:action>",
    methods=["POST"],
)
def delete_tg_project_id(projectname, instance, tg_project_id, action):
    return TGProjectHandler(projectname, instance, action).delete_tg_project(
        tg_project_id
    )


@publication_routes.route(
    "/clear_tg_project/<string:projectname>/<string:instance>/<string:tg_project_id>/<string:action>",
    methods=["POST"],
)
def clear_tg_project(projectname, instance, tg_project_id, action):
    return TGProjectHandler(projectname, instance, action).clear_tg_project(
        tg_project_id
    )


@publication_routes.route(
    "/create_tg_project/<string:projectname>/<string:instance>/<string:action>",
    methods=["POST"],
)
def create_tg_project(projectname, instance, action):
    return TGProjectHandler(projectname, instance, action).create_tg_project(
        request.form.get("tg_projectname")
    )


@publication_routes.route(
    "/upload_project/<string:projectname>/<string:instance>/<string:action>",
    methods=["POST"],
)
def upload_project(projectname, instance, action):
    return TGProjectHandler(projectname, instance, action).upload_tg_project()


@publication_routes.route(
    "/upload_collection/<string:projectname>/<string:collection>/<string:instance>/<string:action>",
    methods=["POST"],
)
def upload_collection(projectname, collection, instance, action):
    return TGProjectHandler(projectname, instance, action).upload_collection(
        collection
    )


@publication_routes.route(
    "/upload_other_files/<string:projectname>/<string:instance>/<string:action>",
    methods=["POST"],
)
def upload_other_files(projectname, instance, action):
    return TGProjectHandler(projectname, instance, action).upload_other_files()


@publication_routes.route(
    "/publish_project/<string:projectname>/<string:instance>/<string:action>",
    methods=["POST"],
)
def publish_project(projectname, instance, action):
    return TGProjectHandler(projectname, instance, action).publish_project()
