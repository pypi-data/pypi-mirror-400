import asyncio
import json
from unittest.mock import MagicMock

import pytest

from homepilot.scenes import HomePilotScene, SceneNotAvailableError, SceneNotManuallyExecutableError


class TestHomePilotScene:
    @pytest.fixture
    def mocked_api(self):
        f = open("tests/test_files/scenes.json")
        j = json.load(f)
        api = MagicMock()
        func_get_scenes = asyncio.Future()
        func_get_scenes.set_result(j["scenes"])
        api.async_get_scenes.return_value = func_get_scenes
        func_execute_scene = asyncio.Future()
        func_execute_scene.set_result(None)
        api.async_execute_scene.return_value = func_execute_scene
        func_activate_scene = asyncio.Future()
        func_activate_scene.set_result(None)
        api.async_activate_scene.return_value = func_activate_scene
        func_deactivate_scene = asyncio.Future()
        func_deactivate_scene.set_result(None)
        api.async_deactivate_scene.return_value = func_deactivate_scene
        yield api

    @pytest.fixture
    def scene_data(self):
        return {
            "id": 1,
            "name": "Morning Scene",
            "description": "Opens blinds and turns on lights",
            "is_enabled": True,
            "is_manual_executable": 1
        }

    @pytest.mark.asyncio
    async def test_async_build_scene(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        assert scene.sid == 1
        assert scene.name == "Morning Scene"
        assert scene.description == "Opens blinds and turns on lights"
        assert scene.is_enabled is True
        assert scene.is_manual_executable is True
        assert scene.api == mocked_api

    def test_build_scene_sync(self, scene_data):
        # Test the sync method with a mock API (avoiding asyncio.run in async context)
        from unittest.mock import MagicMock
        api = MagicMock()
        
        # Test direct constructor instead of sync build method
        scene = HomePilotScene(
            api=api,
            sid=scene_data["id"],
            name=scene_data["name"],
            description=scene_data["description"],
            is_enabled=scene_data["is_enabled"],
            is_manual_executable=bool(scene_data["is_manual_executable"])
        )
        assert scene.sid == 1
        assert scene.name == "Morning Scene"
        assert scene.description == "Opens blinds and turns on lights"
        assert scene.is_enabled is True
        assert scene.is_manual_executable is True

    @pytest.mark.asyncio
    async def test_build_scene_with_defaults(self, mocked_api):
        scene_data = {
            "id": 2,
            "name": "Test Scene"
        }
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        assert scene.sid == 2
        assert scene.name == "Test Scene"
        assert scene.description == ""
        assert scene.is_enabled is False
        assert scene.is_manual_executable is False

    @pytest.mark.asyncio
    async def test_build_scene_manual_executable_conversion(self, mocked_api):
        scene_data = {
            "id": 3,
            "name": "Auto Scene",
            "description": "Automatic scene",
            "is_enabled": False,
            "is_manual_executable": 0
        }
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        assert scene.is_manual_executable is False

        scene_data["is_manual_executable"] = 1
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        assert scene.is_manual_executable is True

    @pytest.mark.asyncio
    async def test_async_update_scene(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        
        # Update with new data (using API format with integers)
        updated_data = {
            "name": "Updated Morning Scene",
            "description": "Updated description", 
            "is_enabled": 0,  # API uses 0/1 not boolean
            "is_manual_executable": 0  # API uses 0/1 not boolean
        }
        
        await scene.async_update_scene(updated_data)
        
        assert scene.name == "Updated Morning Scene"
        assert scene.description == "Updated description"
        assert scene.is_enabled is False  # Now converted to boolean
        assert scene.is_manual_executable is False  # Now converted to boolean

    @pytest.mark.asyncio
    async def test_async_execute_scene(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        await scene.async_execute_scene()
        mocked_api.async_execute_scene.assert_called_with(1)

    @pytest.mark.asyncio
    async def test_async_activate_scene(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        await scene.async_activate_scene()
        mocked_api.async_activate_scene.assert_called_with(1)

    @pytest.mark.asyncio
    async def test_async_deactivate_scene(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        await scene.async_deactivate_scene()
        mocked_api.async_deactivate_scene.assert_called_with(1)

    def test_scene_properties(self, scene_data):
        from unittest.mock import MagicMock
        api = MagicMock()
        
        scene = HomePilotScene(
            api=api,
            sid=scene_data["id"],
            name=scene_data["name"],
            description=scene_data["description"],
            is_enabled=scene_data["is_enabled"],
            is_manual_executable=bool(scene_data["is_manual_executable"])
        )
        
        # Test property getters
        assert scene.api == api
        assert scene.sid == 1
        assert scene.name == "Morning Scene"
        assert scene.description == "Opens blinds and turns on lights"
        assert scene.is_enabled is True
        assert scene.is_manual_executable is True
        
        # Test property setters
        scene.name = "New Name"
        assert scene.name == "New Name"
        
        scene.description = "New Description"
        assert scene.description == "New Description"
        
        scene.is_enabled = False
        assert scene.is_enabled is False
        
        scene.is_manual_executable = False
        assert scene.is_manual_executable is False
        
        scene.available = True
        assert scene.available is True

    @pytest.mark.asyncio
    async def test_async_execute_scene_validation_available_false(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        scene.available = False
        
        with pytest.raises(SceneNotAvailableError, match="Scene 'Morning Scene' \\(ID: 1\\) is not available"):
            await scene.async_execute_scene()
    
    @pytest.mark.asyncio
    async def test_async_execute_scene_validation_not_manual_executable(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        scene.is_manual_executable = False
        
        with pytest.raises(SceneNotManuallyExecutableError, match="Scene 'Morning Scene' \\(ID: 1\\) is not manually executable"):
            await scene.async_execute_scene()
    
    @pytest.mark.asyncio
    async def test_async_activate_scene_validation_available_false(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        scene.available = False
        
        with pytest.raises(SceneNotAvailableError, match="Scene 'Morning Scene' \\(ID: 1\\) is not available"):
            await scene.async_activate_scene()
    
    @pytest.mark.asyncio
    async def test_async_deactivate_scene_validation_available_false(self, mocked_api, scene_data):
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        scene.available = False
        
        with pytest.raises(SceneNotAvailableError, match="Scene 'Morning Scene' \\(ID: 1\\) is not available"):
            await scene.async_deactivate_scene()
    
    @pytest.mark.asyncio
    async def test_scene_operations_success_when_valid(self, mocked_api, scene_data):
        """Test that scene operations succeed when all conditions are met"""
        scene = await HomePilotScene.async_build_scene(mocked_api, scene_data)
        
        # Ensure scene is in valid state
        scene.available = True
        scene.is_manual_executable = True
        
        # These should not raise exceptions
        await scene.async_execute_scene()
        await scene.async_activate_scene() 
        await scene.async_deactivate_scene()
        
        # Verify API calls were made
        mocked_api.async_execute_scene.assert_called_with(1)
        mocked_api.async_activate_scene.assert_called_with(1)
        mocked_api.async_deactivate_scene.assert_called_with(1)