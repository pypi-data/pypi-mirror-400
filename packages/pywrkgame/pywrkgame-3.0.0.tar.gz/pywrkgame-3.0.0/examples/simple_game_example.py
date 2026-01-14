"""
Simple Game Example - Complete game in 10 lines
Demonstrates PyWRKGame's high-level API simplicity
"""

import sys
sys.path.insert(0, '../python')

from pywrkgame_api import Game

# Create a complete game in 10 lines
game = Game("Simple Game", 800, 600)
player = game.create_sprite("player.png", 400, 300)

@game.on_update
def update(dt):
    player.move(game.input.x * 200 * dt, game.input.y * 200 * dt)

game.run()
