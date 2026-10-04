"""Browserprobe für die Forschen-Typen: startet das Arbeitsblatt mit den Test-Fixtures statt der echten Inhalte.

    python werkzeuge/qa_forschen.py            # http://forschen.localhost:5085  (Wegwerf-DB, KI aus)
    DB_PATH=<Wegwerf>.db PORT=5085 python werkzeuge/qa_forschen.py

Was passiert (nichts davon verändert Dateien des Projekts):
  * Die fünf plan_<reiter>.py werden im Arbeitsspeicher durch die Stationspläne aus tests/fixtures_forschen.js ersetzt
    (Aufgaben 901–913, die Lesestrecke steht mitten in der Liste, am Ende und oben – genau das, was getestet werden soll).
  * index.html bekommt statt der fünf inhalte_<reiter>.js nur /qa-forschen/inhalte.js (= die Fixtures als INHALTE.tabs).
  * Lesestrecken, Glossar, Film und 3D-Modell sind die echten.
Zwei Hosts, weil Cookies pro Host gelten (nie 127.0.0.1 benutzen):
  Schüler  http://forschen.localhost:5085/login
  Lehrkraft http://lehrer-forschen.localhost:5085   (Cookie: python werkzeuge/lehrer_api.py cookie, mit QA_BASE_URL und demselben DB_PATH)
Port 5060/5061 sind im Browser gesperrt. Lehrkraft nie über das Passwortformular.
"""
import json
import os
import re
import subprocess
import sys
import types

HIER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HIER)
sys.path.insert(0, HIER)
import qa_umgebung  # noqa: E402

os.environ.setdefault("PORT", "5085")
qa_umgebung.setzen()
sys.path.insert(0, ROOT)

FIXTURES = os.path.join(ROOT, "tests", "fixtures_forschen.js")


def _fixture_plan() -> dict:
    """Die Stationspläne aus den Fixtures (über Node als JSON)."""
    code = ("const vm=require('vm'),fs=require('fs');const c={window:{}};vm.createContext(c);"
            f"vm.runInContext(fs.readFileSync({json.dumps(FIXTURES)},'utf8'),c);"
            "process.stdout.write(JSON.stringify(c.window.FORSCHEN_FIXTURES.plan));")
    return json.loads(subprocess.run(["node", "-e", code], capture_output=True, text=True, encoding="utf-8", check=True).stdout)


def _fake_plaene() -> None:
    for key, p in _fixture_plan().items():
        modul = types.ModuleType(f"plan_{key}")
        modul.STATIONEN = [int(n) if str(n).isdigit() else n for n in p["STATIONEN"]]
        modul.TYPEN = {int(n) if str(n).isdigit() else n: t for n, t in p["TYPEN"].items()}
        sys.modules[f"plan_{key}"] = modul


_fake_plaene()
import jinja2  # noqa: E402

import app as ab  # noqa: E402
from flask import Response  # noqa: E402


class _IndexUmbau(jinja2.BaseLoader):
    """Liefert index.html mit den Fixtures statt der echten Inhaltsdateien."""

    def __init__(self, innen):
        self.innen = innen

    def get_source(self, environment, template):
        quelle, name, aktuell = self.innen.get_source(environment, template)
        if template == "index.html":
            quelle = re.sub(r"\s*<script src=\"\{\{ url_for\('static', filename='js/inhalte_[a-z]+\.js', v=v\) \}\}\" defer></script>", "", quelle)
            quelle = quelle.replace("<script src=\"{{ url_for('static', filename='js/inhalte.js', v=v) }}\" defer></script>",
                                    "<script src=\"{{ url_for('static', filename='js/inhalte.js', v=v) }}\" defer></script>\n"
                                    "  <script src=\"/qa-forschen/inhalte.js\" defer></script>")
        return quelle, name, (lambda: False)

    def list_templates(self):
        return self.innen.list_templates()


ab.app.jinja_env.loader = _IndexUmbau(ab.app.jinja_env.loader)


@ab.app.route("/qa-forschen/inhalte.js")
def qa_inhalte():
    js = open(FIXTURES, encoding="utf-8").read() + "\n;(() => { INHALTE.tabs.push(...window.FORSCHEN_FIXTURES.tabs); })();\n"
    return Response(js, mimetype="application/javascript", headers={"Cache-Control": "no-store"})


if __name__ == "__main__":
    port = int(os.environ["PORT"])
    print(f"Forschen-QA: http://forschen.localhost:{port}/login · Lehrkraft http://lehrer-forschen.localhost:{port} · DB {os.environ['DB_PATH']} · KI aus")
    ab.socketio.run(ab.app, host="127.0.0.1", port=port, allow_unsafe_werkzeug=True)
