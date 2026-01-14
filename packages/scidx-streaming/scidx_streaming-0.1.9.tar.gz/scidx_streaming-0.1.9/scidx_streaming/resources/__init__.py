"""Resource registration and discovery helpers."""

from .delete import delete_resource, delete_resource_by_name
from .register import register_resource
from .search import ResourceSearchResults, search_resources
from .utils import registry
from .update import deactivate_resource, update_resource

SUPPORTED_RESOURCE_TYPES = registry.SUPPORTED_RESOURCE_TYPES
URL_BACKED_RESOURCE_TYPES = registry.URL_BACKED_RESOURCE_TYPES

__all__ = [
    "register_resource",
    "update_resource",
    "deactivate_resource",
    "delete_resource",
    "delete_resource_by_name",
    "SUPPORTED_RESOURCE_TYPES",
    "URL_BACKED_RESOURCE_TYPES",
    "ResourceSearchResults",
    "search_resources",
]
