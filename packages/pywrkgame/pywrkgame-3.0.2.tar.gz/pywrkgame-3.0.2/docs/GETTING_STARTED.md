# Getting Started with PyWRKGame 3.0.0

Welcome to PyWRKGame! This guide will help you create your first game in minutes.

## Table of Contents

1. [Installation](#installation)
2. [Your First Game](#your-first-game)
3. [Understanding the Basics](#understanding-the-basics)
4. [Game Templates](#game-templates)
5. [Adding Interactivity](#adding-interactivity)
6. [Next Steps](#next-steps)

---

## Installation

### Prerequisites

- Python 3.7 or higher
- CMake 3.15 or higher
- C++ compiler (MSVC on Windows, GCC/Clang on Linux/macOS)

### Building from Source

1. Clone the repository:
```bash
git clone https://github.com/pywrkgame/pywrkgame.git
cd pywrkgame
```

2. Build the C++ core:
```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

3. Install Python package:
```bash
cd ..
pip install -e .
```

### Verify Installation

```python
import pywrkgame as pwg
from pywrkgame_api import Game

print("PyWRKGame installed successfully!")
```

---

## Your First Game

Let's create a simple game in just 8 lines of code!

### Step 1: Create a new file

Create a file called `my_first_game.py`:

```python
from pywrkgame_api import Game

# Create game window
game = Game("My First Game", 800, 600)

# Create player sprite
player = game.create_sprite("player.png", 400, 300)

# Add movement
@game.on_update
def update(dt):
    speed = 200
    player.move(game.input.x * speed * dt, game.input.y * speed * dt)

# Run the game
game.run()
```

### Step 2: Run your game

```bash
python my_first_game.py
```

**Congratulations!** You've created your first game with PyWRKGame! 🎮

---

## Understanding the Basics

### The Game Object

The `Game` class is the foundation of every PyWRKGame application:

```python
game = Game(title, width, height, fps)
```

- **title**: Window title
- **width**: Window width in pixels
- **height**: Window height in pixels
- **fps**: Target frames per second (default: 60)

### Sprites

Sprites are 2D images that represent game objects:

```python
sprite = game.create_sprite("texture.png", x, y, scale)
```

- **texture**: Path to image file
- **x, y**: Position on screen
- **scale**: Size multiplier (default: 1.0)

### Update Loop

The update loop runs every frame:

```python
@game.on_update
def update(dt):
    # dt is delta time in seconds
    # Update game logic here
    pass
```

### Input

Access player input through `game.input`:

```python
@game.on_update
def update(dt):
    # Horizontal input: -1 (left), 0 (none), 1 (right)
    if game.input.x > 0:
        player.move(100 * dt, 0)
    
    # Vertical input: -1 (up), 0 (none), 1 (down)
    if game.input.y < 0:
        player.move(0, -100 * dt)
    
    # Button input
    if game.input.buttons.get('fire', False):
        shoot()
```

---

## Game Templates

PyWRKGame includes templates for common game genres. Let's explore each one!

### Platformer Game

Create a platformer in 4 lines:

```python
from pywrkgame_api import quick_platformer

game = quick_platformer("My Platformer")
game.add_player(100, 100)
game.add_platform(0, 500, 800, 50)
game.run()
```

**Features:**
- Gravity and jumping
- Platform collision
- Player movement

**Customize it:**

```python
from pywrkgame_api import PlatformerTemplate

game = PlatformerTemplate("Advanced Platformer", 1280, 720)

# Adjust physics
game.gravity = 1200  # Stronger gravity
game.jump_force = 600  # Higher jumps
game.move_speed = 400  # Faster movement

# Add player
player = game.add_player(100, 100)

# Add multiple platforms
ground = game.add_platform(0, 650, 1280, 70)
platform1 = game.add_platform(200, 500, 300, 50)
platform2 = game.add_platform(600, 400, 300, 50)
platform3 = game.add_platform(1000, 300, 200, 50)

# Custom controls
@game.game.on_update
def update(dt):
    # Add double jump, wall slide, etc.
    pass

game.run()
```

### RPG Game

Create an RPG with NPCs:

```python
from pywrkgame_api import quick_rpg

game = quick_rpg("My RPG")
game.add_player(640, 360)
game.add_npc(200, 200, "Welcome to the village!")
game.add_npc(400, 300, "Beware of the forest!")
game.run()
```

**Features:**
- 8-directional movement
- NPC dialog system
- Collision detection

**Customize it:**

```python
from pywrkgame_api import RPGTemplate

game = RPGTemplate("Epic Quest", 1920, 1080)

# Add player
player = game.add_player(960, 540)

# Add NPCs with different dialogs
merchant = game.add_npc(300, 300, "Would you like to buy something?")
guard = game.add_npc(600, 400, "The king awaits in the castle.")
villager = game.add_npc(900, 500, "Have you heard about the dragon?")

# Custom movement and interactions
@game.game.on_update
def update(dt):
    # Move player
    dx = game.game.input.x * game.move_speed * dt
    dy = game.game.input.y * game.move_speed * dt
    player.move(dx, dy)
    
    # Check NPC interactions
    for npc in game.npcs:
        distance = ((player.x - npc.x)**2 + (player.y - npc.y)**2)**0.5
        if distance < 50 and game.game.input.buttons.get('interact', False):
            print(npc.dialog)

game.run()
```

### Shooter Game

Create a space shooter:

```python
from pywrkgame_api import quick_shooter

game = quick_shooter("Space Battle")
game.add_player(640, 600)
game.spawn_enemy(300, 100)
game.run()
```

**Features:**
- Bullet system
- Enemy spawning
- Collision detection

**Customize it:**

```python
from pywrkgame_api import ShooterTemplate

game = ShooterTemplate("Galactic War", 1280, 720)

# Add player
player = game.add_player(640, 650)

# Spawn multiple enemies
for i in range(5):
    game.spawn_enemy(100 + i * 200, 50)

# Custom shooting and enemy AI
@game.game.on_update
def update(dt):
    # Player movement
    player.move(game.game.input.x * game.move_speed * dt, 0)
    
    # Auto-shoot
    if game.game.input.buttons.get('fire', False):
        game.shoot(player.x, player.y, 0, -1)
    
    # Update bullets
    for bullet in game.bullets:
        bullet.move(0, bullet.velocity_y * game.bullet_speed * dt)
    
    # Enemy movement
    for enemy in game.enemies:
        enemy.move(0, 50 * dt)  # Move down

game.run()
```

### Puzzle Game

Create a match-3 puzzle:

```python
from pywrkgame_api import quick_puzzle

game = quick_puzzle("Gem Matcher")
game.create_grid(8, 8)
game.add_piece(0, 0, "red")
game.run()
```

**Features:**
- Grid system
- Piece swapping
- Match detection

**Customize it:**

```python
from pywrkgame_api import PuzzleTemplate
import random

game = PuzzleTemplate("Jewel Quest", 800, 800)

# Create grid
game.create_grid(8, 8)

# Fill grid with random pieces
colors = ["red", "blue", "green", "yellow", "purple"]
for row in range(8):
    for col in range(8):
        color = random.choice(colors)
        game.add_piece(col, row, color)

# Custom matching logic
@game.game.on_update
def update(dt):
    # Check for matches
    # Implement swap logic
    # Add animations
    pass

game.run()
```

---

## Adding Interactivity

### Keyboard Input

```python
@game.on_update
def update(dt):
    # Arrow keys or WASD
    if game.input.x > 0:  # Right
        player.move(speed * dt, 0)
    elif game.input.x < 0:  # Left
        player.move(-speed * dt, 0)
    
    if game.input.y > 0:  # Down
        player.move(0, speed * dt)
    elif game.input.y < 0:  # Up
        player.move(0, -speed * dt)
```

### Button Actions

```python
@game.on_update
def update(dt):
    # Space bar or button
    if game.input.buttons.get('jump', False):
        player_jump()
    
    # Fire button
    if game.input.buttons.get('fire', False):
        shoot_bullet()
```

### Collision Detection

```python
def check_collision(sprite1, sprite2):
    """Simple bounding box collision"""
    return (abs(sprite1.x - sprite2.x) < 50 and
            abs(sprite1.y - sprite2.y) < 50)

@game.on_update
def update(dt):
    for enemy in enemies:
        if check_collision(player, enemy):
            print("Hit!")
```

### Sprite Animation

```python
@game.on_update
def update(dt):
    # Rotate sprite
    sprite.rotation += 90 * dt  # 90 degrees per second
    
    # Scale sprite
    sprite.scale = 1.0 + 0.5 * math.sin(time)
    
    # Move in circle
    angle += dt
    sprite.x = center_x + radius * math.cos(angle)
    sprite.y = center_y + radius * math.sin(angle)
```

---

## Next Steps

### Learn More

1. **API Reference**: See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation
2. **Examples**: Explore [examples/](../examples/) for complete game examples
3. **Advanced Features**: Learn about physics, audio, networking, and AI

### Build Your Game

Now that you know the basics, try building:

1. **Pong**: Classic paddle game
2. **Snake**: Grow and avoid walls
3. **Breakout**: Break bricks with a ball
4. **Tower Defense**: Defend against waves
5. **Your Own Idea**: Be creative!

### Deploy Your Game

- **Desktop**: Package with PyInstaller
- **Android**: Use Buildozer (see [ANDROID_BUILD.md](../ANDROID_BUILD.md))
- **iOS**: Use Kivy-iOS
- **Web**: Use Pygbag (experimental)

### Get Help

- **Documentation**: https://pywrkgame.readthedocs.io/
- **GitHub Issues**: https://github.com/pywrkgame/pywrkgame/issues
- **Discord Community**: https://discord.gg/pywrkgame
- **Stack Overflow**: Tag your questions with `pywrkgame`

---

## Tips for Success

1. **Start Simple**: Begin with a template and customize it
2. **Iterate Quickly**: Use hot-reloading for rapid development
3. **Test Often**: Run your game frequently to catch bugs early
4. **Optimize Later**: Focus on gameplay first, performance second
5. **Have Fun**: Game development should be enjoyable!

---

## Common Patterns

### Game State Management

```python
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

state = GameState.MENU

@game.on_update
def update(dt):
    if state == GameState.MENU:
        update_menu(dt)
    elif state == GameState.PLAYING:
        update_gameplay(dt)
    elif state == GameState.PAUSED:
        update_pause_menu(dt)
    elif state == GameState.GAME_OVER:
        update_game_over(dt)
```

### Score Tracking

```python
score = 0

def add_score(points):
    global score
    score += points
    print(f"Score: {score}")

@game.on_update
def update(dt):
    # Award points for actions
    if enemy_defeated:
        add_score(100)
```

### Health System

```python
player_health = 100
max_health = 100

def take_damage(amount):
    global player_health
    player_health = max(0, player_health - amount)
    if player_health == 0:
        game_over()

def heal(amount):
    global player_health
    player_health = min(max_health, player_health + amount)
```

---

## Troubleshooting

### Game Won't Start

- Check that PyWRKGame is installed: `pip list | grep pywrkgame`
- Verify C++ bindings are built: Check for `.pyd` or `.so` files in build directory
- Try rebuilding: `cmake --build build --config Release`

### Sprites Not Showing

- Verify texture file exists
- Check file path is correct
- Ensure sprite is within window bounds

### Poor Performance

- Reduce number of sprites
- Lower window resolution
- Disable post-processing effects
- Use sprite batching

---

Happy game development! 🎮✨
