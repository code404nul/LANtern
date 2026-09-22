"""Découverte des parties sur le réseau local par broadcast UDP.

Le client diffuse ``_discover`` chaque seconde ; chaque serveur qui écoute
sur ``discovery_port`` répond ``_announce`` directement au client.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import Config


@dataclass(frozen=True)
class ServerInfo:
    """Une partie trouvée sur le réseau local."""

    name: str
    host: str
    port: int
    players: int
    max_players: int
    phase: str


class ServerBrowser:
    """Cherche en arrière-plan les parties du réseau local."""

    def __init__(self, config: Config | None = None) -> None:
        """Prépare la recherche sans la démarrer ; ``None`` = ``Config()``."""
        raise NotImplementedError

    def start(self) -> None:
        """Démarre la recherche dans un thread réseau."""
        raise NotImplementedError

    def stop(self) -> None:
        """Arrête la recherche et le thread réseau."""
        raise NotImplementedError

    @property
    def servers(self) -> list[ServerInfo]:
        """Parties ayant répondu récemment (copie, sûre depuis le thread pygame)."""
        raise NotImplementedError


class DiscoveryResponder:
    """Interne : répond aux ``_discover`` pour le compte d'un ``Server``."""

    def __init__(self, config: Config) -> None:
        """Prépare le répondeur pour le port ``config.discovery_port``."""
        raise NotImplementedError

    async def start(self) -> None:
        """Ouvre le socket UDP de découverte dans la boucle du serveur."""
        raise NotImplementedError

    def close(self) -> None:
        """Ferme le socket UDP."""
        raise NotImplementedError
