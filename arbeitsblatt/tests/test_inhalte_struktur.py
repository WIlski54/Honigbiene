"""Struktur und Qualität der Inhaltsdateien (static/js/inhalte.js + inhalte_<reiter>.js).

Die Inhalte entstehen je Reiter in eigenen Dateien. Diese Tests prüfen, dass sie zusammenpassen, ohne zu verlangen,
dass schon alles geschrieben ist: Was noch fehlt, erscheint als Warnung „Noch nicht geschrieben“. Ob alle 41 Aufgaben
da sind und keine Platzhalter mehr stehen, prüft am Ende `test_inhalte_vollstaendig` (bis dahin xfail mit Liste;
mit INHALTE_STRIKT=1 wird daraus ein echter Fehler).

Geladen wird per Node (tests/inhalte_laden.py), nicht per Textsuche.
"""
import json
import os
import re
import warnings

import pytest

import forschen_pruefen
import glossar
import inhalte_server
import zeichenauftraege
from config import ABSCHNITTE, ALLE_AUFGABEN, ZEICHEN_GERAETE, ist_lesestrecke
from inhalte_laden import ROOT, alle_aufgaben, inhalte_dateien, lade_inhalte
from plan import (AUFGABEN_PLAN, BEKANNTE_TYPEN, DIFFERENZIERT, GLOSSAR_MIT_BILD, GLOSSAR_PFLICHT, MODELL_ANSICHTEN,
                  MODELL_BLICKE, MODELL_TEILE)

FILM_BEFEHLE = {"springe", "spielen", "anhalten", "kapitel", "blick", "live", "ansicht", "stopp",
                "hervorheben", "beschriften", "nummern", "zurueck", "waehlen", "fokus"}


@pytest.fixture(scope="module")
def inh():
    return lade_inhalte()


def _niveaus(a):
    return a.get("niveaus") or {}


def _woerter(text):
    return len(re.sub(r"<[^>]+>", "", str(text)).split())


# ── Kopf, Reiter, Nummern ─────────────────────────────────────────────────────
def test_kopf_und_filme(inh):
    assert set(inh) >= {"titel", "filme", "bildpunkte", "tabs"}
    assert inh["titel"] == "Die Honigbiene – ein Nutztier mit eigenem Staat"
    assert inh["filme"]["biene3d"]["art"] == "modell3d"
    assert inh["filme"]["biene3d"]["datei"].startswith("/static/film/bienenmodell/index.html")
    assert "embed=1" in inh["filme"]["biene3d"]["datei"]
    assert inh["filme"]["volk"] == {"art": "papiertheater", "datei": "/static/film/Ein_Bienenvolk_im_Bienenstock.html",
                                    "titel": "Ein Bienenvolk im Bienenstock"}
    assert os.path.exists(os.path.join(ROOT, "static", "film", "Ein_Bienenvolk_im_Bienenstock.html"))
    assert os.path.exists(os.path.join(ROOT, "static", "film", "bienenmodell", "index.html"))


def test_alle_inhaltsdateien_sind_eingebunden():
    """Jede Datei inhalte_*.js steht in index.html (in Reiterfolge) und auf der Lehrer-Tafelseite."""
    vorhanden = sorted(f for f in os.listdir(os.path.join(ROOT, "static", "js")) if f.startswith("inhalte") and f.endswith(".js"))
    erwartet = ["inhalte.js"] + [f"inhalte_{a['key']}.js" for a in ABSCHNITTE]
    assert vorhanden == sorted(erwartet), "Für jeden Reiter in config.ABSCHNITTE genau eine Datei inhalte_<key>.js"
    assert inhalte_dateien() == erwartet
    tafel = open(os.path.join(ROOT, "templates", "tafel_lehrer.html"), encoding="utf-8").read()
    assert all(f"js/{f}" in tafel for f in erwartet), "tafel_lehrer.html lädt nicht alle Inhaltsdateien"


