"""LANterne : multijoueur en réseau local pour pygame-ce."""

from .client import Client
from .config import Config
from .debug import DebugOverlay, NetStats, enable_logging
from .discovery import ServerBrowser, ServerInfo
from .entity import NetworkEntity, replicated
from .lobby import Phase, PlayerInfo
from .protocol import PROTOCOL_VERSION
from .server import Player, Server

__version__ = "0.1.0"

__all__ = [
    "Client",
    "Config",
    "DebugOverlay",
    "NetStats",
    "NetworkEntity",
    "PROTOCOL_VERSION",
    "Phase",
    "Player",
    "PlayerInfo",
    "Server",
    "ServerBrowser",
    "ServerInfo",
    "enable_logging",
    "replicated",
]
