"""
RPG Game Example
Demonstrates using the RPG template
"""

import sys
sys.path.insert(0, '../python')

from pywrkgame_api import quick_rpg

# Create an RPG game
game = quick_rpg("My RPG Adventure")
game.add_player(100, 100)
game.add_npc(500, 300, "Welcome to the village!")
game.add_npc(300, 400, "Beware of the dragon!")
game.run()