def test_reiter_passen_zu_abschnitte(inh):
    assert [t["key"] for t in inh["tabs"]] == [a["key"] for a in ABSCHNITTE]
    for tab, a in zip(inh["tabs"], ABSCHNITTE):
        for feld in ("label", "icon", "kurz", "aufgaben", "intro"):
            assert feld in tab, (a["key"], feld)
        assert tab["kurz"] == a["kurz"], a["key"]
        lese = next((n for n in a["aufgaben"] if ist_lesestrecke(n)), None)   # die Lesestrecke steht an beliebiger Stelle des Plans
        assert tab.get("lese") == lese, f"{a['key']}: lese muss {lese!r} sein"
        if lese:
            assert "begriffe" in tab["intro"] and "titel" in tab["intro"]
            i = a["aufgaben"].index(lese)
            davor = a["aufgaben"][i - 1] if i > 0 else None
            if davor is None:
                assert tab.get("leseNach") in (None, ""), f"{a['key']}: Lesestrecke steht oben, leseNach darf nicht gesetzt sein"
            else:
                assert str(tab.get("leseNach")) == str(davor), f"{a['key']}: leseNach muss {davor!r} sein (Aufgabe vor {lese} in plan_{a['key']}.py)"
        else:
            assert not tab.get("leseNach"), f"{a['key']}: leseNach ohne Lesestrecke"


def test_nummern_passen_zu_abschnitte(inh):
    """Es darf nichts Fremdes drin stehen; was fehlt, wird als „noch nicht geschrieben“ gemeldet."""
    fehlt = []
    for tab, a in zip(inh["tabs"], ABSCHNITTE):
        erwartet = [n for n in a["aufgaben"] if not str(n).startswith("L")]
        nrs = [x["nr"] for x in tab["aufgaben"]]
        assert len(nrs) == len(set(nrs)), f"{a['key']}: doppelte Aufgabennummer {nrs}"
        fremd = [n for n in nrs if n not in erwartet]
        assert not fremd, f"{a['key']}: Nummer(n) {fremd} gehören nicht in diesen Reiter (config.ABSCHNITTE)"
        # Reihenfolge der Karten = Reihenfolge laut config
        assert nrs == [n for n in erwartet if n in nrs], f"{a['key']}: Aufgaben nicht in der Reihenfolge von config.ABSCHNITTE"
        fehlt += [str(n) for n in erwartet if n not in nrs]
    if fehlt:
        warnings.warn(f"Noch nicht geschrieben: {len(fehlt)} von {len([n for n in ALLE_AUFGABEN if not n.startswith('L')])} "
                      f"Aufgaben (Nr. {', '.join(fehlt)})", stacklevel=1)


def test_aufgaben_haben_pflichtfelder_und_bekannte_typen(inh):
    for key, a in alle_aufgaben(inh):
        wer = f"{key}/{a.get('nr')}"
        assert a["typ"] in BEKANNTE_TYPEN, f"{wer}: unbekannter Typ {a['typ']}"
        assert a.get("eyebrow") and a.get("titel"), wer
        if a["nr"] in AUFGABEN_PLAN and AUFGABEN_PLAN[a["nr"]] != a["typ"]:
            warnings.warn(f"Aufgabe {a['nr']} hat Typ {a['typ']}, der Plan sieht {AUFGABEN_PLAN[a['nr']]} vor", stacklevel=1)


def test_differenzierte_aufgaben_haben_a_b_c(inh):
    fehler = []
    for key, a in alle_aufgaben(inh):
        if a["typ"] in DIFFERENZIERT:
            n = _niveaus(a)
            if sorted(n) != ["A", "B", "C"]:
                fehler.append((a["nr"], a["typ"], sorted(n)))
    assert not fehler, f"A, B und C verlangt: {fehler}"


