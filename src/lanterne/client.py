"""Client : connexion d'un joueur au serveur, utilisée depuis la boucle pygame.

Le réseau tourne dans un thread asyncio ; les handlers ``@on`` sont appelés
par ``poll()`` dans le thread principal, où pygame peut être utilisé.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

from .config import Config
from .entity import NetworkEntity
from .lobby import Phase, PlayerInfo

if TYPE_CHECKING:
    from .debug import NetStats

F = TypeVar("F", bound=Callable[..., Any])
E = TypeVar("E", bound=NetworkEntity)


class Client:
    """Connexion d'un joueur au serveur."""

    def __init__(self, config: Config | None = None) -> None:
        """Prépare le client sans se connecter ; ``None`` = ``Config()``."""
        raise NotImplementedError

    # --- Connexion ----------------------------------------------------------

    def connect(self, host: str, port: int | None = None, name: str = "Joueur") -> None:
        """Lance la connexion en arrière-plan et rend la main immédiatement.

        ``on_connect`` ou ``on_disconnect`` sera ensuite appelé par ``poll()``.
        ``port`` vaut ``config.port`` par défaut.
        """
        raise NotImplementedError

    def poll(self) -> None:
        """À appeler à chaque frame : exécute les handlers et interpole les entités."""
        raise NotImplementedError

    def close(self) -> None:
        """Envoie ``_bye``, ferme la connexion et arrête le thread réseau."""
        raise NotImplementedError

    # --- Messages -----------------------------------------------------------

    def send(self, msg_type: str, data: Any = None) -> None:
        """Envoie un message au serveur sans attendre.

        Lève ``ValueError`` si ``msg_type`` est réservé (commence par ``_``).
        """
        raise NotImplementedError

    def on(self, msg_type: str) -> Callable[[F], F]:
        """Décorateur : ``func(data)`` reçoit les messages de ce type."""
        raise NotImplementedError

    def on_connect(self, func: F) -> F:
        """Décorateur : ``func()`` est appelé quand le serveur accepte la connexion."""
        raise NotImplementedError

    def on_disconnect(self, func: F) -> F:
        """Décorateur : ``func(reason)`` est appelé si la connexion est refusée ou perdue."""
        raise NotImplementedError

    def on_lobby_update(self, func: F) -> F:
        """Décorateur : ``func(players)`` est appelé à chaque changement du lobby."""
        raise NotImplementedError

    def on_game_start(self, func: F) -> F:
        """Décorateur : ``func()`` est appelé quand l'hôte lance la partie."""
        raise NotImplementedError

    def on_chat(self, func: F) -> F:
        """Décorateur : ``func(player, text)`` est appelé pour chaque message de chat."""
        raise NotImplementedError

    # --- Lobby --------------------------------------------------------------

    def set_ready(self, ready: bool = True) -> None:
        """Indique au serveur si ce joueur est prêt."""
        raise NotImplementedError

    def start_game(self) -> None:
        """Demande le lancement de la partie (ignoré si l'on n'est pas l'hôte)."""
        raise NotImplementedError

    def chat(self, text: str) -> None:
        """Envoie un message de chat (200 caractères max) à tous les joueurs."""
        raise NotImplementedError

    # --- Synchronisation ----------------------------------------------------

    def set_input(self, state: dict[str, Any]) -> None:
        """Mémorise l'état des commandes ; envoyé au plus une fois par tick, s'il change."""
        raise NotImplementedError

    def get_entities(self, cls: type[E] | None = None) -> list[E]:
        """Liste les entités connues, éventuellement filtrées par classe."""
        raise NotImplementedError

    # --- État ---------------------------------------------------------------

    @property
    def connected(self) -> bool:
        """Vrai si le handshake a réussi et que la connexion est ouverte."""
        raise NotImplementedError

    @property
    def player_id(self) -> int | None:
        """Id de ce joueur, connu après ``on_connect``."""
        raise NotImplementedError

    @property
    def is_host(self) -> bool:
        """Vrai si ce joueur est l'hôte de la partie."""
        raise NotImplementedError

    @property
    def players(self) -> list[PlayerInfo]:
        """Joueurs de la partie, d'après le dernier message de lobby."""
        raise NotImplementedError

    @property
    def phase(self) -> Phase | None:
        """Phase du serveur, ou ``None`` avant la connexion."""
        raise NotImplementedError

    @property
    def entities(self) -> dict[int, NetworkEntity]:
        """Entités connues, indexées par id."""
        raise NotImplementedError

    @property
    def rtt(self) -> float:
        """Temps d'aller-retour vers le serveur, en secondes."""
        raise NotImplementedError

    @property
    def stats(self) -> NetStats:
        """Statistiques réseau (débit, messages, snapshots)."""
        raise NotImplementedError
