import asyncio
import json
from unittest.mock import MagicMock

import pytest

from homepilot.cover import HomePilotCover


class TestHomePilotCover:
    @pytest.fixture
    def mocked_api(self):
        f = open("tests/test_files/device_cover.json")
        j = json.load(f)
        api = MagicMock()
        func_get_device = asyncio.Future()
        func_get_device.set_result(j["payload"]["device"])
        api.get_device.return_value = func_get_device
        func_open_cover = asyncio.Future()
        func_open_cover.set_result(None)
        api.async_open_cover.return_value = func_open_cover
        func_close_cover = asyncio.Future()
        func_close_cover.set_result(None)
        api.async_close_cover.return_value = func_close_cover
        func_stop_cover = asyncio.Future()
        func_stop_cover.set_result(None)
        api.async_stop_cover.return_value = func_stop_cover
        func_set_position = asyncio.Future()
        func_set_position.set_result(None)
        api.async_set_position.return_value = func_set_position
        func_ping = asyncio.Future()
        func_ping.set_result(None)
        api.async_ping.return_value = func_ping
        # Add mocks for new weather program commands
        func_sun_start_cmd = asyncio.Future()
        func_sun_start_cmd.set_result(None)
        api.async_sun_start_cmd.return_value = func_sun_start_cmd
        func_sun_stop_cmd = asyncio.Future()
        func_sun_stop_cmd.set_result(None)
        api.async_sun_stop_cmd.return_value = func_sun_stop_cmd
        func_wind_start_cmd = asyncio.Future()
        func_wind_start_cmd.set_result(None)
        api.async_wind_start_cmd.return_value = func_wind_start_cmd
        func_wind_stop_cmd = asyncio.Future()
        func_wind_stop_cmd.set_result(None)
        api.async_wind_stop_cmd.return_value = func_wind_stop_cmd
        func_rain_start_cmd = asyncio.Future()
        func_rain_start_cmd.set_result(None)
        api.async_rain_start_cmd.return_value = func_rain_start_cmd
        func_rain_stop_cmd = asyncio.Future()
        func_rain_stop_cmd.set_result(None)
        api.async_rain_stop_cmd.return_value = func_rain_stop_cmd
        func_goto_dawn_pos_cmd = asyncio.Future()
        func_goto_dawn_pos_cmd.set_result(None)
        api.async_goto_dawn_pos_cmd.return_value = func_goto_dawn_pos_cmd
        func_goto_dusk_pos_cmd = asyncio.Future()
        func_goto_dusk_pos_cmd.set_result(None)
        api.async_goto_dusk_pos_cmd.return_value = func_goto_dusk_pos_cmd
        yield api

    @pytest.mark.asyncio
    async def test_build_from_api(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        assert cover.did == "1"
        assert cover.uid == "407903_1"
        assert cover.name == "Living Room Blinds"
        assert cover.device_number == "14234511"
        assert cover.device_group == "2"
        assert cover.fw_version == "1.2-1"
        assert cover.model == "RolloTron radio beltwinder"
        assert cover.has_ping_cmd is True
        assert cover.can_set_position is True
        assert cover.has_blocking_detection is True
        assert cover.has_obstacle_detection is True
        assert cover.has_sun_start_cmd is True
        assert cover.has_sun_stop_cmd is True
        assert cover.has_wind_start_cmd is True
        assert cover.has_wind_stop_cmd is True
        assert cover.has_rain_start_cmd is True
        assert cover.has_rain_stop_cmd is True
        assert cover.has_goto_dawn_pos_cmd is True
        assert cover.has_goto_dusk_pos_cmd is True
        assert cover.has_sun_prog_active is True
        assert cover.has_wind_prog_active is True
        assert cover.has_rain_prog_active is True

    @pytest.mark.asyncio
    async def test_update_state(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.update_state({
            "statusesMap": {
                "Position": 100,
                "slatposition": 34
            },
            "statusValid": True
        }, mocked_api)
        assert cover.is_closed is True
        assert cover.cover_position == 0
        assert cover.cover_tilt_position == 66
        assert cover.is_closing is False
        assert cover.is_opening is False
        assert cover.available is True
        assert cover.blocking_detection_status is False
        assert cover.obstacle_detection_status is False

        await cover.update_state({
            "statusesMap": {
                "Position": 40,
                "slatposition": 55
            },
            "statusValid": False
        }, mocked_api)
        assert cover.is_closed is False
        assert cover.cover_position == 60
        assert cover.cover_tilt_position == 45
        assert cover.is_closing is False
        assert cover.is_opening is False
        assert cover.available is False
        assert cover.blocking_detection_status is False
        assert cover.obstacle_detection_status is False

    @pytest.mark.asyncio
    async def test_async_open_cover(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_open_cover()
        mocked_api.async_open_cover.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_close_cover(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_close_cover()
        mocked_api.async_close_cover.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_stop_cover(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_stop_cover()
        mocked_api.async_stop_cover.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_set_cover_position(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_set_cover_position(40)
        mocked_api.async_set_position.assert_called_with('1', 60)

    @pytest.mark.asyncio
    async def test_async_ping(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_ping()
        mocked_api.async_ping.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_sun_start_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_sun_start_cmd()
        mocked_api.async_sun_start_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_sun_stop_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_sun_stop_cmd()
        mocked_api.async_sun_stop_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_wind_start_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_wind_start_cmd()
        mocked_api.async_wind_start_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_wind_stop_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_wind_stop_cmd()
        mocked_api.async_wind_stop_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_rain_start_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_rain_start_cmd()
        mocked_api.async_rain_start_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_rain_stop_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_rain_stop_cmd()
        mocked_api.async_rain_stop_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_goto_dawn_pos_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_goto_dawn_pos_cmd()
        mocked_api.async_goto_dawn_pos_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_async_goto_dusk_pos_cmd(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)
        await cover.async_goto_dusk_pos_cmd()
        mocked_api.async_goto_dusk_pos_cmd.assert_called_with('1')

    @pytest.mark.asyncio
    async def test_new_prog_active_properties(self, mocked_api):
        cover = await HomePilotCover.async_build_from_api(mocked_api, 1)

        # Test initial capability detection
        assert cover.has_sun_prog_active is True
        assert cover.has_wind_prog_active is True
        assert cover.has_rain_prog_active is True

        # Test state update for property values
        await cover.update_state({
            "statusesMap": {
                "Position": 50,
                "automaticvalue": 0,
                "manualoverride": 0
            },
            "statusValid": True
        }, mocked_api)

        # Verify values from device data
        assert cover.sun_prog_active_value is False
        assert cover.wind_prog_active_value is True
        assert cover.rain_prog_active_value is False

        # Test property setters
        cover.sun_prog_active_value = True
        assert cover.sun_prog_active_value is True

        cover.wind_prog_active_value = False
        assert cover.wind_prog_active_value is False

        cover.rain_prog_active_value = True
        assert cover.rain_prog_active_value is True
