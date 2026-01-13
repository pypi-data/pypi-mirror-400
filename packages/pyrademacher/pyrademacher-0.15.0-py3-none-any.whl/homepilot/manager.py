import asyncio
import logging
from typing import Dict

from .hub import HomePilotHub
from .sensor import HomePilotSensor
from .switch import HomePilotSwitch
from .cover import HomePilotCover
from .thermostat import HomePilotThermostat
from .actuator import HomePilotActuator
from .api import HomePilotApi, AuthError
from .wallcontroller import HomePilotWallController
from .scenes import HomePilotScene
from .light import  HomePilotLight

from .device import HomePilotDevice

_LOGGER = logging.getLogger(__name__)


class HomePilotManager:
    _api: HomePilotApi
    _devices: Dict[str, HomePilotDevice]
    _scenes: Dict[str, HomePilotScene]
    _include_non_manual_executable: bool

    def __init__(self, api: HomePilotApi, include_non_manual_executable: bool = False) -> None:
        self._api = api
        self._include_non_manual_executable = include_non_manual_executable

    @staticmethod
    def build_manager(api: HomePilotApi, include_non_manual_executable: bool = False):
        return asyncio.run(HomePilotManager.async_build_manager(api, include_non_manual_executable))

    @staticmethod
    async def async_build_manager(api: HomePilotApi, include_non_manual_executable: bool = False):
        manager = HomePilotManager(api, include_non_manual_executable)
        manager.devices = {
            id_type["did"]: await HomePilotManager.async_build_device(manager.api, id_type)
            for id_type in await manager.get_device_ids_types()
            if id_type["type"] in ["-1", "1", "2", "3", "4", "5", "8", "10", "70", "71", "72", "73", "74", "75", "76"]
        }
        try:
            manager.scenes = {
                scene["id"]: await HomePilotScene.async_build_scene(manager.api, scene)
                for scene in await manager.api.async_get_scenes()
                if include_non_manual_executable or scene.get("is_manual_executable", 0) == 1
            }
        except Exception():
            manager.scenes = {}
        return manager

    @staticmethod
    async def async_build_device(api, id_type):
        if id_type["type"] == "-1":
            return await HomePilotHub.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "1":
            return await HomePilotSwitch.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "2":
            return await HomePilotCover.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "3":
            return await HomePilotSensor.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "4":
            return await HomePilotActuator.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "5":
            return await HomePilotThermostat.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "8":
            return await HomePilotCover.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "10":
            return await HomePilotWallController.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "70":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "71":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "72":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "73":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "74":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "75":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        if id_type["type"] == "76":
            return await HomePilotLight.async_build_from_api(api, id_type["did"])
        return None

    async def get_hub_macaddress(self):
        interfaces = await self.api.async_get_interfaces()
        for k in interfaces["interfaces"]:
            if interfaces["interfaces"][k]["enabled"]:
                return interfaces["interfaces"][k]["address"]
        return None

    async def get_nodename(self):
        return (await self.api.async_get_nodename())["nodename"]

    async def get_hub_state(self):
        return {
            "status": await self.api.async_get_fw_status(),
            "version": await self.api.async_get_fw_version(),
            "led": await self.api.async_get_led_status(),
        }

    async def update_state(self, did):
        try:
            if did == "-1":
                state = await self.get_hub_state()
            else:
                state = await self.api.async_get_device_state(did)
        except Exception:
            device: HomePilotDevice = self.devices[did]
            device.available = False

        device: HomePilotDevice = self.devices[did]
        device.update_state(state)
        return device

    async def update_states(self):
        try:
            states = await self.api.async_get_devices_state()
            states["-1"] = await self.get_hub_state()
        except AuthError:
            raise
        except Exception:
            for did in self.devices:
                device: HomePilotDevice = self.devices[did]
                device.available = False
            raise

        for did in self.devices:
            device: HomePilotDevice = self.devices[did]
            if device.did in states:
                await device.update_state(states[did], self.api)
            else:
                device.available = False

        return self.devices

    async def async_update_scenes(self):        
        try:
            scenes_list = await self.api.async_get_scenes()            
        except AuthError:
            raise
        except Exception:
            for sid in self.scenes:
                scene: HomePilotScene = self.scenes[sid]
                scene.available = False
            raise

        # Convert list to dict for easier lookup
        scenes_dict = {scene["id"]: scene for scene in scenes_list}

        for sid in self.scenes:
            scene: HomePilotScene = self.scenes[sid]
            if sid in scenes_dict:
                await scene.async_update_scene(scenes_dict[sid])
                scene.available = True
            else:
                scene.available = False
        return self.scenes

    async def get_device_ids_types(self):
        devices = await self.api.get_devices()
        devices.append(HomePilotHub.get_capabilities())
        return [HomePilotDevice.get_did_type_from_json(device) for device in devices]

    @property
    def api(self) -> HomePilotApi:
        return self._api

    @property
    def devices(self) -> Dict[str, HomePilotDevice]:
        return self._devices

    @devices.setter
    def devices(self, devices: Dict[str, HomePilotDevice]):
        self._devices = devices

    @property
    def scenes(self) -> Dict[str, HomePilotScene]:
        return self._scenes

    @scenes.setter
    def scenes(self, scenes: Dict[str, HomePilotScene]):
        self._scenes = scenes

    @property
    def include_non_manual_executable(self) -> bool:
        return self._include_non_manual_executable
