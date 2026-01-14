"""
Puzzle Game Example
Demonstrates using the puzzle template
"""

import sys
sys.path.insert(0, '../python')

from pywrkgame_api import quick_puzzle

# Create a puzzle game
game = quick_puzzle("Match-3 Puzzle")
game.create_grid(8, 8)

# Add some puzzle pieces
for row in range(8):
    for col in range(8):
        colors = ["red", "blue", "green", "yellow"]
        import random
        color = random.choice(colors)
        game.add_piece(col, row, color)

game.run()
