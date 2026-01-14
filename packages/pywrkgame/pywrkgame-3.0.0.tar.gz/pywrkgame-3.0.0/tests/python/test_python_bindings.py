"""
Unit tests for Python bindings
Tests Python API functionality and error handling
Requirements: 1.1, 4.1
"""

import pytest
import sys
import os

# Add build directory to path
build_dir = os.path.join(os.path.dirname(__file__), '../../build')
if os.path.exists(build_dir):
    sys.path.insert(0, build_dir)

try:
    import pywrkgame as pwg
except ImportError:
    pytest.skip("pywrkgame module not built", allow_module_level=True)


class TestEngineConfig:
    """Test EngineConfig class"""
    
    def test_engine_config_creation(self):
        """Test creating engine configuration"""
        config = pwg.EngineConfig()
        assert config is not None
        
    def test_engine_config_defaults(self):
        """Test default configuration values"""
        config = pwg.EngineConfig()
        assert config.app_name == "PyWRKGame Application"
        assert config.window_width == 1280
        assert config.window_height == 720
        assert config.fullscreen == False
        assert config.vsync == True
        assert config.target_fps == 60
        
    def test_engine_config_modification(self):
        """Test modifying configuration values"""
        config = pwg.EngineConfig()
        config.app_name = "Test Game"
        config.window_width = 1920
        config.window_height = 1080
        config.fullscreen = True
        config.vsync = False
        config.target_fps = 120
        
        assert config.app_name == "Test Game"
        assert config.window_width == 1920
        assert config.window_height == 1080
        assert config.fullscreen == True
        assert config.vsync == False
        assert config.target_fps == 120


class TestEngine:
    """Test Engine class"""
    
    def test_engine_creation(self):
        """Test creating engine instance"""
        engine = pwg.Engine()
        assert engine is not None
        assert not engine.is_initialized()
        
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        
        # Initialize should succeed
        result = engine.initialize(config)
        assert result == True
        assert engine.is_initialized()
        
        # Cleanup
        engine.shutdown()
        
    def test_engine_shutdown(self):
        """Test engine shutdown"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        engine.shutdown()
        # After shutdown, engine should still exist but may not be initialized
        assert engine is not None
        
    def test_engine_repr(self):
        """Test engine string representation"""
        engine = pwg.Engine()
        repr_str = repr(engine)
        assert "Engine" in repr_str
        assert "initialized=False" in repr_str
        
        config = pwg.EngineConfig()
        engine.initialize(config)
        repr_str = repr(engine)
        assert "initialized=True" in repr_str
        
        engine.shutdown()


class TestEngineErrorHandling:
    """Test error handling in Engine"""
    
    def test_update_without_initialization(self):
        """Test that update fails without initialization"""
        engine = pwg.Engine()
        
        with pytest.raises(pwg.PyWRKGameError):
            engine.update(0.016)
            
    def test_render_without_initialization(self):
        """Test that render fails without initialization"""
        engine = pwg.Engine()
        
        with pytest.raises(pwg.PyWRKGameError):
            engine.render()
            
    def test_create_game_object_without_initialization(self):
        """Test that creating game object fails without initialization"""
        engine = pwg.Engine()
        
        with pytest.raises(pwg.PyWRKGameError):
            engine.create_game_object()


class TestEntityManager:
    """Test EntityManager class"""
    
    def test_entity_manager_access(self):
        """Test accessing entity manager from engine"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        entity_manager = engine.get_entity_manager()
        assert entity_manager is not None
        
        engine.shutdown()
        
    def test_create_entity(self):
        """Test creating entities"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        entity_manager = engine.get_entity_manager()
        entity1 = entity_manager.create_entity()
        entity2 = entity_manager.create_entity()
        
        assert entity1 != pwg.INVALID_ENTITY
        assert entity2 != pwg.INVALID_ENTITY
        assert entity1 != entity2
        
        engine.shutdown()
        
    def test_entity_validity(self):
        """Test entity validity checking"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        entity_manager = engine.get_entity_manager()
        entity = entity_manager.create_entity()
        
        assert entity_manager.is_entity_valid(entity)
        assert not entity_manager.is_entity_valid(pwg.INVALID_ENTITY)
        
        engine.shutdown()
        
    def test_destroy_entity(self):
        """Test destroying entities"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        entity_manager = engine.get_entity_manager()
        entity = entity_manager.create_entity()
        
        assert entity_manager.is_entity_valid(entity)
        
        entity_manager.destroy_entity(entity)
        assert not entity_manager.is_entity_valid(entity)
        
        engine.shutdown()
        
    def test_entity_count(self):
        """Test entity count tracking"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        entity_manager = engine.get_entity_manager()
        initial_count = entity_manager.get_entity_count()
        
        entity1 = entity_manager.create_entity()
        assert entity_manager.get_entity_count() == initial_count + 1
        
        entity2 = entity_manager.create_entity()
        assert entity_manager.get_entity_count() == initial_count + 2
        
        entity_manager.destroy_entity(entity1)
        assert entity_manager.get_entity_count() == initial_count + 1
        
        engine.shutdown()


