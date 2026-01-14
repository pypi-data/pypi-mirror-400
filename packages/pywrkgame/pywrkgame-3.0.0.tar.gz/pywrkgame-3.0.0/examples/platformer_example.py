"""
Platformer Game Example
Demonstrates using the platformer template
"""

import sys
sys.path.insert(0, '../python')

from pywrkgame_api import quick_platformer

# Create a platformer game in 4 lines
game = quick_platformer("My Platformer")
game.add_player(100, 100)
game.add_platform(0, 500, 800, 50)
game.run()
