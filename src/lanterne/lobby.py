"""Lobby : informations publiques sur les joueurs et phase de la partie."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    """Étape où en est la partie."""

    LOBBY = "lobby"
    GAME = "game"


@dataclass(frozen=True)
class PlayerInfo:
    """Description d'un joueur telle que la voient les clients."""

    id: int
    name: str
    ready: bool
    is_host: bool
