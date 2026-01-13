import asyncio
from typing import Optional, Dict, Any
from .const import (
    APICAP_DEVICE_TYPE_LOC,
    APICAP_ID_DEVICE_LOC,
    APICAP_NAME_DEVICE_LOC,
    APICAP_PING_CMD,
    APICAP_PROD_CODE_DEVICE_LOC,
    APICAP_PROT_ID_DEVICE_LOC,
    APICAP_VERSION_CFG,
    APICAP_RGB_CFG,
    APICAP_COLOR_TEMP_CFG,
    APICAP_COLOR_MODE_CFG,
    SUPPORTED_DEVICES,
)
from .api import HomePilotApi
from .device import HomePilotDevice, HomePilotAutoConfigDevice

class HomePilotLight(HomePilotAutoConfigDevice):
    _is_on: bool
    _brightness: int
    _has_rgb: bool
    _r_value: int
    _g_value: int
    _b_value: int
    _has_color_temp: bool
    _color_temp_value: int
    _has_color_mode: int
    _color_mode: str

    def __init__(
        self,
        api: HomePilotApi,
        did: int,
        uid: str,
        name: str,
        device_number: str,
        model: str,
        fw_version: str,
        device_group: int,
        has_ping_cmd: bool = False,
        has_rgb: bool = False,
        has_color_temp: bool = False,
        has_color_mode: bool = False,
        device_map: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            api=api,
            did=did,
            uid=uid,
            name=name,
            device_number=device_number,
            model=model,
            fw_version=fw_version,
            device_group=device_group,
            has_ping_cmd=has_ping_cmd,
            device_map=device_map,
        )
        self._has_rgb = has_rgb
        self._has_color_temp = has_color_temp
        self._has_color_mode = has_color_mode


    @staticmethod
    def build_from_api(api: HomePilotApi, did: str):
        return asyncio.run(HomePilotLight.async_build_from_api(api, did))

    @staticmethod
    async def async_build_from_api(api: HomePilotApi, did):
        """Build a new HomePilotDevice from the response of API"""
        device = await api.get_device(did)
        device_map = HomePilotDevice.get_capabilities_map(device)
        return HomePilotLight(
            api=api,
            did=device_map[APICAP_ID_DEVICE_LOC]["value"],
            uid=device_map[APICAP_PROT_ID_DEVICE_LOC]["value"],
            name=device_map[APICAP_NAME_DEVICE_LOC]["value"],
            device_number=device_map[APICAP_PROD_CODE_DEVICE_LOC]["value"],
            model=SUPPORTED_DEVICES[device_map[APICAP_PROD_CODE_DEVICE_LOC]["value"]][
                "name"
            ]
            if device_map[APICAP_PROD_CODE_DEVICE_LOC]["value"] in SUPPORTED_DEVICES
            else "Generic Device",
            fw_version=device_map[APICAP_VERSION_CFG]["value"] if APICAP_VERSION_CFG in device_map else ""
            if APICAP_VERSION_CFG in device_map else "",
            device_group=device_map[APICAP_DEVICE_TYPE_LOC]["value"],
            has_ping_cmd=APICAP_PING_CMD in device_map,
            has_rgb=APICAP_RGB_CFG in device_map,
            has_color_temp=APICAP_COLOR_TEMP_CFG in device_map,
            has_color_mode=APICAP_COLOR_MODE_CFG in device_map,
            device_map=device_map,
        )

    async def update_state(self, state, api):
        await super().update_state(state, api)
        self.is_on = state["statusesMap"]["Position"] != 0
        self.brightness = state["statusesMap"]["Position"]
        if self.has_rgb:
            self.r_value: int = int(state["statusesMap"]["rgb"].lower()[2:4], 16)
            self.g_value: int = int(state["statusesMap"]["rgb"].lower()[4:6], 16)
            self.b_value: int = int(state["statusesMap"]["rgb"].lower()[6:8], 16)
        self.color_temp_value = state["statusesMap"]["colortemperature"] if self.has_color_temp else 0
        self.color_mode_value = state["statusesMap"]["colormode"] if self.has_color_mode else 0
        device = await api.get_device(self.did)
        device_map = HomePilotDevice.get_capabilities_map(device)
        await super().update_device_state(state, device_map)
    @property
    def is_on(self) -> bool:
        return self._is_on

    @is_on.setter
    def is_on(self, is_on):
        self._is_on = is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        self._brightness = brightness

    @property
    def has_rgb(self) -> int:
        return self._has_rgb

    @property
    def has_color_temp(self) -> int:
        return self._has_color_temp

    @property
    def has_color_mode(self) -> int:
        return self._has_color_mode

    @property
    def r_value(self) -> int:
        return self._r_value

    @r_value.setter
    def r_value(self, r_value):
        self._r_value = r_value

    @property
    def g_value(self) -> int:
        return self._g_value

    @g_value.setter
    def g_value(self, g_value):
        self._g_value = g_value

    @property
    def b_value(self) -> int:
        return self._b_value

    @b_value.setter
    def b_value(self, b_value):
        self._b_value = b_value

    @property
    def color_temp_value(self) -> int:
        return self._color_temp_value

    @color_temp_value.setter
    def color_temp_value(self, color_temp_value):
        self._color_temp_value = color_temp_value

    @property
    def color_mode_value(self) -> int:
        return self._color_mode_value

    @color_mode_value.setter
    def color_mode_value(self, color_mode_value):
        self._color_mode_value = color_mode_value

    async def async_turn_on(self) -> None:
        await self.api.async_turn_on(self.did)

    async def async_turn_off(self) -> None:
        await self.api.async_turn_off(self.did)

    async def async_set_brightness(self, new_brightness) -> None:
        await self.api.async_set_position(self.did, new_brightness)

    async def async_set_rgb(self, r, g, b) -> None:
        new_rgb: str = f"0x{(r * pow(2,16) + g * pow(2,8) + b):06X}"
        await self.api.async_set_rgb(self.did, new_rgb)

    async def async_set_color_temp(self, new_color_temp) -> None:
        await self.api.async_set_color_temp(self.did, new_color_temp)

    async def async_toggle(self) -> None:
        if self.is_on:
            await self.async_turn_off()
        else:
            await self.async_turn_on()
