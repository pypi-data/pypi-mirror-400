# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

import os

from flask import Blueprint, render_template, request, send_file
from flask_json import json_response

from io import BytesIO

from tg_model.tei import TEIParser

from tgp_backend.directories import generateList
from tgp_backend.project import Project
from tgp_backend.util import parse_request_data

log = logging.getLogger(__name__)

collection_routes = Blueprint("collection", __name__)


# ***TABS***
# **********
@collection_routes.route(
    "/tab_select_directories/<string:projectname>", methods=["GET", "POST"]
)
def tab_select_directories(projectname):

    project = Project(projectname)
    if request.method == "POST":
        project.project_config.update(
            tei_directories=request.form.getlist("selected_folder")
        )

    tei_directories = [
        sp["inpath"] for sp in project.project_config.get_subprojects()
    ]

    return render_template(
        "tabs/select_directories.html",
        project=project,
        selected_directories=tei_directories,
    )


@collection_routes.route(
    "/tab_manage_collections/<string:projectname>", methods=["GET"]
)
def tab_manage_collections(projectname):

    project = Project(projectname)

    return render_template(
        "tabs/manage_collections.html",
        project=project,
    )


@collection_routes.route(
    "/tab_validate_metadata/<string:projectname>", methods=["GET"]
)
@collection_routes.route(
    "/tab_validate_metadata/<string:projectname>/<string:refresh>",
    methods=["GET"],
)
def tab_validate_metadata(projectname, refresh=True):

    project = Project(projectname)
    return render_template(
        "tabs/validate_metadata.html",
        projectname=projectname,
        validation_results=project.get_validation_results(refresh=refresh),
    )


# ***OTHER***
# **********
@collection_routes.route(
    "/load_collection/<string:projectname>/<string:collectionname>",
    methods=["GET"],
)
def load_collection(projectname, collectionname):
    collection = None
    project = Project(projectname)
    collection = None
    if collectionname:
        collection = project.get_collection(collectionname)

    return render_template(
        "details/manage_collection.html",
        collectionname=collectionname,
        collection=collection["config"],
        project=project,
    )


@collection_routes.route(
    "/save_collection_attributes/<string:projectname>/<string:collectionname>",
    methods=["POST"],
)
def save_collection_attributes(projectname, collectionname):
    project = Project(projectname)
    collection = project.get_collection(collectionname)
    collection_config = collection["config"]

    multi_attribs = ["collector", "rights_holder"]
    for multi_attrib in multi_attribs:
        elements = []
        for name, url in zip(
            request.form.getlist(f"{multi_attrib}_name"),
            request.form.getlist(f"{multi_attrib}_url"),
        ):
            elements.append({"fullname": name, "url": url})
        setattr(collection_config, multi_attrib, elements)

    for attrib in ["short_title", "long_title"]:
        value = request.form.get(attrib)
        setattr(collection_config, attrib, value)

    collection_config.save()
    return load_collection(
        projectname=projectname, collectionname=collectionname
    )


@collection_routes.route(
    "/save_collection_classifications/<string:projectname>/<string:collectionname>",
    methods=["POST"],
)
def save_collection_classifications(projectname, collectionname):
    project = Project(projectname)
    collection = project.get_collection(collectionname)
    collection_config = collection["config"]

    # Save basic classifications...
    collection_config.basic_classifications = parse_request_data(
        request, "basic_classifications"
    )
    # ...and GND subjects
    collection_config.gnd_subjects = parse_request_data(
        request, "gnd_subjects"
    )

    collection_config.save()
    return load_collection(
        projectname=projectname, collectionname=collectionname
    )


