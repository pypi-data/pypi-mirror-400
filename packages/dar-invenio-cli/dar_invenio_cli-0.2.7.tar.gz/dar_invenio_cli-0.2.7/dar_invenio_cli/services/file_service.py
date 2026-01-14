#
# Copyright (C) 2025 Masaryk University
#
# DAR-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""File service for handling file uploads in the MU Invenio CLI application."""

import os

import requests

from dar_invenio_cli.config import Config
from dar_invenio_cli.uploaders.file_uploader import FileUploader
from dar_invenio_cli.uploaders.multipart_uploader import MultipartUploader


class FileService:
    def __init__(self, config: Config, record_id: str):
        self.config = config
        self.record_id = record_id
        self.headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }

    def upload_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f"File does not exist: {file_path}")
            return

        file_size = os.path.getsize(file_path)
        if file_size <= 100 * 1024 * 1024:  # 100MB threshold
            uploaded = FileUploader(self.config, self.record_id).upload(file_path)
        else:
            uploaded = MultipartUploader(self.config, self.record_id).upload(file_path)
        if uploaded < 0:
            print(f"File upload failed: {file_path}")
            deleted = self.delete_file(file_path)
            if not deleted:
                print(f"Failed to clean up after upload failure for {file_path}. Please check the server.")

    def delete_file(self, file_path):
        file_name = file_path.split("/")[-1]
        delete_url = f"{self.config.base_model_url}/{self.record_id}/draft/files/{file_name}"
        try:
            response = requests.delete(delete_url, headers=self.headers, verify=False)
            if response.status_code != 204:
                print(f"Error deleting file {file_name}: {response.status_code}")
                return False
            print(f"File {file_name} deleted successfully.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting file {file_name}: {e}")
            return False
