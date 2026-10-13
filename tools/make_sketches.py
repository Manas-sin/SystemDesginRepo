"""Builds every diagrams/*.excalidraw file from the sketch definitions below,
then embeds them into the pages (see embed_sketches.py).

    python3 tools/make_sketches.py

Each sketch is plain data: boxes, text, arrows, badges and sticky notes.
The output opens in excalidraw.com (menu → Open) and is drawn on the site
by js/sketch.js, so the editable file and the page always match."""
import json, os, random, textwrap, time, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "diagrams")
random.seed(7)
TS = int(time.time() * 1000)

INK, GRAY, BLUE_TXT, RED_TXT, TEAL_TXT = "#1e1e1e", "#868e96", "#1971c2", "#e03131", "#0b7285"
BLUE, YELLOW, GREEN, RED, ORANGE, VIOLET, LIGHT = "#a5d8ff", "#ffec99", "#b2f2bb", "#ffc9c9", "#ffd8a8", "#d0bfff", "#e9ecef"


class Sketch:
    """Coordinates you pass in start just below the title; Y shifts them down."""

    def __init__(self, title, subtitle):
        self.items = []
        self.Y = 100
        self.items.append(dict(t="text", x=0, y=0, lines=[title], size=28, align="left", color=INK, g=None))
        self.items.append(dict(t="text", x=0, y=42, lines=[subtitle], size=16, align="left", color=GRAY, g=None))

    def box(self, name, x, y, w, h, fill, lines, dashed=False, size=15):
        self.items.append(dict(t="rect", x=x, y=self.Y + y, w=w, h=h, fill=fill, dashed=dashed, g=name))
        th = len(lines) * size * 1.25
        self.items.append(dict(t="text", x=x + w / 2, y=self.Y + y + (h - th) / 2, lines=lines, size=size, align="center", color=INK, g=name))

    def text(self, x, y, lines, size=13, align="left", color=GRAY):
        if isinstance(lines, str):
            lines = [lines]
        self.items.append(dict(t="text", x=x, y=self.Y + y, lines=lines, size=size, align=align, color=color, g=None))

    def arrow(self, pts, dashed=False, label=None, lx=0, ly=0, anchor="middle", color=INK, double=False, head=True):
        self.items.append(dict(t="arrow", pts=[[x, self.Y + y] for x, y in pts], dashed=dashed, color=color,
                               double=double, head=head,
                               label=None if label is None else dict(x=lx, y=self.Y + ly, text=label, anchor=anchor)))

    def line(self, pts, color="#adb5bd"):
        self.arrow(pts, color=color, head=False)

    def badge(self, cx, cy, n):
        self.items.append(dict(t="badge", x=cx, y=self.Y + cy, n=n))

    def notes(self, y, items, w=215, gap=10, size=13):
        """items: list of (title, body). Bodies are word-wrapped to the note width."""
        chars = int((w - 20) / (size * 0.5))
        wrapped = [[t] + textwrap.wrap(b, chars) for t, b in items]
        h = (max(len(l) for l in wrapped)) * size * 1.25 + 18
        for i, lines in enumerate(wrapped):
            x = i * (w + gap)
            g = f"note{i+1}"
            self.items.append(dict(t="rect", x=x, y=self.Y + y, w=w, h=h, fill=YELLOW, dashed=False, g=g))
            self.items.append(dict(t="text", x=x + 10, y=self.Y + y + 9, lines=lines, size=size, align="left", color=INK, g=g))


