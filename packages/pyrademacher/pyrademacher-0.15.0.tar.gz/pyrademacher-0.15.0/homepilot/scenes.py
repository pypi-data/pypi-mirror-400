import asyncio
from typing import Optional, Dict, Any
from .api import HomePilotApi


class SceneNotAvailableError(Exception):
    """Raised when trying to execute operations on an unavailable scene"""
    pass


class SceneNotManuallyExecutableError(Exception):
    """Raised when trying to manually execute a non-manually executable scene"""
    pass


class HomePilotScene:
    """HomePilot Scene"""

    _api: HomePilotApi
    _sid: int
    _name: str
    _description: str
    _is_enabled: bool
    _is_manual_executable: bool
    _available: bool
    def __init__(
        self,
        api: HomePilotApi,
        sid: int,
        name: str,
        description: str,
        is_enabled: bool = False,
        is_manual_executable: bool = False,
    ) -> None:
        self._api = api
        self._sid = sid
        self._name = name
        self._description = description
        self._is_enabled = is_enabled
        self._is_manual_executable = is_manual_executable
        self._available = True

    @staticmethod
    def build_scene(api: HomePilotApi, scene_data: Dict[str, Any]):
        return asyncio.run(HomePilotScene.async_build_scene(api, scene_data))

    @staticmethod
    async def async_build_scene(api: HomePilotApi, scene_data: Dict[str, Any]):
        """Build a new HomePilotScene from the response of API"""
        return HomePilotScene(
            api=api,
            sid=scene_data["id"],
            name=scene_data["name"],
            description=scene_data.get("description", ""),
            is_enabled=bool(scene_data.get("is_enabled", 0)),
            is_manual_executable=bool(scene_data.get("is_manual_executable", 0)),
        )

    async def async_update_scene(self, scene) -> None:                
        self.name = scene["name"]
        self.description = scene["description"]
        self.is_enabled = bool(scene["is_enabled"])
        self.is_manual_executable = bool(scene["is_manual_executable"])        

    async def async_execute_scene(self) -> None:
        """Execute the scene manually. Requires scene to be available and manually executable."""
        if not self.available:
            raise SceneNotAvailableError(f"Scene '{self.name}' (ID: {self.sid}) is not available")
        if not self.is_manual_executable:
            raise SceneNotManuallyExecutableError(f"Scene '{self.name}' (ID: {self.sid}) is not manually executable")
        await self._api.async_execute_scene(self._sid)

    async def async_activate_scene(self) -> None:
        """Activate the scene. Requires scene to be available."""
        if not self.available:
            raise SceneNotAvailableError(f"Scene '{self.name}' (ID: {self.sid}) is not available")
        await self._api.async_activate_scene(self._sid)

    async def async_deactivate_scene(self) -> None:
        """Deactivate the scene. Requires scene to be available."""
        if not self.available:
            raise SceneNotAvailableError(f"Scene '{self.name}' (ID: {self.sid}) is not available")
        await self._api.async_deactivate_scene(self._sid)

    @property
    def api(self) -> HomePilotApi:
        return self._api

    @property
    def sid(self) -> int:
        return self._sid

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def available(self) -> bool:
        return self._available

    @available.setter
    def available(self, available):
        self._available = available

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, is_enabled: bool):
        self._is_enabled = is_enabled

    @property
    def is_manual_executable(self) -> bool:
        return self._is_manual_executable

    @is_manual_executable.setter
    def is_manual_executable(self, is_manual_executable: bool):
        self._is_manual_executable = is_manual_executable
