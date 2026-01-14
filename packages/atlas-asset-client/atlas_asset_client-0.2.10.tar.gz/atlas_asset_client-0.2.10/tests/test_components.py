"""Tests for typed component models."""

from __future__ import annotations

import json
import warnings

import httpx
import pytest
from atlas_asset_http_client_python import (
    AtlasCommandHttpClient,
    CommunicationsComponent,
    EntityComponents,
    GeometryComponent,
    HealthComponent,
    MediaRefItem,
    MilViewComponent,
    SensorRefItem,
    TaskCatalogComponent,
    TaskComponents,
    TaskParametersComponent,
    TaskProgressComponent,
    TaskQueueComponent,
    TelemetryComponent,
    components_to_dict,
)


class TestTelemetryComponent:
    """Tests for TelemetryComponent."""

    def test_basic_creation(self):
        telemetry = TelemetryComponent(
            latitude=40.7128,
            longitude=-74.0060,
            altitude_m=120,
            speed_m_s=8.2,
            heading_deg=165,
        )
        assert telemetry.latitude == 40.7128
        assert telemetry.longitude == -74.0060
        assert telemetry.altitude_m == 120
        assert telemetry.speed_m_s == 8.2
        assert telemetry.heading_deg == 165

    def test_optional_fields(self):
        telemetry = TelemetryComponent(latitude=40.7128)
        assert telemetry.latitude == 40.7128
        assert telemetry.longitude is None
        assert telemetry.altitude_m is None

    def test_to_dict_excludes_none(self):
        telemetry = TelemetryComponent(latitude=40.7128, longitude=-74.0060)
        result = telemetry.model_dump(exclude_none=True)
        assert result == {"latitude": 40.7128, "longitude": -74.0060}
        assert "altitude_m" not in result


class TestGeometryComponent:
    """Tests for GeometryComponent."""

    def test_point_geometry(self):
        geometry = GeometryComponent(type="Point", coordinates=[-74.0060, 40.7128])
        assert geometry.type == "Point"
        assert geometry.coordinates == [-74.0060, 40.7128]

    def test_linestring_geometry(self):
        geometry = GeometryComponent(
            type="LineString",
            coordinates=[[-74.0060, 40.7128], [-74.0050, 40.7138]],
        )
        assert geometry.type == "LineString"

    def test_polygon_geometry(self):
        geometry = GeometryComponent(
            type="Polygon",
            coordinates=[[[-74.0060, 40.7128], [-74.0050, 40.7138], [-74.0060, 40.7128]]],
        )
        assert geometry.type == "Polygon"


class TestEntityComponents:
    """Tests for EntityComponents with multiple components."""

    def test_full_entity_components(self):
        components = EntityComponents(
            telemetry=TelemetryComponent(
                latitude=40.7128,
                longitude=-74.0060,
                altitude_m=120,
                speed_m_s=8.2,
                heading_deg=165,
            ),
            task_catalog=TaskCatalogComponent(supported_tasks=["move_to_location", "survey_grid"]),
            health=HealthComponent(battery_percent=76),
            communications=CommunicationsComponent(link_state="connected"),
            task_queue=TaskQueueComponent(current_task_id=None, queued_task_ids=[]),
            media_refs=[
                MediaRefItem(object_id="obj-123", role="camera_feed"),
                MediaRefItem(object_id="obj-456", role="thumbnail"),
            ],
            sensor_refs=[
                SensorRefItem(
                    sensor_id="radar-1",
                    type="radar",
                    vertical_fov=60,
                    horizontal_fov=90,
                    vertical_orientation=10,
                    horizontal_orientation=45,
                )
            ],
            mil_view=MilViewComponent(classification="friendly", last_seen="2025-11-23T10:05:00Z"),
        )
        result = components.model_dump(exclude_none=True)
        assert result["telemetry"]["latitude"] == 40.7128
        assert result["task_catalog"]["supported_tasks"] == ["move_to_location", "survey_grid"]
        assert result["health"]["battery_percent"] == 76
        assert result["communications"]["link_state"] == "connected"
        assert len(result["media_refs"]) == 2
        assert len(result["sensor_refs"]) == 1
        assert result["mil_view"]["classification"] == "friendly"

    def test_custom_components_allowed(self):
        components = EntityComponents(
            telemetry=TelemetryComponent(latitude=40.7128),
            custom_weather={"wind_speed": 12, "gusts": 18},
        )
        result = components.model_dump(exclude_none=True)
        assert result["custom_weather"] == {"wind_speed": 12, "gusts": 18}

    def test_unknown_component_raises_error(self):
        with pytest.raises(ValueError, match="Unknown component"):
            EntityComponents(
                unknown_component={"foo": "bar"},
            )