# ------------------------------------------------------------------ approach
def approach_route():
    s = Sketch("How to tackle any system design question",
               "45 minutes · go in order · say each step out loud · always finish on trade-offs")
    s.Y = 90
    steps = [
        ("1 · Clarify requirements", "5 min",
         ["Features: what must it do?", "Targets: users, latency,", "availability, consistency.", "Ask — don't assume."],
         ["Say: “Is it read-heavy or", "write-heavy? How many", "daily users?”"]),
        ("2 · Estimate", "5 min",
         ["Back-of-the-envelope:", "DAU → QPS → storage →", "bandwidth. It justifies", "every later choice."],
         ["Say: “100M DAU × 10 req", "÷ 86,400 s ≈ 12k QPS;", "peak is 3× that.”"]),
        ("3 · Define the API", "3 min",
         ["3–5 endpoints, with inputs", "and outputs. Pins down", "exactly what the system", "must do."],
         ["Say: “POST /upload → id;", "GET /file/{id}.”"]),
        ("4 · Data model", "5 min",
         ["Main entities and keys.", "SQL or NoSQL — and why.", "Note the indexes you", "will need."],
         ["Say: “Users and orders are", "relational → SQL; the", "event log → NoSQL.”"]),
        ("5 · High-level design", "10 min",
         ["Draw the boxes (picture", "below). Walk one request", "through them, end to end."],
         ["Say: “Client → LB → API →", "cache → DB. Files to S3,", "slow work to a queue.”"]),
        ("6 · Deep dive", "12 min",
         ["Pick 1–2 boxes that matter", "most for THIS question:", "replication, failover,", "sharding, caching, hot keys,", "real-time push."],
         ["Say: “The DB is the only", "stateful piece — here is", "how it survives a crash.”"]),
        ("7 · Bottlenecks & trade-offs", "5 min",
         ["Single points of failure,", "10× load, back-pressure,", "monitoring. Name the CAP", "trade-off you chose."],
         ["Say: “For the feed I chose", "availability over strict", "consistency, because…”"]),
        ("You should end with", "",
         ["• features + numbers", "• an API", "• a schema", "• one picture", "• one deep dive", "• the trade-offs you chose"],
         []),
    ]
    BW, BH, GAP = 270, 250, 40
    pos = [(0, 0), (310, 0), (620, 0), (930, 0), (0, 320), (310, 320), (620, 320), (930, 320)]
    for i, ((title, mins, body, say), (x, y)) in enumerate(zip(steps, pos)):
        g = f"step{i+1}"
        s.items.append(dict(t="rect", x=x, y=s.Y + y, w=BW, h=BH, fill=LIGHT if i == 7 else BLUE, dashed=False, g=g))
        s.items.append(dict(t="text", x=x + 14, y=s.Y + y + 12, lines=[title], size=17, align="left", color=INK, g=g))
        if mins:
            s.items.append(dict(t="text", x=x + 14, y=s.Y + y + 36, lines=["⏱ " + mins], size=12, align="left", color=GRAY, g=g))
        s.items.append(dict(t="text", x=x + 14, y=s.Y + y + 60, lines=body, size=14, align="left", color=INK, g=g))
        if say:
            s.items.append(dict(t="text", x=x + 14, y=s.Y + y + BH - 14 - len(say) * 14 * 1.25, lines=say, size=14, align="left", color=BLUE_TXT, g=g))
    for i in range(7):
        if i == 3:
            continue
        x, y = pos[i]
        s.arrow([[x + BW, y + BH / 2], [x + BW + GAP, y + BH / 2]])
    s.arrow([[930 + BW / 2, BH], [930 + BW / 2, 285], [BW / 2, 285], [BW / 2, 320]])
    return s


