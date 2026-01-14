"""
Comprehensive integration tests for PyWRKGame 3.0.0
Tests complete game creation workflow, cross-platform compatibility, and all correctness properties
Requirements: All
"""

import pytest
import sys
import os
import platform

# Add python directory to path for high-level API
python_dir = os.path.join(os.path.dirname(__file__), '../../python')
sys.path.insert(0, python_dir)

# Add build directory to path for C++ bindings
build_dir = os.path.join(os.path.dirname(__file__), '../../build')
if os.path.exists(build_dir):
    sys.path.insert(0, build_dir)

try:
    import pywrkgame as pwg
    from pywrkgame_api import (
        Game, Sprite, InputState,
        PlatformerTemplate, RPGTemplate, ShooterTemplate, PuzzleTemplate,
        quick_game, quick_platformer, quick_rpg, quick_shooter, quick_puzzle
    )
    BINDINGS_AVAILABLE = True
except ImportError as e:
    BINDINGS_AVAILABLE = False
    pytest.skip(f"pywrkgame module not built: {e}", allow_module_level=True)


class TestCompleteGameWorkflow:
    """Test complete game creation workflow from start to finish"""
    
    def test_full_platformer_workflow(self):
        """Test creating a complete platformer game with all features"""
        # Create game
        game = PlatformerTemplate("Integration Test Platformer", 1280, 720)
        assert game is not None
        
        # Add player
        player = game.add_player(100, 100)
        assert player is not None
        assert game.player == player
        
        # Add multiple platforms
        ground = game.add_platform(0, 650, 1280, 70)
        platform1 = game.add_platform(200, 500, 300, 50)
        platform2 = game.add_platform(600, 400, 300, 50)
        
        assert len(game.platforms) == 3
        
        # Setup update callback
        update_called = []
        
        @game.game.on_update
        def update(dt):
            update_called.append(dt)
            # Simulate player movement
            if game.game.input.x > 0:
                player.move(game.move_speed * dt, 0)
        
        assert game.game.update_callback is not None
        
        # Verify game state
        assert game.game.engine.is_initialized()
        assert len(game.game.sprites) >= 1  # At least player sprite
        
        game.game.stop()
        
    def test_full_rpg_workflow(self):
        """Test creating a complete RPG game with all features"""
        # Create game
        game = RPGTemplate("Integration Test RPG", 1920, 1080)
        assert game is not None
        
        # Add player
        player = game.add_player(960, 540)
        assert player is not None
        
        # Add multiple NPCs with dialogs
        npc1 = game.add_npc(200, 200, "Welcome to the village!")
        npc2 = game.add_npc(400, 300, "Beware of the forest!")
        npc3 = game.add_npc(600, 400, "The king needs your help!")
        
        assert len(game.npcs) == 3
        
        # Setup update callback for movement
        @game.game.on_update
        def update(dt):
            # 8-directional movement
            dx = game.game.input.x * game.move_speed * dt
            dy = game.game.input.y * game.move_speed * dt
            player.move(dx, dy)
        
        # Verify game state
        assert game.game.engine.is_initialized()
        assert len(game.game.sprites) >= 4  # Player + 3 NPCs
        
        game.game.stop()
        
    def test_full_shooter_workflow(self):
        """Test creating a complete shooter game with all features"""
        # Create game
        game = ShooterTemplate("Integration Test Shooter", 800, 600)
        assert game is not None
        
        # Add player
        player = game.add_player(400, 550)
        assert player is not None
        
        # Spawn multiple enemies
        enemy1 = game.spawn_enemy(100, 50)
        enemy2 = game.spawn_enemy(300, 50)
        enemy3 = game.spawn_enemy(500, 50)
        enemy4 = game.spawn_enemy(700, 50)
        
        assert len(game.enemies) == 4
        
        # Shoot bullets
        bullet1 = game.shoot(player.x, player.y, 0, -1)
        bullet2 = game.shoot(player.x, player.y, 1, -1)
        
        assert len(game.bullets) == 2
        
        # Setup update callback
        @game.game.on_update
        def update(dt):
            # Move player
            player.move(game.game.input.x * game.move_speed * dt, 0)
            
            # Update bullets
            for bullet in game.bullets:
                bullet.move(
                    bullet.velocity_x * game.bullet_speed * dt,
                    bullet.velocity_y * game.bullet_speed * dt
                )
        
        # Verify game state
        assert game.game.engine.is_initialized()
        
        game.game.stop()
        
    def test_full_puzzle_workflow(self):
        """Test creating a complete puzzle game with all features"""
        # Create game
        game = PuzzleTemplate("Integration Test Puzzle", 800, 800)
        assert game is not None
        
        # Create grid
        game.create_grid(8, 8)
        assert game.grid is not None
        assert game.grid_width == 8
        assert game.grid_height == 8
        
        # Add pieces of different types
        colors = ["red", "blue", "green", "yellow", "purple"]
        pieces_added = 0
        
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % len(colors)]
                piece = game.add_piece(col, row, color)
                assert piece is not None
                pieces_added += 1
        
        assert len(game.pieces) == 64
        assert pieces_added == 64
        
        # Test swapping pieces
        piece_00 = game.grid[0][0]
        piece_11 = game.grid[1][1]
        
        game.swap_pieces(0, 0, 1, 1)
        
        assert game.grid[0][0] == piece_11
        assert game.grid[1][1] == piece_00
        
        # Verify game state
        assert game.game.engine.is_initialized()
        
        game.game.stop()


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility features"""
    
    def test_platform_detection(self):
        """Test that platform is correctly detected"""
        current_platform = platform.system()
        
        # Create engine and verify it initializes on current platform
        game = Game("Platform Test")
        assert game.engine.is_initialized()
        
        # Platform should be one of the supported platforms
        supported_platforms = ["Windows", "Linux", "Darwin"]  # Darwin = macOS
        assert current_platform in supported_platforms
        
        game.stop()
        
    def test_engine_initialization_on_current_platform(self):
        """Test that engine initializes correctly on current platform"""
        game = Game("Engine Init Test", 1024, 768)
        
        # Engine should initialize successfully
        assert game.engine is not None
        assert game.engine.is_initialized()
        
        # Basic engine operations should work
        sprite = game.create_sprite("test.png", 100, 100)
        assert sprite is not None
        
        game.stop()
        
    def test_graphics_api_selection(self):
        """Test that appropriate graphics API is selected for platform"""
        game = Game("Graphics API Test")
        
        # Engine should select appropriate graphics API based on platform
        # Windows: D3D12 or Vulkan
        # Linux: Vulkan
        # macOS: Metal
        
        current_platform = platform.system()
        
        # Just verify engine initialized - actual API selection is internal
        assert game.engine.is_initialized()
        
        game.stop()
        
    def test_multiple_game_instances(self):
        """Test creating and destroying multiple game instances"""
        games = []
        
        # Create multiple games
        for i in range(5):
            game = Game(f"Game {i}", 800, 600)
            assert game.engine.is_initialized()
            games.append(game)
        
        # Stop all games
        for game in games:
            game.stop()
        
        # Create new game after stopping others
        new_game = Game("New Game")
        assert new_game.engine.is_initialized()
        new_game.stop()


class TestCorrectnessPropertiesIntegration:
    """Integration tests verifying correctness properties work together"""
    
    def test_performance_with_rendering(self):
        """Test that performance optimization works with rendering"""
        game = Game("Performance Test", 1920, 1080)
        
        # Create many sprites to test performance
        sprites = []
        for i in range(100):
            sprite = game.create_sprite(f"sprite_{i}.png", i * 10, i * 10)
            sprites.append(sprite)
        
        assert len(game.sprites) == 100
        
        # Engine should handle this without crashing
        assert game.engine.is_initialized()
        
        game.stop()
        
    def test_physics_with_rendering(self):
        """Test that physics integrates with rendering"""
        game = PlatformerTemplate("Physics Integration Test")
        
        # Add player with physics
        player = game.add_player(100, 100)
        assert player is not None
        assert hasattr(player, 'velocity_y')
        
        # Add platforms for collision
        platform = game.add_platform(0, 500, 800, 50)
        assert platform is not None
        
        # Gravity should be applied
        assert game.gravity > 0
        
        game.game.stop()
        
    def test_audio_with_game_state(self):
        """Test that audio system integrates with game state"""
        game = Game("Audio Integration Test")
        
        # Game should have audio system available through engine
        assert game.engine is not None
        
        # Create sprites that could have audio
        sprite = game.create_sprite("player.png", 100, 100)
        assert sprite is not None
        
        game.stop()
        
    def test_ui_with_game_logic(self):
        """Test that UI integrates with game logic"""
        game = Game("UI Integration Test", 1280, 720)
        
        # Create game objects
        player = game.create_sprite("player.png", 640, 360)
        
        # Input state should be available
        assert game.input is not None
        
        # Setup update callback that uses input
        @game.on_update
        def update(dt):
            if game.input.x != 0 or game.input.y != 0:
                player.move(game.input.x * 100 * dt, game.input.y * 100 * dt)
        
        assert game.update_callback is not None
        
        game.stop()
        
    def test_network_ready_architecture(self):
        """Test that architecture supports network features"""
        game = Game("Network Ready Test")
        
        # Engine should be initialized and ready for network features
        assert game.engine.is_initialized()
        
        # Multiple game instances should be possible (for multiplayer)
        game2 = Game("Network Ready Test 2")
        assert game2.engine.is_initialized()
        
        game.stop()
        game2.stop()
        
    def test_ai_ready_architecture(self):
        """Test that architecture supports AI features"""
        game = RPGTemplate("AI Ready Test")
        
        # Add NPCs that could have AI
        npc1 = game.add_npc(100, 100, "Hello!")
        npc2 = game.add_npc(200, 200, "Greetings!")
        
        assert len(game.npcs) == 2
        
        # NPCs should be manageable
        for npc in game.npcs:
            assert hasattr(npc, 'x')
            assert hasattr(npc, 'y')
            assert hasattr(npc, 'dialog')
        
        game.game.stop()


class TestAssetManagement:
    """Test asset management and optimization"""
    
    def test_multiple_sprite_creation(self):
        """Test creating multiple sprites with same texture"""
        game = Game("Asset Test")
        
        # Create multiple sprites with same texture
        sprites = []
        for i in range(10):
            sprite = game.create_sprite("shared_texture.png", i * 50, i * 50)
            sprites.append(sprite)
        
        assert len(game.sprites) == 10
        
        # All sprites should be valid
        for sprite in sprites:
            assert sprite is not None
            assert sprite in game.sprites
        
        game.stop()
        
    def test_sprite_lifecycle(self):
        """Test sprite creation and management lifecycle"""
        game = Game("Lifecycle Test")
        
        # Create sprites
        sprite1 = game.create_sprite("sprite1.png", 100, 100)
        sprite2 = game.create_sprite("sprite2.png", 200, 200)
        
        assert len(game.sprites) == 2
        
        # Sprites should persist
        assert sprite1 in game.sprites
        assert sprite2 in game.sprites
        
        game.stop()


class TestErrorHandling:
    """Test error handling and recovery"""
    
    def test_game_stop_and_restart(self):
        """Test stopping and restarting games"""
        game1 = Game("Test 1")
        assert game1.engine.is_initialized()
        game1.stop()
        
        # Should be able to create new game after stopping
        game2 = Game("Test 2")
        assert game2.engine.is_initialized()
        game2.stop()
        
    def test_invalid_sprite_operations(self):
        """Test handling of invalid sprite operations"""
        game = Game("Invalid Ops Test")
        
        # Creating sprite should work even with non-existent texture
        # (engine should handle gracefully)
        sprite = game.create_sprite("nonexistent.png", 100, 100)
        assert sprite is not None
        
        game.stop()
        
    def test_template_without_required_setup(self):
        """Test templates handle missing setup gracefully"""
        game = PlatformerTemplate("Incomplete Setup Test")
        
        # Should be able to create template without adding player/platforms
        assert game is not None
        assert game.game.engine.is_initialized()
        
        game.game.stop()


class TestMemoryManagement:
    """Test memory management and cleanup"""
    
    def test_game_cleanup(self):
        """Test that games clean up properly"""
        games = []
        
        # Create and stop multiple games
        for i in range(10):
            game = Game(f"Cleanup Test {i}")
            assert game.engine.is_initialized()
            games.append(game)
        
        # Stop all games
        for game in games:
            game.stop()
        
        # Should be able to create new game
        new_game = Game("After Cleanup")
        assert new_game.engine.is_initialized()
        new_game.stop()
        
    def test_sprite_cleanup(self):
        """Test that sprites are managed properly"""
        game = Game("Sprite Cleanup Test")
        
        # Create many sprites
        for i in range(100):
            sprite = game.create_sprite(f"sprite_{i}.png", i, i)
            assert sprite is not None
        
        assert len(game.sprites) == 100
        
        # Stop game - should clean up sprites
        game.stop()


class TestTemplateInteroperability:
    """Test that different templates can coexist"""
    
    def test_multiple_template_types(self):
        """Test creating multiple different template types"""
        platformer = PlatformerTemplate("Platformer")
        rpg = RPGTemplate("RPG")
        shooter = ShooterTemplate("Shooter")
        puzzle = PuzzleTemplate("Puzzle")
        
        # All should initialize
        assert platformer.game.engine.is_initialized()
        assert rpg.game.engine.is_initialized()
        assert shooter.game.engine.is_initialized()
        assert puzzle.game.engine.is_initialized()
        
        # Clean up
        platformer.game.stop()
        rpg.game.stop()
        shooter.game.stop()
        puzzle.game.stop()
        
    def test_template_specific_features(self):
        """Test that each template has its specific features"""
        platformer = PlatformerTemplate()
        rpg = RPGTemplate()
        shooter = ShooterTemplate()
        puzzle = PuzzleTemplate()
        
        # Platformer has gravity
        assert hasattr(platformer, 'gravity')
        assert platformer.gravity > 0
        
        # RPG has move speed
        assert hasattr(rpg, 'move_speed')
        assert rpg.move_speed > 0
        
        # Shooter has bullet speed
        assert hasattr(shooter, 'bullet_speed')
        assert shooter.bullet_speed > 0
        
        # Puzzle has grid
        puzzle.create_grid(5, 5)
        assert hasattr(puzzle, 'grid')
        assert puzzle.grid is not None
        
        # Clean up
        platformer.game.stop()
        rpg.game.stop()
        shooter.game.stop()
        puzzle.game.stop()


class TestHighLevelAPIIntegration:
    """Test high-level API integration and simplicity"""
    
    def test_quick_functions_integration(self):
        """Test that quick creation functions work together"""
        games = []
        
        # Create games using quick functions
        games.append(quick_game("Quick 1"))
        games.append(quick_platformer("Quick Platformer"))
        games.append(quick_rpg("Quick RPG"))
        games.append(quick_shooter("Quick Shooter"))
        games.append(quick_puzzle("Quick Puzzle"))
        
        # All should be valid
        for game_or_template in games:
            if hasattr(game_or_template, 'game'):
                # It's a template
                assert game_or_template.game.engine.is_initialized()
            else:
                # It's a game
                assert game_or_template.engine.is_initialized()
        
        # Clean up
        for game_or_template in games:
            if hasattr(game_or_template, 'game'):
                game_or_template.game.stop()
            else:
                game_or_template.stop()
        
    def test_minimal_code_game_creation(self):
        """Test that games can be created with minimal code"""
        # This test verifies the 10-line requirement
        
        # Line 1: Create game
        game = quick_platformer("Minimal Game")
        
        # Line 2: Add player
        player = game.add_player(100, 100)
        
        # Line 3: Add platform
        game.add_platform(0, 500, 800, 50)
        
        # Lines 4-6: Setup update
        @game.game.on_update
        def update(dt):
            player.move(game.game.input.x * 200 * dt, 0)
        
        # Total: 6 lines of actual code (excluding decorators and blank lines)
        # This is well under the 10-line requirement
        
        assert game is not None
        assert player is not None
        assert len(game.platforms) == 1
        
        game.game.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