@collection_routes.route(
    "/save_collection_metadata/<string:projectname>/<string:collectionname>",
    methods=["POST"],
)
def save_collection_metadata(projectname, collectionname):
    project = Project(projectname)
    collection = project.get_collection(collectionname)
    collection_config = collection["config"]
    for attrib in request.form:
        if "xpath" in attrib:
            key = attrib.replace("_xpath", "")
            type_ = "xpath"
        elif "value" in attrib:
            key = attrib.replace("_value", "")
            type_ = "value"
        if key in collection_config.xpath_or_value_attribs:
            cc_attrib = getattr(collection_config, key)
            cc_attrib[type_] = request.form.get(attrib)
        else:
            log.warning(
                f"Attribute '{attrib}' not found in collection config."
            )
    collection_config.save()
    return load_collection(
        projectname=projectname, collectionname=collectionname
    )


@collection_routes.route(
    "/download_collection_yaml/<string:projectname>/<string:collectionname>",
    methods=["GET"],
)
def download_collection_yaml(projectname, collectionname):
    project = Project(projectname)
    collection = project.get_collection(collectionname)
    return send_file(
        collection["config"].path,
        mimetype="application/yaml",
        as_attachment=True,
        download_name=f"{collectionname}.yaml",
    )


@collection_routes.route(
    "/upload_collection_yaml/<string:projectname>/<string:collectionname>",
    methods=["POST"],
)
def upload_collection_yaml(projectname, collectionname):
    collection = Project(projectname).get_collection(collectionname)

    # Get the uploaded file and save it to the collection config path
    new_config_file = request.files.get("config")
    new_config_file.save(collection["config"].path)

    # Reload the collection config
    new_collection = Project(projectname).get_collection(collectionname)

    # Preserve short and long title
    for key in ["short_title", "long_title"]:
        setattr(
            new_collection["config"], key, getattr(collection["config"], key)
        )
    new_collection["config"].save()

    # reload the collection view
    return load_collection(
        projectname=projectname, collectionname=collectionname
    )


@collection_routes.route(
    "/modal/tei_explorer/<string:projectname>/<string:collectionname>",
    methods=["GET", "POST"],
)
def modal_tei_explorer(projectname, collectionname):
    project = Project(projectname)
    # collection = project.get_collection(collectionname)
    dir_list_dict, file_list_dict = generateList(
        project.get_subproject_inpath(collectionname)
    )

    xpath = request.args.get("xpath", "")

    return render_template(
        "modal/tei_explorer.html",
        projectname=projectname,
        collectionname=collectionname,
        dir_list=dir_list_dict,
        file_list=file_list_dict,
        xpath=xpath,
        project=project,
    )


@collection_routes.route("/load_tei_content", methods=["GET"])
def load_tei_content():
    path = request.args.get("path")
    log.debug("load_tei_content path: %s" % path)
    _type = request.args.get("type")
    if path is not None:
        tei_parser = TEIParser(fullpath=path)
        if _type == "header":
            return json_response(
                value="OK",
                content=tei_parser.find(
                    "//teiHeader", node_as_text=True
                ).decode("utf-8"),
            )
        elif _type == "text":
            return json_response(
                value="OK",
                content=tei_parser.find(".//text", node_as_text=True).decode(
                    "utf-8"
                ),
            )
        return json_response(value="Unknown type requested!")


@collection_routes.route(
    "/modal/xpath_parser/<string:projectname>/<string:collectionname>",
    methods=["GET", "POST"],
)
def modal_xpath_parser(
    projectname,
    collectionname,
):
    project = Project(projectname)
    collection = project.get_collection(
        collectionname,
    )
    collection_parser = collection["parser"]

    xpath = request.args.get("xpath")
    if not xpath:
        xpath = request.form.get("xpath", "")

    return render_template(
        "modal/xpath_parser.html",
        xpath=xpath,
        projectname=projectname,
        collectionname=collectionname,
        collection_parser=collection_parser,
    )


@collection_routes.route("/export_tsv/<projectname>/<collectionname>")
def export_tsv(projectname, collectionname):
    project = Project(projectname)
    collection = project.get_collection(
        collectionname,
    )
    filepath = collection["modeler"].export()
    if os.path.isfile(filepath):
        with open(filepath, "rb") as file:
            file_content = BytesIO(file.read())

        return send_file(
            file_content,
            download_name=os.path.basename(filepath),
            as_attachment=True,
        )
