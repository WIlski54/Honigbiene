"""Live-Verbindung hinter Coolify/Traefik.

TLS endet am Proxy. Bei einem WebSocket-Upgrade meldet Traefik der App
„X-Forwarded-Proto: wss“ – die Standardprüfung von Engine.IO erlaubt dann nur
„http://host“ und „wss://host“ und lehnt den Browser (Origin „https://host“) mit
„Not an accepted origin.“ ab. Folge im Unterricht: Das Dashboard bekam keine
Live-Meldungen, wartende Lernende der Fortsetzungsstunde tauchten nie auf.
"""

import app as appmodule

HOST = "honigbiene.example.org"
HANDSHAKE = "/socket.io/?EIO=4&transport=polling"


def _handshake(origin, proto=None, host=HOST):
    headers = {"Host": host, "Origin": origin}
    if proto:
        headers["X-Forwarded-Proto"] = proto
    return appmodule.app.test_client().get(HANDSHAKE, headers=headers)


def test_browser_hinter_tls_proxy_wird_beim_websocket_upgrade_angenommen(client):
    r = _handshake(f"https://{HOST}", proto="wss")
    assert r.status_code == 200, r.get_data(as_text=True)


def test_normale_anfrage_hinter_tls_proxy_und_lokal(client):
    assert _handshake(f"https://{HOST}", proto="https").status_code == 200
    assert _handshake("http://localhost:5000", host="localhost:5000").status_code == 200


def test_fremde_seite_bleibt_ausgesperrt(client):
    """Schutz gegen Cross-Site-WebSocket-Hijacking: nur Seiten dieses Hosts."""
    for origin in ("https://boese.example", f"https://{HOST}.boese.example", "null", f"ftp://{HOST}"):
        assert _handshake(origin, proto="wss").status_code == 400, origin