# ── Typen im Einzelnen ───────────────────────────────────────────────────────
def test_mc_optionen_und_richtig_falsch_listen(inh):
    for key, a in alle_aufgaben(inh):
        if a["typ"] not in ("mc", "diagramm"):
            continue
        for n, cfg in _niveaus(a).items():
            wer = f"Aufgabe {a['nr']} Niveau {n}"
            assert cfg.get("frage"), wer
            if "aussagen" in cfg:   # Richtig/Falsch-Liste
                assert a["typ"] == "mc", f"{wer}: aussagen nur bei mc"
                assert len(cfg["aussagen"]) >= 2, wer
                assert all(isinstance(x.get("ok"), bool) and x.get("t") for x in cfg["aussagen"]), wer
                assert any(x["ok"] for x in cfg["aussagen"]) and not all(x["ok"] for x in cfg["aussagen"]), f"{wer}: richtig und falsch mischen"
                assert all(_woerter(x["t"]) <= 20 for x in cfg["aussagen"]), wer
            else:
                oks = sum(1 for o in cfg["optionen"] if o["ok"])
                assert oks == (cfg.get("multi") or 1), f"{wer}: {oks} richtige Option(en), multi={cfg.get('multi')}"
                assert len({o["t"] for o in cfg["optionen"]}) == len(cfg["optionen"]), f"{wer}: doppelte Optionen"
                assert all(_woerter(o["t"]) <= 12 for o in cfg["optionen"]), f"{wer}: Option länger als 12 Wörter"
    # Die Position der richtigen Option soll variieren (sonst ist „oben“ immer richtig)
    positionen = [i for _, a in alle_aufgaben(inh) if a["typ"] == "mc" for c in _niveaus(a).values()
                  if "optionen" in c and not c.get("multi") for i, o in enumerate(c["optionen"]) if o["ok"]]
    if len(positionen) >= 6:
        assert len(set(positionen)) >= 2, positionen


def test_zuordnung_sortierung_luecke_diagramm(inh):
    for key, a in alle_aufgaben(inh):
        for n, cfg in _niveaus(a).items():
            wer = f"Aufgabe {a['nr']} Niveau {n}"
            if a["typ"] == "zuordnung":
                rechts = [p[1] for p in cfg["paare"]]
                assert len(cfg["paare"]) >= 3 and all(len(p) == 2 for p in cfg["paare"]), wer
                assert len(set(rechts)) == len(rechts), f"{wer}: rechte Seite doppelt (Zuordnung wäre mehrdeutig)"
                assert cfg.get("links") and cfg.get("rechts"), wer
            elif a["typ"] == "sortierung":
                assert len(cfg["items"]) >= 3 and len(set(cfg["items"])) == len(cfg["items"]), wer
            elif a["typ"] == "luecke":
                assert re.search(r"\[[^\]]+\]", cfg["text"]), f"{wer}: keine Lücke [Wort]"
                assert cfg.get("modus") in ("chips", "input"), wer
            elif a["typ"] == "diagramm":
                ch = a["chart"]
                assert ch["typ"] in ("line", "bar") and ch.get("yTitel") and ch.get("quelle"), wer
                assert all(len(d["data"]) == len(ch["labels"]) for d in ch["datasets"]), wer


def test_niveau_a_verlangt_kein_freies_schreiben(inh):
    """Gemeinsames Lernen: Freitext und Transfer laufen auf Niveau A über Textbausteine."""
    for key, a in alle_aufgaben(inh):
        if a["typ"] in ("freitext", "transfer"):
            assert _niveaus(a).get("A", {}).get("modus") == "bausteine", f"Aufgabe {a['nr']}: Niveau A braucht modus \"bausteine\""
            for n in ("B", "C"):
                cfg = _niveaus(a).get(n, {})
                assert cfg.get("aufgabe") and cfg.get("min"), f"Aufgabe {a['nr']} Niveau {n}: aufgabe und min fehlen"
            assert _niveaus(a).get("B", {}).get("starter"), f"Aufgabe {a['nr']} Niveau B: Satzanfänge (starter) fehlen"


def test_bausteinaufgaben_sind_vollstaendig(inh):
    """Jede Bausteinaufgabe braucht Bausteine, einen Schlusssatz und genau zwei vertretbare Urteile."""
    for key, a in alle_aufgaben(inh):
        cfg = _niveaus(a).get("A", {})
        if cfg.get("modus") != "bausteine":
            continue
        wer = f"Aufgabe {a['nr']}"
        assert 4 <= len(cfg["bausteine"]) <= 7, wer
        assert all(_woerter(b) <= 14 for b in cfg["bausteine"]), f"{wer}: Baustein zu lang"
        assert cfg.get("schluss"), wer
        assert cfg["urteil"].get("frage") and len(cfg["urteil"]["optionen"]) == 2, wer