class TestGameObject:
    """Test GameObject wrapper class"""
    
    def test_create_game_object(self):
        """Test creating game objects"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        game_object = engine.create_game_object()
        assert game_object is not None
        assert game_object.is_valid()
        
        engine.shutdown()
        
    def test_game_object_entity_id(self):
        """Test getting entity ID from game object"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        game_object = engine.create_game_object()
        entity_id = game_object.get_entity_id()
        
        assert entity_id != pwg.INVALID_ENTITY
        
        engine.shutdown()
        
    def test_game_object_validity(self):
        """Test game object validity"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        game_object = engine.create_game_object()
        assert game_object.is_valid()
        
        game_object.destroy()
        assert not game_object.is_valid()
        
        engine.shutdown()
        
    def test_game_object_repr(self):
        """Test game object string representation"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        game_object = engine.create_game_object()
        repr_str = repr(game_object)
        
        assert "GameObject" in repr_str
        assert "entity_id=" in repr_str
        assert "valid=True" in repr_str
        
        engine.shutdown()
        
    def test_multiple_game_objects(self):
        """Test creating multiple game objects"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        obj1 = engine.create_game_object()
        obj2 = engine.create_game_object()
        obj3 = engine.create_game_object()
        
        assert obj1.get_entity_id() != obj2.get_entity_id()
        assert obj2.get_entity_id() != obj3.get_entity_id()
        assert obj1.get_entity_id() != obj3.get_entity_id()
        
        assert obj1.is_valid()
        assert obj2.is_valid()
        assert obj3.is_valid()
        
        engine.shutdown()


class TestExceptionMapping:
    """Test Python exception mapping"""
    
    def test_pywrkgame_error_exists(self):
        """Test that PyWRKGameError exception exists"""
        assert hasattr(pwg, 'PyWRKGameError')
        
    def test_initialization_error_exists(self):
        """Test that InitializationError exception exists"""
        assert hasattr(pwg, 'InitializationError')
        
    def test_resource_error_exists(self):
        """Test that ResourceError exception exists"""
        assert hasattr(pwg, 'ResourceError')
        
    def test_rendering_error_exists(self):
        """Test that RenderingError exception exists"""
        assert hasattr(pwg, 'RenderingError')
        
    def test_physics_error_exists(self):
        """Test that PhysicsError exception exists"""
        assert hasattr(pwg, 'PhysicsError')
        
    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from base exception"""
        # All custom exceptions should be catchable as Exception
        engine = pwg.Engine()
        
        try:
            engine.update(0.016)
        except Exception as e:
            # Should catch PyWRKGameError
            assert isinstance(e, Exception)


class TestComponentManager:
    """Test ComponentManager class"""
    
    def test_component_manager_access(self):
        """Test accessing component manager from engine"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        component_manager = engine.get_component_manager()
        assert component_manager is not None
        
        engine.shutdown()


class TestSystemManager:
    """Test SystemManager class"""
    
    def test_system_manager_access(self):
        """Test accessing system manager from engine"""
        engine = pwg.Engine()
        config = pwg.EngineConfig()
        engine.initialize(config)
        
        system_manager = engine.get_system_manager()
        assert system_manager is not None
        
        engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
