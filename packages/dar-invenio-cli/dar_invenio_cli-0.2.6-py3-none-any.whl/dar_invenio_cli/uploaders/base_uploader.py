#
# Copyright (C) 2025 Masaryk University
#
# DAR-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Base uploader class for the MU Invenio CLI application."""

import abc

import requests

from dar_invenio_cli.config import Config


def get_file_entity(entries, file_name):
    for entry in entries:
        if entry.get("key") == file_name:
            return entry
    return None


class BaseUploader:
    def __init__(self, config: Config, record_id: str):
        self.config = config
        self.record_id = record_id
        self.headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }

    @abc.abstractmethod
    def upload(self, file_path):
        pass

    def init_file(self, file_name, init_data=None):
        init_url = f"{self.config.base_model_url}/{self.record_id}/draft/files"
        try:
            response = requests.post(
                init_url,
                json=init_data,
                headers=self.headers,
                verify=False
            )
            if response.status_code != 201:
                return {}
            entries = response.json()["entries"]
            return get_file_entity(entries, file_name)
        except requests.exceptions.RequestException as e:
            print(f"Error initializing file upload: {e}")
            return {}

    def commit_file(self, file_name):
        commit_url = f"{self.config.base_model_url}/{self.record_id}/draft/files/{file_name}/commit"
        try:
            response = requests.post(
                commit_url,
                json={},
                headers=self.headers,
                verify=False
            )
            if response.status_code != 200:
                return False
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error commiting file: {e}")
            return False

    def get_files(self):
        get_url = f"{self.config.base_model_url}/{self.record_id}/draft/files"
        try:
            response = requests.get(get_url, headers=self.headers, verify=False)
            if response.status_code != 200:
                return []
            return response.json().get("entries", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching files: {e}")
            return []

    def get_file(self, file_name):
        files = self.get_files()
        return get_file_entity(files, file_name)