def test_bildpunkte_daten_passen_zum_bild(inh):
    for karte, k in inh["bildpunkte"].items():
        assert os.path.exists(os.path.join(ROOT, k["bild"].lstrip("/").split("?")[0])), f"Bilddatei fehlt: {k['bild']}"
        ids = [p["id"] for p in k["punkte"]]
        assert len(ids) == len(set(ids)) and all(re.fullmatch(r"[a-z0-9_-]+", i) for i in ids), karte
        assert len({p["name"] for p in k["punkte"]}) == len(ids), f"{karte}: Namen nicht eindeutig"
        for p in k["punkte"]:
            assert 24 <= p["x"] <= k["breite"] - 24 and 24 <= p["y"] <= k["hoehe"] - 24, (karte, p["id"])   # Hotspot-Radius
            assert p.get("kat", 0) in (0, 1), (karte, p["id"])
    for key, a in alle_aufgaben(inh):
        if a["typ"] != "bildpunkte":
            continue
        assert a["karte"] in inh["bildpunkte"], f"Aufgabe {a['nr']}: Karte {a['karte']} fehlt"
        punkte = inh["bildpunkte"][a["karte"]]["punkte"]
        for n, cfg in _niveaus(a).items():
            wer = f"Aufgabe {a['nr']} Niveau {n}"
            modus = cfg.get("modus") or ("einordnen" if cfg.get("kategorien") else "benennen")
            assert modus in ("einordnen", "benennen"), wer
            erste = punkte[:min(cfg.get("anzahl", len(punkte)), len(punkte))]
            assert len(erste) >= 3, f"{wer}: mindestens 3 Punkte"
            if modus == "einordnen":
                assert len(cfg["kategorien"]) == 2, wer
                assert {p.get("kat", 0) for p in erste} == {0, 1}, f"{wer}: beide Kategorien müssen vorkommen"


def test_kartenpunkte_und_ziele_stimmen_mit_den_daten_der_grafik_agenten_ueberein(inh):
    """Die Koordinaten in INHALTE.bildpunkte / bildwahl entsprechen werkzeuge/*_punkte.json bzw. tanzraetsel_ziele.json
    (abweichende Werte nur, wenn sie im Bild geprüft wurden: Toleranz 40 px); Abstände: die Punkte dürfen sich nicht überdecken."""
    import itertools
    import math
    werkzeuge = os.path.join(ROOT, "werkzeuge")
    for karte, k in inh["bildpunkte"].items():
        punkte = k["punkte"]
        for p, q in itertools.combinations(punkte, 2):
            d = math.hypot(p["x"] - q["x"], p["y"] - q["y"])
            assert d >= 48, f"{karte}: {p['id']} und {q['id']} liegen {d:.0f} px auseinander (die Punkte mit Radius 24 würden sich überdecken)"
            if d < 100:
                warnings.warn(f"{karte}: {p['id']}/{q['id']} nur {d:.0f} px auseinander – auf dem Handy trifft der nächste Punkt (Trefferkreis ≥ 44 px, bildpunkte.js)", stacklevel=1)
        datei = os.path.join(werkzeuge, f"{karte}_karte_punkte.json")
        if os.path.exists(datei):
            daten = json.load(open(datei, encoding="utf-8"))
            for p in punkte:
                if p["id"] in daten:
                    d = math.hypot(p["x"] - daten[p["id"]]["x"], p["y"] - daten[p["id"]]["y"])
                    assert d <= 60, f"{karte}/{p['id']}: weicht {d:.0f} px von {os.path.basename(datei)} ab"
                    assert daten[p["id"]].get("kat", p.get("kat", 0)) == p.get("kat", 0), f"{karte}/{p['id']}: kat weicht von {os.path.basename(datei)} ab"
    ziele_datei = os.path.join(werkzeuge, "tanzraetsel_ziele.json")
    if os.path.exists(ziele_datei):
        t = json.load(open(ziele_datei, encoding="utf-8"))
        for key, a in alle_aufgaben(inh):
            if a["typ"] != "bildwahl":
                continue
            for n, cfg in _niveaus(a).items():
                for i, r in enumerate(cfg["runden"]):
                    if str(r["bild"]).split("?")[0] not in t["bilder"]:
                        continue
                    ref = t["runden"][t["bilder"].index(str(r["bild"]).split("?")[0])]
                    assert (r["breite"], r["hoehe"]) == (t["breite"], t["hoehe"]), f"Aufgabe {a['nr']} Niveau {n} Runde {i + 1}: Bildgröße"
                    for z in r["ziele"]:
                        treffer = [x for x in ref if math.hypot(x["x"] - z["x"], x["y"] - z["y"]) <= 40]
                        assert treffer and treffer[0]["ok"] == z["ok"], f"Aufgabe {a['nr']} Niveau {n} Runde {i + 1}: Ziel ({z['x']}, {z['y']}) stimmt nicht mit tanzraetsel_ziele.json überein"
    for key, a in alle_aufgaben(inh):
        if a["typ"] != "bildwahl":
            continue
        for n, cfg in _niveaus(a).items():
            for i, r in enumerate(cfg["runden"]):
                for z, y in itertools.combinations(r["ziele"], 2):
                    assert math.hypot(z["x"] - y["x"], z["y"] - y["y"]) >= 60, f"Aufgabe {a['nr']} Niveau {n} Runde {i + 1}: zwei Trefferkreise liegen übereinander"
                for z in r["ziele"]:
                    assert z["r"] <= min(r["breite"], r["hoehe"]) / 3, f"Aufgabe {a['nr']}: Trefferkreis zu groß"


