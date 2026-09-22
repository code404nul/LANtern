# API publique de LANterne

> Statut : **API cible**, pas encore implémentée. Le fonctionnement interne
> est expliqué dans [ARCHITECTURE.md](ARCHITECTURE.md).

Tout s'importe depuis le paquet principal :

```python
from lanterne import Server, Client, Config, NetworkEntity, replicated
# aussi : Player, PlayerInfo, Phase, ServerBrowser, ServerInfo,
#        DebugOverlay, NetStats, enable_logging
```

Trois règles à retenir :

1. **Côté client**, appelez `client.poll()` une fois par frame. C'est là que
   vos handlers `@client.on(...)` s'exécutent, dans le thread de pygame.
2. **Côté serveur**, les handlers s'exécutent dans le thread du serveur : ils
   doivent être rapides, ne jamais appeler `time.sleep()` et ne jamais
   utiliser pygame.
3. Les données envoyées doivent être sérialisables en JSON : `dict`, `list`,
   `str`, `int`, `float`, `bool`, `None`. Les tuples deviennent des listes et
   les clés de dictionnaire deviennent des chaînes.

---

## Configuration — `lanterne.config`

### `Config`

```python
@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 5050
    discovery_port: int = 5051
    game_id: str = "lanterne"
    server_name: str = "Partie LANterne"
    max_players: int = 8
    use_lobby: bool = True
    allow_join_in_game: bool = False
    discoverable: bool = True
    tick_rate: int = 30
    interpolation_delay: float = 0.08
    heartbeat_interval: float = 1.0
    timeout: float = 5.0
    handshake_timeout: float = 5.0
    max_message_size: int = 1_048_576
    despawn_on_disconnect: bool = True
    sim_latency: float = 0.0
    sim_jitter: float = 0.0
    sim_loss: float = 0.0
```

Rassemble tous les réglages ; passez **la même** configuration au serveur et
aux clients (mettez-la dans un fichier importé par les deux).

| Champ | Signification |
|---|---|
| `host` | Adresse sur laquelle le serveur écoute (`"0.0.0.0"` = toutes les cartes réseau). |
| `port` | Port TCP du jeu. Un **port** est un numéro qui désigne un programme sur une machine. |
| `discovery_port` | Port UDP de la découverte LAN. |
| `game_id` | Nom du jeu : un client d'un autre jeu est refusé. |
| `server_name` | Nom affiché dans la liste des parties. |
| `max_players` | Nombre maximal de joueurs connectés. |
| `use_lobby` | `False` : pas de lobby, la partie démarre tout de suite. |
| `allow_join_in_game` | Autorise les connexions pendant la partie. |
| `discoverable` | Le serveur répond à la découverte LAN. |
| `tick_rate` | Ticks serveur par seconde. |
| `interpolation_delay` | Retard d'affichage côté client, en secondes, pour l'interpolation. |
| `heartbeat_interval` / `timeout` | Fréquence des pings / silence avant déconnexion (s). |
| `handshake_timeout` | Délai pour recevoir `_hello` après la connexion (s). |
| `max_message_size` | Taille maximale d'un message, en octets. |
| `despawn_on_disconnect` | Supprime les entités d'un joueur qui part. |
| `sim_latency`, `sim_jitter` | Retard simulé et sa variation aléatoire (s), pour tester. |
| `sim_loss` | Probabilité (0 à 1) de simuler une perte de paquet (voir ARCHITECTURE §7). |

```python
CONFIG = Config(game_id="pong", max_players=2, tick_rate=20)
```

---

## Serveur — `lanterne.server`

### `Server(config: Config | None = None)`

Serveur qui fait autorité sur la partie ; sans argument, utilise `Config()`.

```python
server = Server(CONFIG)
```

### `Server.start() -> None`

Démarre le serveur dans un thread réseau et rend la main tout de suite (pour
l'hôte d'un listen server).

```python
server.start()
```

### `Server.run() -> None`

