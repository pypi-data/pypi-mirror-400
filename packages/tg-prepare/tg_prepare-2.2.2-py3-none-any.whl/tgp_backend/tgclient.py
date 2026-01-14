# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de
import logging

from tgadmin.tgadmin import _crud_delete_op
from tgadmin.tgimport import TGimport

from tgclients import (
    TextgridAuth,
    TextgridConfig,
    TextgridCrud,
    TextgridSearch,
)
from tgclients.config import PROD_SERVER, TEST_SERVER

log = logging.getLogger(__name__)


class TGclient(object):
    def __init__(self, sid, instance="test", verbose=False):
        self.sid = sid

        if instance == "live":
            self.server = PROD_SERVER
        else:
            self.server = TEST_SERVER
        self.config = TextgridConfig(self.server)

        self.crud = TextgridCrud(self.config)
        self.tgauth = TextgridAuth(self.config)
        self.tgsearch = TextgridSearch(self.config, nonpublic=True)

        self._contents = {}

    def check_session(self):
        try:
            if self.sid:
                self.tgsearch.search(sid=self.sid)
                return True
        except Exception as e:
            log.error(f"Error checking session id: {self.sid} : {e}")
        return False
        # return self.tgauth.check_session(self.sid)  # returns username

    def create_project(self, name, description=""):
        log.info(f"Creating project {name}")
        return self.tgauth.create_project(self.sid, name, description)

    def clear_project(self, project_id):
        # delete content of project
        # repeat until whole content has been deleted
        # (necessary because of default limit in '_crud_delete_op')
        log.info(f"Clearing project contents {project_id}")
        content = self.get_project_content(project_id)
        handled_count = 0
        initial_count = int(content.hits)
        while handled_count < initial_count:
            for tgobj in content.result:
                # can only delete objects that are not already published
                if tgobj.object_value.generic.generated.availability == None:
                    _crud_delete_op(self, tgobj)
                handled_count += 1
            content = self.get_project_content(project_id)

    def delete_project(self, project_id):
        self.clear_project(project_id)

        log.info(f"Deleting project {project_id}")
        return self.tgauth.delete_project(self.sid, project_id)

    def get_project_content(self, project_id):
        log.warning("Deprecated: use TGclient.get_project_contents() instead")
        contents = self.tgsearch.search(
            filters=["project.id:" + project_id], sid=self.sid
        )
        return contents

    def _query_contents(self, tg_project_id):
        if not self._contents.get(tg_project_id):
            log.debug(f"Querying contents for project id: {tg_project_id}")
            try:
                self._contents[tg_project_id] = self.tgsearch.search(
                    filters=["project.id:" + tg_project_id],
                    sid=self.sid,
                )
            except Exception as e:
                log.error(f"Error querying contents for project: {e}")
                return []

        return self._contents[tg_project_id].result

    def get_project_contents(
        self,
        tg_project_id,
        public=None,
        count=False,
        category=None,
    ):
        _filter = None
        if category == "tei":
            _filter = ["text/xml"]
        elif category == "images":
            _filter = ["image/jpeg", "image/png", "image/gif"]
        elif category == "other":
            _filter = [
                "image/png",
                "text/markdown",
                "application/xslt+xml",
                "text/tg.portalconfig+xml",
            ]

        contents = self._query_contents(tg_project_id)
        results = {}
        for tgobj in contents:
            result = {}
            result["title"] = tgobj.object_value.generic.provided.title[0]
            result["tguri"] = (
                tgobj.object_value.generic.generated.textgrid_uri.value
            )
            result["mime"] = tgobj.object_value.generic.provided.format
            result["published"] = (
                tgobj.object_value.generic.generated.availability is not None
            )
            log.debug(f"Found object: {result}")

            if _filter is None or result["mime"] in _filter:
                results[result["title"]] = result
            else:
                log.info(
                    "Skipping object with unsupported mime-type: %s"
                    % result["mime"]
                )
        return len(results) if count else results

    def get_project_description(self, project_id):
        desc = self.tgauth.get_project_description(project_id)
        if desc:
            return {
                "id": project_id,
                "name": desc.name,
                "description": desc.description,
                "tei_count": self.get_project_contents(
                    project_id, count=True, category="tei"
                ),
                "img_count": self.get_project_contents(
                    project_id, count=True, category="images"
                ),
                "other_count": self.get_project_contents(
                    project_id, count=True, category="other"
                ),
                "content_count": self.get_project_contents(
                    project_id, count=True
                ),
            }
        else:
            log.warning(f"Cannot find project description for: {project_id}")

    def get_assigned_projects(self):
        log.info("Listing assigned projects")
        # TODO: this needs a better error handling to indicate user,
        # that the session-id seeems to be invalid
        try:
            _projects = self.tgauth.list_assigned_projects(self.sid)
        except Exception as e:
            log.error(f"Error listing assigned projects: {e}")
            return []

        for project_id in _projects:
            yield self.get_project_description(project_id)

    # def upload(self, filenames: list[str], project_id: str, imex_file: str):
    #     tg_importer = TGimport(
    #         self.sid,
    #         self.crud,
    #         project_id=project_id,
    #         ignore_warnings=True,
    #         imex_location=imex_file,
    #     )
    #     tg_importer.upload(filenames=filenames, threaded=True)

    def publish(self, tg_project_id):
        log.info(f"Publishing project {tg_project_id}")
        # TODO: implement publish logic in tgclients
        # see tgadmin.tgadmin.publish() tgadmin.py::Z646
        breakpoint()
