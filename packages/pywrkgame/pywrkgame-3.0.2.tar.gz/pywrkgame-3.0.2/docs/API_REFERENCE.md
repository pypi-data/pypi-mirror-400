# PyWRKGame 3.0.0 API Reference

Complete API reference for PyWRKGame 3.0.0 - High-Performance Game Engine

## Table of Contents

1. [Core Classes](#core-classes)
2. [Game Templates](#game-templates)
3. [Quick Creation Functions](#quick-creation-functions)
4. [Visual Scripting](#visual-scripting)
5. [Input System](#input-system)
6. [Sprite Management](#sprite-management)
7. [Engine Core](#engine-core)
8. [Platform Features](#platform-features)

---

## Core Classes

### Game

Main game class for creating games.

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
game = Game("My Game", 1920, 1080, 120)
```

#### Properties

- `title` (str): Game window title
- `width` (int): Window width
- `height` (int): Window height
- `fps` (int): Target FPS
- `engine` (Engine): C++ engine core instance
- `input` (InputState): Input state manager
- `sprites` (list): List of all sprites
- `update_callback` (function): Update callback function

#### Methods

##### create_sprite()

```python
create_sprite(texture, x, y, scale=1.0) -> Sprite
```

Create a new sprite.

**Parameters:**
- `texture` (str): Path to texture file
- `x` (float): X position
- `y` (float): Y position
- `scale` (float): Sprite scale (default: 1.0)

**Returns:** Sprite object

**Example:**
```python
player = game.create_sprite("player.png", 100, 100, scale=2.0)
```

##### on_update()

```python
@game.on_update
def update(dt):
    # Update logic here
    pass
```

Decorator for registering update callback.

**Parameters:**
- `dt` (float): Delta time in seconds

**Example:**
```python
@game.on_update
def update(dt):
    player.move(100 * dt, 0)
```

##### run()

```python
run()
```

Start the game loop. This is a blocking call.

**Example:**
```python
game.run()
```

##### stop()

```python
stop()
```

Stop the game and clean up resources.

**Example:**
```python
game.stop()
```

---

### Sprite

Represents a 2D sprite in the game.

#### Properties

- `x` (float): X position
- `y` (float): Y position
- `scale` (float): Sprite scale
- `texture` (str): Texture path

#### Methods

##### move()

```python
move(dx, dy)
```

Move sprite by delta values.

**Parameters:**
- `dx` (float): X movement
- `dy` (float): Y movement

**Example:**
```python
sprite.move(10, -5)
```

##### set_position()

```python
set_position(x, y)
```

Set absolute position.

**Parameters:**
- `x` (float): New X position
- `y` (float): New Y position

**Example:**
```python
sprite.set_position(640, 360)
```

##### get_position()

```python
get_position() -> tuple
```

Get current position.

**Returns:** Tuple (x, y)

**Example:**
```python
x, y = sprite.get_position()
```

---

### InputState

Manages input state for the game.

#### Properties

- `x` (float): Horizontal input (-1.0 to 1.0)
- `y` (float): Vertical input (-1.0 to 1.0)
- `buttons` (dict): Button states

#### Example

```python
if game.input.x > 0:
    player.move(speed * dt, 0)

if game.input.buttons.get('fire', False):
    shoot()
```

---

## Game Templates

### PlatformerTemplate

Template for platformer games with gravity and platforms.

#### Constructor

```python
PlatformerTemplate(title="Platformer", width=1280, height=720)
```

**Parameters:**
- `title` (str): Game title
- `width` (int): Window width
- `height` (int): Window height

#### Properties

- `game` (Game): Underlying Game instance
- `gravity` (float): Gravity force (default: 980)
- `move_speed` (float): Player movement speed (default: 300)
- `jump_force` (float): Jump force (default: 500)
- `player` (Sprite): Player sprite
- `platforms` (list): List of platforms

#### Methods

##### add_player()

```python
add_player(x, y) -> Sprite
```

Add player to the game.

**Parameters:**
- `x` (float): Starting X position
- `y` (float): Starting Y position

**Returns:** Player sprite

**Example:**
```python
player = game.add_player(100, 100)
```

##### add_platform()

```python
add_platform(x, y, width, height) -> dict
```

Add a platform.

**Parameters:**
- `x` (float): Platform X position
- `y` (float): Platform Y position
- `width` (float): Platform width
- `height` (float): Platform height

**Returns:** Platform dictionary

**Example:**
```python
ground = game.add_platform(0, 650, 1280, 70)
```

##### run()

```python
run()
```

Start the platformer game loop.

---

### RPGTemplate

Template for RPG games with NPCs and dialog.

#### Constructor

```python
RPGTemplate(title="RPG", width=1280, height=720)
```

#### Properties

- `game` (Game): Underlying Game instance
- `move_speed` (float): Movement speed (default: 200)
- `player` (Sprite): Player sprite
- `npcs` (list): List of NPCs

#### Methods

##### add_player()

```python
add_player(x, y) -> Sprite
```

Add player character.

**Example:**
```python
player = game.add_player(640, 360)
```

##### add_npc()

```python
add_npc(x, y, dialog) -> Sprite
```

Add NPC with dialog.

**Parameters:**
- `x` (float): NPC X position
- `y` (float): NPC Y position
- `dialog` (str): NPC dialog text

**Returns:** NPC sprite

**Example:**
```python
npc = game.add_npc(500, 300, "Welcome, traveler!")
```

---

### ShooterTemplate

Template for shooter games with bullets and enemies.

#### Constructor

```python
ShooterTemplate(title="Shooter", width=1280, height=720)
```

#### Properties

- `game` (Game): Underlying Game instance
- `move_speed` (float): Movement speed (default: 300)
- `bullet_speed` (float): Bullet speed (default: 500)
- `player` (Sprite): Player sprite
- `enemies` (list): List of enemies
- `bullets` (list): List of bullets

#### Methods

##### add_player()

```python
add_player(x, y) -> Sprite
```

Add player ship/character.

##### spawn_enemy()

```python
spawn_enemy(x, y) -> Sprite
```

Spawn an enemy.

**Parameters:**
- `x` (float): Enemy X position
- `y` (float): Enemy Y position

**Returns:** Enemy sprite

##### shoot()

```python
shoot(x, y, dx, dy) -> Sprite
```

Fire a bullet.

**Parameters:**
- `x` (float): Starting X position
- `y` (float): Starting Y position
- `dx` (float): X direction (-1.0 to 1.0)
- `dy` (float): Y direction (-1.0 to 1.0)

**Returns:** Bullet sprite

**Example:**
```python
bullet = game.shoot(player.x, player.y, 0, -1)  # Shoot up
```

---

### PuzzleTemplate

Template for puzzle games with grid systems.

#### Constructor

```python
PuzzleTemplate(title="Puzzle", width=800, height=800)
```

#### Properties

- `game` (Game): Underlying Game instance
- `grid` (list): 2D grid array
- `grid_width` (int): Grid width
- `grid_height` (int): Grid height
- `pieces` (list): List of puzzle pieces

#### Methods

##### create_grid()

```python
create_grid(width, height)
```

Create puzzle grid.

**Parameters:**
- `width` (int): Grid width in cells
- `height` (int): Grid height in cells

**Example:**
```python
game.create_grid(8, 8)
```

##### add_piece()

```python
add_piece(col, row, piece_type) -> dict
```

Add a puzzle piece.

**Parameters:**
- `col` (int): Column index
- `row` (int): Row index
- `piece_type` (str): Piece type/color

**Returns:** Piece dictionary

**Example:**
```python
piece = game.add_piece(0, 0, "red")
```

##### swap_pieces()

```python
swap_pieces(col1, row1, col2, row2)
```

Swap two pieces.

**Parameters:**
- `col1` (int): First piece column
- `row1` (int): First piece row
- `col2` (int): Second piece column
- `row2` (int): Second piece row

**Example:**
```python
game.swap_pieces(0, 0, 1, 0)
```

---

## Quick Creation Functions

Convenience functions for rapid game creation.

### quick_game()

```python
quick_game(title="Quick Game") -> Game
```

Create a game quickly.

**Example:**
```python
game = quick_game("My Quick Game")
```

### quick_platformer()

```python
quick_platformer(title="Platformer") -> PlatformerTemplate
```

Create a platformer game quickly.

### quick_rpg()

```python
quick_rpg(title="RPG") -> RPGTemplate
```

Create an RPG game quickly.

### quick_shooter()

```python
quick_shooter(title="Shooter") -> ShooterTemplate
```

Create a shooter game quickly.

### quick_puzzle()

```python
quick_puzzle(title="Puzzle") -> PuzzleTemplate
```

Create a puzzle game quickly.

---

## Visual Scripting

### VisualScriptNode

Represents a node in a visual script.

#### Constructor

```python
VisualScriptNode(node_type)
```

**Parameters:**
- `node_type` (str): Type of node ("start", "action", "condition", etc.)

#### Properties

- `node_type` (str): Node type
- `connections` (list): List of connections to other nodes

#### Methods

##### connect_to()

```python
connect_to(target_node, output_port, input_port)
```

Connect this node to another node.

**Parameters:**
- `target_node` (VisualScriptNode): Target node
- `output_port` (str): Output port name
- `input_port` (str): Input port name

**Example:**
```python
node1.connect_to(node2, "output", "input")
```

---

### VisualScript

Container for visual script nodes.

#### Constructor

```python
VisualScript()
```

#### Properties

- `nodes` (list): List of nodes
- `start_node` (VisualScriptNode): Starting node

#### Methods

##### add_node()

```python
add_node(node)
```

Add a node to the script.

**Parameters:**
- `node` (VisualScriptNode): Node to add

**Example:**
```python
script = VisualScript()
node = VisualScriptNode("start")
script.add_node(node)
```

##### execute()

```python
execute()
```

Execute the visual script.

---

## Engine Core

### Engine

Low-level C++ engine core (accessed via `game.engine`).

#### Methods

##### is_initialized()

```python
is_initialized() -> bool
```

Check if engine is initialized.

**Returns:** True if initialized

**Example:**
```python
if game.engine.is_initialized():
    print("Engine ready!")
```

---

## Platform Features

### Platform Detection

```python
import platform

current_platform = platform.system()
# Returns: "Windows", "Linux", "Darwin" (macOS)
```

### Mobile Features

When running on mobile platforms (Android/iOS), additional features are available:

- Touch input gestures
- Device sensors (accelerometer, gyroscope)
- Haptic feedback
- Battery-based performance scaling
- Automatic pause/resume

---

## Complete Example

Here's a complete game using the API:

```python
from pywrkgame_api import quick_platformer

# Create platformer game
game = quick_platformer("My Platformer Game")

# Add player
player = game.add_player(100, 100)

# Add platforms
ground = game.add_platform(0, 650, 1280, 70)
platform1 = game.add_platform(300, 500, 400, 50)
platform2 = game.add_platform(800, 400, 300, 50)

# Setup controls
@game.game.on_update
def update(dt):
    # Horizontal movement
    if game.game.input.x != 0:
        player.move(game.move_speed * game.game.input.x * dt, 0)
    
    # Jump
    if game.game.input.buttons.get('jump', False):
        if player.on_ground:
            player.velocity_y = -game.jump_force

# Run game
game.run()
```

---

## Performance Tips

1. **Sprite Management**: Reuse sprites instead of creating new ones
2. **Update Callbacks**: Keep update logic efficient
3. **Asset Loading**: Load assets at startup, not during gameplay
4. **Mobile Optimization**: Use lower resolution textures on mobile

---

## Error Handling

```python
try:
    game = Game("My Game")
    # Game code here
    game.run()
except Exception as e:
    print(f"Error: {e}")
finally:
    game.stop()
```

---

## Next Steps

- See [examples/](../examples/) for complete game examples
- Read [GETTING_STARTED.md](GETTING_STARTED.md) for tutorials
- Check [ANDROID_BUILD.md](../ANDROID_BUILD.md) for mobile deployment

---

## Support

For API questions and issues:
- GitHub Issues: https://github.com/pywrkgame/pywrkgame/issues
- Documentation: https://pywrkgame.readthedocs.io/
- Community: https://discord.gg/pywrkgame
