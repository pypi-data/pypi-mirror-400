import asyncio
import json
from unittest.mock import MagicMock
import pytest
from homepilot.api import HomePilotApi
from homepilot.cover import HomePilotCover
from homepilot.hub import HomePilotHub

from homepilot.manager import HomePilotManager
from homepilot.sensor import ContactState, HomePilotSensor
from homepilot.switch import HomePilotSwitch
from homepilot.scenes import HomePilotScene


TEST_HOST = "test_host"


class TestHomePilotManager:
    @pytest.fixture
    def mocked_api(self):
        api = MagicMock(HomePilotApi)

        f = open("tests/test_files/devices.json")
        devices = json.load(f)
        func_get_devices = asyncio.Future()
        func_get_devices.set_result(devices["payload"]["devices"])
        api.get_devices.return_value = yield from func_get_devices

        f1 = open("tests/test_files/device_cover.json")
        device1 = json.load(f1)
        func_get_device1 = asyncio.Future()
        func_get_device1.set_result(device1["payload"]["device"])

        f2 = open("tests/test_files/device_env_sensor.json")
        device2 = json.load(f2)
        func_get_device2 = asyncio.Future()
        func_get_device2.set_result(device2["payload"]["device"])

        f3 = open("tests/test_files/device_switch.json")
        device3 = json.load(f3)
        func_get_device3 = asyncio.Future()
        func_get_device3.set_result(device3["payload"]["device"])

        f4 = open("tests/test_files/device_contact_sensor.json")
        device4 = json.load(f4)
        func_get_device4 = asyncio.Future()
        func_get_device4.set_result(device4["payload"]["device"])

        # Need to provide more responses since update_state methods now call get_device
        api.get_device.side_effect = [
            (yield from func_get_device1),  # Initial build: cover
            (yield from func_get_device2),  # Initial build: env sensor  
            (yield from func_get_device3),  # Initial build: switch
            (yield from func_get_device4),  # Initial build: contact sensor
            (yield from func_get_device1),  # Initial build: hub (uses cover device)
            (yield from func_get_device1),  # Update state: cover
            (yield from func_get_device2),  # Update state: env sensor
            (yield from func_get_device3),  # Update state: switch
            (yield from func_get_device4),  # Update state: contact sensor
            (yield from func_get_device1),  # Update state: hub
        ]

        f_actuators = open("tests/test_files/actuators.json")
        actuators_response = json.load(f_actuators)
        actuators = {str(device["did"]): device for device in
                     actuators_response["devices"]}
        f_actuators = open("tests/test_files/sensors.json")
        sensors_response = json.load(f_actuators)
        sensors = {str(device["did"]): device for device in sensors_response[
            "meters"]}
        func_get_devices_state = asyncio.Future()
        func_get_devices_state.set_result({**actuators, **sensors})
        api.async_get_devices_state.return_value = \
            yield from func_get_devices_state

        func_get_fw_version = asyncio.Future()
        func_get_fw_version.set_result({
            "hw_platform": "ampere",
            "sw_platform": "bridge",
            "version": "5.4.3",
            "df_stick_version": "2.0"
        })
        api.async_get_fw_version.return_value = yield from func_get_fw_version
        func_get_fw_status = asyncio.Future()
        func_get_fw_status.set_result({
            "version": "5.4.9",
            "update_channel": "manifest-ampere-5.4.0",
            "is_default": True,
            "update_status": "UPDATE_AVAILABLE"
        })
        api.async_get_fw_status.return_value = yield from func_get_fw_status
        func_get_led_status = asyncio.Future()
        func_get_led_status.set_result({"status": "disabled"})
        api.async_get_led_status.return_value = yield from func_get_led_status

        # Add scene mocking
        f_scenes = open("tests/test_files/scenes.json")
        scenes_response = json.load(f_scenes)
        func_get_scenes = asyncio.Future()
        func_get_scenes.set_result(scenes_response["scenes"])
        api.async_get_scenes.return_value = yield from func_get_scenes

        yield api

    @pytest.mark.asyncio
    async def test_build_manager(self, mocked_api):
        manager = await HomePilotManager.async_build_manager(mocked_api)
        assert list(manager.devices.keys()) == \
            ['1', '1010012', '1010018', '1010072', '-1']
        assert isinstance(manager.devices['1'], HomePilotCover)
        assert isinstance(manager.devices['1010012'], HomePilotSensor)
        assert isinstance(manager.devices['1010018'], HomePilotSwitch)
        assert isinstance(manager.devices['1010072'], HomePilotSensor)
        assert isinstance(manager.devices['-1'], HomePilotHub)

    @pytest.mark.asyncio
    async def test_update_state(self, mocked_api):
        manager = await HomePilotManager.async_build_manager(mocked_api)
        await manager.update_states()
        assert manager.devices["1"].cover_position == 35
        assert manager.devices["1"].cover_tilt_position == 11
        assert manager.devices["1010012"].temperature_value == 2.5
        assert manager.devices["1010012"].sun_height_value == -7
        assert manager.devices["1010018"].is_on
        assert manager.devices["1010072"].contact_state_value == \
            ContactState.OPEN
        assert manager.devices["1010072"].battery_level_value == 99
        assert not manager.devices["-1"].led_status
        assert manager.devices["-1"].fw_update_version == "5.4.9"

    @pytest.mark.asyncio
    async def test_build_manager_with_scenes(self, mocked_api):
        manager = await HomePilotManager.async_build_manager(mocked_api)
        # Should only include manual executable scenes by default
        assert len(manager.scenes) == 2
        assert 1 in manager.scenes
        assert 2 in manager.scenes
        assert 3 not in manager.scenes  # Not manual executable
        
        # Check scene properties (API returns integers, but build method converts both to boolean)
        scene1 = manager.scenes[1]
        assert isinstance(scene1, HomePilotScene)
        assert scene1.name == "Morning Scene"
        assert scene1.description == "Opens blinds and turns on lights"
        assert scene1.is_enabled is True  # Build method converts to boolean
        assert scene1.is_manual_executable is True  # Build method converts this to boolean

    @pytest.mark.asyncio
    async def test_build_manager_include_non_manual_executable(self, mocked_api):
        manager = await HomePilotManager.async_build_manager(mocked_api, include_non_manual_executable=True)
        # Should include all scenes when flag is True
        assert len(manager.scenes) == 3
        assert 1 in manager.scenes
        assert 2 in manager.scenes
        assert 3 in manager.scenes  # Now included
        
        # Check non-manual executable scene
        scene3 = manager.scenes[3]
        assert scene3.name == "Auto Scene"
        assert scene3.is_manual_executable is False

    @pytest.mark.asyncio
    async def test_manager_scene_properties(self, mocked_api):
        manager = await HomePilotManager.async_build_manager(mocked_api)
        
        # Test include_non_manual_executable property
        assert manager.include_non_manual_executable is False
        
        manager_with_flag = await HomePilotManager.async_build_manager(mocked_api, include_non_manual_executable=True)
        assert manager_with_flag.include_non_manual_executable is True

    @pytest.mark.asyncio
    async def test_async_update_scenes(self):
        # Create a simpler test setup
        from unittest.mock import MagicMock
        api = MagicMock()
        
        # Mock initial scenes (using API format with integers)
        initial_scenes_data = [
            {"id": 1, "name": "Morning Scene", "description": "Opens blinds", "is_enabled": 1, "is_manual_executable": 1},
            {"id": 2, "name": "Evening Scene", "description": "Closes blinds", "is_enabled": 1, "is_manual_executable": 1}
        ]
        
        # Mock get_devices (empty for simplicity)
        func_get_devices = asyncio.Future()
        func_get_devices.set_result([])
        api.get_devices.return_value = func_get_devices
        
        # Mock initial get_scenes
        func_get_scenes = asyncio.Future()
        func_get_scenes.set_result(initial_scenes_data)
        api.async_get_scenes.return_value = func_get_scenes
        
        # Create manager
        manager = HomePilotManager(api)
        manager.devices = {}
        
        # Build scenes manually
        manager.scenes = {}
        for scene_data in initial_scenes_data:
            if scene_data.get("is_manual_executable", 0) == 1:
                scene = await HomePilotScene.async_build_scene(api, scene_data)
                manager.scenes[scene_data["id"]] = scene
        
        # Mock updated scenes data as LIST (what the API actually returns)
        updated_scenes_data = [
            {"id": 1, "name": "Updated Morning Scene", "description": "Updated description", "is_enabled": 0, "is_manual_executable": 1},
            {"id": 2, "name": "Updated Evening Scene", "description": "Updated evening description", "is_enabled": 1, "is_manual_executable": 1}
        ]
        
        # Create new mock for update call
        updated_func_get_scenes = asyncio.Future()
        updated_func_get_scenes.set_result(updated_scenes_data)
        api.async_get_scenes.return_value = updated_func_get_scenes
        
        # Update scenes
        await manager.async_update_scenes()
        
        # Verify scenes were updated and marked as available
        assert manager.scenes[1].available is True
        assert manager.scenes[2].available is True
        assert manager.scenes[1].name == "Updated Morning Scene"
        assert manager.scenes[1].is_enabled is False  # Now converted to boolean by async_update_scene

    @pytest.mark.asyncio
    async def test_async_update_scenes_with_missing_scene(self):
        # Create a simpler test setup
        from unittest.mock import MagicMock
        api = MagicMock()
        
        # Mock initial scenes (using API format with integers)
        initial_scenes_data = [
            {"id": 1, "name": "Morning Scene", "description": "Opens blinds", "is_enabled": 1, "is_manual_executable": 1},
            {"id": 2, "name": "Evening Scene", "description": "Closes blinds", "is_enabled": 1, "is_manual_executable": 1}
        ]
        
        # Create manager and build scenes manually
        manager = HomePilotManager(api)
        manager.devices = {}
        manager.scenes = {}
        for scene_data in initial_scenes_data:
            scene = await HomePilotScene.async_build_scene(api, scene_data)
            manager.scenes[scene_data["id"]] = scene
        
        # Mock updated scenes data with missing scene ID 2 as LIST (what API returns)
        updated_scenes_data = [
            {"id": 1, "name": "Updated Morning Scene", "description": "Updated description", "is_enabled": 0, "is_manual_executable": 1}
            # Scene 2 is missing from the list
        ]
        
        updated_func_get_scenes = asyncio.Future()
        updated_func_get_scenes.set_result(updated_scenes_data)
        api.async_get_scenes.return_value = updated_func_get_scenes
        
        await manager.async_update_scenes()
        
        # Scene 1 should be available and updated
        assert manager.scenes[1].available is True
        assert manager.scenes[1].name == "Updated Morning Scene"
        # Scene 2 should be marked as unavailable
        assert manager.scenes[2].available is False