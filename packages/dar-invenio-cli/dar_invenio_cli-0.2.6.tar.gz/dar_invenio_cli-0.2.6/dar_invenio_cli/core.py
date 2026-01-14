import requests
from pathlib import Path
import json
from typing import Optional, List, Dict, Any

from dar_invenio_cli.config import Config
from dar_invenio_cli.services.file_service import FileService
from dar_invenio_cli.tools import get_create_body


def create_draft(config: Config, json_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new draft record using the configured Invenio model endpoint.

    Args:
        config (Config): Configuration object containing `base_model_url`,
            `headers`, and other settings required to call the API.
        json_body (dict): JSON-serializable payload to send as the create body
            for the draft. This should follow the target system's expected
            schema (metadata, owners, access, etc.).

    Returns:
        dict | None: The parsed JSON response from the server if creation
        succeeded (HTTP 201). Returns None on failure or exception.

    Notes:
        - Network or request exceptions are caught and cause a None return.
        - SSL verification is disabled here (verify=False) to mirror the
          previous behavior; consider enabling verification in production.
    """
    create_url = f"{config.base_model_url}/"
    try:
        response = requests.post(create_url, json=json_body, headers=config.headers, verify=False)
    except requests.exceptions.RequestException as e:
        print(f"Error creating draft: {e}")
        return None
    if response.status_code == 201:
        print("Draft created successfully.")
    else:
        print(f"Failed to create draft: {response.status_code} - {response.text}")
        return None
    response_json = response.json()
    return response_json

def validate_json_metadata(metadata_json: dict) -> bool:
    """
    Validate the provided JSON metadata for draft creation.

    Args:
        metadata_json (dict): The JSON metadata to validate.
    Returns:
        bool: True if the metadata is valid, False otherwise.
    """

    # Basic type check
    if not isinstance(metadata_json, dict):
        print("Metadata must be a JSON object (dict).")
        return False

    if "metadata" in metadata_json:
        print("Metadata json is in invalid format: it should not contain a top-level 'metadata' key.")
        return False

    if not isinstance(metadata_json, dict):
        print("The 'metadata' value must be a JSON object.")
        return False

    allowed_keys = {
        "additionalMetadata",
        "alternateIdentifiers",
        "assetType",
        "contactPoints",
        "contributors",
        "creators",
        "dataLevel",
        "datasetType",
        "descriptions",
        "geoLocations",
        "habitatReferences",
        "keywords",
        "language",
        "licenses",
        "methods",
        "projects",
        "publicationDate",
        "relatedIdentifiers",
        "responsibleOrganizations",
        "siteReferences",
        "taxonomicCoverages",
        "temporalCoverages",
        "temporalResolution",
        "titles",
    }

    found_keys = set(metadata_json.keys())

    unexpected = found_keys - allowed_keys

    if unexpected:
        print(f"Unexpected top-level metadata fields: {', '.join(sorted(unexpected))}")
        return False

    return True


def create_draft_from_file(config: Config, json_file_path: str) -> Optional[Dict[str, Any]]:
    """
    Create a draft using JSON content read from a file.

    Args:
        config (Config): Configuration object used to perform the create
            operation (see `create_draft`).
        json_file_path (str): Path to a JSON file containing the body to send
            to the create endpoint. The file should contain a JSON object.

    Returns:
        dict | None: The created draft response JSON on success, otherwise None.

    Raises:
        ValueError: If the file does not contain valid JSON.
        OSError: If the file cannot be read.
    """
    path = Path(json_file_path)
    if not path.is_file():
        print(f"JSON file not found: {json_file_path}")
        return None

    try:
        with path.open("r", encoding="utf-8") as fh:
            json_body = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in file {json_file_path}: {e}")
        return None
    except OSError as e:
        print(f"Error reading file {json_file_path}: {e}")
        return None

    body_to_send = get_create_body(json_body, config.community)

    return create_draft(config, body_to_send)


def create_draft_from_name(config: Config, name: str) -> Optional[Dict[str, Any]]:
    """
    Create a simple draft using a title/name string.

    Args:
        config (Config): Configuration object used to perform the create
            operation (see `create_draft`).
        name (str): Title text to use when building the draft metadata.

    Returns:
        dict | None: The created draft response JSON on success, otherwise None.
    """
    metadata = {
        "titles": [
            {
                "titleLanguage": "eng",
                "titleText": name
            }
        ]
    }
    created_draft = create_draft(config, get_create_body(metadata, config.community))
    return created_draft


def create_drafts_from_files(config: Config, json_files_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Create multiple drafts from a list of JSON file paths.

    Args:
        config (Config): Configuration object used to perform the create
            operation (see `create_draft`).
        json_files_paths (list[str]): Iterable of file paths to JSON files.

    Returns:
        list[dict]: A list with the parsed JSON responses for drafts that were
        successfully created. Failed creations will not appear in the list.
    """
    created = []
    for json_file_path in json_files_paths:
        result = create_draft_from_file(config, json_file_path)
        if result:
            created.append(result)
    return created


def create_drafts_from_folder(config: Config, folder_path: str) -> List[Dict[str, Any]]:
    """
    Create drafts for every JSON file in the provided folder.

    Args:
        config (Config): Configuration object used to perform the create
            operation (see `create_draft`).
        folder_path (str): Path to a directory; all files matching "*.json"
            will be read and used to create drafts.

    Returns:
        list[dict]: List of successfully created draft response JSON objects.
    """
    folder = Path(folder_path)
    json_file_paths = [str(path) for path in folder.glob("*.json") if path.is_file()]
    return create_drafts_from_files(config, json_file_paths)


def upload_files_to_draft(config: Config, draft_id: str, file_paths: List[str]) -> None:
    """
    Upload one or more files to an existing draft using the FileService.

    Args:
        config (Config): Configuration object containing credentials and URLs
            required by `FileService`.
        draft_id (str): Identifier of the draft (record) to attach files to.
        file_paths (list[str]): Iterable of local file paths to upload.

    Returns:
        None

    Notes:
        - Errors during individual file uploads are handled by `FileService`.
    """
    file_service = FileService(config, draft_id)
    for file_path in file_paths:
        file_service.upload_file(file_path)


def upload_files_to_draft_from_folder(config: Config, draft_id: str, folder_path: str) -> None:
    """
    Upload all regular files found in `folder_path` to a draft.

    Args:
        config (Config): Configuration object containing credentials and URLs
            required by `FileService`.
        draft_id (str): Identifier of the draft (record) to attach files to.
        folder_path (str): Path to a directory whose files will be uploaded.

    Returns:
        None
    """
    folder = Path(folder_path)
    file_paths = [str(path) for path in folder.glob("*") if path.is_file()]
    upload_files_to_draft(config, draft_id, file_paths)
