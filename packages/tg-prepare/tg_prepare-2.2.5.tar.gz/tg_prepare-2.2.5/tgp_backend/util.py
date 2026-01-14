# -*- coding: utf-8 -*-
# Copyright (C) 2023-2024 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
import logging

import os
import re

from collections import defaultdict

from .config import get_config_value

log = logging.getLogger(__name__)


def config(*args, **kwargs):
    log.warning(
        """
            Using deprecated config function.
            Please use tgp_backend.config.get_config_value instead.
        """
    )
    return get_config_value(*args, **kwargs)


def cli_startup(log_level=logging.INFO, log_file=None):
    log_config = dict(
        level=log_level,
        format="%(asctime)s %(name)-10s %(levelname)-4s %(message)s",
    )
    if log_file:
        log_config["filename"] = log_file

    logging.basicConfig(**log_config)
    logging.getLogger("").setLevel(log_level)


def get_file_extension(fname):
    found_extension = re.search("\.[A-Za-z0-9]*$", fname, re.IGNORECASE)
    if found_extension:
        return found_extension[0][1:].lower()
    return ""


def list_files_and_folders(path, get_selectable=False):

    selectable_folders = []

    def recursive_list(dir_path, depth=0):
        items = []
        for entry in os.scandir(dir_path):
            if entry.name.startswith("."):
                continue

            if entry.is_dir():
                children = recursive_list(entry.path, depth=depth + 1)
                contains_xml = any(
                    f.get("name", "").endswith(".xml") for f in children
                )
                item = {
                    "type": "folder",
                    "name": entry.name,
                    "depth": depth,
                    "path": entry.path,
                    "contains_xml": contains_xml,
                    "children": {"count": len(children), "list": children},
                }
                items.append(item)
                if contains_xml:
                    selectable_folders.append(item)
            else:
                items.append(
                    {
                        "type": "file",
                        "name": entry.name,
                        "depth": depth,
                        "path": entry.path,
                    }
                )
        return items

    result = recursive_list(path)
    if get_selectable:
        return selectable_folders
    else:
        return result


def get_selectable_folders(path):

    return list_files_and_folders(path, get_selectable=True)


def remove_empty_strings_from_dict(d):
    for key in d:
        if d[key] == "":
            d[key] = None
    return d


def parse_request_data(request, attrib_prefix):
    """
    Processes form data and creates a list of dictionaries
    for the specified attributes.
    """
    grouped_data = defaultdict(lambda: defaultdict(list))

    # Group data based on prefix
    for key in request.form.keys():
        if key.startswith(attrib_prefix):
            try:
                _, field, data_type = key.split("-")
                grouped_data[field][data_type] = request.form.getlist(key)
            except ValueError:
                log.warning(
                    f"Invalid key format: {key}. Expected format: '{attrib_prefix}-field-data_type'."
                )
                continue  # Skip invalid keys

    # Transform grouped data into desired structure
    max_length = max(len(data["xpath"]) for data in grouped_data.values())
    return [
        {
            field: {
                "xpath": data["xpath"][i],
                "value": data["value"][i],
            }
            for field, data in grouped_data.items()
        }
        for i in range(max_length)
    ]
