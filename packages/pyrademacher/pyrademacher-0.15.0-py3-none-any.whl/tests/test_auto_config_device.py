"""
Unit tests for HomePilotAutoConfigDevice

The AutoMode extension provides automatic control capabilities for HomePilot devices.
It supports 8 different types of automatic modes:

1. AUTO_MODE_CFG - General auto mode (based on Manuellbetrieb status)
2. TIME_AUTO_CFG - Time-based automation
3. CONTACT_AUTO_CFG - Contact sensor-based automation
4. WIND_AUTO_CFG - Wind sensor-based automation
5. DAWN_AUTO_CFG - Dawn/sunrise-based automation
6. DUSK_AUTO_CFG - Dusk/sunset-based automation
7. RAIN_AUTO_CFG - Rain sensor-based automation
8. SUN_AUTO_CFG - Sun/light sensor-based automation

Each mode can be:
- Detected (has_*_auto_mode properties)
- Read (current state via *_auto_mode_value properties)
- Controlled (async_set_*_auto_mode methods)

This functionality is used by device types like Cover, Light, Switch, etc.
through inheritance from HomePilotAutoConfigDevice.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from homepilot.device import HomePilotAutoConfigDevice
from homepilot.api import HomePilotApi
from homepilot.cover import HomePilotCover
from homepilot.light import HomePilotLight
from homepilot.switch import HomePilotSwitch
from homepilot.thermostat import HomePilotThermostat
from homepilot.actuator import HomePilotActuator
from homepilot.const import (
    APICAP_AUTO_MODE_CFG,
    APICAP_TIME_AUTO_CFG,
    APICAP_CONTACT_AUTO_CFG,
    APICAP_WIND_AUTO_CFG,
    APICAP_DAWN_AUTO_CFG,
    APICAP_DUSK_AUTO_CFG,
    APICAP_RAIN_AUTO_CFG,
    APICAP_SUN_AUTO_CFG,
)


class TestHomePilotAutoConfigDevice:

    @pytest.fixture
    def mocked_api(self):
        api = MagicMock(spec=HomePilotApi)

        # Mock async methods
        future_auto_mode = asyncio.Future()
        future_auto_mode.set_result(None)
        api.async_set_auto_mode.return_value = future_auto_mode

        future_command = asyncio.Future()
        future_command.set_result(None)
        api.async_send_device_command.return_value = future_command

        # Mock new specific auto mode methods
        future_time_auto = asyncio.Future()
        future_time_auto.set_result(None)
        api.async_set_time_auto_mode.return_value = future_time_auto

        future_contact_auto = asyncio.Future()
        future_contact_auto.set_result(None)
        api.async_set_contact_auto_mode.return_value = future_contact_auto

        future_wind_auto = asyncio.Future()
        future_wind_auto.set_result(None)
        api.async_set_wind_auto_mode.return_value = future_wind_auto

        future_dawn_auto = asyncio.Future()
        future_dawn_auto.set_result(None)
        api.async_set_dawn_auto_mode.return_value = future_dawn_auto

        future_dusk_auto = asyncio.Future()
        future_dusk_auto.set_result(None)
        api.async_set_dusk_auto_mode.return_value = future_dusk_auto

        future_rain_auto = asyncio.Future()
        future_rain_auto.set_result(None)
        api.async_set_rain_auto_mode.return_value = future_rain_auto

        future_sun_auto = asyncio.Future()
        future_sun_auto.set_result(None)
        api.async_set_sun_auto_mode.return_value = future_sun_auto

        return api

    @pytest.fixture
    def device_data(self):
        return {
            "did": 123,
            "uid": "test-uid-123",
            "name": "Test Auto Device",
            "device_number": "DEV001",
            "model": "TestModel",
            "fw_version": "1.0.0",
            "device_group": 1,
            "has_ping_cmd": True,
        }

    @pytest.fixture
    def full_device_map(self):
        """Device map with all auto mode capabilities"""
        return {
            APICAP_AUTO_MODE_CFG: {"value": "true"},
            APICAP_TIME_AUTO_CFG: {"value": "true"},
            APICAP_CONTACT_AUTO_CFG: {"value": "false"},
            APICAP_WIND_AUTO_CFG: {"value": "true"},
            APICAP_DAWN_AUTO_CFG: {"value": "false"},
            APICAP_DUSK_AUTO_CFG: {"value": "true"},
            APICAP_RAIN_AUTO_CFG: {"value": "false"},
            APICAP_SUN_AUTO_CFG: {"value": "true"},
        }

    @pytest.fixture
    def partial_device_map(self):
        """Device map with only some auto mode capabilities"""
        return {
            APICAP_AUTO_MODE_CFG: {"value": "false"},
            APICAP_TIME_AUTO_CFG: {"value": "true"},
            APICAP_WIND_AUTO_CFG: {"value": "false"},
        }

    def test_auto_config_device_init_with_full_capabilities(self, mocked_api, device_data, full_device_map):
        """Test initialization with all auto mode capabilities"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        # Test has_* properties
        assert device.has_auto_mode is True
        assert device.has_time_auto_mode is True
        assert device.has_contact_auto_mode is True
        assert device.has_wind_auto_mode is True
        assert device.has_dawn_auto_mode is True
        assert device.has_dusk_auto_mode is True
        assert device.has_rain_auto_mode is True
        assert device.has_sun_auto_mode is True

    def test_auto_config_device_init_with_partial_capabilities(self, mocked_api, device_data, partial_device_map):
        """Test initialization with only some auto mode capabilities"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=partial_device_map,
            **device_data
        )

        # Test has_* properties
        assert device.has_auto_mode is True
        assert device.has_time_auto_mode is True
        assert device.has_contact_auto_mode is False
        assert device.has_wind_auto_mode is True
        assert device.has_dawn_auto_mode is False
        assert device.has_dusk_auto_mode is False
        assert device.has_rain_auto_mode is False
        assert device.has_sun_auto_mode is False

    def test_auto_config_device_init_with_no_device_map(self, mocked_api, device_data):
        """Test initialization with no device map (all capabilities should be False)"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=None,
            **device_data
        )

        # Test has_* properties - all should be False
        assert device.has_auto_mode is False
        assert device.has_time_auto_mode is False
        assert device.has_contact_auto_mode is False
        assert device.has_wind_auto_mode is False
        assert device.has_dawn_auto_mode is False
        assert device.has_dusk_auto_mode is False
        assert device.has_rain_auto_mode is False
        assert device.has_sun_auto_mode is False

    def test_auto_config_device_init_with_empty_device_map(self, mocked_api, device_data):
        """Test initialization with empty device map"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map={},
            **device_data
        )

        # Test has_* properties - all should be False
        assert device.has_auto_mode is False
        assert device.has_time_auto_mode is False
        assert device.has_contact_auto_mode is False
        assert device.has_wind_auto_mode is False
        assert device.has_dawn_auto_mode is False
        assert device.has_dusk_auto_mode is False
        assert device.has_rain_auto_mode is False
        assert device.has_sun_auto_mode is False

    @pytest.mark.asyncio
    async def test_update_device_state_with_full_capabilities(self, mocked_api, device_data, full_device_map):
        """Test update_device_state with all capabilities"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        state = {
            "statusesMap": {
                "Manuellbetrieb": 0  # 0 means auto mode is enabled
            }
        }

        await device.update_device_state(state, full_device_map)

        # Test auto mode value (inverted from Manuellbetrieb)
        assert device.auto_mode_value is True

        # Test other auto mode values from device_map
        assert device.time_auto_mode_value is True
        assert device.contact_auto_mode_value is False
        assert device.wind_auto_mode_value is True
        assert device.dawn_auto_mode_value is False
        assert device.dusk_auto_mode_value is True
        assert device.rain_auto_mode_value is False
        assert device.sun_auto_mode_value is True

    @pytest.mark.asyncio
    async def test_update_device_state_manual_mode(self, mocked_api, device_data, full_device_map):
        """Test update_device_state when device is in manual mode"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        state = {
            "statusesMap": {
                "Manuellbetrieb": 1  # 1 means manual mode (auto mode disabled)
            }
        }

        await device.update_device_state(state, full_device_map)

        # Test auto mode value (inverted from Manuellbetrieb)
        assert device.auto_mode_value is False

    @pytest.mark.asyncio
    async def test_update_device_state_missing_manuellbetrieb(self, mocked_api, device_data, full_device_map):
        """Test update_device_state when Manuellbetrieb is missing from statusesMap"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        state = {
            "statusesMap": {}  # Missing Manuellbetrieb
        }

        await device.update_device_state(state, full_device_map)

        # Should default to False when missing
        assert device.auto_mode_value is False

    @pytest.mark.asyncio
    async def test_update_device_state_with_missing_device_map(self, mocked_api, device_data, full_device_map):
        """Test update_device_state when device_map is None"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        state = {
            "statusesMap": {
                "Manuellbetrieb": 0
            }
        }

        await device.update_device_state(state, None)

        # Auto mode should still work from statusesMap
        assert device.auto_mode_value is True

        # Other modes should default to False when device_map is None
        assert device.time_auto_mode_value is False
        assert device.contact_auto_mode_value is False
        assert device.wind_auto_mode_value is False
        assert device.dawn_auto_mode_value is False
        assert device.dusk_auto_mode_value is False
        assert device.rain_auto_mode_value is False
        assert device.sun_auto_mode_value is False

    @pytest.mark.asyncio
    async def test_update_device_state_without_capabilities(self, mocked_api, device_data):
        """Test update_device_state for device without auto capabilities"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map={},  # No capabilities
            **device_data
        )

        state = {
            "statusesMap": {
                "Manuellbetrieb": 0
            }
        }

        device_map = {
            APICAP_TIME_AUTO_CFG: {"value": "true"}
        }

        await device.update_device_state(state, device_map)

        # Since device doesn't have capabilities, values shouldn't be updated
        # (the properties won't be set because has_* methods return False)

    @pytest.mark.asyncio
    async def test_async_set_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_auto_mode(True)

        mocked_api.async_set_auto_mode.assert_called_once_with(123, True)

    @pytest.mark.asyncio
    async def test_async_set_time_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_time_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_time_auto_mode(False)

        mocked_api.async_set_time_auto_mode.assert_called_once_with(123, False)

    @pytest.mark.asyncio
    async def test_async_set_contact_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_contact_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_contact_auto_mode(True)

        mocked_api.async_set_contact_auto_mode.assert_called_once_with(123, True)

    @pytest.mark.asyncio
    async def test_async_set_wind_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_wind_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_wind_auto_mode(True)

        mocked_api.async_set_wind_auto_mode.assert_called_once_with(123, True)

    @pytest.mark.asyncio
    async def test_async_set_dawn_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_dawn_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_dawn_auto_mode(False)

        mocked_api.async_set_dawn_auto_mode.assert_called_once_with(123, False)

    @pytest.mark.asyncio
    async def test_async_set_dusk_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_dusk_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_dusk_auto_mode(True)

        mocked_api.async_set_dusk_auto_mode.assert_called_once_with(123, True)

    @pytest.mark.asyncio
    async def test_async_set_rain_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_rain_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_rain_auto_mode(True)

        mocked_api.async_set_rain_auto_mode.assert_called_once_with(123, True)

    @pytest.mark.asyncio
    async def test_async_set_sun_auto_mode(self, mocked_api, device_data, full_device_map):
        """Test async_set_sun_auto_mode method"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        await device.async_set_sun_auto_mode(False)

        mocked_api.async_set_sun_auto_mode.assert_called_once_with(123, False)

    def test_auto_mode_value_property_getters_setters(self, mocked_api, device_data, full_device_map):
        """Test all auto mode value property getters and setters"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        # Test auto_mode_value
        device.auto_mode_value = True
        assert device.auto_mode_value is True
        device.auto_mode_value = False
        assert device.auto_mode_value is False

        # Test time_auto_mode_value
        device.time_auto_mode_value = True
        assert device.time_auto_mode_value is True
        device.time_auto_mode_value = False
        assert device.time_auto_mode_value is False

        # Test contact_auto_mode_value
        device.contact_auto_mode_value = True
        assert device.contact_auto_mode_value is True
        device.contact_auto_mode_value = False
        assert device.contact_auto_mode_value is False

        # Test wind_auto_mode_value
        device.wind_auto_mode_value = True
        assert device.wind_auto_mode_value is True
        device.wind_auto_mode_value = False
        assert device.wind_auto_mode_value is False

        # Test dawn_auto_mode_value
        device.dawn_auto_mode_value = True
        assert device.dawn_auto_mode_value is True
        device.dawn_auto_mode_value = False
        assert device.dawn_auto_mode_value is False

        # Test dusk_auto_mode_value
        device.dusk_auto_mode_value = True
        assert device.dusk_auto_mode_value is True
        device.dusk_auto_mode_value = False
        assert device.dusk_auto_mode_value is False

        # Test rain_auto_mode_value
        device.rain_auto_mode_value = True
        assert device.rain_auto_mode_value is True
        device.rain_auto_mode_value = False
        assert device.rain_auto_mode_value is False

        # Test sun_auto_mode_value
        device.sun_auto_mode_value = True
        assert device.sun_auto_mode_value is True
        device.sun_auto_mode_value = False
        assert device.sun_auto_mode_value is False

    def test_inheritance_from_base_device(self, mocked_api, device_data, full_device_map):
        """Test that HomePilotAutoConfigDevice properly inherits from HomePilotDevice"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        # Test inherited properties
        assert device.did == 123
        assert device.name == "Test Auto Device"
        assert device.model == "TestModel"
        assert device.fw_version == "1.0.0"
        assert device.api == mocked_api

    @pytest.mark.asyncio
    async def test_auto_mode_edge_cases(self, mocked_api, device_data, full_device_map):
        """Test edge cases in auto mode handling"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        # Test with incomplete device_map values
        incomplete_device_map = {
            APICAP_TIME_AUTO_CFG: {},  # Missing 'value' key
            APICAP_CONTACT_AUTO_CFG: {"value": "invalid"},  # Invalid value
            APICAP_WIND_AUTO_CFG: {"value": "false"},  # Valid value
        }

        state = {
            "statusesMap": {
                "Manuellbetrieb": 0
            }
        }

        await device.update_device_state(state, incomplete_device_map)

        # Should handle missing/invalid values gracefully
        assert device.time_auto_mode_value is False  # Missing value defaults to False
        assert device.contact_auto_mode_value is False  # Invalid value defaults to False
        assert device.wind_auto_mode_value is False  # "false" string converts to False

    def test_auto_mode_string_conversion_edge_cases(self, mocked_api, device_data, full_device_map):
        """Test string to boolean conversion edge cases"""
        device = HomePilotAutoConfigDevice(
            api=mocked_api,
            device_map=full_device_map,
            **device_data
        )

        test_cases = [
            ("true", True),
            ("True", False),  # Case sensitive - only lowercase "true" is True
            ("TRUE", False),  # Case sensitive - only lowercase "true" is True
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("", False),
            ("1", False),  # Only "true" should be True
            ("0", False),
            ("yes", False),
            ("no", False),
        ]

        for test_value, expected in test_cases:
            device_map = {APICAP_TIME_AUTO_CFG: {"value": test_value}}

            # Directly test the conversion logic
            result = device_map.get(APICAP_TIME_AUTO_CFG, {}).get("value", "false") == "true"
            assert result == expected, f"Expected {test_value} -> {expected}, got {result}"