def approach_picture():
    s = Sketch("The picture to draw in step 5",
               "Numbers point to the notes at the bottom. L19–L22 are the lesson notes on this site.")
    s.box("orch", 470, 30, 180, 60, RED, ["Orchestrator (leader)"])
    s.box("cdn", 230, 30, 150, 60, VIOLET, ["CDN"])
    s.box("client", 0, 190, 150, 80, BLUE, ["Client", "(web / mobile)"])
    s.box("lb", 230, 190, 150, 80, LIGHT, ["Load balancer"])
    s.box("api", 470, 180, 180, 100, BLUE, ["API servers × N", "(stateless)"])
    s.box("ws", 470, 330, 180, 70, BLUE, ["WebSocket", "gateway"])
    s.box("cache", 740, 60, 160, 70, ORANGE, ["Cache (Redis)"])
    s.box("db", 740, 190, 160, 80, GREEN, ["Database", "(main)"])
    s.box("rep", 960, 190, 160, 80, GREEN, ["Standby", "replica"], dashed=True)
    s.box("bak", 1180, 190, 160, 80, LIGHT, ["Backups", "(other region)"], dashed=True)
    s.box("queue", 740, 330, 160, 70, LIGHT, ["Queue"])
    s.box("work", 960, 330, 160, 70, BLUE, ["Workers"])
    s.box("s3", 740, 470, 160, 80, VIOLET, ["Blob storage", "(S3)"])
    s.arrow([[150, 230], [230, 230]])
    s.arrow([[75, 190], [75, 160], [305, 160], [305, 90]], label="static files", lx=190, ly=144)
    s.arrow([[380, 230], [470, 230]])
    s.arrow([[305, 270], [305, 365], [470, 365]])
    s.arrow([[560, 90], [560, 180]], dashed=True, label="watches, restarts", lx=572, ly=132, anchor="start")
    s.arrow([[650, 205], [740, 100]], label="hot reads", lx=712, ly=142, anchor="start")
    s.arrow([[650, 230], [740, 230]], label="cache miss", lx=695, ly=212)
    s.arrow([[900, 230], [960, 230]], label="replicate", lx=930, ly=210)
    s.arrow([[1120, 230], [1180, 230]], dashed=True, label="backup", lx=1150, ly=210)
    s.arrow([[650, 255], [740, 365]], label="slow work", lx=712, ly=314, anchor="start")
    s.arrow([[900, 365], [960, 365]])
    s.arrow([[980, 330], [980, 300], [820, 300], [820, 270]])
    s.arrow([[650, 270], [740, 470]], label="signs upload URLs", lx=735, ly=424, anchor="start")
    s.arrow([[75, 270], [75, 600], [820, 600], [820, 550]], dashed=True,
            label="file bytes go straight to S3 with a pre-signed URL — never through the API", lx=450, ly=582)
    for cx, cy, n in [(646, 176, 1), (646, 326, 2), (646, 26, 3), (896, 186, 4), (896, 466, 5), (376, 26, 5), (896, 326, 6)]:
        s.badge(cx, cy, n)
    s.notes(650, [
        ("① L19 · Stateless servers", "Any server can take any request. One dies → the others carry on. Only the database holds state."),
        ("② L21 · Live updates", "HTTP: client asks each time (keep-alive reuses the TCP connection). WebSocket: one open connection, server pushes."),
        ("③ L20 · Auto-recovery", "A leader watches servers and restarts dead ones. If the leader dies, the rest elect a new leader — no human."),
        ("④ L19 · The stateful piece", "Main + standby replica: main dies → replica is promoted. Backups in another region undo mistakes and disasters."),
        ("⑤ L22 · Files", "Bytes go to S3, not the DB. Client uploads straight to S3 with a pre-signed URL. CDN serves files near users."),
        ("⑥ Queue + workers", "Slow or bursty work leaves the request path. Workers retry. If they fall behind, the queue grows — watch it."),
    ])
    return s