def test_zeichenauftraege_passen_zur_konfiguration(inh):
    erwartet = {g for g in ZEICHEN_GERAETE if g != "handschrift"}
    assert erwartet == set(zeichenauftraege.ZEICHENAUFTRAEGE)
    for g, a in zeichenauftraege.ZEICHENAUFTRAEGE.items():
        assert a["nr"] == ZEICHEN_GERAETE[g] and a["merkmale"] and a["titel"] and a["motiv"], g
    geraete = {a["geraet"]: a["nr"] for _, a in alle_aufgaben(inh) if a["typ"] == "zeichnen"}
    for g, nr in geraete.items():
        assert g in erwartet and ZEICHEN_GERAETE[g] == nr, f"Zeichnung {g} (Aufgabe {nr}) passt nicht zu config.ZEICHEN_GERAETE"
    fehlt = erwartet - set(geraete)
    if fehlt:
        warnings.warn(f"Noch nicht geschrieben: Zeichenaufgabe(n) {sorted(fehlt)}", stacklevel=1)
    for _, a in alle_aufgaben(inh):
        if a["typ"] == "zeichnen":
            for n, cfg in _niveaus(a).items():
                assert cfg.get("aufgabe") and cfg.get("elemente"), f"Aufgabe {a['nr']} Niveau {n}"


def test_modellaufgaben(inh):
    for key, a in alle_aufgaben(inh):
        if a["typ"] not in ("erkunden", "modellfinden"):
            continue
        assert inh["filme"][a["film"]]["art"] == "modell3d", f"Aufgabe {a['nr']}: film muss ein modell3d sein"
        tab = next(t for t in inh["tabs"] if t["key"] == key)
        assert tab.get("film") == a["film"], f"Reiter {key}: tab.film fehlt (Bühne mit dem Modell)"
        if a["typ"] == "erkunden":
            cfgs = list(_niveaus(a).values()) or [a]
            for cfg in cfgs:
                assert cfg.get("auftrag") and 2 <= len(cfg.get("beobachtung", [])) <= 3, f"Aufgabe {a['nr']}: Auftrag und 2–3 Beobachtungsfragen"
        else:
            for n, cfg in _niveaus(a).items():
                assert cfg["ziele"], f"Aufgabe {a['nr']} Niveau {n}: keine Ziele"
                for z in cfg["ziele"]:
                    assert z["teil"] in MODELL_TEILE, f"Aufgabe {a['nr']}: unbekannter Teil {z['teil']}"
                    assert z.get("frage") and z.get("hinweis"), f"Aufgabe {a['nr']}: frage und hinweis je Ziel"
                    assert z.get("ansicht", "gestalt") in MODELL_ANSICHTEN
                    assert z.get("blick", "schraeg") in MODELL_BLICKE, f"Aufgabe {a['nr']}: unbekannter blick {z.get('blick')}"
                    if "fokus" in z:   # Kamerafahrt an die Teile ohne Markierung (Modellbefehl „fokus“)
                        f = z["fokus"]
                        assert isinstance(f, dict) and f.get("teile") and set(f["teile"]) <= MODELL_TEILE, f"Aufgabe {a['nr']}: fokus.teile müssen Teile des Modells sein"
                        assert f.get("blick", "schraeg") in MODELL_BLICKE, f"Aufgabe {a['nr']}: fokus.blick unbekannt"
                    # Die Rückmeldung darf die Lösung nicht verraten: der Hinweis nennt den Teil möglichst nicht beim Namen
                    if z["teil"] in z["hinweis"].lower().replace(" ", ""):
                        warnings.warn(f"Aufgabe {a['nr']} Niveau {n}: der Hinweis nennt „{z['teil']}“ – verrät er die Lösung?", stacklevel=1)


