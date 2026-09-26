"""Format des messages : préfixe de longueur + JSON.

Une trame = 4 octets de longueur (entier non signé big-endian) suivis du
corps JSON en UTF-8 : ``{"t": <type>, "d": <données>}``.
Voir docs/ARCHITECTURE.md, section 4.
"""

from __future__ import annotations

import asyncio
import struct
from typing import Any
from json import dumps, loads

PROTOCOL_VERSION = 1
"""Version du protocole, vérifiée pendant le handshake."""

HEADER = struct.Struct("!I")
"""En-tête d'une trame : longueur du corps sur 4 octets, big-endian."""

RESERVED_PREFIX = "_"
"""Les types de message qui commencent par ce préfixe sont réservés à la lib."""

# Types réservés utilisés par la bibliothèque.
HELLO = "_hello"
WELCOME = "_welcome"
REJECT = "_reject"
PING = "_ping"
PONG = "_pong"
BYE = "_bye"
LOBBY = "_lobby"
READY = "_ready"
START = "_start"
CHAT = "_chat"
INPUT = "_input"
SPAWN = "_spawn"
DESPAWN = "_despawn"
SNAPSHOT = "_snapshot"
DISCOVER = "_discover"
ANNOUNCE = "_announce"


class ProtocolError(Exception):
    """Message invalide : JSON cassé, trop gros, enveloppe mal formée…"""


def is_reserved(msg_type: str) -> bool:
    """Indique si ``msg_type`` est réservé à la bibliothèque."""
    return msg_type.startswith(RESERVED_PREFIX)


def encode(msg_type: str, data: Any = None) -> bytes:
    """Construit une trame complète (en-tête + corps JSON) prête à envoyer.

    Lève ``ProtocolError`` si ``data`` n'est pas sérialisable en JSON.
    """
    body = encode_datagram(msg_type, data)
    return HEADER.pack(len(body)) + body


def encode_datagram(msg_type: str, data: Any = None) -> bytes:
    """Encode un message UDP (découverte) : corps JSON seul, sans en-tête."""
    try:
        return dumps(
            {"t": msg_type, "d": data}, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    except (ValueError, TypeError) as e:
        raise ProtocolError(
            f"Data n'est pas sériallisable en JSON car sont types est : {type(data).__name__}"
        ) from e


def decode(body: bytes) -> tuple[str, Any]:
    """Décode le corps JSON d'une trame et renvoie ``(type, données)``.

    Lève ``ProtocolError`` si le corps n'est pas une enveloppe valide.
    """
    try:
        msg = loads(body.decode("utf-8"))
        if not isinstance(msg["t"], str):
            raise ProtocolError(
                f"Le type de la données est invalide. Il doit etre un string, il est {type(msg['t']).__name__}"
            )

        return msg["t"], msg["d"]
    except (KeyError, TypeError, ValueError) as e:
        raise ProtocolError("body est invalide.") from e


async def read_message(reader: asyncio.StreamReader, max_size: int) -> tuple[str, Any]:
    """Lit exactement une trame sur ``reader`` et la décode.

    Lève ``ProtocolError`` si la longueur annoncée est supérieur ou égale à ``max_size``,
    et ``asyncio.IncompleteReadError`` si la connexion se ferme.
    """
    (body_size,) = HEADER.unpack(await reader.readexactly(HEADER.size))
    if body_size >= max_size:
        raise ProtocolError(
            f"Header invalide, taile actuelle : {body_size} et la taille doit être strictement en dessous de {max_size}"
        )
    return decode(await reader.readexactly(body_size))