# ----------------------------------------------------------------- lesson 19
def lesson19():
    s = Sketch("Lesson 19 · Data redundancy & recovery",
               "Stateless servers are replaceable. The database is the one copy of the truth — so make more copies of it.")
    s.box("users", 0, 150, 130, 70, BLUE, ["Users"])
    s.box("lb", 200, 150, 150, 70, LIGHT, ["Load balancer"])
    s.box("api1", 430, 60, 160, 50, BLUE, ["API server 1"])
    s.box("api2", 430, 160, 160, 50, RED, ["API server 2 ✕"], dashed=True)
    s.box("api3", 430, 260, 160, 50, BLUE, ["API server 3"])
    s.box("db", 720, 150, 170, 80, GREEN, ["Database", "(main)"])
    s.box("rep", 980, 150, 170, 80, GREEN, ["Standby replica", "(live copy)"], dashed=True)
    s.box("bak", 720, 330, 170, 90, YELLOW, ["Backup files", "daily changes +", "weekly full"])
    s.box("reg", 980, 330, 170, 90, LIGHT, ["Copy in another", "region"], dashed=True)
    s.arrow([[130, 185], [200, 185]])
    s.arrow([[350, 185], [430, 85]])
    s.arrow([[350, 185], [430, 185]], dashed=True, color=RED_TXT)
    s.arrow([[350, 185], [430, 285]])
    s.arrow([[590, 85], [720, 180]])
    s.arrow([[590, 285], [720, 200]])
    s.arrow([[890, 190], [980, 190]])
    s.text(935, 160, ["replicate", "async / sync"], align="center")
    s.arrow([[805, 230], [805, 330]], label="dump every night", lx=815, ly=268, anchor="start")
    s.arrow([[890, 375], [980, 375]], dashed=True, label="weekly copy", lx=935, ly=356)
    s.text(1065, 240, "main dies → promote me (failover, ~1 min)", color=BLUE_TXT, align="center")
    s.text(795, 252, "what if this disk dies?", color=RED_TXT, align="right")
    for cx, cy, n in [(586, 56, 1), (886, 146, 2), (1146, 146, 3), (886, 326, 4), (1146, 326, 5)]:
        s.badge(cx, cy, n)
    s.notes(470, [
        ("① Stateless API servers", "One dies → the others carry on. Add more any time. Nothing here needs protecting."),
        ("② Stateful database", "The only copy of the truth. If its disk dies the data is gone — unless you made copies."),
        ("③ Standby replica", "Live copy, seconds behind. Main dies → promote it (failover, about a minute). Costs a second server."),
        ("④ Backups", "Daily changes + weekly full. Cheap. Restore takes minutes to hours and loses writes since the last backup."),
        ("⑤ Another region", "One copy far away survives a flood or fire in the data centre. This is disaster recovery."),
        ("⑥ Why both", "A replica copies mistakes (DROP TABLE) in a second; only a backup goes back in time. RPO = data lost, RTO = time down."),
    ])
    return s


# ----------------------------------------------------------------- lesson 20
def lesson20():
    s = Sketch("Lesson 20 · Leader election for auto-recovery",
               "Who restarts a dead server? A worker. A dead worker? The leader. A dead leader? The workers — by election.")
    s.text(75, 28, "SERVERS", align="center")
    s.text(405, 28, "ORCHESTRATOR WORKERS", align="center")
    s.text(785, 28, "LEADER", align="center")
    s.box("sv1", 0, 60, 150, 50, LIGHT, ["Server 1"])
    s.box("sv2", 0, 160, 150, 50, RED, ["Server 2 ✕"], dashed=True)
    s.box("sv3", 0, 260, 150, 50, LIGHT, ["Server 3"])
    s.box("w1", 330, 60, 150, 50, GREEN, ["Worker 1"])
    s.box("w2", 330, 160, 150, 50, GREEN, ["Worker 2"])
    s.box("w3", 330, 260, 150, 50, BLUE, ["Worker 3"])
    s.box("old", 700, 60, 170, 60, RED, ["Leader ✕", "(crashed)"], dashed=True)
    s.box("new", 700, 250, 170, 60, BLUE, ["New leader", "(was worker 3)"])
    s.box("coord", 1000, 130, 220, 100, VIOLET, ["Coordination service", "(etcd / ZooKeeper)", "3 or 5 nodes · majority"])
    s.arrow([[330, 85], [150, 85]], label="ping: healthy?", lx=240, ly=66)
    s.arrow([[330, 185], [150, 185]], dashed=True, color=RED_TXT, label="no reply → replace it", lx=240, ly=166)
    s.arrow([[330, 285], [150, 285]])
    s.text(785, 128, "heartbeats stopped → timeout", color=RED_TXT, align="center")
    s.arrow([[480, 285], [700, 285]], label="ELECTION: promoted", lx=590, ly=266, color=BLUE_TXT)
    s.arrow([[700, 262], [600, 262], [600, 85], [480, 85]], dashed=True, color=BLUE_TXT, label="watches workers", lx=590, ly=66)
    s.arrow([[600, 185], [480, 185]], dashed=True, color=BLUE_TXT)
    s.arrow([[870, 280], [1000, 200]], label="holds the lease (renews every few s)", lx=890, ly=306, anchor="start")
    for cx, cy, n in [(476, 56, 1), (866, 246, 2), (866, 56, 3), (476, 256, 4), (1216, 126, 5), (1216, 160, 6)]:
        s.badge(cx, cy, n)
    s.notes(380, [
        ("① Workers watch servers", "Ping every few seconds. Dead server → start a new one and put it behind the load balancer."),
        ("② Leader watches workers", "Dead worker → start a new worker. Leader and workers run the same code; leader is just a role."),
        ("③ Heartbeat + timeout", "Leader says 'alive' every ~1 s. Silence past the timeout = presumed dead. Too short: false alarms. Too long: slow recovery."),
        ("④ Election", "Workers pick one of themselves (Bully: biggest alive ID wins). Nobody outside the group is needed — the chain ends here."),
        ("⑤ Split brain", "A network split can create two leaders. Rule: leader only with a majority (3 of 5). Use odd group sizes."),
        ("⑥ In practice", "Don't write it. Take a lease (a lock with an expiry) in etcd / ZooKeeper / Consul. Renewals = heartbeat, expiry = timeout."),
    ])
    return s


