# PyWRKGame Python API Documentation

## Overview

PyWRKGame 3.0.0 provides a high-level Python API that makes game development incredibly simple. You can create complete games in as few as 10 lines of code!

## Installation

```bash
pip install pywrkgame
```

Or build from source:

```bash
git clone https://github.com/yourusername/pywrkgame.git
cd pywrkgame
mkdir build && cd build
cmake ..
cmake --build .
pip install -e ..
```

## Quick Start

### Create a Game in 10 Lines

```python
from pywrkgame_api import Game

game = Game("My Game", 800, 600)
player = game.create_sprite("player.png", 400, 300)

@game.on_update
def update(dt):
    player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)

game.run()
```

## Core API

### Game Class

The main class for creating games.

#### Constructor

```python
Game(title="PyWRKGame", width=1280, height=720, fps=60)
```

**Parameters:**
- `title` (str): Window title
- `width` (int): Window width in pixels
- `height` (int): Window height in pixels
- `fps` (int): Target frames per second

**Example:**
```python
game = Game("My Awesome Game", 1920, 1080, 120)
```

#### Methods

##### create_sprite(texture_path, x=0, y=0, scale=1.0)

Create a sprite game object.

**Parameters:**
- `texture_path` (str): Path to texture file
- `x` (float): Initial x position
- `y` (float): Initial y position
- `scale` (float): Sprite scale

**Returns:** Sprite object

**Example:**
```python
player = game.create_sprite("assets/player.png", 100, 100, 2.0)
```

##### on_update(callback)

Decorator to register update callback.

**Parameters:**
- `callback` (function): Function called each frame with delta_time parameter

**Example:**
```python
@game.on_update
def update(dt):
    # Game logic here
    pass
```

##### run()

Start the game loop. This is a blocking call.

**Example:**
```python
game.run()
```

##### stop()

Stop the game loop and cleanup resources.

**Example:**
```python
game.stop()
```

#### Properties

- `title` (str): Game window title
- `width` (int): Window width
- `height` (int): Window height
- `fps` (int): Target FPS
- `sprites` (list): List of all sprites
- `input` (InputState): Current input state
- `engine` (Engine): Low-level engine instance

### Sprite Class

Represents a game object with a texture.

#### Methods

##### move(dx, dy)

Move sprite by delta values.

**Parameters:**
- `dx` (float): Change in x position
- `dy` (float): Change in y position

**Example:**
```python
sprite.move(10, -5)
```

##### set_position(x, y)

Set absolute sprite position.

**Parameters:**
- `x` (float): New x position
- `y` (float): New y position

**Example:**
```python
sprite.set_position(400, 300)
```

##### get_position()

Get current sprite position.

**Returns:** Tuple (x, y)

**Example:**
```python
x, y = sprite.get_position()
```

#### Properties

- `x` (float): X position
- `y` (float): Y position
- `scale` (float): Sprite scale
- `texture_path` (str): Path to texture
- `game_object` (GameObject): Underlying game object

### InputState Class

Tracks input state.

#### Properties

- `x` (float): Horizontal input (-1 to 1)
- `y` (float): Vertical input (-1 to 1)
- `buttons` (dict): Button states

**Example:**
```python
if game.input.x > 0:
    player.move(speed * dt, 0)
    
if game.input.buttons.get('fire'):
    shoot()
```

## Game Templates

PyWRKGame includes pre-built templates for common game genres.

### PlatformerTemplate

Create platformer games with physics and platforms.

```python
from pywrkgame_api import PlatformerTemplate

game = PlatformerTemplate("My Platformer", 1280, 720)
game.add_player(100, 100)
game.add_platform(0, 500, 800, 50)
game.add_platform(300, 400, 400, 50)
game.run()
```

#### Methods

##### add_player(x, y)

Add player character.

**Returns:** Player sprite

##### add_platform(x, y, width, height)

Add a platform.

**Returns:** Platform dictionary

#### Properties

- `gravity` (float): Gravity acceleration (default: 980)
- `player` (Sprite): Player sprite
- `platforms` (list): List of platforms

### RPGTemplate

Create RPG games with NPCs and dialog.

```python
from pywrkgame_api import RPGTemplate

game = RPGTemplate("My RPG", 1280, 720)
game.add_player(100, 100)
game.add_npc(500, 300, "Welcome, traveler!")
game.run()
```

#### Methods

##### add_player(x, y)

Add player character.

**Returns:** Player sprite

##### add_npc(x, y, dialog="Hello!")

Add an NPC with dialog.

**Returns:** NPC sprite

#### Properties

- `move_speed` (float): Movement speed (default: 200)
- `player` (Sprite): Player sprite
- `npcs` (list): List of NPCs

### ShooterTemplate

Create shooter games with enemies and bullets.

```python
from pywrkgame_api import ShooterTemplate

game = ShooterTemplate("Space Shooter", 1280, 720)
game.add_player(640, 600)
game.spawn_enemy(300, 100)
game.run()
```

#### Methods

##### add_player(x, y)

Add player character.

**Returns:** Player sprite

##### spawn_enemy(x, y)

Spawn an enemy.

**Returns:** Enemy sprite

##### shoot(x, y, direction_x, direction_y)

Fire a bullet.

**Returns:** Bullet sprite

#### Properties

- `move_speed` (float): Player movement speed (default: 300)
- `bullet_speed` (float): Bullet speed (default: 500)
- `player` (Sprite): Player sprite
- `enemies` (list): List of enemies
- `bullets` (list): List of bullets

