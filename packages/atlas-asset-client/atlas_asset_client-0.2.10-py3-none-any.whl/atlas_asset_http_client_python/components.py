"""Typed component models for Atlas Command entities, tasks, and objects.

These Pydantic models provide type safety and validation for component data
before it is transmitted to the Atlas Command API.
"""

from __future__ import annotations

import warnings
from typing import Any, List, Literal, Mapping, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

# === Entity Components ===


class TelemetryComponent(BaseModel):
    """Position and motion data for entities."""

    model_config = ConfigDict(extra="forbid")

    latitude: Optional[float] = Field(None, description="Latitude in degrees (WGS84)")
    longitude: Optional[float] = Field(None, description="Longitude in degrees (WGS84)")
    altitude_m: Optional[float] = Field(None, description="Altitude in meters above sea level")
    speed_m_s: Optional[float] = Field(None, description="Horizontal speed in meters/second")
    heading_deg: Optional[float] = Field(None, description="Heading in degrees (0=N, 90=E, etc.)")


class GeometryComponent(BaseModel):
    """GeoJSON geometry for geoentities."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["Point", "LineString", "Polygon"] = Field(
        ..., description="GeoJSON geometry type"
    )
    coordinates: Union[List[float], List[List[float]], List[List[List[float]]]] = Field(
        ..., description="GeoJSON coordinates ([lon, lat] for Point)"
    )


class TaskCatalogComponent(BaseModel):
    """Lists supported task identifiers for an asset."""

    model_config = ConfigDict(extra="forbid")

    supported_tasks: List[str] = Field(
        default_factory=list, description="Task identifiers the asset can accept"
    )


class MediaRefItem(BaseModel):
    """A reference to a media object."""

    model_config = ConfigDict(extra="forbid")

    object_id: str = Field(..., description="Object ID in object storage")
    role: Literal["camera_feed", "thumbnail"] = Field(
        ..., description="Role of the media reference"
    )


class MilViewComponent(BaseModel):
    """Military tactical classification component."""

    model_config = ConfigDict(extra="forbid")

    classification: Literal["friendly", "hostile", "neutral", "unknown", "civilian"] = Field(
        ..., description="Tactical classification"
    )
    last_seen: Optional[str] = Field(None, description="ISO 8601 timestamp of last observation")


class HealthComponent(BaseModel):
    """Health and vital statistics for entities."""

    model_config = ConfigDict(extra="forbid")

    battery_percent: Optional[int] = Field(
        None, ge=0, le=100, description="Battery percentage (0-100)"
    )


class SensorRefItem(BaseModel):
    """A reference to a sensor with FOV/orientation metadata."""

    model_config = ConfigDict(extra="forbid")

    sensor_id: str = Field(..., description="Unique sensor identifier")
    type: str = Field(..., description="Sensor type (e.g., 'radar')")
    vertical_fov: Optional[float] = Field(None, description="Vertical field of view in degrees")
    horizontal_fov: Optional[float] = Field(None, description="Horizontal field of view in degrees")
    vertical_orientation: Optional[float] = Field(
        None, description="Vertical orientation in degrees relative to level"
    )
    horizontal_orientation: Optional[float] = Field(
        None, description="Horizontal orientation in degrees relative to front"
    )


class CommunicationsComponent(BaseModel):
    """Network link status component."""

    model_config = ConfigDict(extra="forbid")

    link_state: Literal["connected", "disconnected", "degraded", "unknown"] = Field(
        ..., description="Network link state"
    )


class TaskQueueComponent(BaseModel):
    """Current and queued work items for an entity."""

    model_config = ConfigDict(extra="forbid")

    current_task_id: Optional[str] = Field(None, description="Current task ID (null if idle)")
    queued_task_ids: List[str] = Field(
        default_factory=list, description="Ordered list of queued task IDs"
    )


class EntityComponents(BaseModel):
    """All supported entity components with optional fields."""

    model_config = ConfigDict(extra="allow")  # Allow custom_* components

    telemetry: Optional[TelemetryComponent] = None
    geometry: Optional[GeometryComponent] = None
    task_catalog: Optional[TaskCatalogComponent] = None
    media_refs: Optional[List[MediaRefItem]] = None
    mil_view: Optional[MilViewComponent] = None
    health: Optional[HealthComponent] = None
    sensor_refs: Optional[List[SensorRefItem]] = None
    communications: Optional[CommunicationsComponent] = None
    task_queue: Optional[TaskQueueComponent] = None

    @model_validator(mode="before")
    @classmethod
    def validate_custom_keys(cls, data: Any) -> Any:
        """Validate that extra keys start with 'custom_'."""
        if isinstance(data, dict):
            known_fields = {
                "telemetry",
                "geometry",
                "task_catalog",
                "media_refs",
                "mil_view",
                "health",
                "sensor_refs",
                "communications",
                "task_queue",
            }
            for key in data:
                if key not in known_fields and not key.startswith("custom_"):
                    raise ValueError(
                        f"Unknown component '{key}'. Custom components must be prefixed with 'custom_'"
                    )
        return data


# === Task Components ===


class TaskParametersComponent(BaseModel):
    """Command parameters for task execution."""

    model_config = ConfigDict(extra="allow")  # Allow any parameters

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None


class TaskProgressComponent(BaseModel):
    """Runtime telemetry about task execution."""

    model_config = ConfigDict(extra="forbid")

    percent: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    updated_at: Optional[str] = Field(None, description="ISO 8601 timestamp of last update")
    status_detail: Optional[str] = Field(None, description="Human-readable status detail")


class TaskComponents(BaseModel):
    """All supported task components."""

    model_config = ConfigDict(extra="allow")  # Allow custom_* and other components

    parameters: Optional[TaskParametersComponent] = None
    progress: Optional[TaskProgressComponent] = None


# === Object Metadata ===


class ObjectReferenceItem(BaseModel):
    """A reference from an object to an entity or task."""

    model_config = ConfigDict(extra="forbid")

    entity_id: Optional[str] = None
    task_id: Optional[str] = None


class ObjectMetadata(BaseModel):
    """Metadata for stored objects (JSON blob fields)."""

    model_config = ConfigDict(extra="allow")  # Allow custom_* fields

    bucket: Optional[str] = Field(None, description="Storage bucket name")
    size_bytes: Optional[int] = Field(None, ge=0, description="File size in bytes")
    usage_hints: Optional[List[str]] = Field(None, description="Hints about object usage")
    referenced_by: Optional[List[ObjectReferenceItem]] = Field(
        None, description="Entities/tasks that reference this object"
    )
    checksum: Optional[str] = Field(None, description="Hash/checksum of object content")
    expiry_time: Optional[str] = Field(None, description="ISO 8601 expiry timestamp")


# === Helper Functions ===


def components_to_dict(
    components: Optional[EntityComponents | TaskComponents | Mapping[str, Any]],
) -> Optional[dict[str, Any]]:
    """Convert typed components to a dictionary for API transmission.

    If a raw dict/Mapping is passed (legacy usage), emit a deprecation warning
    and return it as-is.

    Args:
        components: Typed component model or raw dict

    Returns:
        Dictionary suitable for JSON serialization
    """
    if components is None:
        return None

    if isinstance(components, (EntityComponents, TaskComponents)):
        return components.model_dump(exclude_none=True, by_alias=True)

    # Legacy raw dict usage
    if isinstance(components, Mapping):
        warnings.warn(
            "Passing raw dict for 'components' is deprecated. "
            "Use typed component models (EntityComponents, TaskComponents) instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return dict(components)

    raise TypeError(
        f"Expected EntityComponents, TaskComponents, or Mapping, got {type(components)}"
    )


def object_metadata_to_dict(
    metadata: Optional[ObjectMetadata | Mapping[str, Any]],
) -> Optional[dict[str, Any]]:
    """Convert typed object metadata to a dictionary for API transmission.

    Args:
        metadata: Typed ObjectMetadata or raw dict

    Returns:
        Dictionary suitable for JSON serialization
    """
    if metadata is None:
        return None

    if isinstance(metadata, ObjectMetadata):
        return metadata.model_dump(exclude_none=True, by_alias=True)

    if isinstance(metadata, Mapping):
        warnings.warn(
            "Passing raw dict for object metadata is deprecated. " "Use ObjectMetadata instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return dict(metadata)

    raise TypeError(f"Expected ObjectMetadata or Mapping, got {type(metadata)}")
