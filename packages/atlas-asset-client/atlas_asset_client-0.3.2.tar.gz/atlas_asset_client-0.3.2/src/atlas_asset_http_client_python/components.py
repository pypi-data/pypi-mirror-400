"""Typed component models for Atlas Command entities, tasks, and objects.

These models provide type safety for component data
before it is transmitted to the Atlas Command API.
Refactored to use standard Python dataclasses to avoid Pydantic/Rust dependencies
on low-power hardware.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field, fields
from typing import Any, List, Literal, Mapping, Optional, Union


def _exclude_none(data: Any) -> Any:
    """Recursively remove None values from a dictionary or list."""
    if isinstance(data, dict):
        return {k: _exclude_none(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [_exclude_none(v) for v in data]
    return data


@dataclass
class AtlasModel:
    """Base class providing Pydantic-like model_dump for compatibility."""

    def model_dump(self, exclude_none: bool = False, by_alias: bool = False) -> dict[str, Any]:
        """Convert the model to a dictionary.

        Args:
            exclude_none: Whether to exclude fields with None values.
            by_alias: Included for API compatibility with Pydantic.

        Returns:
            Dictionary representation of the model.
        """

        def serialize(obj: Any) -> Any:
            if isinstance(obj, AtlasModel):
                res = {}
                # Include defined fields
                for f in fields(obj):
                    val = getattr(obj, f.name)
                    res[f.name] = serialize(val)
                # Include extra attributes (for models that allow extra fields)
                for k, v in obj.__dict__.items():
                    if k.startswith("custom_") and k not in res:
                        res[k] = serialize(v)
                return res
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj

        data = serialize(self)
        if exclude_none:
            return _exclude_none(data)
        return data


# === Entity Components ===


@dataclass
class TelemetryComponent(AtlasModel):
    """Position and motion data for entities."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None
    speed_m_s: Optional[float] = None
    heading_deg: Optional[float] = None


@dataclass
class GeometryComponent(AtlasModel):
    """GeoJSON geometry for geoentities."""

    type: Literal["Point", "LineString", "Polygon"]
    coordinates: Union[List[float], List[List[float]], List[List[List[float]]]]


@dataclass
class TaskCatalogComponent(AtlasModel):
    """Lists supported task identifiers for an asset."""

    supported_tasks: List[str] = field(default_factory=list)


@dataclass
class MediaRefItem(AtlasModel):
    """A reference to a media object."""

    object_id: str
    role: Literal["camera_feed", "thumbnail"]


@dataclass
class MilViewComponent(AtlasModel):
    """Military tactical classification component."""

    classification: Literal["friendly", "hostile", "neutral", "unknown", "civilian"]
    last_seen: Optional[str] = None


@dataclass
class HealthComponent(AtlasModel):
    """Health and vital statistics for entities."""

    battery_percent: Optional[int] = None

    def __post_init__(self):
        if self.battery_percent is not None:
            if not (0 <= self.battery_percent <= 100):
                raise ValueError("battery_percent must be between 0 and 100")


@dataclass
class SensorRefItem(AtlasModel):
    """A reference to a sensor with FOV/orientation metadata."""

    sensor_id: str
    type: str
    vertical_fov: Optional[float] = None
    horizontal_fov: Optional[float] = None
    vertical_orientation: Optional[float] = None
    horizontal_orientation: Optional[float] = None


@dataclass
class CommunicationsComponent(AtlasModel):
    """Network link status component."""

    link_state: Literal["connected", "disconnected", "degraded", "unknown"]


@dataclass
class TaskQueueComponent(AtlasModel):
    """Current and queued work items for an entity."""

    current_task_id: Optional[str] = None
    queued_task_ids: List[str] = field(default_factory=list)


@dataclass
class EntityComponents(AtlasModel):
    """All supported entity components with optional fields."""

    telemetry: Optional[TelemetryComponent] = None
    geometry: Optional[GeometryComponent] = None
    task_catalog: Optional[TaskCatalogComponent] = None
    media_refs: Optional[List[MediaRefItem]] = None
    mil_view: Optional[MilViewComponent] = None
    health: Optional[HealthComponent] = None
    sensor_refs: Optional[List[SensorRefItem]] = None
    communications: Optional[CommunicationsComponent] = None
    task_queue: Optional[TaskQueueComponent] = None

    def __init__(self, **kwargs):
        known_fields = {f.name for f in fields(self)}
        for key, value in kwargs.items():
            if key in known_fields:
                setattr(self, key, value)
            elif key.startswith("custom_"):
                setattr(self, key, value)
            else:
                raise ValueError(
                    f"Unknown component '{key}'. Custom components must be prefixed with 'custom_'"
                )


# === Task Components ===


@dataclass
class TaskParametersComponent(AtlasModel):
    """Command parameters for task execution."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None

    def __init__(self, **kwargs):
        # TaskParametersComponent allowed 'extra="allow"' in Pydantic
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class TaskProgressComponent(AtlasModel):
    """Runtime telemetry about task execution."""

    percent: Optional[int] = None
    updated_at: Optional[str] = None
    status_detail: Optional[str] = None

    def __post_init__(self):
        if self.percent is not None:
            if not (0 <= self.percent <= 100):
                raise ValueError("percent must be between 0 and 100")


@dataclass
class TaskComponents(AtlasModel):
    """All supported task components."""

    parameters: Optional[TaskParametersComponent] = None
    progress: Optional[TaskProgressComponent] = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# === Object Metadata ===


@dataclass
class ObjectReferenceItem(AtlasModel):
    """A reference from an object to an entity or task."""

    entity_id: Optional[str] = None
    task_id: Optional[str] = None


@dataclass
class ObjectMetadata(AtlasModel):
    """Metadata for stored objects (JSON blob fields)."""

    bucket: Optional[str] = None
    size_bytes: Optional[int] = None
    usage_hints: Optional[List[str]] = None
    referenced_by: Optional[List[ObjectReferenceItem]] = None
    checksum: Optional[str] = None
    expiry_time: Optional[str] = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


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
