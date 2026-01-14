"""
PyWRKGame High-Level Python API
Simplified game creation API requiring maximum 10 lines of code
Requirements: 4.1, 4.2, 4.4
"""

try:
    import pywrkgame as pwg
except ImportError:
    # Fallback for when module isn't built
    class MockModule:
        pass
    pwg = MockModule()


class Game:
    """
    High-level game class for simplified game creation.
    
    Example usage (10 lines or less):
        game = Game("My Game", 1280, 720)
        player = game.create_sprite("player.png", x=100, y=100)
        enemy = game.create_sprite("enemy.png", x=500, y=300)
        
        @game.on_update
        def update(dt):
            player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)
        
        game.run()
    """
    
    def __init__(self, title="PyWRKGame", width=1280, height=720, fps=60):
        """
        Create a new game.
        
        Args:
            title: Window title
            width: Window width in pixels
            height: Window height in pixels
            fps: Target frames per second
        """
        self.title = title
        self.width = width
        self.height = height
        self.fps = fps
        
        # Initialize engine
        self.config = pwg.EngineConfig()
        self.config.app_name = title
        self.config.window_width = width
        self.config.window_height = height
        self.config.target_fps = fps
        
        self.engine = pwg.Engine()
        self.engine.initialize(self.config)
        
        # Game state
        self.sprites = []
        self.update_callback = None
        self.running = False
        
        # Input state
        self.input = InputState()
        
    def create_sprite(self, texture_path, x=0, y=0, scale=1.0):
        """
        Create a sprite game object.
        
        Args:
            texture_path: Path to texture file
            x: Initial x position
            y: Initial y position
            scale: Sprite scale
            
        Returns:
            Sprite object
        """
        sprite = Sprite(self.engine, texture_path, x, y, scale)
        self.sprites.append(sprite)
        return sprite
        
    def on_update(self, callback):
        """
        Decorator to register update callback.
        
        Args:
            callback: Function to call each frame with delta_time parameter
        """
        self.update_callback = callback
        return callback
        
    def run(self):
        """
        Start the game loop.
        """
        self.running = True
        import time
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Update
            if self.update_callback:
                self.update_callback(delta_time)
                
            self.engine.update(delta_time)
            
            # Render
            self.engine.render()
            
            # Simple frame limiting
            time.sleep(max(0, (1.0 / self.fps) - delta_time))
            
    def stop(self):
        """Stop the game loop."""
        self.running = False
        self.engine.shutdown()


class Sprite:
    """High-level sprite class."""
    
    def __init__(self, engine, texture_path, x, y, scale):
        self.engine = engine
        self.texture_path = texture_path
        self.x = x
        self.y = y
        self.scale = scale
        self.game_object = engine.create_game_object()
        
    def move(self, dx, dy):
        """Move sprite by delta."""
        self.x += dx
        self.y += dy
        
    def set_position(self, x, y):
        """Set sprite position."""
        self.x = x
        self.y = y
        
    def get_position(self):
        """Get sprite position."""
        return (self.x, self.y)


class InputState:
    """Simple input state tracking."""
    
    def __init__(self):
        self.x = 0  # Horizontal input (-1 to 1)
        self.y = 0  # Vertical input (-1 to 1)
        self.buttons = {}  # Button states


# Game Templates

