import copy


def get_create_body(metadata: dict, community: str = "elter", files_enabled: bool = True) -> dict:
    """Returns the base JSON structure for creating a draft."""
    if metadata is None:
        metadata = {}
    base_json = {
        "externalWorkflow": {
            "defaultWorkflowTemplateId": "basic-ingest"
        },
        "files": {"enabled": files_enabled},
        "metadata": metadata,
        "parent": {
            "communities": {"default": community}
        },
    }
    return copy.deepcopy(base_json)
