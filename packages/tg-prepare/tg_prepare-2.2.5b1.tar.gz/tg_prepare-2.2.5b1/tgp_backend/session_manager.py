# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de

import logging

log = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, session):
        self.session = session


class SessionManagerNextcloud(SessionManager):

    def save_credentials(self, form_data):
        log.info("Saving credentials to session")
        self.session["nextcloud"] = {
            "username": form_data.get("nextcloud_user"),
            "password": form_data.get("nextcloud_password"),
            "url": form_data.get("nextcloud_url"),
            "folder": form_data.get("nextcloud_folder", ""),
        }

    def get_credentials(self):
        log.info("Retrieving credentials from session")
        return self.session.get("nextcloud", {})

    def delete_nextcloud_credentials(self):
        log.info("Deleting credentials from session")
        self.session.pop("nextcloud", None)

    def request_has_valid_credentials(self, request):
        """
        Check if the request contains valid Nextcloud credentials.
        """
        relevant_form_keys = [
            "nextcloud_url",
            "nextcloud_user",
            "nextcloud_password",
        ]
        relevant_form_values = [
            request.form.get(key) for key in relevant_form_keys
        ]
        return all(relevant_form_values)
