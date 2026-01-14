# PyWRKGame Examples

This directory contains example games demonstrating PyWRKGame's high-level Python API.

## Simple Game Example

**File:** `simple_game_example.py`

A complete game in just 10 lines of code! This example shows how easy it is to create a basic game with player movement.

```python
game = Game("Simple Game", 800, 600)
player = game.create_sprite("player.png", 400, 300)

@game.on_update
def update(dt):
    player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)

game.run()
```

## Game Templates

PyWRKGame includes pre-built templates for common game genres:

### Platformer Template

**File:** `platformer_example.py`

Create a platformer game in 4 lines:

```python
game = quick_platformer("My Platformer")
game.add_player(100, 100)
game.add_platform(0, 500, 800, 50)
game.run()
```

### RPG Template

**File:** `rpg_example.py`

Create an RPG with NPCs and dialog:

```python
game = quick_rpg("My RPG Adventure")
game.add_player(100, 100)
game.add_npc(500, 300, "Welcome to the village!")
game.run()
```

### Shooter Template

**File:** `shooter_example.py`

Create a shooter game with enemies:

```python
game = quick_shooter("Space Shooter")
game.add_player(640, 600)
game.spawn_enemy(300, 100)
game.run()
```

### Puzzle Template

**File:** `puzzle_example.py`

Create a puzzle game with a grid system:

```python
game = quick_puzzle("Match-3 Puzzle")
game.create_grid(8, 8)
game.add_piece(0, 0, "red")
game.run()
```

## Running Examples

To run any example:

```bash
python examples/simple_game_example.py
```

**Note:** Make sure PyWRKGame is built and installed before running examples.

## API Features

### High-Level Game Class

- **Simple initialization:** `Game(title, width, height, fps)`
- **Sprite creation:** `game.create_sprite(texture, x, y, scale)`
- **Update callbacks:** `@game.on_update` decorator
- **Easy game loop:** `game.run()`

### Game Templates

All templates provide:
- Pre-configured game mechanics
- Genre-specific features
- Minimal setup code
- Easy customization

### Visual Scripting

PyWRKGame also supports visual scripting for non-programmers:

```python
script = VisualScript()
node1 = VisualScriptNode("start")
node2 = VisualScriptNode("action")
node1.connect_to(node2, "output", "input")
script.add_node(node1)
script.add_node(node2)
script.execute()
```

## Requirements

- PyWRKGame 3.0.0 or later
- Python 3.7+
- Built C++ core library

## More Information

See the main README.md for installation instructions and full API documentation.
