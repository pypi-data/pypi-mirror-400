import hashlib
from typing import Any

import aiohttp
from aiohttp import ClientConnectorError
from aiohttp.abc import AbstractCookieJar
from .const import (
    APICAP_AUTO_MODE_CFG,
    APICAP_GOTO_POS_CMD,
    APICAP_PING_CMD,
    APICAP_POS_DOWN_CMD,
    APICAP_POS_UP_CMD,
    APICAP_STOP_CMD,
    APICAP_TARGET_TEMPERATURE_CFG,
    APICAP_TURN_OFF_CMD,
    APICAP_TURN_ON_CMD,
    APICAP_SET_SLAT_POS_CMD,
    APICAP_STOP_SLAT_CMD,
    APICAP_VENTIL_POS_CFG,
    APICAP_VENTIL_POS_MODE_CFG,
    APICAP_SET_RGB_CMD,
    APICAP_SET_COLOR_TEMP_CMD,
    APICAP_TIME_AUTO_CFG,
    APICAP_CONTACT_AUTO_CFG,
    APICAP_WIND_AUTO_CFG,
    APICAP_DAWN_AUTO_CFG,
    APICAP_DUSK_AUTO_CFG,
    APICAP_RAIN_AUTO_CFG,
    APICAP_SUN_AUTO_CFG,
    APICAP_BOOST_TIME_CFG,
    APICAP_BOOST_ACTIVE_CFG,
    APICAP_CONTACT_OPEN_CMD,
    APICAP_CONTACT_CLOSE_CMD,
    APICAP_SUN_START_CMD,
    APICAP_SUN_STOP_CMD,
    APICAP_WIND_START_CMD,
    APICAP_WIND_STOP_CMD,
    APICAP_RAIN_START_CMD,
    APICAP_RAIN_STOP_CMD,
    APICAP_GOTO_DAWN_POS_CMD,
    APICAP_GOTO_DUSK_POS_CMD,
)


