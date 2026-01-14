"""Atlas Asset Client - Alias for atlas_asset_http_client_python.

This module provides a package-name-matching import path.
When installing 'atlas-asset-client', you can import as 'atlas_asset_client'.
"""

# Re-export everything from the actual implementation
# This wildcard import is intentional to create an alias module
from atlas_asset_http_client_python import *  # noqa: F401, F403

# Define __all__ to match the original module's exports
__all__ = [
    "AtlasCommandHttpClient",
    # Entity components
    "EntityComponents",
    "TelemetryComponent",
    "GeometryComponent",
    "TaskCatalogComponent",
    "MediaRefItem",
    "MilViewComponent",
    "HealthComponent",
    "SensorRefItem",
    "CommunicationsComponent",
    "TaskQueueComponent",
    # Task components
    "TaskComponents",
    "TaskParametersComponent",
    "TaskProgressComponent",
    # Object metadata
    "ObjectMetadata",
    "ObjectReferenceItem",
    # Helpers
    "components_to_dict",
    "object_metadata_to_dict",
]