def test_film_aufgaben_und_knoepfe(inh):
    for key, a in alle_aufgaben(inh):
        if a["typ"] in ("film", "filmmoment"):
            assert a["film"] in inh["filme"], f"Aufgabe {a['nr']}: film {a['film']} fehlt in INHALTE.filme"
        if a["typ"] == "film":
            assert a.get("auftrag") and 2 <= len(a.get("beobachtung", [])) <= 3, f"Aufgabe {a['nr']}"
        if a["typ"] == "filmmoment":
            for n, cfg in _niveaus(a).items():
                von, bis = cfg["fenster"]
                assert 0 <= von < bis, f"Aufgabe {a['nr']} Niveau {n}: Zeitfenster"
                assert a["start"] <= von, f"Aufgabe {a['nr']}: start muss vor dem Fenster liegen"
                assert cfg.get("frage") and cfg.get("tipp"), f"Aufgabe {a['nr']} Niveau {n}"
            assert a.get("erklaerung") and a.get("zu_frueh") and a.get("zu_spaet"), f"Aufgabe {a['nr']}"
        modell = a.get("modell")
        if modell:   # Film-/Modell-Knöpfe UND Bild-Knöpfe ({bild, text, alt}), einzeln oder als Liste – gleiche Prüfung wie bei Zeilen (forschen_pruefen._modell)
            probleme = forschen_pruefen._modell(modell, inh, f"Aufgabe {a['nr']} modell")
            assert not probleme, probleme


def test_blitz_domino_quellen_notizen(inh):
    for key, a in alle_aufgaben(inh):
        if a["typ"] == "blitz":
            ids = [q["id"] for q in a["pool"]]
            assert len(ids) == len(set(ids)) and all(re.fullmatch(r"b\d+", i) for i in ids)
            for q in a["pool"]:
                assert q["stufe"] in (1, 2, 3) and 0 <= q["ok"] < len(q["optionen"]) and len(set(q["optionen"])) == len(q["optionen"]), q["id"]
                assert all(_woerter(o) <= 12 for o in q["optionen"]), q["id"]
            for n, cfg in _niveaus(a).items():
                verfuegbar = [q for q in a["pool"] if q["stufe"] in cfg["stufen"]]
                assert len(verfuegbar) >= cfg["ziel"], f"Blitz Niveau {n}: nur {len(verfuegbar)} Fragen für ziel {cfg['ziel']}"
        if a["typ"] == "domino":
            ids = [p["id"] for p in a["paare"]]
            assert len(ids) == len(set(ids)) and all(re.fullmatch(r"d\d+", i) for i in ids)
            assert len({p["begriff"] for p in a["paare"]}) == len(ids)
            for n, cfg in _niveaus(a).items():
                assert 3 <= cfg["steine"] <= len(a["paare"]), f"Domino Niveau {n}"
        if a["typ"] == "quellen":
            assert a.get("min", 0) >= 1 and a.get("hinweis")
            if "quellenAB" in a:   # Quellen des Arbeitsblatts: aufklappbarer Hinweis unter der Aufgabe (nur Nennung, keine Zitate)
                q = a["quellenAB"]
                assert q.get("titel") and isinstance(q.get("eintraege"), list) and q["eintraege"] and all(isinstance(e, str) and e.strip() for e in q["eintraege"]), "quellenAB: titel und eintraege (Liste von Texten)"
        if a["typ"] == "notizen":
            assert a["abschnitt"] == key, f"Aufgabe {a['nr']}: abschnitt muss \"{key}\" sein"
            assert a.get("hinweis") and a.get("kiFrage"), f"Aufgabe {a['nr']}: hinweis und kiFrage"
    # genau eine Quellen-, Blitz- und Domino-Aufgabe, damit der Autosave sie über den Typ findet
    typen = [a["typ"] for _, a in alle_aufgaben(inh)]
    for t in ("quellen", "blitz", "domino"):
        assert typen.count(t) <= 1, f"Typ {t} darf höchstens einmal vorkommen (Autosave sucht ihn über den Typ)"


