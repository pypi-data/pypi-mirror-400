"""
PyWRKGame - High-Performance Game Engine
Version 3.0.0

High-level Python API for game development.
"""

# Import core C++ bindings
try:
    from .pywrkgame import *
except ImportError:
    # Module not built yet
    pass

# Import high-level API
from .pywrkgame_api import (
    Game,
    Sprite,
    InputState,
    PlatformerTemplate,
    RPGTemplate,
    ShooterTemplate,
    PuzzleTemplate,
    VisualScript,
    VisualScriptNode,
    quick_game,
    quick_platformer,
    quick_rpg,
    quick_shooter,
    quick_puzzle,
)

__version__ = "3.0.0"
__all__ = [
    # High-level API
    'Game',
    'Sprite',
    'InputState',
    # Templates
    'PlatformerTemplate',
    'RPGTemplate',
    'ShooterTemplate',
    'PuzzleTemplate',
    # Visual Scripting
    'VisualScript',
    'VisualScriptNode',
    # Quick creation functions
    'quick_game',
    'quick_platformer',
    'quick_rpg',
    'quick_shooter',
    'quick_puzzle',
]
