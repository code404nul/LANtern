"""Outils de debug : logs, statistiques réseau et overlay pygame.

pygame n'est importé qu'à l'intérieur des méthodes de ``DebugOverlay`` :
un serveur dédié peut importer ``lanterne`` sans pygame.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from .client import Client


@dataclass
class NetStats:
    """Statistiques réseau d'un client, mises à jour par ``poll()``."""

    rtt: float = 0.0
    bytes_in_per_s: float = 0.0
    bytes_out_per_s: float = 0.0
    msgs_in_per_s: float = 0.0
    msgs_out_per_s: float = 0.0
    snapshot_rate: float = 0.0
    entity_count: int = 0
    tick: int = 0


def enable_logging(level: str = "INFO", filename: str | None = None) -> None:
    """Affiche les logs du logger ``"lanterne"`` dans la console ou un fichier."""
    raise NotImplementedError


class DebugOverlay:
    """Panneau de statistiques réseau dessiné par-dessus le jeu."""

    def __init__(self, client: Client, toggle_key: int | None = None) -> None:
        """Associe l'overlay à un client ; ``toggle_key`` vaut F3 par défaut."""
        raise NotImplementedError

    def handle_event(self, event: pygame.event.Event) -> None:
        """Affiche ou cache l'overlay quand la touche est pressée."""
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        """Dessine les statistiques sur ``surface`` si l'overlay est visible."""
        raise NotImplementedError
