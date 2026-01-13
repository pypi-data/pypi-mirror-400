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
    SUPPORTED_DEVICES,
)
from .api import HomePilotApi
from .device import HomePilotAutoConfigDevice, HomePilotDevice


class HomePilotActuator(HomePilotAutoConfigDevice):
    _is_on: bool
    _brightness: int

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
            device_map = device_map,
        )

    @staticmethod
    def build_from_api(api: HomePilotApi, did: str):
        return asyncio.run(HomePilotActuator.async_build_from_api(api, did))

    @staticmethod
    async def async_build_from_api(api: HomePilotApi, did):
        """Build a new HomePilotDevice from the response of API"""
        device = await api.get_device(did)
        device_map = HomePilotDevice.get_capabilities_map(device)
        return HomePilotActuator(
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
            fw_version=device_map[APICAP_VERSION_CFG]["value"]
            if APICAP_VERSION_CFG in device_map else "",
            device_group=device_map[APICAP_DEVICE_TYPE_LOC]["value"],
            has_ping_cmd=APICAP_PING_CMD in device_map,
            device_map=device_map,
        )

    async def update_state(self, state, api):
        await super().update_state(state, api)
        self.is_on = state["statusesMap"]["Position"] != 0
        self.brightness = state["statusesMap"]["Position"]
        device_map = HomePilotDevice.get_capabilities_map(await self.api.get_device(self.did))
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

    async def async_turn_on(self) -> None:
        await self.api.async_turn_on(self.did)

    async def async_turn_off(self) -> None:
        await self.api.async_turn_off(self.did)

    async def async_set_brightness(self, new_brightness) -> None:
        await self.api.async_set_position(self.did, new_brightness)

    async def async_toggle(self) -> None:
        if self.is_on:
            await self.async_turn_off()
        else:
            await self.async_turn_on()