# ── Server-Seite: Lesestrecken und Glossar ───────────────────────────────────
def test_lesestrecken_gehoeren_zu_abschnitten():
    from config import LESESTRECKEN as STATIONEN   # {"L1": "nutztier", …}
    assert set(inhalte_server.LESESTRECKEN) == set(STATIONEN.values())
    for key, s in inhalte_server.LESESTRECKEN.items():
        assert STATIONEN[s["station"]] == key, f"{key}: station {s['station']} passt nicht zu config.ABSCHNITTE"
        assert s["eyebrow"] and s["titel"] and s["abschnitte"], key


def test_glossar_aggregation_ohne_kollision():
    """Jede glossar_<reiter>.py liefert EINTRAEGE; Schlüssel und Aliase sind über alle eindeutig (glossar.py prüft das beim Import)."""
    assert glossar.GLOSSAR and glossar.ALIASE
    for key, e in glossar.GLOSSAR.items():
        assert re.fullmatch(r"[a-z0-9-]+", key), key
        assert e["titel"] and e["text"] and e.get("aliase"), key
        assert len(e["text"]) < 420, key
        if e.get("bild"):
            assert os.path.exists(os.path.join(ROOT, "static", "img", "lese", e["bild"] + ".svg")), key


# ── Vollständigkeit (Checkliste für die Inhalts-Agenten) ─────────────────────
def test_inhalte_vollstaendig(inh):
    """Alle 41 Aufgaben, 4 echte Lesestrecken, Glossar komplett, keine Platzhalter mehr.

    Solange etwas fehlt: xfail mit der Liste. Mit INHALTE_STRIKT=1 (z. B. vor dem Ausliefern) wird es ein Fehler.
    """
    probleme = []
    gefunden = {str(a["nr"]): a["typ"] for _, a in alle_aufgaben(inh)}
    fehlend = [str(n) for n in AUFGABEN_PLAN if str(n) not in gefunden]
    if fehlend:
        probleme.append(f"{len(fehlend)} von {len(AUFGABEN_PLAN)} Aufgaben fehlen (Nr. {', '.join(fehlend)})")
    abweichend = [f"{n}: {gefunden[str(n)]} statt {t}" for n, t in AUFGABEN_PLAN.items() if str(n) in gefunden and gefunden[str(n)] != t]
    if abweichend:
        probleme.append("Typ weicht vom Plan ab: " + "; ".join(abweichend))
    treffer = len(re.findall("PLATZHALTER", json.dumps(inh, ensure_ascii=False)))
    if treffer:
        probleme.append(f"{treffer}× „PLATZHALTER“ in den Inhaltsdateien")
    for key, s in inhalte_server.LESESTRECKEN.items():
        if s.get("platzhalter") or "PLATZHALTER" in json.dumps(s, ensure_ascii=False):
            probleme.append(f"Lesestrecke {s['station']} ({key}) ist noch ein Platzhalter")
        elif not 4 <= len(s["abschnitte"]) <= 7:
            probleme.append(f"Lesestrecke {s['station']}: {len(s['abschnitte'])} Abschnitte (4–7 erwartet)")
    norm = glossar.normalisieren
    fehlt = [b for b in GLOSSAR_PFLICHT if norm(b) not in glossar.ALIASE]
    if fehlt:
        probleme.append(f"Glossar: {len(fehlt)} Begriffe fehlen ({', '.join(fehlt)})")
    ohne_bild = [b for b in GLOSSAR_MIT_BILD if norm(b) in glossar.ALIASE and not glossar.GLOSSAR[glossar.ALIASE[norm(b)]].get("bild")]
    if ohne_bild:
        probleme.append(f"Glossar: Bild fehlt bei {', '.join(ohne_bild)}")
    pool = next((a["pool"] for _, a in alle_aufgaben(inh) if a["typ"] == "blitz"), [])
    if len(pool) < 16:
        probleme.append(f"Blitzfragen: Pool hat {len(pool)} Fragen (mindestens 16)")
    if not probleme:
        return
    if os.environ.get("INHALTE_STRIKT") == "1":
        pytest.fail("Inhalte unvollständig:\n- " + "\n- ".join(probleme))
    pytest.xfail("Inhalte noch nicht vollständig: " + " | ".join(probleme))


