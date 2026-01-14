"""
Shooter Game Example
Demonstrates using the shooter template
"""

import sys
sys.path.insert(0, '../python')

from pywrkgame_api import quick_shooter

# Create a shooter game
game = quick_shooter("Space Shooter")
game.add_player(640, 600)
game.spawn_enemy(300, 100)
game.spawn_enemy(500, 150)
game.spawn_enemy(700, 100)
game.run()