class PlatformerTemplate:
    """
    Platformer game template.
    
    Example:
        game = PlatformerTemplate("My Platformer")
        game.add_platform(0, 500, 800, 50)
        game.add_player(100, 100)
        game.run()
    """
    
    def __init__(self, title="Platformer Game", width=1280, height=720):
        self.game = Game(title, width, height)
        self.player = None
        self.platforms = []
        self.gravity = 980  # pixels per second squared
        
    def add_player(self, x, y):
        """Add player character."""
        self.player = self.game.create_sprite("player.png", x, y)
        self.player.velocity_y = 0
        return self.player
        
    def add_platform(self, x, y, width, height):
        """Add a platform."""
        platform = {
            'x': x, 'y': y,
            'width': width, 'height': height
        }
        self.platforms.append(platform)
        return platform
        
    def run(self):
        """Start the platformer game."""
        @self.game.on_update
        def update(dt):
            if self.player:
                # Apply gravity
                self.player.velocity_y += self.gravity * dt
                self.player.move(0, self.player.velocity_y * dt)
                
                # Platform collision (simple)
                for platform in self.platforms:
                    if (self.player.x < platform['x'] + platform['width'] and
                        self.player.x + 32 > platform['x'] and
                        self.player.y < platform['y'] + platform['height'] and
                        self.player.y + 32 > platform['y']):
                        self.player.y = platform['y'] - 32
                        self.player.velocity_y = 0
                        
        self.game.run()


class RPGTemplate:
    """
    RPG game template.
    
    Example:
        game = RPGTemplate("My RPG")
        game.add_player(100, 100)
        game.add_npc(500, 300, "Hello adventurer!")
        game.run()
    """
    
    def __init__(self, title="RPG Game", width=1280, height=720):
        self.game = Game(title, width, height)
        self.player = None
        self.npcs = []
        self.move_speed = 200  # pixels per second
        
    def add_player(self, x, y):
        """Add player character."""
        self.player = self.game.create_sprite("player.png", x, y)
        return self.player
        
    def add_npc(self, x, y, dialog="Hello!"):
        """Add an NPC."""
        npc = self.game.create_sprite("npc.png", x, y)
        npc.dialog = dialog
        self.npcs.append(npc)
        return npc
        
    def run(self):
        """Start the RPG game."""
        @self.game.on_update
        def update(dt):
            if self.player:
                # Move player based on input
                dx = self.game.input.x * self.move_speed * dt
                dy = self.game.input.y * self.move_speed * dt
                self.player.move(dx, dy)
                
        self.game.run()


class ShooterTemplate:
    """
    Shooter game template.
    
    Example:
        game = ShooterTemplate("My Shooter")
        game.add_player(640, 600)
        game.spawn_enemy(300, 100)
        game.run()
    """
    
    def __init__(self, title="Shooter Game", width=1280, height=720):
        self.game = Game(title, width, height)
        self.player = None
        self.enemies = []
        self.bullets = []
        self.move_speed = 300
        self.bullet_speed = 500
        
    def add_player(self, x, y):
        """Add player character."""
        self.player = self.game.create_sprite("player.png", x, y)
        return self.player
        
    def spawn_enemy(self, x, y):
        """Spawn an enemy."""
        enemy = self.game.create_sprite("enemy.png", x, y)
        self.enemies.append(enemy)
        return enemy
        
    def shoot(self, x, y, direction_x, direction_y):
        """Fire a bullet."""
        bullet = self.game.create_sprite("bullet.png", x, y, scale=0.5)
        bullet.velocity_x = direction_x * self.bullet_speed
        bullet.velocity_y = direction_y * self.bullet_speed
        self.bullets.append(bullet)
        return bullet
        
    def run(self):
        """Start the shooter game."""
        @self.game.on_update
        def update(dt):
            if self.player:
                # Move player
                dx = self.game.input.x * self.move_speed * dt
                dy = self.game.input.y * self.move_speed * dt
                self.player.move(dx, dy)
                
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.move(bullet.velocity_x * dt, bullet.velocity_y * dt)
                
                # Remove off-screen bullets
                if bullet.y < -50 or bullet.y > self.game.height + 50:
                    self.bullets.remove(bullet)
                    
        self.game.run()


