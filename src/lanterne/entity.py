"""Entités répliquées : NetworkEntity, attributs replicated(), interpolation."""

from __future__ import annotations

from typing import Any


class Replicated:
    """Descripteur créé par ``replicated()``.

    Côté serveur, chaque affectation marque l'attribut comme modifié pour le
    prochain snapshot. Côté client, la lecture renvoie la valeur interpolée
    si ``interpolate`` est vrai.
    """

    def __init__(self, default: Any, interpolate: bool = False) -> None:
        """Mémorise la valeur par défaut et le mode d'interpolation."""
        raise NotImplementedError

    def __set_name__(self, owner: type, name: str) -> None:
        """Enregistre le nom de l'attribut dans la classe propriétaire."""
        raise NotImplementedError

    def __get__(self, instance: NetworkEntity | None, owner: type) -> Any:
        """Renvoie la valeur de l'attribut pour cette entité."""
        raise NotImplementedError

    def __set__(self, instance: NetworkEntity, value: Any) -> None:
        """Change la valeur ; côté serveur, la marque comme à envoyer."""
        raise NotImplementedError


def replicated(default: Any, interpolate: bool = False) -> Any:
    """Déclare un attribut de classe copié du serveur vers les clients.

    ``default`` doit être sérialisable en JSON (il est copié pour chaque
    entité). ``interpolate=True`` lisse la valeur côté client (nombres
    uniquement).
    """
    raise NotImplementedError


class NetworkEntity:
    """Classe de base des objets partagés entre le serveur et les clients.

    Le serveur les crée avec ``Server.spawn()`` et modifie leurs attributs
    ``replicated`` ; les clients les reçoivent automatiquement. Chaque
    sous-classe est enregistrée sous son nom, qui doit être unique.

    Attributs :
        id: identifiant unique donné par le serveur.
        owner_id: id du joueur propriétaire, ou ``None``.
        is_mine: côté client, vrai si l'entité appartient à ce joueur.
    """

    id: int
    owner_id: int | None
    is_mine: bool

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Enregistre la sous-classe dans le registre des entités."""
        raise NotImplementedError


def get_entity_class(name: str) -> type[NetworkEntity]:
    """Renvoie la sous-classe de ``NetworkEntity`` enregistrée sous ``name``."""
    raise NotImplementedError