# ----------------------------------------------------------------- lesson 21
def lesson21():
    s = Sketch("Lesson 21 · Client-server model & communication protocols",
               "A · one connection, step by step (read top to bottom).   B · the boxes for live updates.")
    s.text(20, -22, "A · One connection, step by step", size=15, color=INK)
    s.text(760, -22, "B · Live updates: the boxes", size=15, color=INK)
    s.box("c", 20, 0, 160, 44, BLUE, ["Client (browser / app)"])
    s.box("sv", 380, 0, 160, 44, BLUE, ["Server"])
    s.line([[100, 44], [100, 470]])
    s.line([[460, 44], [460, 470]])
    msgs = [  # (y, direction, label)
        (80, ">", "SYN"), (108, "<", "SYN-ACK"), (136, ">", "ACK"),
        (185, ">", "GET /orders   (HTTP)"), (213, "<", "200 OK + JSON"),
        (255, ">", "GET /orders/7"), (283, "<", "200 OK"),
        (330, ">", "GET /chat   Upgrade: websocket"), (358, "<", "101 Switching Protocols"),
        (405, "=", "messages both ways, any time"),
        (450, ">", "FIN … ACK  (close)"),
    ]
    for y, d, label in msgs:
        if d == ">":
            s.arrow([[100, y], [460, y]], label=label, lx=280, ly=y - 18)
        elif d == "<":
            s.arrow([[460, y], [100, y]], label=label, lx=280, ly=y - 18)
        else:
            s.arrow([[100, y], [460, y]], double=True, label=label, lx=280, ly=y - 18, color=BLUE_TXT)
    s.text(485, 86, ["① TCP handshake", "1 round trip (TLS adds 1–2)"])
    s.text(485, 225, ["② keep-alive: same connection,", "no new handshake"])
    s.text(485, 336, ["③ upgrade once"])
    s.text(485, 396, ["④ WebSocket: server can push"], color=BLUE_TXT)
    # part B
    s.box("clients", 760, 40, 150, 60, BLUE, ["Clients"])
    s.box("lb", 760, 150, 150, 60, LIGHT, ["Load balancer"])
    s.box("api", 960, 40, 180, 60, BLUE, ["API servers", "(HTTP · stateless)"])
    s.box("ws", 960, 150, 180, 70, ORANGE, ["WebSocket gateways", "(stateful: hold", "connections)"], size=14)
    s.box("db", 1200, 40, 140, 60, GREEN, ["Database"])
    s.box("ps", 1200, 150, 140, 70, VIOLET, ["Pub/sub", "(Redis)"])
    s.arrow([[835, 100], [835, 150]])
    s.arrow([[910, 180], [960, 70]], label="HTTP", lx=925, ly=108, anchor="start")
    s.arrow([[910, 185], [960, 185]], label="ws:// (sticky)", lx=955, ly=214, anchor="end")
    s.arrow([[1140, 70], [1200, 70]], label="read / write", lx=1170, ly=52)
    s.arrow([[1140, 80], [1200, 170]], label="publish event", lx=1150, ly=116, anchor="start")
    s.arrow([[1200, 195], [1140, 195]], label="push to connected users", lx=1170, ly=228)
    s.notes(500, [
        ("① TCP first", "Every connection starts with a 3-message handshake: one round trip (TLS adds 1–2). Opening connections is the expensive part."),
        ("② Reuse the connection", "HTTP/1.1 keeps it open (keep-alive). HTTP/2 lets many requests share one connection at the same time."),
        ("③ WebSocket", "Starts as HTTP, upgrades once (101), then both sides send any time. For chat, live scores — anything the server must push often."),
        ("④ Gateways are stateful", "A user is attached to one gateway. Fan out through pub/sub so any API server can reach any connected user."),
        ("⑤ Pick the method", "Rare updates: short polling. Server-only push: SSE. Both ways, instant: WebSocket. Long polling: the fallback."),
        ("⑥ Protocol = agreed format", "HTTP, Redis's RESP and gRPC all ride on TCP. UDP only for live audio / video, where late data is useless."),
    ])
    return s


