"""
Integration tests for high-level Python API
Tests game template functionality and API simplicity
Requirements: 4.1, 4.4
"""

import pytest
import sys
import os

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
        VisualScript, VisualScriptNode,
        quick_game, quick_platformer, quick_rpg, quick_shooter, quick_puzzle
    )
    BINDINGS_AVAILABLE = True
except ImportError as e:
    BINDINGS_AVAILABLE = False
    pytest.skip(f"pywrkgame module not built: {e}", allow_module_level=True)


class TestGameClass:
    """Test high-level Game class"""
    
    def test_game_creation(self):
        """Test creating a game with default parameters"""
        game = Game()
        assert game is not None
        assert game.title == "PyWRKGame"
        assert game.width == 1280
        assert game.height == 720
        assert game.fps == 60
        game.stop()
        
    def test_game_creation_with_parameters(self):
        """Test creating a game with custom parameters"""
        game = Game("Test Game", 1920, 1080, 120)
        assert game.title == "Test Game"
        assert game.width == 1920
        assert game.height == 1080
        assert game.fps == 120
        game.stop()
        
    def test_game_has_engine(self):
        """Test that game has an initialized engine"""
        game = Game("Test", 800, 600)
        assert game.engine is not None
        assert game.engine.is_initialized()
        game.stop()
        
    def test_game_has_input_state(self):
        """Test that game has input state"""
        game = Game()
        assert game.input is not None
        assert isinstance(game.input, InputState)
        game.stop()


class TestSpriteCreation:
    """Test sprite creation and management"""
    
    def test_create_sprite(self):
        """Test creating a sprite"""
        game = Game()
        sprite = game.create_sprite("test.png", 100, 200)
        
        assert sprite is not None
        assert sprite.x == 100
        assert sprite.y == 200
        assert sprite.scale == 1.0
        assert sprite in game.sprites
        
        game.stop()
        
    def test_create_sprite_with_scale(self):
        """Test creating a sprite with custom scale"""
        game = Game()
        sprite = game.create_sprite("test.png", 50, 75, scale=2.0)
        
        assert sprite.scale == 2.0
        game.stop()
        
    def test_sprite_movement(self):
        """Test sprite movement"""
        game = Game()
        sprite = game.create_sprite("test.png", 100, 100)
        
        sprite.move(50, 25)
        assert sprite.x == 150
        assert sprite.y == 125
        
        sprite.move(-30, -20)
        assert sprite.x == 120
        assert sprite.y == 105
        
        game.stop()
        
    def test_sprite_set_position(self):
        """Test setting sprite position"""
        game = Game()
        sprite = game.create_sprite("test.png", 100, 100)
        
        sprite.set_position(300, 400)
        assert sprite.x == 300
        assert sprite.y == 400
        
        game.stop()
        
    def test_sprite_get_position(self):
        """Test getting sprite position"""
        game = Game()
        sprite = game.create_sprite("test.png", 150, 250)
        
        pos = sprite.get_position()
        assert pos == (150, 250)
        
        game.stop()
        
    def test_multiple_sprites(self):
        """Test creating multiple sprites"""
        game = Game()
        
        sprite1 = game.create_sprite("sprite1.png", 100, 100)
        sprite2 = game.create_sprite("sprite2.png", 200, 200)
        sprite3 = game.create_sprite("sprite3.png", 300, 300)
        
        assert len(game.sprites) == 3
        assert sprite1 in game.sprites
        assert sprite2 in game.sprites
        assert sprite3 in game.sprites
        
        game.stop()


class TestUpdateCallback:
    """Test update callback registration"""
    
    def test_register_update_callback(self):
        """Test registering an update callback"""
        game = Game()
        
        callback_called = []
        
        @game.on_update
        def update(dt):
            callback_called.append(dt)
            
        assert game.update_callback is not None
        assert game.update_callback == update
        
        game.stop()
        
    def test_update_callback_as_decorator(self):
        """Test using on_update as a decorator"""
        game = Game()
        
        @game.on_update
        def my_update(dt):
            pass
            
        assert game.update_callback == my_update
        game.stop()


