# Re-export all types from the native module
from .kish import Team, Square, GameStatus, Action, Board, Game

__all__ = ["Team", "Square", "GameStatus", "Action", "Board", "Game"]
__version__ = "1.0.0"
