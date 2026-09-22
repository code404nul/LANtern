"""Interne : boucle asyncio exécutée dans un thread secondaire.

Ce module ne fait pas partie de l'API publique.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from collections.abc import Callable, Coroutine
from typing import Any

from .config import Config


class NetworkThread:
    """Thread qui fait tourner une boucle asyncio dédiée au réseau.

    Le thread principal (pygame) ne l'utilise que via ``submit()`` et
    ``call_soon()``, qui sont thread-safe.
    """

    def __init__(self, name: str, config: Config) -> None:
        """Prépare le thread sans le démarrer ; ``name`` sert dans les logs."""
        raise NotImplementedError

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Boucle asyncio du thread (disponible après ``start()``)."""
        raise NotImplementedError

    def start(self) -> None:
        """Démarre le thread et attend que sa boucle soit prête."""
        raise NotImplementedError

    def stop(self, timeout: float = 2.0) -> None:
        """Annule les tâches, arrête la boucle et attend la fin du thread."""
        raise NotImplementedError

    def submit(self, coro: Coroutine[Any, Any, Any]) -> concurrent.futures.Future:
        """Planifie une coroutine dans la boucle depuis n'importe quel thread."""
        raise NotImplementedError

    def call_soon(self, func: Callable[..., Any], *args: Any) -> None:
        """Planifie un appel de fonction dans la boucle depuis n'importe quel thread."""
        raise NotImplementedError

    def delayed_write(self, writer: asyncio.StreamWriter, frame: bytes) -> None:
        """Écrit une trame en appliquant la simulation de latence/perte.

        À appeler depuis la boucle. Sans simulation, écrit immédiatement.
        L'ordre des trames est toujours conservé.
        """
        raise NotImplementedError
