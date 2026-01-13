import asyncio

from .const import (
    APICAP_DEVICE_TYPE_LOC,
    APICAP_ID_DEVICE_LOC,
    APICAP_NAME_DEVICE_LOC,
    APICAP_PING_CMD,
    APICAP_PROD_CODE_DEVICE_LOC,
    APICAP_PROT_ID_DEVICE_LOC,
    APICAP_VERSION_CFG,
    SUPPORTED_DEVICES,
    APICAP_BATT_LOW_EVT,
)
from .api import HomePilotApi
from .device import HomePilotDevice

import logging
_LOGGER = logging.getLogger(__name__)

class HomePilotWallController(HomePilotDevice):
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
        has_battery_low: bool = False,
        channels = None,
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
        )
        self._channels = channels
        self._has_battery_low = has_battery_low
        for channel in self._channels:
            setattr(self, f"channel_{channel}", False)

    @staticmethod
    def build_from_api(api: HomePilotApi, did: str):
        return asyncio.run(HomePilotWallController.async_build_from_api(api, did))

    @staticmethod
    async def async_build_from_api(api: HomePilotApi, did):
        """Build a new HomePilotDevice from the response of API"""
        device = await api.get_device(did)
        device_map = HomePilotDevice.get_capabilities_map(device)
        channels = {}
        for i in range(len(device_map)):
            if f"KEY_PUSH_CH{i}_EVT" in device_map:
                channels[i] = device_map[f"KEY_PUSH_CH{i}_EVT"]["timestamp"]
        return HomePilotWallController(
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
            has_battery_low=APICAP_BATT_LOW_EVT in device_map,
            channels=channels,
        )

    async def update_state(self, state, api):
        await super().update_state(state, api)
        if self.has_battery_low and "batteryLow" in state:
            self.battery_low_value = state["batteryLow"]
    
    async def update_channels(self):
        device_map = HomePilotDevice.get_capabilities_map(await self.api.get_device(self.did))
        for i in range(len(device_map)):
            if f"KEY_PUSH_CH{i}_EVT" in device_map:
                keypush = False
                if self._channels[i] != device_map[f"KEY_PUSH_CH{i}_EVT"]["timestamp"]:
                    keypush = True
                setattr(self, f"channel_{i}", keypush)
                self._channels[i] = device_map[f"KEY_PUSH_CH{i}_EVT"]["timestamp"]

    @property
    def channels(self):
        return self._channels

    @property
    def has_battery_low(self) -> bool:
        return self._has_battery_low

    @property
    def battery_low_value(self) -> bool:
        return self._battery_low_value

    @battery_low_value.setter
    def battery_low_value(self, battery_low_value):
        self._battery_low_value = battery_low_value
