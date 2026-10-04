"""Inhalte des Reiters „Abschluss & Quellen“ (Stationen 80 Forscherbuch, 38 Blitzfragen, 39 Domino, 40 Quellen, T Transfer).

Geprüft wird nur static/js/inhalte_abschluss.js. Der Reiter fragt aus allen anderen Reitern; die Wortwahl der Reiter 2–4
gleicht test_wortwahl_passt_zu_den_anderen_reitern ab (fehlt dort noch etwas, gibt es nur eine Warnung).
"""
import os
import re
import warnings

import pytest

import glossar
import lesen_koerper
import lesen_nutzen
import lesen_nutztier
import lesen_volk
from config import ABSCHNITTE
from inhalte_laden import ROOT, lade_inhalte
import plan_abschluss
from plan import AUFGABEN_PLAN, DIFFERENZIERT, STATIONEN_MAX_ABSCHLUSS

NUMMERN = [80, 38, 39, 40, "T"]
KONZEPT = os.path.join(os.path.dirname(ROOT), "AB_KONZEPT.md")

UEBERSPRINGEN = {"kontext", "kiFrage", "typ", "key", "id", "ok", "stufe", "modus", "icon", "kurz", "label", "stufen", "ziel",
                 "steine", "min", "nr"}

# Wörter, die für dieselbe Sache nicht verwendet werden dürfen (feste Wörter im Konzept, DaZ)
VERBOTEN = ["Bienenkorb", "Bienenhaus", "Honigblase", "Pollenhöschen", "Stockbiene", "Honigwabe", "Bienenkönigin",
            "Sammelbiene", "Wächterbiene", "Zuckerfutter"]

# Zu welchem Reiter gehört welche Blitzfrage / welches Domino-Paar? (Abdeckung aller Reiter)
BLITZ_REITER = {
    "nutztier": ["b01", "b02", "b03", "b15"],
    "koerper": ["b04", "b05", "b06", "b12", "b16", "b17", "b24", "b25"],
    "volk": ["b07", "b08", "b09", "b13", "b18", "b19", "b20", "b21", "b26", "b27", "b29", "b30"],
    "nutzen": ["b10", "b11", "b14", "b22", "b23", "b28", "b31"],
}
DOMINO_REITER = {
    "nutztier": ["d01", "d02"], "koerper": ["d03", "d06", "d07", "d09"], "volk": ["d04", "d05", "d08", "d10"],
    "nutzen": ["d11", "d12"],
}


@pytest.fixture(scope="module")
def tab():
    return next(t for t in lade_inhalte()["tabs"] if t["key"] == "abschluss")


@pytest.fixture(scope="module")
def aufg(tab):
    return {a["nr"]: a for a in tab["aufgaben"]}


