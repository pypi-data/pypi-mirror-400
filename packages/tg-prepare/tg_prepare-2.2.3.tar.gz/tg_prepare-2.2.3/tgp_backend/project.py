# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de
import logging

import json
import os
import subprocess

from datetime import datetime

from tg_model.collection import CollectionModeler  # type: ignore
from tg_model.project import Project as ProjectHandler  # type: ignore
from tg_model.tei import TEIParser  # type: ignore

from tg_model.yaml import (  # type: ignore
    CollectionConfig,
    CollectionConfigTemplate,
    ProjectConfigTemplate,
    ProjectConfig,
)

from tgp_backend.config import MAIN_PATH
from tgp_backend.tgclient import TGclient
from tgp_backend.util import (
    list_files_and_folders,
    get_selectable_folders,
)

log = logging.getLogger(__name__)


class Project(object):
    def __init__(self, path):
        self.path = path
        self._project_config = None
        self._collections = None
        self._nextcloud = None

    @property
    def name(self):
        log.warning("Project.name is deprecated, use Project.path instead")
        return self.path

    @property
    def fullpath(self):
        return os.path.join(MAIN_PATH, self.path)
        # return f"{MAIN_PATH}/{self.path}"

    @property
    def title(self):
        return self.project_config.title

    @property
    def description(self):
        return self.project_config.description

    @property
    def collectors(self):
        return self.project_config.collectors

    @property
    def path_data(self):
        return os.path.join(self.fullpath, "data")

    @property
    def path_metadata(self):
        return os.path.join(self.fullpath, "metadata")

    @property
    def path_otherfiles(self):
        return os.path.join(self.path_metadata, "other_files")

    def create(self):
        if not os.path.exists(self.fullpath):
            os.makedirs(self.fullpath)
            os.makedirs(self.path_data)
            os.makedirs(self.path_metadata)
        else:
            log.warning("Project already exists!")

    @property
    def avatar(self):
        if self.project_config.avatar:
            return os.path.join(
                self.path_otherfiles, self.project_config.avatar
            )

    @property
    def xslt(self):
        if self.project_config.xslt:
            return os.path.join(self.path_otherfiles, self.project_config.xslt)

    def save_avatar(self, file):
        if file.filename and file.filename != "":
            file.save(os.path.join(self.path_otherfiles, file.filename))
            self.project_config.avatar = file.filename

    def save_xslt(self, file):
        if file.filename and file.filename != "":
            file.save(os.path.join(self.path_otherfiles, file.filename))
            self.project_config.xslt = file.filename

    def clear_xslt(self):
        self.project_config.xslt = None
        self.project_config.save()

    def update(self, title, description, collectors, avatar, xslt):
        self.project_config.title = title
        self.project_config.description = description
        self.project_config.collectors = collectors

        if avatar:
            self.save_avatar(avatar)
        self.save_xslt(xslt)

        self.project_config.save()

    def clone_git_project(self, url):
        repo_name = url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(self.path_data, repo_name)

        if not os.path.exists(repo_path):
            subprocess.run(["git", "clone", url, repo_path])
        else:
            log.info("Repository already exists!")

    def file_upload(self, files):
        for file in files:
            if file:
                filename = file.filename
                filepath = os.path.join(self.path_data, filename)
                directory = os.path.dirname(filepath)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file.save(filepath)

    def list_files_and_folders(self):
        return list_files_and_folders(self.path_data)

    def get_selectable_folders(self):
        selectable_folders = get_selectable_folders(self.path_data)
        for folder in selectable_folders:
            folder["relative_path"] = folder["path"].replace(
                self.path_data, ""
            )
        return selectable_folders

    @property
    def main_config(self):
        log.warning(
            "Project.main_config is deprecated, use Project.project_config instead"
        )
        return self.project_config

    @property
    def project_config(self):
        if not self._project_config:
            self._project_config = ProjectConfig(
                projectpath=self.path_metadata
            )
            if not self._project_config.exists():
                self._project_config = ProjectConfigTemplate(
                    self.path_metadata
                ).render()
                self._project_config.title = self.path
                self._project_config.save()

        return self._project_config

    @property
    def project_handler(self):
        return ProjectHandler(self.path_metadata)

    def get_subproject_inpath(self, name):
        for subproject in self.project_config.content["subprojects"]:
            if subproject["name"] == name:
                return subproject["inpath"]
        return None

    def _set_collections(self):
        self._collections = {}
        if self.project_config.exists():
            for subproject in self.project_config.content["subprojects"]:
                collection_config = CollectionConfig(subproject["basepath"])
                if not collection_config.exists():
                    collection_config = CollectionConfigTemplate(
                        projectpath=self.path_metadata,
                        subproject=subproject,
                        files=[
                            TEIParser(fullpath=file)
                            for file in subproject["files"]
                        ],
                    ).render(overwrite=False)

                c_modeler = CollectionModeler(subproject, self.path_metadata)
                self._collections[subproject["name"]] = {
                    "config": collection_config,
                    "paths": subproject,
                    "parser": CollectionParser(collection_config),
                    "modeler": c_modeler,
                    "path": c_modeler.get_collection_path(),
                }

    @property
    def collections(self):
        if self._collections is None:
            self._set_collections()
        return self._collections

    def get_collection_paths(self):
        return [c["path"] for c in self.collections.values()]

    def get_collection(self, title):
        return self.collections.get(title)

    def get_collection_parser(self, collection):
        return CollectionParser(collection)

    def get_tgp(self, instance):
        return TGProject(self, instance)

    def _save_validation_results(self, results, filepath):
        """
        Saves the validation results to a JSON file.
        Adds the date of the last execution.
        """
        results["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        log.info(f"Validation results saved to {filepath}")

    def _run_validation(self, file_attributes=False):
        validation_results = self.project_handler.validate(
            file_attributes=file_attributes
        )
        self._save_validation_results(validation_results, self.validation_file)
        return validation_results

    @property
    def validation_file(self):
        """
        Returns the path to the validation results file.
        """
        return os.path.join(self.path_metadata, "validation_results.json")

    def get_validation_results(self, refresh=False, file_attributes=False):
        """
        Returns stored validation results.
        If no results are saved or `refresh=True`, a new validation will
        be performed.
        """
        # If `refresh` is set or file doesn't exist, perform new validation
        if refresh or not os.path.exists(self.validation_file):
            validation_results = self._run_validation(
                file_attributes=file_attributes
            )
        else:
            # Load results from file
            with open(self.validation_file, "r", encoding="utf-8") as f:
                validation_results = json.load(f)

        if "ready_for_publication" not in validation_results:
            validation_results = self._run_validation(
                file_attributes=file_attributes
            )
        return validation_results


class TGProject(object):

    def __init__(self, project, instance):
        if isinstance(project, Project):
            self.project = project
        else:
            raise ValueError(
                "Project must be an instance of Project or a project path."
            )
        self.instance = instance
        self.project_config = self.project.project_config
        self.collections = self.project.collections
        self._tg_client = None
        self._tg_session_id = None
        self._tg_project_id = None

    def check_session(self):
        return self.tg_client.check_session()

    @property
    def tg_session_id(self):
        if not self._tg_session_id:
            self._tg_session_id = self.project_config.get_tg_session_id(
                self.instance
            )
        return self._tg_session_id

    @tg_session_id.setter
    def tg_session_id(self, session_id):
        self._tg_session_id = session_id
        self.project_config.set_tg_session_id(session_id, self.instance)

    @property
    def imex_file(self):
        return os.path.join(self.project_config.projectpath, "config.imex")

    @property
    def tg_project_id(self):
        if not self._tg_project_id:
            self._tg_project_id = self.project_config.get_tg_project_id(
                self.instance
            )
        return self._tg_project_id

    @tg_project_id.setter
    def tg_project_id(self, project_id):
        self._tg_project_id = project_id
        self.project_config.set_tg_project_id(project_id, self.instance)

    @property
    def tg_client(self):
        if not self._tg_client:
            self._tg_client = TGclient(self.tg_session_id, self.instance)
        return self._tg_client

    def create_tg_project(self, name, description=""):
        # def create_tg_project(self, name, instance="test", description=""):
        if not self.tg_session_id:
            return []
        tg_project_id = self.tg_client.create_project(name, description)
        if tg_project_id:
            self.tg_project_id = tg_project_id

    def clear_tg_project(self, tg_project_id):
        # def clear_tg_project(self, tg_project_id, instance="test"):
        if not self.tg_session_id:
            return False
        # clear contents of tg-project at textgrid server
        self.tg_client.clear_project(tg_project_id)

        # remove imex files locally
        for c in self.project.collections.values():
            c["modeler"].remove_imex_file()
        self.project_config.other_files.remove_imex_file()

        return True

    def delete_tg_project(self, tg_project_id):
        # def delete_tg_project(self, tg_project_id, instance="test"):
        if not self.tg_session_id:
            return False
        # delete tg-project at textgrid server
        res = self.tg_client.delete_project(tg_project_id)
        # delete tg-project at local config if successful AND
        # is the currently defined project_id
        if res and tg_project_id == self.tg_project_id:
            self.tg_project_id = None
        return True

    def get_tg_projects(self):
        # def get_tg_projects(self, instance="test"):
        if not self.tg_session_id:
            return []
        return self.tg_client.get_assigned_projects()

    def get_tg_project(self, project_id):
        if self.tg_session_id:
            return self.tg_client.get_project_description(project_id)

    def upload_tg_project(self):
        # def upload_tg_project(self, instance="test"):
        if not self.tg_session_id:
            return False

        for c_name in self.collections:
            collection = self.collections[c_name]
            # step 1: create required metadata
            collection["modeler"].render_collection()
            # step 2: upload collection to textgrid server
            collection["modeler"].upload(
                tg_session_id=self.tg_session_id,
                tg_project_id=self.tg_project_id,
                tg_server=self.instance,
            )

    def upload_collection(self, collection_name):
        # def upload_collection(self, collection_name, instance="test"):
        if not self.tg_session_id:
            return False
        log.info("Uploading collection (%s)..." % collection_name)
        collection = self.project.get_collection(collection_name)
        # step 1: create required metadata
        collection["modeler"].render_collection()
        # step 2: upload collection to textgrid server
        collection["modeler"].upload(
            tg_session_id=self.tg_session_id,
            tg_project_id=self.tg_project_id,
            tg_server=self.instance,
        )

    def upload_other_files(self):
        # def upload_other_files(self, instance="test"):
        if not self.tg_session_id:
            return False
        log.info("Uploading other files...")
        self.project_config.other_files.upload(
            tg_session_id=self.tg_session_id,
            tg_project_id=self.tg_project_id,
            tg_server=self.instance,
        )

    def get_project_contents(self):
        return self.tg_client.get_project_contents(self.tg_project_id)

    def publish_project(self):
        # def publish_project(self, instance="test"):
        if not self.tg_session_id:
            return False
        log.info("Publishing project...")
        self.tg_client.publish(self.tg_project_id)


class CollectionParser(object):

    def __init__(self, collection):
        self.collection = collection
        self._elements = None

    @property
    def elements(self):
        if self._elements is None:
            self._elements = []
            for file in self.collection.elements:
                self._elements.append(
                    {
                        "file": file,
                        "tei_parser": TEIParser(fullpath=file["fullpath"]),
                    }
                )
        return self._elements

    def test_xpath(self, xpath):
        results = []
        for element in self.elements:
            result = element["tei_parser"].find(xpath)
            if result is not None:
                results.append(
                    {
                        "filename": element["file"]["filename"],
                        "result": result,
                    }
                )
        return {
            "results": results,
            "count": {
                "total": len(self.collection.elements),
                "found": len(results),
                "percentage": round(
                    len(results) / len(self.collection.elements) * 100
                ),
            },
        }