Fait tourner le serveur dans le thread courant jusqu'à Ctrl+C (pour un
serveur dédié sans fenêtre).

```python
if __name__ == "__main__":
    server.run()
```

### `Server.stop() -> None`

Envoie `_bye` à tous les joueurs, ferme les connexions et arrête le thread.

```python
server.stop()
```

### `Server.on(msg_type: str)` (décorateur)

Enregistre la fonction appelée avec `(player, data)` quand un client envoie
un message de ce type.

```python
@server.on("shoot")
def handle_shoot(player, data):
    server.broadcast("explosion", {"x": data["x"], "y": data["y"]})
```

### `Server.on_connect(func)` (décorateur)

Appelé avec `(player)` quand un joueur a terminé le handshake.

```python
@server.on_connect
def welcome(player):
    player.send("motd", "Bienvenue " + player.name)
```

### `Server.on_disconnect(func)` (décorateur)

Appelé avec `(player, reason)` quand un joueur part (`"quit"`, `"timeout"`,
`"kicked"`, `"connection_lost"`, `"protocol_error"`).

```python
@server.on_disconnect
def bye(player, reason):
    print(player.name, "est parti :", reason)
```

### `Server.on_game_start(func)` (décorateur)

Appelé sans argument quand la partie passe du lobby au jeu.

```python
@server.on_game_start
def setup():
    server.spawn(Ball)
```

### `Server.on_tick(func)` (décorateur)

Appelé avec `(dt)` à chaque tick de jeu (`dt = 1 / tick_rate` secondes), puis
un snapshot est envoyé.

```python
@server.on_tick
def update(dt):
    for ball in server.get_entities(Ball):
        ball.x += ball.vx * dt
```

### `Server.send(player: Player, msg_type: str, data=None) -> None`

Envoie un message à un seul joueur.

```python
server.send(player, "score", {"value": 10})
```

### `Server.broadcast(msg_type: str, data=None, exclude: Player | None = None) -> None`

Envoie un message à tous les joueurs, sauf `exclude` s'il est donné.

```python
server.broadcast("goal", {"team": "red"}, exclude=player)
```

### `Server.kick(player: Player, reason: str = "kicked") -> None`

Déconnecte un joueur en lui indiquant la raison.

```python
server.kick(player, "triche détectée")
```

### `Server.players -> dict[int, Player]` (propriété)

Joueurs connectés, indexés par leur id.

```python
names = [p.name for p in server.players.values()]
```

### `Server.get_player(player_id: int) -> Player | None`

Renvoie le joueur de cet id, ou `None` s'il n'est plus là.

```python
owner = server.get_player(square.owner_id)
```

### `Server.phase -> Phase` et `Server.tick -> int` (propriétés)

Phase actuelle (`Phase.LOBBY` ou `Phase.GAME`) et numéro du tick courant.

```python
if server.phase is Phase.GAME and server.tick % 30 == 0: ...
```

### `Server.start_game() -> None` / `Server.end_game() -> None`