class TestPlatformerTemplate:
    """Test platformer game template"""
    
    def test_platformer_creation(self):
        """Test creating a platformer game"""
        game = PlatformerTemplate("Test Platformer")
        assert game is not None
        assert game.game.title == "Test Platformer"
        assert game.gravity == 980
        game.game.stop()
        
    def test_platformer_add_player(self):
        """Test adding player to platformer"""
        game = PlatformerTemplate()
        player = game.add_player(100, 100)
        
        assert player is not None
        assert game.player == player
        assert player.x == 100
        assert player.y == 100
        assert hasattr(player, 'velocity_y')
        
        game.game.stop()
        
    def test_platformer_add_platform(self):
        """Test adding platforms"""
        game = PlatformerTemplate()
        platform = game.add_platform(0, 500, 800, 50)
        
        assert platform is not None
        assert platform in game.platforms
        assert platform['x'] == 0
        assert platform['y'] == 500
        assert platform['width'] == 800
        assert platform['height'] == 50
        
        game.game.stop()
        
    def test_platformer_multiple_platforms(self):
        """Test adding multiple platforms"""
        game = PlatformerTemplate()
        
        platform1 = game.add_platform(0, 500, 400, 50)
        platform2 = game.add_platform(500, 400, 300, 50)
        platform3 = game.add_platform(200, 300, 200, 50)
        
        assert len(game.platforms) == 3
        game.game.stop()


class TestRPGTemplate:
    """Test RPG game template"""
    
    def test_rpg_creation(self):
        """Test creating an RPG game"""
        game = RPGTemplate("Test RPG")
        assert game is not None
        assert game.game.title == "Test RPG"
        assert game.move_speed == 200
        game.game.stop()
        
    def test_rpg_add_player(self):
        """Test adding player to RPG"""
        game = RPGTemplate()
        player = game.add_player(150, 200)
        
        assert player is not None
        assert game.player == player
        assert player.x == 150
        assert player.y == 200
        
        game.game.stop()
        
    def test_rpg_add_npc(self):
        """Test adding NPC to RPG"""
        game = RPGTemplate()
        npc = game.add_npc(300, 400, "Hello adventurer!")
        
        assert npc is not None
        assert npc in game.npcs
        assert npc.dialog == "Hello adventurer!"
        
        game.game.stop()
        
    def test_rpg_multiple_npcs(self):
        """Test adding multiple NPCs"""
        game = RPGTemplate()
        
        npc1 = game.add_npc(100, 100, "Welcome!")
        npc2 = game.add_npc(200, 200, "Good day!")
        npc3 = game.add_npc(300, 300, "Farewell!")
        
        assert len(game.npcs) == 3
        game.game.stop()


class TestShooterTemplate:
    """Test shooter game template"""
    
    def test_shooter_creation(self):
        """Test creating a shooter game"""
        game = ShooterTemplate("Test Shooter")
        assert game is not None
        assert game.game.title == "Test Shooter"
        assert game.move_speed == 300
        assert game.bullet_speed == 500
        game.game.stop()
        
    def test_shooter_add_player(self):
        """Test adding player to shooter"""
        game = ShooterTemplate()
        player = game.add_player(640, 600)
        
        assert player is not None
        assert game.player == player
        
        game.game.stop()
        
    def test_shooter_spawn_enemy(self):
        """Test spawning enemies"""
        game = ShooterTemplate()
        enemy = game.spawn_enemy(300, 100)
        
        assert enemy is not None
        assert enemy in game.enemies
        
        game.game.stop()
        
    def test_shooter_shoot(self):
        """Test shooting bullets"""
        game = ShooterTemplate()
        bullet = game.shoot(100, 100, 0, -1)
        
        assert bullet is not None
        assert bullet in game.bullets
        assert hasattr(bullet, 'velocity_x')
        assert hasattr(bullet, 'velocity_y')
        
        game.game.stop()


class TestPuzzleTemplate:
    """Test puzzle game template"""
    
    def test_puzzle_creation(self):
        """Test creating a puzzle game"""
        game = PuzzleTemplate("Test Puzzle")
        assert game is not None
        assert game.game.title == "Test Puzzle"
        game.game.stop()
        
    def test_puzzle_create_grid(self):
        """Test creating puzzle grid"""
        game = PuzzleTemplate()
        game.create_grid(8, 8)
        
        assert game.grid is not None
        assert game.grid_width == 8
        assert game.grid_height == 8
        assert len(game.grid) == 8
        assert len(game.grid[0]) == 8
        
        game.game.stop()
        
    def test_puzzle_add_piece(self):
        """Test adding puzzle pieces"""
        game = PuzzleTemplate()
        game.create_grid(5, 5)
        
        piece = game.add_piece(2, 3, "red")
        
        assert piece is not None
        assert piece in game.pieces
        assert piece['col'] == 2
        assert piece['row'] == 3
        assert piece['type'] == "red"
        assert game.grid[3][2] == piece
        
        game.game.stop()
        
    def test_puzzle_swap_pieces(self):
        """Test swapping puzzle pieces"""
        game = PuzzleTemplate()
        game.create_grid(4, 4)
        
        piece1 = game.add_piece(0, 0, "blue")
        piece2 = game.add_piece(1, 1, "green")
        
        game.swap_pieces(0, 0, 1, 1)
        
        assert game.grid[0][0] == piece2
        assert game.grid[1][1] == piece1
        
        game.game.stop()