class TestTaskComponents:
    """Tests for TaskComponents."""

    def test_task_with_parameters_and_progress(self):
        components = TaskComponents(
            parameters=TaskParametersComponent(latitude=40.123, longitude=-74.456, altitude_m=120),
            progress=TaskProgressComponent(
                percent=65,
                updated_at="2025-11-25T08:45:00Z",
                status_detail="En route to destination",
            ),
        )
        result = components.model_dump(exclude_none=True)
        assert result["parameters"]["latitude"] == 40.123
        assert result["progress"]["percent"] == 65
        assert result["progress"]["status_detail"] == "En route to destination"


class TestComponentsToDict:
    """Tests for the components_to_dict helper."""

    def test_with_typed_components(self):
        components = EntityComponents(
            telemetry=TelemetryComponent(latitude=40.7128, longitude=-74.0060)
        )
        result = components_to_dict(components)
        assert result == {"telemetry": {"latitude": 40.7128, "longitude": -74.0060}}

    def test_with_raw_dict_emits_warning(self):
        raw_components = {"telemetry": {"latitude": 40.7128}}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = components_to_dict(raw_components)
            assert len(w) == 1
            assert "deprecated" in str(w[0].message).lower()
        assert result == {"telemetry": {"latitude": 40.7128}}

    def test_with_none(self):
        result = components_to_dict(None)
        assert result is None


class TestHttpClientWithTypedComponents:
    """Tests for HTTP client with typed components."""

    @pytest.mark.asyncio
    async def test_create_entity_with_typed_components(self):
        captured: dict[str, httpx.Request] = {}

        async def handler(request: httpx.Request) -> httpx.Response:
            captured["request"] = request
            return httpx.Response(200, json={"entity_id": "asset-1"})

        client = AtlasCommandHttpClient(
            "http://atlas.local",
            transport=httpx.MockTransport(handler),
        )

        components = EntityComponents(
            telemetry=TelemetryComponent(
                latitude=40.7128,
                longitude=-74.0060,
                altitude_m=120,
            ),
            health=HealthComponent(battery_percent=85),
        )

        async with client:
            entity = await client.create_entity(
                entity_id="asset-1",
                entity_type="asset",
                alias="demo",
                subtype="drone",
                components=components,
            )

        assert entity["entity_id"] == "asset-1"
        req = captured["request"]
        payload = json.loads(req.content)
        assert payload["components"]["telemetry"]["latitude"] == 40.7128
        assert payload["components"]["telemetry"]["longitude"] == -74.0060
        assert payload["components"]["health"]["battery_percent"] == 85

    @pytest.mark.asyncio
    async def test_create_task_with_typed_components(self):
        captured: dict[str, httpx.Request] = {}

        async def handler(request: httpx.Request) -> httpx.Response:
            captured["request"] = request
            return httpx.Response(200, json={"task_id": "task-1"})

        client = AtlasCommandHttpClient(
            "http://atlas.local",
            transport=httpx.MockTransport(handler),
        )

        components = TaskComponents(
            parameters=TaskParametersComponent(
                latitude=40.123,
                longitude=-74.456,
                altitude_m=120,
            ),
        )

        async with client:
            task = await client.create_task(
                task_id="task-1",
                entity_id="asset-1",
                components=components,
            )

        assert task["task_id"] == "task-1"
        req = captured["request"]
        payload = json.loads(req.content)
        assert payload["components"]["parameters"]["latitude"] == 40.123
        assert payload["components"]["parameters"]["longitude"] == -74.456

    @pytest.mark.asyncio
    async def test_update_entity_with_typed_components(self):
        captured: dict[str, httpx.Request] = {}

        async def handler(request: httpx.Request) -> httpx.Response:
            captured["request"] = request
            return httpx.Response(200, json={"entity_id": "asset-1"})

        client = AtlasCommandHttpClient(
            "http://atlas.local",
            transport=httpx.MockTransport(handler),
        )

        components = EntityComponents(
            telemetry=TelemetryComponent(latitude=41.0, longitude=-75.0),
        )

        async with client:
            await client.update_entity("asset-1", components=components)

        req = captured["request"]
        payload = json.loads(req.content)
        assert payload["components"]["telemetry"]["latitude"] == 41.0

    @pytest.mark.asyncio
    async def test_backwards_compatibility_with_raw_dict(self):
        """Verify raw dict components still work (with deprecation warning)."""
        captured: dict[str, httpx.Request] = {}

        async def handler(request: httpx.Request) -> httpx.Response:
            captured["request"] = request
            return httpx.Response(200, json={"entity_id": "asset-1"})

        client = AtlasCommandHttpClient(
            "http://atlas.local",
            transport=httpx.MockTransport(handler),
        )

        raw_components = {"telemetry": {"latitude": 40.7128, "longitude": -74.0060}}

        async with client:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                await client.create_entity(
                    entity_id="asset-1",
                    entity_type="asset",
                    alias="demo",
                    subtype="drone",
                    components=raw_components,
                )
                # Should emit deprecation warning
                assert len(w) == 1
                assert "deprecated" in str(w[0].message).lower()

        req = captured["request"]
        payload = json.loads(req.content)
        assert payload["components"]["telemetry"]["latitude"] == 40.7128
