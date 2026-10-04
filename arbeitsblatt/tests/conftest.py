import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_tmpdir = tempfile.mkdtemp(prefix="honigbiene-test-")
os.environ["DB_PATH"] = os.path.join(_tmpdir, "test.db")
os.environ["LEHRER_PASSWORD"] = "test-geheim"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GEMINI_API_KEY"] = ""
os.environ["SOCKETIO_ASYNC_MODE"] = "threading"
for _k in ("ISERV_WEBDAV_URL", "ISERV_WEBDAV_USERNAME", "ISERV_WEBDAV_PASSWORD", "ISERV_BACKUP_ENCRYPTION_KEY", "ISERV_CA_BUNDLE"):
    os.environ[_k] = ""

import app as appmodule  # noqa: E402
import db as dbmod  # noqa: E402
import presence  # noqa: E402
from config import ABSCHNITTE, ist_lesestrecke  # noqa: E402

# Echte Stationsnummern des Plans (plan_<reiter>.py) in Planreihenfolge, ohne Lesestrecken. Gerüsttests benutzen NR[i]
# statt fester Nummern, damit sie nicht brechen, wenn die Inhalts-Agenten ihre Stationspläne umbauen.
NR = [n for a in ABSCHNITTE for n in a["aufgaben"] if not ist_lesestrecke(n)]


def frische_sitzung():
    dbmod.clear_live_data()
    dbmod.delete_all_named_snapshots()
    presence.reset()


@pytest.fixture()
def client():
    frische_sitzung()
    appmodule.app.config["TESTING"] = True
    return appmodule.app.test_client()


def anmelden(c, pseudonym="Silberfuchs", klasse="6a"):
    resp = c.post("/login", data={"pseudonym": pseudonym, "klasse": klasse, "privacy_ok": "on"})
    assert resp.status_code == 302, resp.get_data(as_text=True)[:300]
    return c


@pytest.fixture()
def student(client):
    return anmelden(client)


def session_werte(c):
    with c.session_transaction() as s:
        return dict(s)


@pytest.fixture()
def teacher():
    c = appmodule.app.test_client()
    resp = c.post("/lehrer/login", data={"passwort": "test-geheim"})
    assert resp.status_code == 302
    return c


@pytest.fixture()
def teacher_token(teacher):
    return session_werte(teacher)["lehrer_token"]