class TestQuickCreationFunctions:
    """Test quick creation convenience functions"""
    
    def test_quick_game(self):
        """Test quick_game function"""
        game = quick_game("Quick Test")
        assert game is not None
        assert game.title == "Quick Test"
        game.stop()
        
    def test_quick_platformer(self):
        """Test quick_platformer function"""
        game = quick_platformer("Quick Platformer")
        assert game is not None
        assert isinstance(game, PlatformerTemplate)
        game.game.stop()
        
    def test_quick_rpg(self):
        """Test quick_rpg function"""
        game = quick_rpg("Quick RPG")
        assert game is not None
        assert isinstance(game, RPGTemplate)
        game.game.stop()
        
    def test_quick_shooter(self):
        """Test quick_shooter function"""
        game = quick_shooter("Quick Shooter")
        assert game is not None
        assert isinstance(game, ShooterTemplate)
        game.game.stop()
        
    def test_quick_puzzle(self):
        """Test quick_puzzle function"""
        game = quick_puzzle("Quick Puzzle")
        assert game is not None
        assert isinstance(game, PuzzleTemplate)
        game.game.stop()


class TestVisualScripting:
    """Test visual scripting system"""
    
    def test_visual_script_node_creation(self):
        """Test creating visual script nodes"""
        node = VisualScriptNode("start")
        assert node is not None
        assert node.node_type == "start"
        
    def test_visual_script_creation(self):
        """Test creating visual scripts"""
        script = VisualScript()
        assert script is not None
        assert len(script.nodes) == 0
        
    def test_visual_script_add_node(self):
        """Test adding nodes to visual script"""
        script = VisualScript()
        node1 = VisualScriptNode("start")
        node2 = VisualScriptNode("action")
        
        script.add_node(node1)
        script.add_node(node2)
        
        assert len(script.nodes) == 2
        assert script.start_node == node1
        
    def test_visual_script_node_connection(self):
        """Test connecting visual script nodes"""
        node1 = VisualScriptNode("start")
        node2 = VisualScriptNode("action")
        
        node1.connect_to(node2, "output", "input")
        
        assert len(node1.connections) == 1
        assert node1.connections[0]['target'] == node2


class TestAPISimplicity:
    """Test that API meets simplicity requirements (max 10 lines)"""
    
    def test_simple_game_creation_line_count(self):
        """Test that a simple game can be created in 10 lines or less"""
        # This is a conceptual test - the actual code would be:
        # 1. game = Game("Simple Game", 800, 600)
        # 2. player = game.create_sprite("player.png", 400, 300)
        # 3. 
        # 4. @game.on_update
        # 5. def update(dt):
        # 6.     player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)
        # 7. 
        # 8. game.run()
        
        # Total: 8 lines (including blank lines for readability)
        # This meets the requirement of max 10 lines
        
        game = Game("Simple Game", 800, 600)
        player = game.create_sprite("player.png", 400, 300)
        
        @game.on_update
        def update(dt):
            player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)
        
        # Would call game.run() but we don't want to block tests
        assert game is not None
        assert player is not None
        game.stop()
        
    def test_template_game_creation_line_count(self):
        """Test that template games can be created in minimal lines"""
        # Platformer in 4 lines:
        # 1. game = quick_platformer("My Platformer")
        # 2. game.add_player(100, 100)
        # 3. game.add_platform(0, 500, 800, 50)
        # 4. game.run()
        
        game = quick_platformer("My Platformer")
        game.add_player(100, 100)
        game.add_platform(0, 500, 800, 50)
        
        assert game is not None
        game.game.stop()


class TestInputState:
    """Test input state tracking"""
    
    def test_input_state_creation(self):
        """Test creating input state"""
        input_state = InputState()
        assert input_state is not None
        
    def test_input_state_defaults(self):
        """Test input state default values"""
        input_state = InputState()
        assert input_state.x == 0
        assert input_state.y == 0
        assert isinstance(input_state.buttons, dict)
        
    def test_input_state_modification(self):
        """Test modifying input state"""
        input_state = InputState()
        input_state.x = 1.0
        input_state.y = -0.5
        input_state.buttons['fire'] = True
        
        assert input_state.x == 1.0
        assert input_state.y == -0.5
        assert input_state.buttons['fire'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