# ----------------------------------------------------------------- lesson 22
def lesson22():
    s = Sketch("Lesson 22 · Blob storage & S3",
               "Files are bytes. Bytes go to blob storage; the database keeps one small row per file. Follow the numbers.")
    s.box("client", 0, 150, 150, 80, BLUE, ["Client", "(web / mobile)"])
    s.box("api", 330, 150, 170, 80, BLUE, ["API servers", "(stateless)"])
    s.box("db", 315, 330, 200, 90, GREEN, ["Database", "one row per file:", "owner · key · size · status"], size=14)
    s.box("s3", 680, 150, 200, 90, VIOLET, ["Blob storage (S3)", "bucket / key"])
    s.box("cdn", 680, 20, 200, 60, VIOLET, ["CDN (edge cache)"])
    s.box("std", 1000, 150, 150, 60, LIGHT, ["Standard"])
    s.box("ia", 1000, 250, 150, 60, LIGHT, ["Infrequent access"])
    s.box("gl", 1000, 350, 150, 60, LIGHT, ["Glacier (archive)"])
    s.text(1075, 120, "Lifecycle rules", align="center")
    s.text(1075, 436, "delete", align="center")
    s.arrow([[150, 175], [330, 175]], label="① ask: upload URL for photo.jpg", lx=240, ly=132)
    s.arrow([[330, 205], [150, 205]], label="② pre-signed URL (5 min)", lx=240, ly=214)
    s.arrow([[75, 230], [75, 300], [780, 300], [780, 240]], label="③ PUT the bytes straight to S3 (multipart if large)", lx=430, ly=282)
    s.arrow([[415, 230], [415, 330]], label="④ after upload: save the row", lx=425, ly=244, anchor="start")
    s.arrow([[780, 150], [780, 80]], dashed=True, label="⑤ first read fetches from S3", lx=790, ly=104, anchor="start")
    s.arrow([[75, 150], [75, 50], [680, 50]], label="⑥ downloads go via the CDN  (GET cdn…/photo.jpg)", lx=380, ly=30)
    s.arrow([[880, 195], [1000, 180]], label="stored in a class", lx=940, ly=160)
    s.arrow([[1075, 210], [1075, 250]], dashed=True, label="after 30 days", lx=1085, ly=218, anchor="start")
    s.arrow([[1075, 310], [1075, 350]], dashed=True, label="after 1 year", lx=1085, ly=318, anchor="start")
    s.arrow([[1075, 410], [1075, 432]], dashed=True)
    s.notes(480, [
        ("① Blob = any file as bytes", "Images, video, PDFs, backups. The database keeps only a small row about each file, never the bytes."),
        ("② Not the server's disk", "Servers must stay stateless. A file on server 1 is invisible to server 2 and dies with that disk."),
        ("③ Bucket + key", "Bucket = top-level container. Key = the full name, like a path. Use a generated ID as the key; the real file name goes in the DB row."),
        ("④ Pre-signed URL", "A temporary link made by your API: one action, one key, a few minutes. The bytes never pass through the API."),
        ("⑤ Durable ≠ available", "11 nines durability (won't be lost) vs 99.99% availability (~53 min a year unreachable). Reads are slow-ish → CDN in front."),
        ("⑥ Lifecycle + versioning", "Standard → Infrequent → Glacier → delete. Colder = cheaper to keep, slower and pricier to read. Versioning undoes mistakes."),
    ])
    return s