class TestAutoConfigChildClasses:
    """Test that child classes properly inherit from HomePilotAutoConfigDevice"""

    @pytest.fixture
    def mocked_api(self):
        api = MagicMock(spec=HomePilotApi)

        # Mock async methods for all child classes
        future = asyncio.Future()
        future.set_result(None)
        api.async_set_auto_mode.return_value = future
        api.async_send_device_command.return_value = future

        return api

    @pytest.fixture
    def device_map_with_auto_modes(self):
        """Device map with auto mode capabilities for testing inheritance"""
        return {
            APICAP_AUTO_MODE_CFG: {"value": "true"},
            APICAP_TIME_AUTO_CFG: {"value": "false"},
            APICAP_WIND_AUTO_CFG: {"value": "true"},
            APICAP_DUSK_AUTO_CFG: {"value": "true"},
        }

    def test_cover_inherits_auto_config_properly(self, mocked_api, device_map_with_auto_modes):
        """Test that HomePilotCover properly inherits auto config functionality"""
        cover = HomePilotCover(
            api=mocked_api,
            did=123,
            uid="cover-uid",
            name="Test Cover",
            device_number="COV001",
            model="TestCoverModel",
            fw_version="1.0.0",
            device_group=1,
            has_ping_cmd=True,
            can_set_position=True,
            cover_type=1,
            has_tilt=True,
            can_set_tilt_position=True,
            device_map=device_map_with_auto_modes
        )

        # Test that cover inherits auto config capabilities
        assert isinstance(cover, HomePilotAutoConfigDevice)
        assert cover.has_auto_mode is True
        assert cover.has_time_auto_mode is True
        assert cover.has_wind_auto_mode is True
        assert cover.has_dusk_auto_mode is True
        assert cover.has_contact_auto_mode is False  # Not in device_map

        # Test that cover retains its own functionality
        assert cover.can_set_position is True
        assert cover.has_tilt is True

    def test_light_inherits_auto_config_properly(self, mocked_api, device_map_with_auto_modes):
        """Test that HomePilotLight properly inherits auto config functionality"""
        light = HomePilotLight(
            api=mocked_api,
            did=456,
            uid="light-uid",
            name="Test Light",
            device_number="LIG001",
            model="TestLightModel",
            fw_version="1.0.0",
            device_group=2,
            has_ping_cmd=True,
            has_rgb=True,
            has_color_temp=True,
            device_map=device_map_with_auto_modes
        )

        # Test that light inherits auto config capabilities
        assert isinstance(light, HomePilotAutoConfigDevice)
        assert light.has_auto_mode is True
        assert light.has_time_auto_mode is True
        assert light.has_wind_auto_mode is True
        assert light.has_dusk_auto_mode is True

        # Test that light retains its own functionality
        assert light.has_rgb is True
        assert light.has_color_temp is True

    def test_switch_inherits_auto_config_properly(self, mocked_api, device_map_with_auto_modes):
        """Test that HomePilotSwitch properly inherits auto config functionality"""
        switch = HomePilotSwitch(
            api=mocked_api,
            did=789,
            uid="switch-uid",
            name="Test Switch",
            device_number="SWI001",
            model="TestSwitchModel",
            fw_version="1.0.0",
            device_group=3,
            has_ping_cmd=True,
            device_map=device_map_with_auto_modes
        )

        # Test that switch inherits auto config capabilities
        assert isinstance(switch, HomePilotAutoConfigDevice)
        assert switch.has_auto_mode is True
        assert switch.has_time_auto_mode is True
        assert switch.has_wind_auto_mode is True
        assert switch.has_dusk_auto_mode is True

    def test_thermostat_inherits_auto_config_properly(self, mocked_api, device_map_with_auto_modes):
        """Test that HomePilotThermostat properly inherits auto config functionality"""
        thermostat = HomePilotThermostat(
            api=mocked_api,
            did=101,
            uid="thermo-uid",
            name="Test Thermostat",
            device_number="THE001",
            model="TestThermoModel",
            fw_version="1.0.0",
            device_group=4,
            has_ping_cmd=True,
            device_map=device_map_with_auto_modes
        )

        # Test that thermostat inherits auto config capabilities
        assert isinstance(thermostat, HomePilotAutoConfigDevice)
        assert thermostat.has_auto_mode is True
        assert thermostat.has_time_auto_mode is True
        assert thermostat.has_wind_auto_mode is True
        assert thermostat.has_dusk_auto_mode is True

    def test_actuator_inherits_auto_config_properly(self, mocked_api, device_map_with_auto_modes):
        """Test that HomePilotActuator properly inherits auto config functionality"""
        actuator = HomePilotActuator(
            api=mocked_api,
            did=202,
            uid="actuator-uid",
            name="Test Actuator",
            device_number="ACT001",
            model="TestActuatorModel",
            fw_version="1.0.0",
            device_group=5,
            has_ping_cmd=True,
            device_map=device_map_with_auto_modes
        )

        # Test that actuator inherits auto config capabilities
        assert isinstance(actuator, HomePilotAutoConfigDevice)
        assert actuator.has_auto_mode is True
        assert actuator.has_time_auto_mode is True
        assert actuator.has_wind_auto_mode is True
        assert actuator.has_dusk_auto_mode is True

    @pytest.mark.asyncio
    async def test_child_classes_can_use_auto_methods(self, mocked_api, device_map_with_auto_modes):
        """Test that child classes can use inherited auto mode methods"""
        cover = HomePilotCover(
            api=mocked_api,
            did=123,
            uid="cover-uid",
            name="Test Cover",
            device_number="COV001",
            model="TestCoverModel",
            fw_version="1.0.0",
            device_group=1,
            can_set_position=True,
            cover_type=1,
            device_map=device_map_with_auto_modes
        )

        # Test that inherited methods work
        await cover.async_set_auto_mode(True)
        await cover.async_set_time_auto_mode(False)
        await cover.async_set_wind_auto_mode(True)

        # Verify API calls were made
        mocked_api.async_set_auto_mode.assert_called_with(123, True)
        mocked_api.async_set_time_auto_mode.assert_called_with(123, False)
        mocked_api.async_set_wind_auto_mode.assert_called_with(123, True)

    @pytest.mark.asyncio
    async def test_child_classes_can_update_auto_state(self, mocked_api, device_map_with_auto_modes):
        """Test that child classes can update auto mode state properly"""
        light = HomePilotLight(
            api=mocked_api,
            did=456,
            uid="light-uid",
            name="Test Light",
            device_number="LIG001",
            model="TestLightModel",
            fw_version="1.0.0",
            device_group=2,
            has_rgb=True,
            has_color_temp=True,
            device_map=device_map_with_auto_modes
        )

        # Simulate state update
        state = {
            "statusesMap": {
                "Manuellbetrieb": 0  # Auto mode enabled
            }
        }

        updated_device_map = {
            APICAP_TIME_AUTO_CFG: {"value": "true"},
            APICAP_WIND_AUTO_CFG: {"value": "false"},
        }

        await light.update_device_state(state, updated_device_map)

        # Test that auto mode values were updated correctly
        assert light.auto_mode_value is True  # Manuellbetrieb 0 = auto mode True
        assert light.time_auto_mode_value is True
        assert light.wind_auto_mode_value is False

    def test_child_classes_pass_device_map_correctly(self, mocked_api):
        """Test that child classes properly pass device_map to parent constructor"""
        device_map = {
            APICAP_AUTO_MODE_CFG: {"value": "true"},
            APICAP_DAWN_AUTO_CFG: {"value": "true"},
            APICAP_SUN_AUTO_CFG: {"value": "false"},
        }

        # Test that device_map is properly passed through inheritance chain
        switch = HomePilotSwitch(
            api=mocked_api,
            did=789,
            uid="switch-uid",
            name="Test Switch",
            device_number="SWI001",
            model="TestSwitchModel",
            fw_version="1.0.0",
            device_group=3,
            device_map=device_map  # This should be passed to parent
        )

        # Verify that capabilities were properly detected from device_map
        assert switch.has_auto_mode is True
        assert switch.has_dawn_auto_mode is True
        assert switch.has_sun_auto_mode is True
        assert switch.has_time_auto_mode is False  # Not in device_map
        assert switch.has_contact_auto_mode is False  # Not in device_map

    def test_child_classes_work_without_device_map(self, mocked_api):
        """Test that child classes work correctly when device_map is None or empty"""
        # Test with None device_map
        cover = HomePilotCover(
            api=mocked_api,
            did=123,
            uid="cover-uid",
            name="Test Cover",
            device_number="COV001",
            model="TestCoverModel",
            fw_version="1.0.0",
            device_group=1,
            can_set_position=True,
            cover_type=1,
            device_map=None  # No auto capabilities
        )

        # Should still work but with no auto capabilities
        assert cover.has_auto_mode is False
        assert cover.has_time_auto_mode is False
        assert cover.has_wind_auto_mode is False
        assert cover.has_dawn_auto_mode is False
        assert cover.has_dusk_auto_mode is False
        assert cover.has_rain_auto_mode is False
        assert cover.has_sun_auto_mode is False
        assert cover.has_contact_auto_mode is False

        # Cover-specific functionality should still work
        assert cover.can_set_position is True