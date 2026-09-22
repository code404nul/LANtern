"""Configuration centralisée de LANterne."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    """Tous les réglages réseau d'un jeu.

    Passez la même instance (ou les mêmes valeurs) au serveur et aux
    clients. Le détail de chaque champ est dans docs/API.md.
    """

    # Connexion
    host: str = "0.0.0.0"
    port: int = 5050
    discovery_port: int = 5051
    game_id: str = "lanterne"
    server_name: str = "Partie LANterne"
    max_players: int = 8

    # Lobby
    use_lobby: bool = True
    allow_join_in_game: bool = False
    discoverable: bool = True

    # Synchronisation
    tick_rate: int = 30
    interpolation_delay: float = 0.08
    despawn_on_disconnect: bool = True

    # Connexion : délais et limites (secondes, octets)
    heartbeat_interval: float = 1.0
    timeout: float = 5.0
    handshake_timeout: float = 5.0
    max_message_size: int = 1_048_576

    # Simulation d'un mauvais réseau (outils de debug)
    sim_latency: float = 0.0
    sim_jitter: float = 0.0
    sim_loss: float = 0.0