# ---------------------------------------------------------- excalidraw output
def nonce():
    return random.randint(1, 2 ** 31 - 1)


def el(kind, x, y, w, h, **k):
    e = dict(id=f"e{nonce():x}", type=kind, x=x, y=y, width=w, height=h, angle=0,
             strokeColor=INK, backgroundColor="transparent", fillStyle="solid",
             strokeWidth=2, strokeStyle="solid", roughness=1, opacity=100,
             groupIds=[], frameId=None, roundness=None, seed=nonce(), version=1,
             versionNonce=nonce(), isDeleted=False, boundElements=[], updated=TS,
             link=None, locked=False)
    e.update(k)
    return e


def ex_text(x, y, lines, size, align, color, g):
    t = "\n".join(lines)
    w = max(len(l) for l in lines) * size * 0.55
    h = len(lines) * size * 1.25
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    return el("text", x, y, w, h, text=t, originalText=t, fontSize=size, fontFamily=5,
              textAlign=align, verticalAlign="top", containerId=None, lineHeight=1.25,
              autoResize=True, strokeColor=color, groupIds=[g] if g else [])


def to_excalidraw(items):
    out = []
    for it in items:
        if it["t"] == "rect":
            out.append(el("rectangle", it["x"], it["y"], it["w"], it["h"], backgroundColor=it["fill"],
                          roundness={"type": 3}, strokeStyle="dashed" if it["dashed"] else "solid",
                          groupIds=[it["g"]] if it["g"] else []))
        elif it["t"] == "text":
            out.append(ex_text(it["x"], it["y"], it["lines"], it["size"], it["align"], it["color"], it["g"]))
        elif it["t"] == "arrow":
            pts = it["pts"]
            x0, y0 = pts[0]
            rel = [[px - x0, py - y0] for px, py in pts]
            xs = [p[0] for p in rel]; ys = [p[1] for p in rel]
            out.append(el("arrow" if it["head"] else "line", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
                          points=rel, lastCommittedPoint=None, startBinding=None, endBinding=None,
                          startArrowhead="arrow" if it["double"] else None,
                          endArrowhead="arrow" if it["head"] else None, elbowed=False,
                          roundness={"type": 2} if len(pts) == 2 else None,
                          strokeColor=it["color"], strokeStyle="dashed" if it["dashed"] else "solid"))
            if it["label"]:
                lb = it["label"]
                out.append(ex_text(lb["x"], lb["y"], [lb["text"]], 13,
                                   {"middle": "center", "start": "left", "end": "right"}[lb["anchor"]], GRAY, None))
        elif it["t"] == "badge":
            g = f"badge{nonce():x}"
            out.append(el("ellipse", it["x"] - 13, it["y"] - 13, 26, 26, backgroundColor=RED, groupIds=[g]))
            out.append(ex_text(it["x"], it["y"] - 8, [str(it["n"])], 13, "center", INK, g))
    return out


SKETCHES = {
    "approach-route": approach_route,
    "approach-picture": approach_picture,
    "19-data-redundancy-recovery": lesson19,
    "20-leader-election": lesson20,
    "21-client-server-protocols": lesson21,
    "22-blob-storage-s3": lesson22,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, build in SKETCHES.items():
        doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
               "elements": to_excalidraw(build().items),
               "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"}, "files": {}}
        with open(os.path.join(OUT, name + ".excalidraw"), "w") as f:
            json.dump(doc, f, indent=1, ensure_ascii=False)
        print(f"wrote diagrams/{name}.excalidraw ({len(doc['elements'])} elements)")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "embed_sketches.py")], check=True)
