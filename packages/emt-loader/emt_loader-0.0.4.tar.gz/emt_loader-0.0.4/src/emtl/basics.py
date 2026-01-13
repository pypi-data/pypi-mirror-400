import requests

from typing import Any
from emtl.utils import _get_base_url, _get_cache


def authenticate(secret: str) -> bool:
    # todo
    pass


def get_available_dataset_ids() -> list[str]:
    """
    Fetch all available dataset ids.

    Returns:
        list[str]: List of all available dataset ids.
    """

    # request
    url = f"{_get_base_url()}/dataset_ids"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    # parse
    data = response.json()
    if not isinstance(data, list) or not all(isinstance(d, str) for d in data):
        raise ValueError("Fetched dataset ids have an invalid format.")
    return data


def get_request_schema(dataset_id: str) -> dict[str, Any]:
    """
    Fetch the request schema for the given dataset id.

    Args:
        dataset_id (str): Unique id of the dataset.

    Returns:
        dict[str, Any]: Request schema as a dict.
    """

    # request
    url = f"{_get_base_url()}/schema/{dataset_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    # parse
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"Schema for '{dataset_id}' not found.")
    return data


def clear_cache() -> None:
    """Clears local data cache. All cached data will be permanently deleted."""
    _get_cache().clear()