Lance la partie (normalement déclenché par l'hôte via `client.start_game()`) /
supprime les entités et revient au lobby.

```python
@server.on("all_dead")
def finish(player, data):
    server.end_game()
```

### `Server.spawn(cls: type[NetworkEntity], owner: Player | None = None, **attrs) -> NetworkEntity`

Crée une entité répliquée chez tous les clients, avec des valeurs initiales
optionnelles.

```python
square = server.spawn(Square, owner=player, x=10.0, color=[255, 0, 0])
```

### `Server.despawn(entity: NetworkEntity) -> None`

Supprime une entité chez tous les clients.

```python
server.despawn(bullet)
```

### `Server.get_entities(cls: type[NetworkEntity] | None = None) -> list[NetworkEntity]`

Liste les entités vivantes, éventuellement filtrées par classe.

```python
for bullet in server.get_entities(Bullet): ...
```

### `Player`

Un joueur connecté, vu par le serveur. Créé par la bibliothèque, jamais par
vous.

| Attribut | Type | Description |
|---|---|---|
| `id` | `int` | Identifiant unique attribué par le serveur. |
| `name` | `str` | Pseudo. |
| `ready` | `bool` | A cliqué sur « prêt » dans le lobby. |
| `is_host` | `bool` | Premier joueur connecté ; seul à pouvoir lancer la partie. |
| `input` | `dict` | Dernier état envoyé par `client.set_input()` (non fiable : à valider). |
| `rtt` | `float` | Temps d'aller-retour mesuré, en secondes. |
| `address` | `tuple[str, int]` | IP et port du client. |

### `Player.send(msg_type: str, data=None) -> None`

Raccourci pour `server.send(player, msg_type, data)`.

```python
player.send("you_lose")
```

---

## Client — `lanterne.client`

### `Client(config: Config | None = None)`

Connexion d'un joueur au serveur ; à utiliser depuis la boucle pygame.

```python
client = Client(CONFIG)
```

### `Client.connect(host: str, port: int | None = None, name: str = "Joueur") -> None`

Lance la connexion en arrière-plan et rend la main tout de suite ;
`on_connect` ou `on_disconnect` sera appelé par `poll()` (port par défaut :
`config.port`).

```python
client.connect("192.168.1.42", name="Alice")
```

### `Client.poll() -> None`

À appeler une fois par frame : exécute les handlers des messages reçus et
met à jour les entités (interpolation). Ne bloque jamais.

```python
while running:
    client.poll()
```

### `Client.close() -> None`

Envoie `_bye`, ferme la connexion et arrête le thread réseau.

```python
client.close()
```

### `Client.send(msg_type: str, data=None) -> None`

Envoie un message au serveur sans attendre ; lève `ValueError` si le type
commence par `_`.

```python
client.send("shoot", {"x": 120, "y": 40})
```

### `Client.on(msg_type: str)` (décorateur)

Enregistre la fonction appelée avec `(data)` quand le serveur envoie ce type
de message.

```python
@client.on("score")
def show_score(data):
    print("Score :", data["value"])
```

### `Client.on_connect(func)` / `Client.on_disconnect(func)` (décorateurs)

Appelés sans argument quand le serveur a accepté la connexion / avec
`(reason)` quand la connexion est refusée ou perdue.

```python
@client.on_disconnect
def lost(reason):
    print("Déconnecté :", reason)
```

### `Client.on_lobby_update(func)` (décorateur)

Appelé avec `(players)` (liste de `PlayerInfo`) chaque fois que le lobby
change.

```python
@client.on_lobby_update
def refresh(players):
    print(", ".join(p.name + (" ✔" if p.ready else "") for p in players))
```

### `Client.on_game_start(func)` (décorateur)

Appelé sans argument quand l'hôte lance la partie.

```python
@client.on_game_start
def go():
    global scene
    scene = "game"
```

### `Client.on_chat(func)` (décorateur)

Appelé avec `(player, text)` pour chaque message de chat reçu.

```python
@client.on_chat
def chat(player, text):
    messages.append(f"{player.name}: {text}")
```

### `Client.set_ready(ready: bool = True) -> None`

Indique au serveur que ce joueur est prêt (ou plus prêt) dans le lobby.

```python
client.set_ready(True)
```

### `Client.start_game() -> None`

Demande le lancement de la partie ; ignoré si le joueur n'est pas l'hôte ou
si tout le monde n'est pas prêt.

```python
if client.is_host and start_button_clicked:
    client.start_game()
```

### `Client.chat(text: str) -> None`

Envoie un message de chat (200 caractères max) à tous les joueurs.

```python
client.chat("gg")
```

### `Client.set_input(state: dict) -> None`

Mémorise l'état des commandes du joueur ; il est envoyé au serveur au plus
une fois par tick, et seulement s'il a changé.

```python
keys = pygame.key.get_pressed()
client.set_input({"jump": keys[pygame.K_SPACE]})
```

### `Client.get_entities(cls: type[NetworkEntity] | None = None) -> list[NetworkEntity]`

Liste les entités connues du client, éventuellement filtrées par classe.

```python
for square in client.get_entities(Square):
    pygame.draw.rect(screen, square.color, (square.x, square.y, 40, 40))
```

### Propriétés du client

| Propriété | Type | Description |
|---|---|---|
| `connected` | `bool` | Handshake réussi et connexion ouverte. |
| `player_id` | `int \| None` | Id de ce joueur (après `on_connect`). |
| `is_host` | `bool` | Ce joueur est l'hôte. |
| `players` | `list[PlayerInfo]` | Joueurs de la partie. |
| `phase` | `Phase \| None` | Phase du serveur. |
| `entities` | `dict[int, NetworkEntity]` | Entités par id. |
| `rtt` | `float` | Temps d'aller-retour, en secondes. |
| `stats` | `NetStats` | Statistiques réseau (M4). |

```python
font.render(f"ping : {client.rtt * 1000:.0f} ms", True, "white")
```

---

## Lobby — `lanterne.lobby`

### `PlayerInfo`

```python
@dataclass(frozen=True)
class PlayerInfo:
    id: int
    name: str
    ready: bool
    is_host: bool
```

Description d'un joueur telle que la voient les clients.

```python
me = next(p for p in client.players if p.id == client.player_id)
```

### `Phase`

Énumération `Phase.LOBBY` / `Phase.GAME` : l'étape où en est la partie.

```python
if client.phase is Phase.LOBBY:
    draw_lobby()
```

---

## Découverte LAN — `lanterne.discovery`

### `ServerBrowser(config: Config | None = None)`

Cherche en arrière-plan les parties du réseau local, par broadcast UDP.

```python
browser = ServerBrowser(CONFIG)
```

### `ServerBrowser.start() -> None` / `ServerBrowser.stop() -> None`

Commence / arrête la recherche (une question par seconde).

```python
browser.start()
```

### `ServerBrowser.servers -> list[ServerInfo]` (propriété)

Parties trouvées récemment (celles qui ne répondent plus depuis 3 s
disparaissent). Lecture sûre depuis le thread pygame.

```python
for i, info in enumerate(browser.servers):
    print(i, info.name, f"{info.players}/{info.max_players}")
```

### `ServerInfo`

```python
@dataclass(frozen=True)
class ServerInfo:
    name: str
    host: str
    port: int
    players: int
    max_players: int
    phase: str
```

Une partie trouvée sur le réseau.

```python
client.connect(info.host, info.port, name="Bob")
```

---

## Synchronisation — `lanterne.entity`

### `NetworkEntity`

Classe de base des objets partagés : le serveur les crée avec `spawn()` et
modifie leurs attributs, les clients les reçoivent automatiquement. Chaque
sous-classe doit avoir un nom unique.

| Attribut | Type | Description |
|---|---|---|
| `id` | `int` | Identifiant unique donné par le serveur. |
| `owner_id` | `int \| None` | Id du joueur propriétaire (paramètre `owner` de `spawn()`). |
| `is_mine` | `bool` | Côté client : l'entité appartient à ce joueur. |

```python
class Ball(NetworkEntity):
    x = replicated(0.0, interpolate=True)
    y = replicated(0.0, interpolate=True)
```

### `replicated(default, interpolate: bool = False)`

Déclare un attribut de classe copié du serveur vers les clients ; avec
`interpolate=True` (nombres uniquement), sa valeur est lissée côté client.

```python
class Hero(NetworkEntity):
    hp = replicated(100)
    x = replicated(0.0, interpolate=True)
```

Attention : seule une **affectation** est détectée. `self.color[0] = 5` ne
sera pas envoyé ; écrivez `self.color = [5, 0, 0]`.

---

## Outils — `lanterne.debug`

### `enable_logging(level: str = "INFO", filename: str | None = None) -> None`

Affiche les logs de LANterne dans la console (ou dans un fichier) ; `"DEBUG"`
montre chaque message.

```python
enable_logging("DEBUG")
```

### `DebugOverlay(client: Client, toggle_key: int | None = None)`

Petit panneau de statistiques réseau dessiné par-dessus le jeu ; F3 par
défaut pour l'afficher ou le cacher.

```python
overlay = DebugOverlay(client)
```

### `DebugOverlay.handle_event(event) -> None` / `DebugOverlay.draw(surface) -> None`

À appeler dans la boucle d'événements / après avoir dessiné le jeu.

```python
for event in pygame.event.get():
    overlay.handle_event(event)
...
overlay.draw(screen)
```

### `NetStats`

Statistiques lues par l'overlay, disponibles dans `client.stats` : `rtt`,
`bytes_in_per_s`, `bytes_out_per_s`, `msgs_in_per_s`, `msgs_out_per_s`,
`snapshot_rate`, `entity_count`, `tick`.

```python
print(f"{client.stats.bytes_in_per_s / 1024:.1f} Kio/s")
```

### Simuler un mauvais réseau

Pas de fonction : réglez la configuration.

```python
CONFIG = Config(sim_latency=0.1, sim_jitter=0.02, sim_loss=0.05)
```

---

## Protocole — `lanterne.protocol` (avancé)

Rarement utile dans un jeu, mais exposé pour les tests.

| Nom | Description |
|---|---|
| `PROTOCOL_VERSION: int` | Version du protocole, vérifiée au handshake. |
| `encode(msg_type: str, data=None) -> bytes` | Construit une trame complète (en-tête + JSON). |
| `decode(body: bytes) -> tuple[str, Any]` | Lit le corps JSON d'une trame et renvoie `(type, data)`. |
| `is_reserved(msg_type: str) -> bool` | Vrai si le type commence par `_`. |
| `ProtocolError` | Exception levée pour un message invalide. |

```python
frame = encode("move", {"dx": 1})
assert decode(frame[4:]) == ("move", {"dx": 1})
```

---

## Exemple complet : deux joueurs qui bougent un carré

Lancez `python square.py host` sur le PC de l'hôte, puis
`python square.py 192.168.1.42` (IP de l'hôte) sur l'autre PC. Au premier
lancement, Windows demande d'autoriser Python dans le pare-feu : acceptez pour
les réseaux privés.

```python
import sys
import pygame
from lanterne import Client, Config, NetworkEntity, Server, replicated

CONFIG = Config(game_id="square", use_lobby=False)
SPEED = 200  # pixels par seconde


class Square(NetworkEntity):
    x = replicated(300.0, interpolate=True)
    y = replicated(220.0, interpolate=True)
    color = replicated([255, 255, 255])


server = None
if sys.argv[1] == "host":
    server = Server(CONFIG)

    @server.on_connect
    def create_square(player):
        color = [230, 80, 80] if player.is_host else [80, 140, 230]
        server.spawn(Square, owner=player, color=color)

    @server.on_tick
    def move_squares(dt):  # thread du serveur : pas de pygame ici
        for square in server.get_entities(Square):
            keys = server.get_player(square.owner_id).input
            square.x += (keys.get("right", 0) - keys.get("left", 0)) * SPEED * dt
            square.y += (keys.get("down", 0) - keys.get("up", 0)) * SPEED * dt

    server.start()

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
client = Client(CONFIG)
client.connect("127.0.0.1" if server else sys.argv[1], name="Joueur")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    k = pygame.key.get_pressed()
    client.set_input({"left": k[pygame.K_LEFT], "right": k[pygame.K_RIGHT],
                      "up": k[pygame.K_UP], "down": k[pygame.K_DOWN]})
    client.poll()
    screen.fill("black")
    for square in client.get_entities(Square):
        pygame.draw.rect(screen, square.color, (square.x, square.y, 40, 40))
    pygame.display.flip()
    clock.tick(60)

client.close()
if server:
    server.stop()
pygame.quit()
```