### PuzzleTemplate

Create puzzle games with grid systems.

```python
from pywrkgame_api import PuzzleTemplate

game = PuzzleTemplate("Match-3", 1280, 720)
game.create_grid(8, 8)
game.add_piece(0, 0, "red")
game.add_piece(1, 0, "blue")
game.run()
```

#### Methods

##### create_grid(cols, rows)

Create puzzle grid.

##### add_piece(col, row, piece_type)

Add a puzzle piece.

**Returns:** Piece dictionary

##### swap_pieces(col1, row1, col2, row2)

Swap two pieces.

#### Properties

- `grid` (list): 2D grid array
- `grid_width` (int): Grid width
- `grid_height` (int): Grid height
- `pieces` (list): List of pieces

## Quick Creation Functions

Convenience functions for one-line game creation.

### quick_game(title, width, height)

Create a game in one line.

```python
game = quick_game("Quick Game", 800, 600)
```

### quick_platformer(title)

Create a platformer in one line.

```python
game = quick_platformer("My Platformer")
```

### quick_rpg(title)

Create an RPG in one line.

```python
game = quick_rpg("My RPG")
```

### quick_shooter(title)

Create a shooter in one line.

```python
game = quick_shooter("My Shooter")
```

### quick_puzzle(title)

Create a puzzle game in one line.

```python
game = quick_puzzle("My Puzzle")
```

## Visual Scripting

PyWRKGame supports visual scripting for non-programmers.

### VisualScript Class

Container for visual script nodes.

```python
from pywrkgame_api import VisualScript, VisualScriptNode

script = VisualScript()
start_node = VisualScriptNode("start")
action_node = VisualScriptNode("action")

start_node.connect_to(action_node, "output", "input")
script.add_node(start_node)
script.add_node(action_node)

script.execute()
```

#### Methods

##### add_node(node)

Add a node to the script.

##### execute()

Execute the visual script.

### VisualScriptNode Class

Individual node in a visual script.

#### Constructor

```python
VisualScriptNode(node_type)
```

#### Methods

##### connect_to(other_node, output_name, input_name)

Connect this node's output to another node's input.

##### execute()

Execute this node.

## Low-Level API

For advanced users, the low-level C++ API is also exposed.

### Engine Class

```python
import pywrkgame as pwg

config = pwg.EngineConfig()
config.app_name = "My Game"
config.window_width = 1280
config.window_height = 720

engine = pwg.Engine()
engine.initialize(config)

# Game loop
while running:
    engine.update(delta_time)
    engine.render()

engine.shutdown()
```

### EntityManager

```python
entity_manager = engine.get_entity_manager()
entity = entity_manager.create_entity()
entity_manager.destroy_entity(entity)
```

### GameObject

```python
game_object = engine.create_game_object()
entity_id = game_object.get_entity_id()
game_object.destroy()
```

## Exception Handling

PyWRKGame provides custom exceptions for error handling.

### Exception Hierarchy

- `PyWRKGameError` - Base exception
  - `InitializationError` - Engine initialization failed
  - `ResourceError` - Resource loading/management error
  - `RenderingError` - Graphics rendering error
  - `PhysicsError` - Physics simulation error

### Example

```python
import pywrkgame as pwg

try:
    engine = pwg.Engine()
    engine.initialize(config)
except pwg.InitializationError as e:
    print(f"Failed to initialize: {e}")
except pwg.PyWRKGameError as e:
    print(f"Engine error: {e}")
```

## Best Practices

### 1. Use High-Level API for Rapid Development

```python
# Good - Simple and readable
game = quick_platformer("My Game")
game.add_player(100, 100)
game.run()
```

### 2. Use Templates for Common Genres

Templates provide pre-built mechanics and save development time.

### 3. Keep Update Logic Simple

```python
@game.on_update
def update(dt):
    # Keep logic simple and focused
    update_player(dt)
    update_enemies(dt)
    check_collisions()
```

### 4. Cleanup Resources

```python
try:
    game.run()
finally:
    game.stop()
```

### 5. Use Visual Scripting for Non-Programmers

Visual scripting allows designers to create game logic without coding.

## Examples

See the `examples/` directory for complete working examples:

- `simple_game_example.py` - Basic game in 10 lines
- `platformer_example.py` - Platformer template usage
- `rpg_example.py` - RPG template usage
- `shooter_example.py` - Shooter template usage
- `puzzle_example.py` - Puzzle template usage

## Performance Tips

1. **Batch sprite creation** - Create all sprites at initialization
2. **Minimize sprite count** - Use object pooling for bullets/particles
3. **Optimize update logic** - Avoid expensive operations in update loop
4. **Use appropriate FPS** - 60 FPS for most games, 30 FPS for mobile

## Troubleshooting

### Module Not Found

```python
import sys
sys.path.insert(0, 'path/to/build')
import pywrkgame
```

### Engine Initialization Failed

Check that graphics drivers are up to date and system meets requirements.

### Performance Issues

- Reduce sprite count
- Lower target FPS
- Disable post-processing effects
- Use simpler physics

## Support

- GitHub: https://github.com/yourusername/pywrkgame
- Documentation: https://pywrkgame.readthedocs.io
- Issues: https://github.com/yourusername/pywrkgame/issues

## License

PyWRKGame is released under the MIT License.