class HomePilotApi:
    _host: str
    _password: str
    _api_version: int
    _base_path: str
    _authenticated: bool = False
    _cookie_jar: Any = None
    _session: aiohttp.ClientSession | None = None

    def __init__(self, host, password, api_version = 1) -> None:
        self._host = host
        self._password = password
        self._api_version = api_version
        self._base_path = HomePilotApi.get_base_path(api_version)
        self._session = None
        self._cookie_jar = None 

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create persistent session"""
        if self._session is None or self._session.closed:
            if self._cookie_jar is None:
                self._cookie_jar = aiohttp.CookieJar(unsafe=True)
            self._session = aiohttp.ClientSession(cookie_jar=self._cookie_jar)
        return self._session

    async def async_close(self):
        """Close the session properly"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
        self._authenticated = False
    @staticmethod
    async def test_connection(host: str) -> str:
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(f"http://{host}/")
                if response.status != 200:
                    response = await session.get(f"http://{host}/hp/devices/0")
                    if response.status != 200:
                        if response.status != 401:
                            return "error"
                        # Otherwise try for login requirements
                    else:
                        return "ok_v2"

                response = await session.post(
                    f"http://{host}/authentication/password_salt"
                )
                if response.status == 500:
                    return "ok"
                else:
                    if response.status == 401:
                        response = await session.post(
                            f"http://{host}/hp/authentication/password_salt"
                        )
                        if response.status == 200:
                            return "auth_required_v2"
                        else:
                            return "error"
                    return "auth_required"
            except ClientConnectorError:
                return "error"

    @staticmethod
    def get_base_path(api_version) -> str:
        if api_version == 2:
            return "/hp"
        else:
            return ""

    @staticmethod
    async def test_auth(host: str, password: str, api_version: int = 1, session_in: aiohttp.ClientSession = None) -> AbstractCookieJar:
        session = session_in or aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))
        try:
            base_path = HomePilotApi.get_base_path(api_version)
            async with session.post(f"http://{host}{base_path}/authentication/password_salt") as response:
                response_data = await response.json()
                if response.status == 500 and response_data["error_code"] == 5007:
                    raise AuthError()
                if response.status != 200 or response_data["error_code"] != 0:
                    raise CannotConnect()
                salt = response_data["password_salt"]
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
                salted_password = hashlib.sha256(
                    f"{salt}{hashed_password}".encode("utf-8")
                ).hexdigest()
                response = await session.post(
                    f"http://{host}{base_path}/authentication/login",
                    json={"password": salted_password, "password_salt": salt},
                )
                if response.status != 200:
                    raise AuthError()
                return session.cookie_jar
        finally:
            if session_in is None:
                await session.close()
                
    async def authenticate(self):
        if not self.authenticated and self.password != "":
            self.cookie_jar = await HomePilotApi.test_auth(self.host, self.password, self.api_version, await self._get_session())
            self._authenticated = True

    async def get_devices(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(f"http://{self._host}{self._base_path}/devices") as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            if response["error_code"] != 0:
                return []
            if "payload" in response and "devices" in response["payload"]:
                devices = response["payload"]["devices"]
                return devices
            return []

    async def get_device(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(f"http://{self._host}{self._base_path}/devices/{did}") as response:
            response = await response.json()
            if response["error_code"] != 0:
                return []
            if "payload" in response and "device" in response["payload"]:
                device = response["payload"]["device"]
                return device
            return None

    async def async_get_fw_status(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/service/system-update-image/status"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            return response

    async def async_get_interfaces(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/service/system/networkmgr/v1/interfaces"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            return response

    async def async_get_fw_version(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/service/system-update-image/version"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            return response

    async def async_get_nodename(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/service/system/networkmgr/v1/nodename"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            return response

    async def async_get_led_status(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/service/system/leds/status"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            return response

    async def async_get_device_state(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/v4/devices/{did}"
        ) as response:
            response = await response.json()
            if response["response"] != "get_device":
                device = {}
            else:
                if "device" in response:
                    device = response["device"]
                else:
                    device = {}
            return device

    async def async_get_devices_state(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/v4/devices?devtype=Actuator"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            if response["response"] != "get_visible_devices":
                actuators = {}
            else:
                if response["devices"]:
                    devices = response["devices"]
                    actuators = {str(device["did"]): device for device in devices}
                else:
                    actuators = {}
        async with session.get(
            f"http://{self._host}{self._base_path}/v4/devices?devtype=Sensor"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            if response["response"] != "get_meters":
                sensors = {}
            else:
                if response["meters"]:
                    devices = response["meters"]
                    sensors = {str(device["did"]): device for device in devices}
                else:
                    sensors = {}
        async with session.get(
            f"http://{self._host}{self._base_path}/v4/devices?devtype=Transmitter"
        ) as response:
            if response.status == 401:
                raise AuthError()
            response = await response.json()
            if response["response"] != "get_transmitters":
                transmitters = {}
            else:
                if response["transmitters"]:
                    devices = response["transmitters"]
                    transmitters = {str(device["did"]): device for device in devices}
                else:
                    transmitters = {}
        return {**actuators, **sensors, **transmitters}

    async def async_ping(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}", json={"name": APICAP_PING_CMD}
        ) as response:
            return await response.json()

    async def async_open_cover(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}", json={"name": APICAP_POS_UP_CMD}
        ) as response:
            return await response.json()

    async def async_close_cover(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}", json={"name": APICAP_POS_DOWN_CMD}
        ) as response:
            return await response.json()

    async def async_stop_cover(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}", json={"name": APICAP_STOP_CMD}
        ) as response:
            return await response.json()

    async def async_set_position(self, did, position):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_GOTO_POS_CMD, "value": position},
        ) as response:
            return await response.json()

    async def async_open_cover_tilt(self, did) -> None:
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_SET_SLAT_POS_CMD, "value": 0},
        ) as response:
            return await response.json()

    async def async_close_cover_tilt(self, did) -> None:
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_SET_SLAT_POS_CMD, "value": 100},
        ) as response:
            return await response.json()

    async def async_set_cover_tilt_position(self, did, position) -> None:
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_SET_SLAT_POS_CMD, "value": position},
        ) as response:
            return await response.json()

    async def async_stop_cover_tilt(self, did) -> None:
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_STOP_SLAT_CMD},
        ) as response:
            return await response.json()

    async def async_set_ventilation_position_mode(self, did, mode) -> None:
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_VENTIL_POS_MODE_CFG, "value": mode},
        ) as response:
            return await response.json()

    async def async_set_ventilation_position(self, did, position) -> None:
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_VENTIL_POS_CFG, "value": str(int(position))},
        ) as response:
            return await response.json()

    async def async_turn_on(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}", json={"name": APICAP_TURN_ON_CMD}
        ) as response:
            return await response.json()

    async def async_turn_off(self, did):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}", json={"name": APICAP_TURN_OFF_CMD}
        ) as response:
            return await response.json()

    async def async_set_target_temperature(self, did, temperature):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_TARGET_TEMPERATURE_CFG, "value": temperature},
        ) as response:
            return await response.json()

    async def async_send_device_command(self, did, command, value):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": command, "value": value},
        ) as response:
            return await response.json()

    async def async_set_auto_mode(self, did, auto_mode):
        return await self.async_send_device_command(did, APICAP_AUTO_MODE_CFG, auto_mode)

    async def async_set_temperature_thresh_cfg(self, did, thresh_number, temperature):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": f"TEMPERATURE_THRESH_{thresh_number}_CFG", "value": temperature},
        ) as response:
            return await response.json()

    async def async_set_rgb(self, did, rgb_value):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_SET_RGB_CMD, "value": rgb_value},
        ) as response:
            return await response.json()

    async def async_set_color_temp(self, did, color_temp_value):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/devices/{did}",
            json={"name": APICAP_SET_COLOR_TEMP_CMD, "value": color_temp_value},
        ) as response:
            return await response.json()

    async def async_turn_led_on(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.post(
            f"http://{self._host}{self._base_path}/service/system/leds/enable"
        ) as response:
            return await response.json()

    async def async_turn_led_off(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.post(
            f"http://{self._host}{self._base_path}/service/system/leds/disable"
        ) as response:
            return await response.json()

    async def async_set_auto_update_on(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/service/system-update-image/auto_update",
            json={"auto_update": True},
        ) as response:
            return await response.json()

    async def async_set_auto_update_off(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.put(
            f"http://{self._host}{self._base_path}/service/system-update-image/auto_update",
            json={"auto_update": False},
        ) as response:
            return await response.json()

    async def async_update_firmware(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.post(
            f"http://{self._host}{self._base_path}/service/system-update-image/startupdate"
        ) as response:
            return await response.json()

# Scenes
    async def async_get_scenes(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/scenes"
        ) as response:
            if response.status == 401:
                raise AuthError()
            if response.status == 200:
                responseJson = await response.json()
                if "scenes" in responseJson:
                    scenes = responseJson["scenes"]
                    return scenes
            return []

    async def async_get_scenes_v4(self):
        await self.authenticate()
        session = await self._get_session()
        async with session.get(
            f"http://{self._host}{self._base_path}/v4/scenes"
        ) as response:
            if response.status == 401:
                raise AuthError()
            if response.status == 200:
                responseJson = await response.json()
                if "scenes" in responseJson:
                    scenes = responseJson["scenes"]
                    return scenes
            return []

    async def async_execute_scene(self, sid: int):
        await self.authenticate()
        session = await self._get_session()
        async with session.post(
            f"http://{self._host}{self._base_path}/scenes/{sid}/actions",
            json={ "request_type": "EXECUTESCENE", "trigger_event": "TRIGGER_SCENE_MANUALLY_EVT" }
        ) as response:
            return await response.json()

    async def async_activate_scene(self, sid: int):
        await self.authenticate()
        session = await self._get_session()
        async with session.post(
            f"http://{self._host}{self._base_path}/scenes/{sid}/actions",
            json={ "request_type": "SWITCHSCENE", "trigger_event": "SCENE_MODE_CMD", "value": True }
        ) as response:
            return await response.json()

    async def async_deactivate_scene(self, sid: int):
        await self.authenticate()
        session = await self._get_session()
        async with session.post(
            f"http://{self._host}{self._base_path}/scenes/{sid}/actions",
            json={ "request_type": "SWITCHSCENE", "trigger_event": "SCENE_MODE_CMD", "value": False }
        ) as response:
            return await response.json()

    async def async_set_time_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_TIME_AUTO_CFG, auto_mode)

    async def async_set_contact_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_CONTACT_AUTO_CFG, auto_mode)

    async def async_set_wind_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_WIND_AUTO_CFG, auto_mode)

    async def async_set_dawn_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_DAWN_AUTO_CFG, auto_mode)

    async def async_set_dusk_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_DUSK_AUTO_CFG, auto_mode)

    async def async_set_rain_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_RAIN_AUTO_CFG, auto_mode)

    async def async_set_sun_auto_mode(self, did, auto_mode):
        await self.async_send_device_command(did, APICAP_SUN_AUTO_CFG, auto_mode)

    async def async_contact_open_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_CONTACT_OPEN_CMD, None)

    async def async_contact_close_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_CONTACT_CLOSE_CMD, None)

    async def async_set_boost_active_cfg(self, did, boost_active):
        return await self.async_send_device_command(did, APICAP_BOOST_ACTIVE_CFG, boost_active)

    async def async_set_boost_time_cfg(self, did, boost_time):
        return await self.async_send_device_command(did, APICAP_BOOST_TIME_CFG, boost_time)

    async def async_sun_start_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_SUN_START_CMD, None)

    async def async_sun_stop_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_SUN_STOP_CMD, None)

    async def async_wind_start_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_WIND_START_CMD, None)

    async def async_wind_stop_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_WIND_STOP_CMD, None)

    async def async_rain_start_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_RAIN_START_CMD, None)

    async def async_rain_stop_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_RAIN_STOP_CMD, None)

    async def async_goto_dawn_pos_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_GOTO_DAWN_POS_CMD, None)

    async def async_goto_dusk_pos_cmd(self, did):
        return await self.async_send_device_command(did, APICAP_GOTO_DUSK_POS_CMD, None)

    @property
    def host(self):
        return self._host

    @property
    def password(self):
        return self._password

    @property
    def api_version(self):
        return self._api_version

    @property
    def authenticated(self):
        return self._authenticated

    @property
    def cookie_jar(self):
        return self._cookie_jar

    @cookie_jar.setter
    def cookie_jar(self, cookie_jar):
        self._cookie_jar = cookie_jar

class CannotConnect(BaseException):
    """Error to indicate we cannot connect."""


class AuthError(BaseException):
    """Error to indicate an authentication error."""