def _texte(obj):
    """Alle Texte, die Kinder sehen (rekursiv, ohne technische Felder)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from _texte(x)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in UEBERSPRINGEN:
                yield from _texte(v)


def _klar(text):
    return re.sub(r"<[^>]+>", "", text)


def _saetze(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", _klar(text)) if s.strip()]


def _woerter(s):
    return len(s.split())


def _zahlen(text):
    ohne = re.sub(r"(Reiter|Lesestrecke|Kapitel|Szene|Abschnitt|Aufgabe) \d+", "", text)
    return {int(re.sub(r"\D", "", z)) for z in re.findall(r"\d+(?:[   ]\d{3})*", ohne)}


def _konzept_zahlen():
    if not os.path.exists(KONZEPT):
        pytest.skip("AB_KONZEPT.md liegt nicht neben dem Projekt")
    text = open(KONZEPT, encoding="utf-8").read()
    abschnitt = text.split("## Gesicherte Fakten", 1)[1].split("\n## ", 1)[0]
    return _zahlen(abschnitt)


def _kindertexte(tab):
    return [t for t in _texte(tab["aufgaben"])]


# ── Vollständigkeit und Typen ───────────────────────────────────────────────────────────
def test_reiter_und_aufgaben_vollstaendig(tab, aufg):
    abschnitt = next(a for a in ABSCHNITTE if a["key"] == "abschluss")
    assert tab["label"] == "Abschluss & Quellen" and tab["kurz"] == "A" and not tab.get("lese") and "film" not in tab
    assert [a["nr"] for a in tab["aufgaben"]] == NUMMERN == abschnitt["aufgaben"] == plan_abschluss.STATIONEN
    assert len(NUMMERN) <= STATIONEN_MAX_ABSCHLUSS
    for nr in NUMMERN:
        assert aufg[nr]["typ"] == AUFGABEN_PLAN[nr], f"Aufgabe {nr}: Typ {aufg[nr]['typ']} statt {AUFGABEN_PLAN[nr]}"
        assert aufg[nr]["eyebrow"] and aufg[nr]["titel"]
        assert "modell" not in aufg[nr] and "film" not in aufg[nr]


def test_forscherbuch_80(aufg):
    a = aufg[80]
    assert a["typ"] == "forscherbuch" == plan_abschluss.TYPEN[80] and a["eyebrow"] == "Mein Forscherbuch"
    assert all(w in a["hinweis"] for w in ("Forscherfragen", "Vermutungen", "Erkenntnisse", "drucken", "PDF"))
    assert [n for n in NUMMERN].index(80) == 0, "Das Forscherbuch schaut zuerst zurück"
    assert "Welche deiner Fragen vom Anfang ist jetzt beantwortet?" in a["hinweis"], "Rückblick auf die Fragen an den Imker (Reiter 1, Station „Fragen sammeln“)"


def test_keine_platzhalter_mehr(tab):
    for text in _kindertexte(tab):
        assert "PLATZHALTER" not in text.upper(), text[:60]
    quelle = open(os.path.join(ROOT, "static", "js", "inhalte_abschluss.js"), encoding="utf-8").read()
    assert "PLATZHALTER" not in quelle.upper()


def test_abc_wo_verlangt(aufg):
    for nr in NUMMERN:
        if aufg[nr]["typ"] in DIFFERENZIERT:
            assert sorted(aufg[nr]["niveaus"]) == ["A", "B", "C"], nr


# ── 38 Blitzfragen ──────────────────────────────────────────────────────────────────────
def test_blitz_pool(aufg):
    a = aufg[38]
    pool = a["pool"]
    assert len(pool) >= 20
    ids = [q["id"] for q in pool]
    assert ids == [f"b{i:02d}" for i in range(1, len(pool) + 1)], "ids b01, b02 … ohne Lücken (stehen im Autosave)"
    assert len({q["frage"] for q in pool}) == len(pool), "jede Frage nur einmal"
    for q in pool:
        assert q["stufe"] in (1, 2, 3) and len(q["optionen"]) == 3 and len(set(q["optionen"])) == 3, q["id"]
        assert 0 <= q["ok"] < 3 and q["frage"].endswith("?"), q["id"]
        assert all(_woerter(o) <= 12 for o in q["optionen"]), q["id"]
        assert _woerter(q["frage"]) <= 18, q["id"]
    # genug Fragen je Niveau: ziel plus drei Fehlversuche
    for niv, cfg in a["niveaus"].items():
        verfuegbar = [q for q in pool if q["stufe"] in cfg["stufen"]]
        assert len(verfuegbar) >= cfg["ziel"] + 3, f"{niv}: nur {len(verfuegbar)} Fragen für ziel {cfg['ziel']}"
        assert cfg["hinweis"]
    zahl = {s: sum(1 for q in pool if q["stufe"] == s) for s in (1, 2, 3)}
    assert all(zahl[s] >= 6 for s in (1, 2, 3)), zahl
    assert [a["niveaus"][n]["ziel"] for n in "ABC"] == sorted(a["niveaus"][n]["ziel"] for n in "ABC")


def test_blitz_loesungspositionen_verteilt(aufg):
    pool = aufg[38]["pool"]
    pos = [q["ok"] for q in pool]
    for p in (0, 1, 2):
        anteil = pos.count(p) / len(pos)
        assert 0.2 <= anteil <= 0.45, f"Position {p}: {pos.count(p)} von {len(pos)}"
    for s in (1, 2, 3):
        assert len({q["ok"] for q in pool if q["stufe"] == s}) == 3, f"Stufe {s}: alle drei Positionen kommen vor"
    # nicht drei gleiche Positionen hintereinander
    for i in range(len(pos) - 2):
        assert not (pos[i] == pos[i + 1] == pos[i + 2]), f"b{i + 1:02d}–b{i + 3:02d}: dreimal dieselbe Position"
    # die richtige Antwort ist nicht auffällig die längste
    laengste = sum(1 for q in pool if len(q["optionen"][q["ok"]]) == max(len(o) for o in q["optionen"])
                   and sum(len(o) == len(q["optionen"][q["ok"]]) for o in q["optionen"]) == 1)
    assert laengste / len(pool) <= 0.5, f"{laengste} von {len(pool)} richtigen Antworten sind die längsten"


def test_blitz_aus_allen_reitern(aufg):
    pool = {q["id"]: q for q in aufg[38]["pool"]}
    gesamt = [i for ids in BLITZ_REITER.values() for i in ids]
    assert sorted(gesamt) == sorted(pool), "jede Frage hat genau einen Reiter (BLITZ_REITER im Test pflegen)"
    for reiter, ids in BLITZ_REITER.items():
        assert len(ids) >= 4, f"{reiter}: mindestens vier Fragen"
        assert len({pool[i]["stufe"] for i in ids}) >= 2, f"{reiter}: Fragen in mindestens zwei Stufen"
    # Stufe 1 = Grundbegriffe aus allen Reitern, damit auch Niveau A alle Reiter wiederholt
    stufe1 = {pool[i]["stufe"] == 1 for r in BLITZ_REITER.values() for i in r}
    assert stufe1 == {True, False}
    for reiter, ids in BLITZ_REITER.items():
        assert any(pool[i]["stufe"] == 1 for i in ids), f"{reiter}: keine Stufe-1-Frage (Niveau A fragt den Reiter nie)"


# ── 39 Domino ───────────────────────────────────────────────────────────────────────────
def test_domino(aufg):
    a = aufg[39]
    paare = a["paare"]
    assert len(paare) >= 12
    assert [p["id"] for p in paare] == [f"d{i:02d}" for i in range(1, len(paare) + 1)]
    assert len({p["begriff"] for p in paare}) == len(paare)
    assert len({p["definition"] for p in paare}) == len(paare), "Erklärungen müssen eindeutig sein"
    for p in paare:
        assert _woerter(p["definition"]) <= 12, p["id"]
        # die Erklärung verrät den Begriff nicht (das ganze Wort, ohne Endung -n/-e, steht nicht darin)
        wort = re.sub(r"[^a-zäöüß]", "", p["begriff"].lower()).rstrip("ne")
        assert wort not in p["definition"].lower(), f"{p['id']}: die Erklärung nennt den Begriff"
    schritte = [a["niveaus"][n]["steine"] for n in "ABC"]
    assert schritte == [6, 9, 12] and schritte[-1] <= len(paare)
    # geschlossene Kette wie im Client: Stein i = Erklärung von Paar i, rechts der Begriff von Paar i+1
    for n in schritte:
        teil = paare[:n]
        steine = [(p["definition"], teil[(i + 1) % n]["begriff"]) for i, p in enumerate(teil)]
        assert len({s[0] for s in steine}) == n and len({s[1] for s in steine}) == n
    gesamt = [i for ids in DOMINO_REITER.values() for i in ids]
    assert sorted(gesamt) == sorted(p["id"] for p in paare)
    # schon die ersten sechs Paare (Niveau A) kommen aus mehreren Reitern
    erste = {r for r, ids in DOMINO_REITER.items() if any(i in ids for i in [p["id"] for p in paare[:6]])}
    assert len(erste) >= 3, erste
    assert all(cfg["hinweis"] for cfg in a["niveaus"].values())


# ── 40 Quellen ──────────────────────────────────────────────────────────────────────────
def test_quellen(aufg):
    q = aufg[40]
    assert q["min"] == 2 and q["titel"] == "Woher weißt du es?"
    for wort in ("Lesestrecken", "Film", "3D-Modell", "zwei Quellen", "warum"):
        assert wort in q["hinweis"], wort
    assert "Ein Bienenvolk im Bienenstock" in q["hinweis"] and "Die Honigbiene in 3D" in q["hinweis"]
    eintraege = q["quellenAB"]["eintraege"]
    ganz = " | ".join(eintraege)
    for quelle in ("Deutscher Imkerbund", "Länderinstitut für Bienenkunde Hohen Neuendorf", "NABU", "Karl von Frisch", "COLOSS BEEBOOK"):
        assert quelle in ganz, quelle
    assert len(eintraege) == 6 and len(set(eintraege)) == 6
    assert any("Apfelzweig-Beispiel" in e and "ausgedacht" in e for e in eintraege), "Das ausgedachte Beispiel aus dem Reiter Nutzen gehört ins Quellenverzeichnis"
    # nur Nennung, keine Zitate
    assert not re.search(r"[„“\"»«]", ganz), "Zitate gehören nicht ins Quellenverzeichnis"
    assert all(len(e) <= 120 for e in eintraege)


# ── T Transfer ──────────────────────────────────────────────────────────────────────────
def test_transfer(aufg):
    t = aufg["T"]
    n = t["niveaus"]
    assert t["titel"] == "Zwei Bienenvölker für unsere Schule"
    assert t["eyebrow"].startswith("Sprachwerkstatt · Transfer")
    # Sprachziel: begründen mit weil, denn, deshalb
    assert "„weil“ oder „denn“" in n["B"]["aufgabe"] and "„weil“" in n["C"]["aufgabe"]
    A, B, C = n["A"], n["B"], n["C"]
    assert A["modus"] == "bausteine" and 4 <= len(A["bausteine"]) <= 7
    assert all(_woerter(b) <= 14 for b in A["bausteine"]), "Baustein länger als 14 Wörter"
    assert len(set(A["bausteine"])) == len(A["bausteine"])
    assert A["schluss"] and len(A["urteil"]["optionen"]) == 2 and A["urteil"]["frage"]
    # Die Reihenfolge ergibt sich aus Verbindungswörtern (Tipp: jede andere Folge wäre sprachlich holprig)
    b = A["bausteine"]
    assert "Schule" in b[0] and "Bienenvölker" in b[0]
    assert b[1].startswith("Dafür") and b[2].startswith("Er ") and "aber auch" in b[3] and b[-1].startswith("Außerdem")
    # Inhalt: Imker, Blüten, nicht schlagen (Stachel, Reiter „Die Biene“). „Ruhig bleiben“ und „Abstand halten“ werden im AB nirgends vermittelt
    # und stehen deshalb nicht in den Bausteinen (Audit 4.10.2026).
    ganz = " ".join(b)
    for wort in ("Imker", "Blüten", "schlagen"):
        assert wort in ganz, wort
    assert "ruhig" not in ganz and "Abstand" not in ganz
    # zwei vertretbare Urteile, beide mit Begründung
    gut, vorsicht = A["urteil"]["optionen"]
    assert gut.startswith("Gute Idee, weil") and vorsicht.startswith("Nur mit Vorsicht, weil")
    assert "bestäuben" in gut and "stechen" in vorsicht
    # B und C
    assert len(B["starter"]) >= 3 and len(B["begriffe"]) >= 4 and 100 <= B["min"] < C["min"]
    assert "starter" not in C and len(C["begriffe"]) >= len(B["begriffe"]) and C["min"] >= 200
    for cfg in (A, B, C):
        assert "Schule soll zwei Bienenvölker bekommen" in cfg["aufgabe"] or "Schule soll zwei Bienenvölker bekommen" in b[0] \
            or "zwei Bienenvölker" in cfg["aufgabe"]
    assert "Schulleitung" in B["aufgabe"] and "Schulleitung" in C["aufgabe"]
    assert "Beurteile" in C["aufgabe"] and "dafür" in C["aufgabe"] and "dagegen" in C["aufgabe"]
    assert "was ein Bienenvolk braucht" in B["aufgabe"] and "verhalten" in B["aufgabe"]
    # KI-Kontext nennt die Begriffe der Niveaus
    for begriff in set(B["begriffe"]) | set(C["begriffe"]):
        assert begriff in t["kontext"], begriff
    assert "Klasse 6" in t["kontext"]


# ── Sprache, feste Wörter, Zahlen ───────────────────────────────────────────────────────
def test_saetze_sind_kurz(tab):
    zu_lang = []
    for text in _kindertexte(tab):
        for satz in _saetze(text):
            if _woerter(satz) > 18:
                zu_lang.append((_woerter(satz), satz[:80]))
    assert not zu_lang, zu_lang


def test_feste_woerter_statt_synonyme(tab):
    ganz = " ".join(_kindertexte(tab))
    for w in VERBOTEN:
        assert w.lower() not in ganz.lower(), f"„{w}“ statt des festen Worts"
    assert not re.search(r"Imker[^.]{0,40}Bienenstock", ganz), "Der Imker arbeitet am Bienenkasten"
    # Bienenkasten = Holzkiste, Bienenstock = ganzes Zuhause: „Bienenstock“ nur für Zuhause/Film
    assert "Bienenstock" in ganz and "Bienenkasten" in ganz


def test_jede_zahl_steht_im_konzept(tab):
    erlaubt = _konzept_zahlen()
    for text in _kindertexte(tab):
        fremd = _zahlen(text) - erlaubt
        assert not fremd, f"Zahl {fremd} steht nicht im Konzept: {text[:70]}"
    assert {21, 2000, 3} <= erlaubt
    alle = " ".join(_kindertexte(tab))
    assert "21 Tage" in alle and "2 000" in alle


def test_wortwahl_passt_zu_den_anderen_reitern(aufg):
    """Die Begriffe des Dominos und der Blitzfragen stehen auch in den Glossaren/Lesestrecken der Reiter 1–4."""
    norm = glossar.normalisieren
    fehlt = [p["begriff"] for p in aufg[39]["paare"] if glossar.eintrag_fuer(p["begriff"]) is None]
    if fehlt:
        warnings.warn(f"Noch nicht geschrieben (Glossar anderer Reiter): {', '.join(fehlt)}", stacklevel=1)
    strecken = " ".join(a["text"] + a["erklaerung"] + a["frage"] for m in (lesen_nutztier, lesen_koerper, lesen_volk, lesen_nutzen)
                        for s in m.LESESTRECKEN.values() if not s.get("platzhalter") for a in s["abschnitte"])
    # Wintertraube und Schwänzeltanz liefert der Film (Kapitel 11 und 9: „Traube“, „Tanz“, „Schwänzeln“) und das Glossar;
    # alle anderen Begriffe der Blitzfragen stehen in den Lesestrecken.
    film_und_glossar = {"wintertraube", "schwänzeltanz"}
    for begriff in ("Wintertraube", "Schwänzeltanz", "Pollenkörbchen", "Honigmagen", "Facettenaugen"):
        genutzt = any(begriff.lower() in q["frage"].lower() or any(begriff.lower() in o.lower() for o in q["optionen"])
                      for q in aufg[38]["pool"])
        if not genutzt:
            continue
        if begriff.lower() in film_und_glossar:
            if glossar.eintrag_fuer(begriff) is None:
                warnings.warn(f"Noch nicht geschrieben (Glossar): {begriff}", stacklevel=1)
        elif strecken.strip() and begriff.lower() not in strecken.lower():
            warnings.warn(f"Blitzfragen nennen „{begriff}“, die Lesestrecken (bisher) nicht", stacklevel=1)
    assert norm("Drohnen") and norm("Varroa-Milbe")