class PuzzleTemplate:
    """
    Puzzle game template.
    
    Example:
        game = PuzzleTemplate("My Puzzle")
        game.create_grid(8, 8)
        game.add_piece(0, 0, "red")
        game.run()
    """
    
    def __init__(self, title="Puzzle Game", width=1280, height=720):
        self.game = Game(title, width, height)
        self.grid = None
        self.pieces = []
        self.grid_width = 0
        self.grid_height = 0
        
    def create_grid(self, cols, rows):
        """Create puzzle grid."""
        self.grid_width = cols
        self.grid_height = rows
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        
    def add_piece(self, col, row, piece_type):
        """Add a puzzle piece."""
        if self.grid and 0 <= row < self.grid_height and 0 <= col < self.grid_width:
            piece = {
                'col': col,
                'row': row,
                'type': piece_type
            }
            self.grid[row][col] = piece
            self.pieces.append(piece)
            return piece
        return None
        
    def swap_pieces(self, col1, row1, col2, row2):
        """Swap two pieces."""
        if self.grid:
            piece1 = self.grid[row1][col1]
            piece2 = self.grid[row2][col2]
            self.grid[row1][col1] = piece2
            self.grid[row2][col2] = piece1
            
    def run(self):
        """Start the puzzle game."""
        self.game.run()


# Visual Scripting Interface

class VisualScriptNode:
    """Base class for visual scripting nodes."""
    
    def __init__(self, node_type):
        self.node_type = node_type
        self.inputs = {}
        self.outputs = {}
        self.connections = []
        
    def execute(self):
        """Execute this node."""
        pass
        
    def connect_to(self, other_node, output_name, input_name):
        """Connect this node's output to another node's input."""
        self.connections.append({
            'target': other_node,
            'output': output_name,
            'input': input_name
        })


class VisualScript:
    """Visual scripting system."""
    
    def __init__(self):
        self.nodes = []
        self.start_node = None
        
    def add_node(self, node):
        """Add a node to the script."""
        self.nodes.append(node)
        if self.start_node is None:
            self.start_node = node
            
    def execute(self):
        """Execute the visual script."""
        if self.start_node:
            current = self.start_node
            while current:
                current.execute()
                # Follow connections
                if current.connections:
                    current = current.connections[0]['target']
                else:
                    break


# Convenience functions for quick game creation

def quick_game(title="Quick Game", width=1280, height=720):
    """
    Create a game in one line.
    
    Example:
        game = quick_game("My Game")
    """
    return Game(title, width, height)


def quick_platformer(title="Platformer"):
    """Create a platformer game in one line."""
    return PlatformerTemplate(title)


def quick_rpg(title="RPG"):
    """Create an RPG game in one line."""
    return RPGTemplate(title)


def quick_shooter(title="Shooter"):
    """Create a shooter game in one line."""
    return ShooterTemplate(title)


def quick_puzzle(title="Puzzle"):
    """Create a puzzle game in one line."""
    return PuzzleTemplate(title)


# Example: Complete game in 10 lines
def example_simple_game():
    """
    Example of creating a complete game in 10 lines.
    """
    game = Game("Simple Game", 800, 600)
    player = game.create_sprite("player.png", 400, 300)
    
    @game.on_update
    def update(dt):
        player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)
    
    game.run()


if __name__ == "__main__":
    print("PyWRKGame High-Level API")
    print("========================")
    print()
    print("Quick game creation examples:")
    print()
    print("1. Simple game (10 lines):")
    print("   game = Game('My Game', 1280, 720)")
    print("   player = game.create_sprite('player.png', 100, 100)")
    print("   ")
    print("   @game.on_update")
    print("   def update(dt):")
    print("       player.move(game.input.x * 200 * dt, 0)")
    print("   ")
    print("   game.run()")
    print()
    print("2. Platformer template:")
    print("   game = quick_platformer('My Platformer')")
    print("   game.add_player(100, 100)")
    print("   game.add_platform(0, 500, 800, 50)")
    print("   game.run()")
    print()
    print("3. RPG template:")
    print("   game = quick_rpg('My RPG')")
    print("   game.add_player(100, 100)")
    print("   game.add_npc(500, 300, 'Hello!')")
    print("   game.run()")