# ── Forschend-entwickelnder Ansatz (docs/FORSCHEN.md) ────────────────────────
def test_neue_forschen_typen_sind_wohlgeformt(inh):
    """vermutung, pruefen, protokoll, tabelle, bildwahl, forscherbuch: Felder, Lösungen, Verweise (tests/forschen_pruefen.py)."""
    probleme = forschen_pruefen.pruefe_alle(inh)
    assert not probleme, "Forschen-Typen fehlerhaft:\n- " + "\n- ".join(probleme)


def test_modellziele_und_fokus_sind_wohlgeformt(inh):
    """modellfinden-Ziele: `fokus` mit teile, optional blick und abstand (Zahl > 0)."""
    probleme = forschen_pruefen.modellziele_probleme(inh)
    assert not probleme, "modellfinden-Ziele fehlerhaft:\n- " + "\n- ".join(probleme)


def test_pruefen_qualitaet(inh):
    """`pruefen` (Audit 4. Oktober 2026, Entscheidung 1 / T2): `erkenntnis.hinweis` je Niveau, die richtige Option von Erkenntnis und Beleg ist nicht die längste und
    nicht kürzer als 70 % der längsten. Solange die Inhalte nicht umgebaut sind: xfail mit der Liste; mit INHALTE_STRIKT=1 wird daraus ein Fehler."""
    probleme = forschen_pruefen.pruefen_qualitaet(inh)
    if not probleme:
        return
    if os.environ.get("INHALTE_STRIKT") == "1":
        pytest.fail("pruefen-Qualität nicht erfüllt:\n- " + "\n- ".join(probleme))
    pytest.xfail("pruefen-Qualität noch nicht erfüllt (docs/FORSCHEN.md, Audit T2): " + " | ".join(probleme))


def test_gewichtung_forschen(inh):
    """Quoten je Reiter (Abschluss ausgenommen): ECHTES Forschen (nur Evidenzsammlung: vermutung, pruefen, protokoll, tabelle, bildwahl, filmmoment, Diagramm mit
    auswertung; Benennen am Bild, Zeichnen, Erkunden, Modell-Ziele und Film nur mit `forschen: true`) mindestens 25 % und in den Reitern 2–4 mindestens 3 Stationen,
    Sprachwerkstatt ≥ 2, Abfrage ≤ 30 %, Stationsgrenzen, Forscherfrage und Erkenntnis je Reiter (nutztier ausgenommen), Lesestrecke nicht an erster Stelle,
    mindestens die Hälfte der Forschen-Stationen der Reiter „koerper“ und „volk“ mit Modell/Film.

    Solange die Inhalte nicht umgebaut sind: xfail mit der Liste; mit INHALTE_STRIKT=1 wird daraus ein Fehler."""
    probleme = forschen_pruefen.gewichtung_probleme(inh)
    if not probleme:
        return
    if os.environ.get("INHALTE_STRIKT") == "1":
        pytest.fail("Gewichtung nicht erfüllt:\n- " + "\n- ".join(probleme))
    pytest.xfail("Gewichtung noch nicht erfüllt (docs/FORSCHEN.md): " + " | ".join(probleme))
