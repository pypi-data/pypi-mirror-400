# -*- coding: utf-8 -*-
# Copyright (C) 2023-2024 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
import logging

import os
import re

from tgp_backend.config import MAX_FILENAME_LENGTH
from tgp_backend.util import get_file_extension

log = logging.getLogger(__name__)


def generateList(path=None):
    path = path if path else os.getcwd()
    if not path.startswith("/"):
        path = "/%s" % path
    dList = []
    fList = []
    tp_dict = {}

    log.debug("generateList - path: %s" % path)

    for name in os.listdir(path):
        fullpath = "%s/%s" % (path, name)
        if not name.startswith("."):
            if os.path.isdir(fullpath):
                dList.append({"fullpath": fullpath, "name": name})
            else:
                fList.append({"fullpath": fullpath, "name": name})
    dir_list_dict = []
    file_list_dict = []
    # curDir = os.getcwd()
    curDir = path

    for d in dList:
        if len(d["name"]) > MAX_FILENAME_LENGTH:
            dots = "..."
        else:
            dots = ""
        temp_dir = {}
        temp_dir["f"] = d["name"][0:MAX_FILENAME_LENGTH] + dots
        temp_dir["name"] = d["name"]
        temp_dir["f_url"] = re.sub("#", "|HASHTAG|", d["fullpath"])
        temp_dir["currentDir"] = curDir
        temp_dir["f_complete"] = d["fullpath"]
        temp_dir["size"] = "---"

        dir_list_dict.append(temp_dir)

    for f in fList:
        image = None
        try:
            tp = get_file_extension(f["name"])
        except Exception as e:
            log.warn(e)
            pass
        if not image:
            image = "files_icon/unknown-icon.png"
        if len(f["name"]) > MAX_FILENAME_LENGTH:
            dots = "..."
        else:
            dots = ""
        temp_file = {}
        temp_file["f"] = f["name"][0:MAX_FILENAME_LENGTH] + dots
        temp_file["name"] = f["name"]
        temp_file["name_stripped"] = f["name"].replace(f".{tp}", "")
        temp_file["f_url"] = re.sub("#", "|HASHTAG|", f["fullpath"])
        temp_file["extension"] = tp.lower()
        temp_file["currentDir"] = curDir
        temp_file["fullpath"] = f["fullpath"]
        temp_file["image"] = image
        temp_file["is_xml"] = tp.lower() == "xml"

        file_list_dict.append(temp_file)

    return dir_list_dict, file_list_dict
