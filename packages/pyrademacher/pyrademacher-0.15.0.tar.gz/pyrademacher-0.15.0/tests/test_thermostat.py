import asyncio
import json
from unittest.mock import MagicMock

import pytest

from homepilot.thermostat import HomePilotThermostat


class TestHomePilotThermostat:
    @pytest.fixture
    def mocked_api(self):
        f = open("tests/test_files/device_thermostat.json")
        j = json.load(f)
        api = MagicMock()
        func_get_device = asyncio.Future()
        func_get_device.set_result(j["payload"]["device"])
        api.get_device.return_value = func_get_device
        func_set_target_temperature = asyncio.Future()
        func_set_target_temperature.set_result(None)
        api.async_set_target_temperature.return_value = func_set_target_temperature
        func_set_auto_mode = asyncio.Future()
        func_set_auto_mode.set_result(None)
        api.async_set_auto_mode.return_value = func_set_auto_mode
        func_contact_open_cmd = asyncio.Future()
        func_contact_open_cmd.set_result(None)
        api.async_contact_open_cmd.return_value = func_contact_open_cmd
        func_contact_close_cmd = asyncio.Future()
        func_contact_close_cmd.set_result(None)
        api.async_contact_close_cmd.return_value = func_contact_close_cmd
        func_set_boost_active_cfg = asyncio.Future()
        func_set_boost_active_cfg.set_result(None)
        api.async_set_boost_active_cfg.return_value = func_set_boost_active_cfg
        func_set_boost_time_cfg = asyncio.Future()
        func_set_boost_time_cfg.set_result(None)
        api.async_set_boost_time_cfg.return_value = func_set_boost_time_cfg
        func_contact_open_cmd = asyncio.Future()
        func_contact_open_cmd.set_result(None)
        api.async_contact_open_cmd.return_value = func_contact_open_cmd
        func_contact_close_cmd = asyncio.Future()
        func_contact_close_cmd.set_result(None)
        api.async_contact_close_cmd.return_value = func_contact_close_cmd
        func_set_boost_active_cfg = asyncio.Future()
        func_set_boost_active_cfg.set_result(None)
        api.async_set_boost_active_cfg.return_value = func_set_boost_active_cfg
        func_set_boost_time_cfg = asyncio.Future()
        func_set_boost_time_cfg.set_result(None)
        api.async_set_boost_time_cfg.return_value = func_set_boost_time_cfg
        yield api

    @pytest.mark.asyncio
    async def test_build_from_api(self, mocked_api):
        thermostat: HomePilotThermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        assert thermostat.did == "1010014"
        assert thermostat.uid == "733e25_A_1"
        assert thermostat.name == "Wohnzimmer-Raumthermostat"
        assert thermostat.device_number == "32501812_A"
        assert thermostat.device_group == "5"
        assert thermostat.fw_version == "1.4-1"
        assert thermostat.model == "DuoFern Room Thermostat"
        assert thermostat.has_ping_cmd is True
        assert thermostat.min_temperature == -40.0
        assert thermostat.max_temperature == 80.0
        assert thermostat.has_temperature is True
        assert thermostat.has_target_temperature is True
        assert thermostat.can_set_target_temperature is True
        assert thermostat.min_target_temperature == 4.0
        assert thermostat.max_target_temperature == 40.0
        assert thermostat.step_target_temperature == 0.5
        assert thermostat.has_relais_status is True
        assert thermostat.has_ext_open_window_detect is True
        assert thermostat.has_int_open_window_detect is True
        assert thermostat.has_boost_time is True
        assert thermostat.has_boost_active is True
        assert thermostat.has_contact_open_cmd is True
        assert thermostat.has_contact_close_cmd is True

    @pytest.mark.asyncio
    async def test_update_state(self, mocked_api):
        thermostat: HomePilotThermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.update_state({
            "statusesMap": {
                "Manuellbetrieb": 100,
                "Position": 240,
                "acttemperatur": 212,
                "relaisstatus": 1,
                "automaticvalue": 215,
                "manualoverride": 0
            },
            "statusValid": True
        }, mocked_api)
        assert thermostat.temperature_value == 21.2
        assert thermostat.target_temperature_value == 24.0
        assert thermostat.relais_status == 1
        assert thermostat.ext_open_window_detect_value is False
        assert thermostat.int_open_window_detect_value is True
        assert thermostat.boost_time_value == 30.0
        assert thermostat.boost_active_value is False
        assert thermostat.ext_open_window_detect_value is False
        assert thermostat.int_open_window_detect_value is True
        assert thermostat.boost_time_value == 30.0
        assert thermostat.boost_active_value is False

    @pytest.mark.asyncio
    async def test_async_set_target_temperature(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_set_target_temperature(10)
        mocked_api.async_set_target_temperature.assert_called_with('1010014', 10)

    @pytest.mark.asyncio
    async def test_async_set_auto_mode(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_set_auto_mode(True)
        mocked_api.async_set_auto_mode.assert_called_with('1010014', True)

    @pytest.mark.asyncio
    async def test_async_contact_open_cmd(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_contact_open_cmd()
        mocked_api.async_contact_open_cmd.assert_called_with('1010014')

    @pytest.mark.asyncio
    async def test_async_contact_close_cmd(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_contact_close_cmd()
        mocked_api.async_contact_close_cmd.assert_called_with('1010014')

    @pytest.mark.asyncio
    async def test_async_set_boost_active_cfg(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_set_boost_active_cfg(True)
        mocked_api.async_set_boost_active_cfg.assert_called_with('1010014', True)

    @pytest.mark.asyncio
    async def test_async_set_boost_time_cfg(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_set_boost_time_cfg(60.0)
        mocked_api.async_set_boost_time_cfg.assert_called_with('1010014', 60.0)

    @pytest.mark.asyncio
    async def test_async_contact_open_cmd(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_contact_open_cmd()
        mocked_api.async_contact_open_cmd.assert_called_with('1010014')

    @pytest.mark.asyncio
    async def test_async_contact_close_cmd(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_contact_close_cmd()
        mocked_api.async_contact_close_cmd.assert_called_with('1010014')

    @pytest.mark.asyncio
    async def test_async_set_boost_active_cfg(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_set_boost_active_cfg(True)
        mocked_api.async_set_boost_active_cfg.assert_called_with('1010014', True)

    @pytest.mark.asyncio
    async def test_async_set_boost_time_cfg(self, mocked_api):
        thermostat = await HomePilotThermostat.async_build_from_api(mocked_api, 1)
        await thermostat.async_set_boost_time_cfg(60.0)
        mocked_api.async_set_boost_time_cfg.assert_called_with('1010014', 60.0)
