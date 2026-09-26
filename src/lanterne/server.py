"""Serveur qui fait autorité sur la partie.

Les handlers enregistrés sur le serveur s'exécutent dans son thread
asyncio : ils doivent être rapides et ne jamais utiliser pygame.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from .config import Config
from .entity import NetworkEntity
from .lobby import Phase, PlayerInfo

F = TypeVar("F", bound=Callable[..., Any])
E = TypeVar("E", bound=NetworkEntity)


class Player:
    """Un joueur connecté, vu par le serveur. Créé par la bibliothèque.

    Attributs :
        id: identifiant unique attribué par le serveur.
        name: pseudo.
        ready: a indiqué être prêt dans le lobby.
        is_host: premier joueur connecté, seul à pouvoir lancer la partie.
        input: dernier état envoyé par ``Client.set_input()`` (non fiable).
        rtt: temps d'aller-retour mesuré, en secondes.
        address: IP et port du client.
    """

    id: int
    name: str
    ready: bool
    is_host: bool
    input: dict[str, Any]
    rtt: float
    address: tuple[str, int]

    def send(self, msg_type: str, data: Any = None) -> None:
        """Envoie un message à ce joueur (raccourci de ``Server.send``)."""
        raise NotImplementedError

    def to_info(self) -> PlayerInfo:
        """Renvoie la description publique de ce joueur."""
        raise NotImplementedError


class Server:
    """Serveur de jeu : connexions, handshake, lobby, tick et réplication."""

    def __init__(self, config: Config | None = None) -> None:
        """Prépare le serveur sans ouvrir de socket ; ``None`` = ``Config()``."""
        self.config = config

    # --- Démarrage et arrêt -------------------------------------------------

    def start(self) -> None:
        """Démarre le serveur dans un thread réseau et rend la main (listen server)."""
        raise NotImplementedError

    def run(self) -> None:
        """Fait tourner le serveur dans le thread courant jusqu'à Ctrl+C (serveur dédié)."""
        raise NotImplementedError

    def stop(self) -> None:
        """Envoie ``_bye`` à tous, ferme les connexions et arrête le thread."""
        raise NotImplementedError

    # --- Handlers -----------------------------------------------------------

    def on(self, msg_type: str) -> Callable[[F], F]:
        """Décorateur : ``func(player, data)`` reçoit les messages de ce type."""
        raise NotImplementedError

    def on_connect(self, func: F) -> F:
        """Décorateur : ``func(player)`` est appelé après un handshake réussi."""
        raise NotImplementedError

    def on_disconnect(self, func: F) -> F:
        """Décorateur : ``func(player, reason)`` est appelé quand un joueur part."""
        raise NotImplementedError

    def on_game_start(self, func: F) -> F:
        """Décorateur : ``func()`` est appelé au passage du lobby au jeu."""
        raise NotImplementedError

    def on_tick(self, func: F) -> F:
        """Décorateur : ``func(dt)`` est appelé à chaque tick de jeu."""
        raise NotImplementedError

    # --- Messages -----------------------------------------------------------

    def send(self, player: Player, msg_type: str, data: Any = None) -> None:
        """Envoie un message à un seul joueur."""
        raise NotImplementedError

    def broadcast(self, msg_type: str, data: Any = None, exclude: Player | None = None) -> None:
        """Envoie un message à tous les joueurs, sauf ``exclude``."""
        raise NotImplementedError

    def kick(self, player: Player, reason: str = "kicked") -> None:
        """Déconnecte un joueur en lui indiquant la raison."""
        raise NotImplementedError

    # --- Joueurs et phase ---------------------------------------------------

    @property
    def players(self) -> dict[int, Player]:
        """Joueurs connectés, indexés par id."""
        raise NotImplementedError

    def get_player(self, player_id: int) -> Player | None:
        """Renvoie le joueur de cet id, ou ``None`` s'il n'est plus connecté."""
        raise NotImplementedError

    @property
    def phase(self) -> Phase:
        """Phase actuelle de la partie."""
        raise NotImplementedError

    @property
    def tick(self) -> int:
        """Numéro du tick courant."""
        raise NotImplementedError

    def start_game(self) -> None:
        """Passe en phase ``GAME`` et prévient les clients."""
        raise NotImplementedError

    def end_game(self) -> None:
        """Supprime toutes les entités et revient au lobby."""
        raise NotImplementedError

    # --- Entités ------------------------------------------------------------

    def spawn(self, cls: type[E], owner: Player | None = None, **attrs: Any) -> E:
        """Crée une entité répliquée chez tous les clients."""
        raise NotImplementedError

    def despawn(self, entity: NetworkEntity) -> None:
        """Supprime une entité chez tous les clients."""
        raise NotImplementedError

    def get_entities(self, cls: type[E] | None = None) -> list[E]:
        """Liste les entités vivantes, éventuellement filtrées par classe."""
        raise NotImplementedError
