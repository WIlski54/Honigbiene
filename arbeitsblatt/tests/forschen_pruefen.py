"""Strukturprüfungen für die Forschen-Typen und die Gewichtung (docs/FORSCHEN.md) – als reine Funktionen.

Dieselben Funktionen prüfen die echten Inhalte (tests/test_inhalte_struktur.py), die Test-Fixtures und die Beispiele aus
docs/FORSCHEN_BEISPIELE.js (tests/test_forschen.py). Jede Funktion liefert eine Liste verständlicher Meldungen; leer = in Ordnung.
Weiche Hinweise (Touchziele, Wortzahl) kommen als Warnungen über `warnings`, nicht als Fehler.
"""
import os
import re
import warnings

from inhalte_laden import ROOT
from plan import (ABFRAGE_TYPEN, ECHT_FORSCHEN_TYPEN, QUOTE_ABFRAGE_MAX, SPRACHWERKSTATT_MIN,
                  STATIONEN_MAX_ABSCHLUSS, max_stationen, min_forschen, min_forschen_anzahl, vermutung_pflicht)

FILM_BEFEHLE = {"springe", "spielen", "anhalten", "kapitel", "blick", "live", "ansicht", "stopp",
                "hervorheben", "beschriften", "nummern", "zurueck", "waehlen", "fokus"}
NEUE_TYPEN = ("vermutung", "pruefen", "protokoll", "tabelle", "bildwahl", "forscherbuch")
ZEILENARTEN = ("zahl", "wahl", "mehrfach", "text")
ID_MUSTER = re.compile(r"[a-z][a-z0-9_]*")


def _woerter(text):
    return len(re.sub(r"<[^>]+>", "", str(text)).split())


def _text(x):
    return isinstance(x, str) and bool(x.strip())


def _zahl(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _ganz(x):
    return isinstance(x, int) and not isinstance(x, bool)


def ist_bild_knopf(k):
    """Bild-Knopf: { bild, text, alt } ohne `film` – öffnet ein Bild im Bild-Fenster (für Stationen ohne Film/Modell)."""
    return isinstance(k, dict) and bool(k.get("bild")) and not k.get("film")


def knopf_liste(m):
    """`modell` ist ein Knopf ODER eine Liste von Knöpfen (Aufgabe, Zeile in protokoll/tabelle)."""
    return [x for x in (m if isinstance(m, list) else [m] if m else [])]


def _modell(k, inh, wer):
    """Ein Knopf `modell` (Aufgabenebene oder Zeile) oder eine Liste von Knöpfen: Film vorhanden, Befehle erlaubt, Bild-Knopf mit Datei und alt."""
    if isinstance(k, list):
        if not k:
            return [f"{wer}: modell ist eine leere Liste"]
        p = []
        for j, x in enumerate(k, start=1):
            p += _modell(x, inh, f"{wer}[{j}]")
        return p
    p = []
    if ist_bild_knopf(k):
        pfad = str(k["bild"]).split("?")[0].lstrip("/")
        if not os.path.isfile(os.path.join(ROOT, pfad)):
            p.append(f"{wer}: Bilddatei fehlt ({k['bild']})")
        if not _text(k.get("text")):
            p.append(f"{wer}: modell.text fehlt")
        if not _text(k.get("alt")):
            p.append(f"{wer}: modell.alt (Bildbeschreibung) fehlt")
        return p
    if not isinstance(k, dict) or k.get("film") not in inh["filme"]:
        return [f"{wer}: modell.film fehlt oder ist unbekannt"]
    if not _text(k.get("text")):
        p.append(f"{wer}: modell.text fehlt")
    if "spielen" in k and not isinstance(k["spielen"], bool):
        p.append(f"{wer}: modell.spielen muss true oder false sein")
    if "pflicht" in k and not isinstance(k["pflicht"], bool):
        p.append(f"{wer}: modell.pflicht muss true oder false sein")
    art = inh["filme"][k["film"]]["art"]
    for b in k.get("befehle") or []:
        if b.get("mw") not in FILM_BEFEHLE:
            p.append(f"{wer}: unbekannter Befehl {b.get('mw')}")
        elif art == "papiertheater" and b["mw"] not in ("springe", "kapitel", "spielen", "anhalten"):
            p.append(f"{wer}: der Film kennt nur springe/kapitel/spielen/anhalten")
        elif art == "papiertheater" and b["mw"] == "kapitel" and not 1 <= b.get("n", 1) <= 12:
            p.append(f"{wer}: Kapitel 1–12")
        elif art == "papiertheater" and b["mw"] == "springe" and not (_zahl(b.get("t")) and b["t"] >= 0):
            p.append(f"{wer}: springe braucht t (Sekunden, ≥ 0)")
        elif b["mw"] == "fokus" and "abstand" in b and not (_zahl(b["abstand"]) and b["abstand"] > 0):
            p.append(f"{wer}: fokus.abstand muss eine Zahl > 0 sein")
        elif art != "papiertheater" and b["mw"] == "kapitel":
            p.append(f"{wer}: das 3D-Modell hat keine Kapitel")
    return p


def _optionen_ok(ops, wer, minimum=2, max_woerter=12):
    p = []
    if not isinstance(ops, list) or len(ops) < minimum:
        return [f"{wer}: mindestens {minimum} Optionen nötig"]
    if not all(_text(o) for o in ops):
        p.append(f"{wer}: Optionen müssen Text sein")
    elif len(set(ops)) != len(ops):
        p.append(f"{wer}: doppelte Optionen")
    elif any(_woerter(o) > max_woerter for o in ops):
        p.append(f"{wer}: Option länger als {max_woerter} Wörter")
    return p


def _ok_optionen(ops, wer, genau_eins=True):
    """Optionen als [{t, ok}] – genau eine (oder mindestens eine) richtig, mindestens zwei Optionen, Text ≤ 20 Wörter (Sätze auf Niveau C)."""
    p = []
    if not isinstance(ops, list) or len(ops) < 2:
        return [f"{wer}: mindestens 2 Optionen {{t, ok}} nötig"]
    if not all(isinstance(o, dict) and _text(o.get("t")) and isinstance(o.get("ok"), bool) for o in ops):
        return [f"{wer}: jede Option braucht t (Text) und ok (true/false)"]
    oks = sum(1 for o in ops if o["ok"])
    if genau_eins and oks != 1:
        p.append(f"{wer}: genau eine Option muss ok sein ({oks} gefunden)")
    if len({o["t"] for o in ops}) != len(ops):
        p.append(f"{wer}: doppelte Optionen")
    if any(_woerter(o["t"]) > 20 for o in ops):
        p.append(f"{wer}: Option länger als 20 Wörter")
    return p


def _niveaus(a, p, wer):
    n = a.get("niveaus")
    if not isinstance(n, dict) or sorted(n) != ["A", "B", "C"]:
        p.append(f"{wer}: niveaus A, B und C verlangt (gefunden: {sorted(n) if isinstance(n, dict) else n})")
        return {}
    return n


def pruefe_aufgabe(a, inh, vermutung_ids=None):
    """Prüft eine Aufgabe der neuen Typen. `vermutung_ids` = alle ids der Stationen `vermutung` im ganzen AB."""
    typ = a.get("typ")
    if typ not in NEUE_TYPEN:
        return []
    wer = f"Aufgabe {a.get('nr')} ({typ})"
    p = []
    if not (_text(a.get("eyebrow")) and _text(a.get("titel"))):
        p.append(f"{wer}: eyebrow und titel fehlen")
    if a.get("erkenntnis") is not None and not _text(a["erkenntnis"]):
        p.append(f"{wer}: erkenntnis muss ein Satz sein")
    elif a.get("erkenntnis") and _woerter(a["erkenntnis"]) > 30:
        p.append(f"{wer}: erkenntnis (Merksatz) ist zu lang")
    if a.get("modell") is not None:
        p += _modell(a["modell"], inh, f"{wer} modell")
    if typ == "forscherbuch":
        return p
    niv = _niveaus(a, p, wer)
    for n, c in niv.items():
        w = f"{wer} Niveau {n}"
        if not isinstance(c, dict):
            p.append(f"{w}: muss ein Objekt sein")
            continue
        if typ == "vermutung":
            p += _vermutung(a, n, c, w)
        elif typ == "pruefen":
            p += _pruefen(a, n, c, w, vermutung_ids)
        elif typ == "protokoll":
            p += _protokoll(a, n, c, w, inh)
        elif typ == "tabelle":
            p += _tabelle(c, w, inh)
        elif typ == "bildwahl":
            p += _bildwahl(c, w)
    if typ == "vermutung":
        if not (_text(a.get("id")) and ID_MUSTER.fullmatch(a["id"])):
            p.append(f"{wer}: id fehlt oder ist ungültig (Kleinbuchstaben, Ziffern, _ ; z. B. v_anzahl)")
    if typ == "pruefen" and not _text(a.get("erkenntnis")):
        p.append(f"{wer}: erkenntnis (Merksatz für das Forscherbuch) fehlt")
    return p


def _vermutung(a, n, c, w):
    p = []
    ops = c.get("optionen")
    if n == "A":
        p += _optionen_ok(ops, w + " optionen")
    elif n == "B":
        p += _optionen_ok(ops, w + " optionen")
        if not _text(c.get("satzanfang")):
            p.append(f"{w}: satzanfang fehlt")
        if "begruendung" in c and not (isinstance(c["begruendung"], list) and all(_text(x) for x in c["begruendung"])):
            p.append(f"{w}: begruendung muss eine Liste von Bausteinen sein")
    else:
        if not (_text(c.get("satzanfang")) and c.get("frei") is True):
            p.append(f"{w}: satzanfang und frei: true verlangt")
        if ops is not None:
            p += _optionen_ok(ops, w + " optionen")
        if not _ganz(c.get("min")) or c["min"] < 20:
            p.append(f"{w}: min (Zeichen) von mindestens 20 verlangt")
    if "mehrfach" in c and not isinstance(c["mehrfach"], bool):
        p.append(f"{w}: mehrfach muss true oder false sein")
    if "min" in c and not _ganz(c["min"]):
        p.append(f"{w}: min muss eine ganze Zahl sein")
    return p


def _pruefen(a, n, c, w, vermutung_ids):
    p = []
    if vermutung_ids is not None and a.get("vermutung") not in vermutung_ids:
        p.append(f"{w}: vermutung „{a.get('vermutung')}“ verweist auf keine Station vermutung (ids: {sorted(vermutung_ids)})")
    elif vermutung_ids is None and not _text(a.get("vermutung")):
        p.append(f"{w}: vermutung (id) fehlt")
    erk = c.get("erkenntnis")
    if not isinstance(erk, dict):
        return p + [f"{w}: erkenntnis {{frage, optionen}} fehlt"]
    p += _ok_optionen(erk.get("optionen"), w + " erkenntnis")
    if n == "B":
        b = c.get("beleg")
        if not isinstance(b, dict):
            p.append(f"{w}: beleg {{frage, optionen}} fehlt")
        else:
            p += _ok_optionen(b.get("optionen"), w + " beleg")
    if n == "C":
        s = c.get("satz")
        if not (isinstance(s, dict) and _text(s.get("anfang")) and _ganz(s.get("min")) and s["min"] >= 20):
            p.append(f"{w}: satz {{anfang, min ≥ 20}} fehlt")
    return p


def _protokoll(a, n, c, w, inh):
    p = []
    zeilen = c.get("zeilen")
    if not isinstance(zeilen, list) or not zeilen:
        return [f"{w}: zeilen fehlen"]
    for i, z in enumerate(zeilen, start=1):
        zw = f"{w} Zeile {i}"
        art = z.get("art", "zahl")
        if not _text(z.get("frage")):
            p.append(f"{zw}: frage fehlt")
        if art not in ZEILENARTEN:
            p.append(f"{zw}: art {art!r} unbekannt")
            continue
        if art == "zahl":
            if not _zahl(z.get("loesung")):
                p.append(f"{zw}: loesung muss eine Zahl sein")
            if "toleranz" in z and not (_zahl(z["toleranz"]) and z["toleranz"] >= 0):
                p.append(f"{zw}: toleranz muss eine Zahl ≥ 0 sein")
            if "schritt" in z and not (_zahl(z["schritt"]) and z["schritt"] > 0):
                p.append(f"{zw}: schritt muss eine Zahl > 0 sein")
        elif art == "wahl":
            p += _optionen_ok(z.get("optionen"), zw + " optionen")
            if not (_ganz(z.get("loesung")) and isinstance(z.get("optionen"), list) and 0 <= z["loesung"] < len(z["optionen"])):
                p.append(f"{zw}: loesung muss der Index einer Option sein")
        elif art == "mehrfach":
            p += _optionen_ok(z.get("optionen"), zw + " optionen", minimum=3)
            ops = z.get("optionen") if isinstance(z.get("optionen"), list) else []
            ls = z.get("loesung")
            if not (isinstance(ls, list) and ls and all(_ganz(x) and 0 <= x < len(ops) for x in ls) and len(set(ls)) == len(ls) and len(ls) < len(ops)):
                p.append(f"{zw}: loesung muss eine Liste von Indizes sein (mindestens einer, nicht alle)")
        else:
            if "min" in z and not _ganz(z["min"]):
                p.append(f"{zw}: min muss eine ganze Zahl sein")
        for feld in ("hinweis", "hinweis2", "erklaerung", "fehlertext", "okText", "kurz", "einheit", "satzanfang"):
            if feld in z and not _text(z[feld]):
                p.append(f"{zw}: {feld} muss Text sein")
        if z.get("modell") is not None:
            p += _modell(z["modell"], inh, zw + " modell")
        if art != "text" and not (_text(z.get("hinweis"))):
            warnings.warn(f"{zw}: kein hinweis (nach zwei Fehlern gibt es sonst keinen Tipp)", stacklevel=2)
    s = c.get("schluss")
    if s is not None:
        if not isinstance(s, dict):
            p.append(f"{w}: schluss muss ein Objekt sein")
        else:
            bs = s.get("bausteine")
            if bs is not None:
                if not (isinstance(bs, list) and len(bs) >= 2):
                    p.append(f"{w}: schluss.bausteine braucht mindestens 2 Bausteine")
                else:
                    ok = [b for b in bs if isinstance(b, str) or (isinstance(b, dict) and b.get("ok") is not False)]
                    if not all(_text(b if isinstance(b, str) else (b.get("t") if isinstance(b, dict) else None)) for b in bs):
                        p.append(f"{w}: schluss.bausteine müssen Text oder {{t, ok}} sein")
                    elif not ok:
                        p.append(f"{w}: schluss.bausteine: mindestens ein Baustein muss stimmen")
            elif "min" in s and not _ganz(s["min"]):
                p.append(f"{w}: schluss.min muss eine ganze Zahl sein")
            if not _text(s.get("anfang")) and bs is not None:
                p.append(f"{w}: schluss.anfang fehlt")
    return p


def spaltenname(s):
    """Überschrift einer Tabellenspalte: Text oder Objekt { name, bild, alt } (wie forschen.js spaltenName)."""
    return s.get("name") if isinstance(s, dict) else s


def _bild_ok(x, wer):
    """Spalten- und Zeilenbilder: Datei vorhanden und `alt` (Bildbeschreibung) nicht leer. x = Objekt mit bild/alt; ohne `bild`
    gibt es nichts zu prüfen (eine Spalte nur mit `name` ist erlaubt)."""
    if not isinstance(x, dict) or "bild" not in x:
        return []
    p = []
    pfad = str(x.get("bild") or "").split("?")[0].lstrip("/")
    if not pfad or not os.path.isfile(os.path.join(ROOT, pfad)):
        p.append(f"{wer}: Bilddatei fehlt ({x.get('bild')})")
    if not _text(x.get("alt")):
        p.append(f"{wer}: alt (Bildbeschreibung) fehlt")
    return p


def _tabelle(c, w, inh):
    p = []
    sp, zeilen = c.get("spalten"), c.get("zeilen")
    if not (isinstance(sp, list) and len(sp) >= 2 and all(_text(spaltenname(x)) for x in sp)):
        return [f"{w}: spalten (mindestens 2 Überschriften, Text oder {{ name, bild, alt }}) fehlen"]
    namen = [spaltenname(x) for x in sp]
    if len(set(namen)) != len(namen):
        p.append(f"{w}: doppelte Spaltenüberschriften")
    for j, x in enumerate(sp, start=1):
        p += _bild_ok(x, f"{w} Spalte {j} ({namen[j - 1]})")
    if not isinstance(zeilen, list) or not zeilen:
        return p + [f"{w}: zeilen fehlen"]
    for i, z in enumerate(zeilen, start=1):
        zw = f"{w} Zeile {i}"
        if not _text(z.get("merkmal")):
            p.append(f"{zw}: merkmal fehlt")
        p += _bild_ok(z, zw + " (Zeilenbild)")
        ops = z.get("optionen")
        p += _optionen_ok(ops, zw + " optionen", max_woerter=8)
        ls = z.get("loesung")
        if not (isinstance(ls, list) and len(ls) == len(sp) and isinstance(ops, list) and all(_ganz(x) and 0 <= x < len(ops) for x in ls)):
            p.append(f"{zw}: loesung braucht je Spalte den Index einer Option ({len(sp)} Werte)")
        if z.get("modell") is not None:
            p += _modell(z["modell"], inh, zw + " modell")
        for feld in ("hinweis", "hinweis2"):
            if feld in z and not _text(z[feld]):
                p.append(f"{zw}: {feld} muss Text sein")
    return p


def _bildwahl(c, w):
    p = []
    if "auftrag" in c and not _text(c["auftrag"]):
        p.append(f"{w}: auftrag muss Text sein")
    runden = c.get("runden")
    if not isinstance(runden, list) or not runden:
        return [f"{w}: runden fehlen"]
    for i, r in enumerate(runden, start=1):
        rw = f"{w} Runde {i}"
        pfad = str(r.get("bild", "")).split("?")[0].lstrip("/")
        if not pfad or not os.path.exists(os.path.join(ROOT, pfad)):
            p.append(f"{rw}: Bilddatei fehlt ({r.get('bild')})")
        if not (_ganz(r.get("breite")) and _ganz(r.get("hoehe"))):
            p.append(f"{rw}: breite und hoehe (Pixel im Bild) fehlen")
            continue
        if not _text(r.get("frage")):
            p.append(f"{rw}: frage fehlt")
        ziele = r.get("ziele")
        if not (isinstance(ziele, list) and len(ziele) >= 2):
            p.append(f"{rw}: mindestens 2 ziele nötig")
            continue
        if not any(z.get("ok") is True for z in ziele):
            p.append(f"{rw}: mindestens ein Ziel muss ok: true sein")
        for k, z in enumerate(ziele, start=1):
            if not (_zahl(z.get("x")) and _zahl(z.get("y")) and _zahl(z.get("r")) and isinstance(z.get("ok"), bool)):
                p.append(f"{rw} Ziel {k}: x, y, r (Zahlen) und ok (true/false) verlangt")
                continue
            if not (0 <= z["x"] <= r["breite"] and 0 <= z["y"] <= r["hoehe"]):
                p.append(f"{rw} Ziel {k}: Mittelpunkt liegt außerhalb des Bildes")
            if z["r"] < 60:
                warnings.warn(f"{rw} Ziel {k}: r = {z['r']} ist klein (Touchziel ≥ 44 px bei 375 px Breite braucht etwa r ≥ 60)", stacklevel=2)
        for feld in ("hinweis", "erklaerung"):
            if feld in r and not _text(r[feld]):
                p.append(f"{rw}: {feld} muss Text sein")
    return p


# ── Qualität von `pruefen` (Audit 4. Oktober 2026, Entscheidung 1 / T2) ──────
LAENGE_MIN_ANTEIL = 0.7        # die richtige Option ist nicht kürzer als 70 % der längsten


def _laengen_probleme(ops, wer):
    """Die richtige Option darf nicht (allein) die längste sein und nicht kürzer als 70 % der längsten – sonst rät man nach der Länge."""
    if not isinstance(ops, list) or len(ops) < 2 or not all(isinstance(o, dict) and _text(o.get("t")) for o in ops):
        return []                                         # kaputte Optionen meldet _ok_optionen
    laengen = [len(o["t"].strip()) for o in ops]
    laengste = max(laengen)
    p = []
    for i, o in enumerate(ops):
        if not o.get("ok"):
            continue
        if laengen[i] == laengste and laengen.count(laengste) == 1:
            p.append(f"{wer}: die richtige Option ist die längste ({laengen[i]} Zeichen) – alle Optionen gleich lang und gleich gebaut formulieren")
        elif laengen[i] < LAENGE_MIN_ANTEIL * laengste:
            p.append(f"{wer}: die richtige Option ist zu kurz ({laengen[i]} Zeichen, die längste hat {laengste}; mindestens {int(LAENGE_MIN_ANTEIL * 100)} %)")
    return p


def pruefen_qualitaet(inh):
    """Qualitätsregeln für `pruefen` (über die Strukturprüfung hinaus): `erkenntnis.hinweis` je Niveau Pflicht (kommt nach zwei Fehlern),
    die richtige Option von Erkenntnis und Beleg ist nicht die längste und nicht kürzer als 70 % der längsten."""
    p = []
    for t in inh["tabs"]:
        for a in t["aufgaben"]:
            if a.get("typ") != "pruefen":
                continue
            for n, c in sorted((a.get("niveaus") or {}).items()):
                if not isinstance(c, dict):
                    continue
                w = f"Aufgabe {a.get('nr')} (pruefen) Niveau {n}"
                erk = c.get("erkenntnis")
                if isinstance(erk, dict):
                    if not _text(erk.get("hinweis")):
                        p.append(f"{w}: erkenntnis.hinweis fehlt (der Tipp nach zwei Fehlern)")
                    p += _laengen_probleme(erk.get("optionen"), w + " erkenntnis")
                bel = c.get("beleg")
                if isinstance(bel, dict):
                    p += _laengen_probleme(bel.get("optionen"), w + " beleg")
    return p


# ── Ziele von `modellfinden` und `fokus`-Befehle ─────────────────────────────
def fokus_probleme(f, wer):
    """Ein `fokus`: { teile: [Teil, …], blick?: Text, abstand?: Zahl > 0 } (Ziel von modellfinden) bzw. der Befehl {mw: "fokus", teile, blick?, abstand?} an einem Knopf."""
    if not isinstance(f, dict):
        return [f"{wer}: fokus muss ein Objekt sein"]
    p = []
    teile = f.get("teile")
    if not (isinstance(teile, list) and teile and all(_text(t) for t in teile)):
        p.append(f"{wer}: fokus.teile fehlt (Liste mit mindestens einem Teil)")
    if "blick" in f and not _text(f["blick"]):
        p.append(f"{wer}: fokus.blick muss Text sein")
    if "abstand" in f and not (_zahl(f["abstand"]) and f["abstand"] > 0):
        p.append(f"{wer}: fokus.abstand muss eine Zahl > 0 sein")
    return p


def modellziele_probleme(inh):
    """Ziele der Aufgaben vom Typ `modellfinden`: Teil vorhanden, `fokus` wohlgeformt (teile/blick/abstand)."""
    p = []
    for t in inh["tabs"]:
        for a in t["aufgaben"]:
            if a.get("typ") != "modellfinden":
                continue
            for n, c in sorted((a.get("niveaus") or {}).items()):
                for i, z in enumerate((c or {}).get("ziele") or [], start=1):
                    if "fokus" in z:
                        p += fokus_probleme(z["fokus"], f"Aufgabe {a.get('nr')} Niveau {n} Ziel {i}")
    return p


# ── Gesamtprüfung über alle Aufgaben ─────────────────────────────────────────
def pruefe_alle(inh):
    """Alle Aufgaben der neuen Typen + übergreifende Regeln (eindeutige ids, Verweise, genau ein Forscherbuch im Abschluss)."""
    alle = [(t["key"], a) for t in inh["tabs"] for a in t["aufgaben"]]
    ids = [a.get("id") for _, a in alle if a.get("typ") == "vermutung"]
    p = []
    if len(ids) != len(set(ids)):
        p.append(f"Vermutungs-ids nicht eindeutig: {sorted(i for i in set(ids) if ids.count(i) > 1)}")
    vorhanden = {i for i in ids if i}
    for key, a in alle:
        p += pruefe_aufgabe(a, inh, vorhanden)
    buecher = [(k, a["nr"]) for k, a in alle if a.get("typ") == "forscherbuch"]
    if len(buecher) > 1:
        p.append(f"höchstens ein Forscherbuch im AB (gefunden: {buecher})")
    if buecher and buecher[0][0] != "abschluss":
        p.append(f"Das Forscherbuch gehört in den Reiter „abschluss“ (steht in {buecher[0][0]})")
    return p


# ── Gewichtung (docs/FORSCHEN.md, „Gewichtung“) ──────────────────────────────
def ist_sprachwerkstatt(a):
    return str(a.get("eyebrow", "")).strip().startswith("Sprachwerkstatt")


def forschen_schalter(a):
    """`forschen: true` an der Aufgabe oder an einer Niveau-Konfiguration: die Station sammelt Evidenz, obwohl ihr Typ sonst nur „Anwenden“ ist."""
    if a.get("forschen") is True:
        return True
    return any(isinstance(c, dict) and c.get("forschen") is True for c in (a.get("niveaus") or {}).values())


def zaehlt_als_forschen(a):
    """Ehrliche Zählung (Audit 4. Oktober 2026, Entscheidung 3): Forschen zählt nur, wo das Kind EVIDENZ sammelt – ECHT_FORSCHEN_TYPEN.
    `bildpunkte` (Benennen/Einordnen), `erkunden`, `modellfinden`, `film` und `zeichnen` sind Anwenden/Vokabeln und zählen nur mit `forschen: true`.
    `forschen: false` nimmt auch einen echten Typ aus der Zählung."""
    if a.get("typ") == "diagramm":
        return bool(a.get("auswertung"))          # Diagramm nur mit Auswertung (Feld `auswertung`, siehe FORSCHEN.md)
    if a.get("typ") in ECHT_FORSCHEN_TYPEN:
        return a.get("forschen") is not False
    return forschen_schalter(a)


def _mit_film_oder_modell(m):
    """Enthält `modell` (Knopf oder Liste) mindestens einen Film-/Modell-Knopf? (Ein reiner Bild-Knopf zählt nicht.)"""
    return any(isinstance(k, dict) and k.get("film") for k in knopf_liste(m))


def arbeitet_mit_modell(a):
    """Arbeitet die Station unmittelbar mit Modell oder Film? (Typ, Aufgaben-Knopf oder Zeilen-/Zellen-Knopf; ein reiner Bild-Knopf zählt nicht)"""
    if a.get("typ") in ("erkunden", "modellfinden", "film", "filmmoment") or _mit_film_oder_modell(a.get("modell")):
        return True
    for c in (a.get("niveaus") or {}).values():
        if any(isinstance(z, dict) and _mit_film_oder_modell(z.get("modell")) for z in (c.get("zeilen") or []) if isinstance(c, dict)):
            return True
    return False


def gewichtung(tab):
    """Kennzahlen eines Reiters (Lesestrecke zählt nicht mit, siehe FORSCHEN.md)."""
    aufg = tab["aufgaben"]
    n = len(aufg)
    forschen = [a for a in aufg if zaehlt_als_forschen(a)]
    sprach = [a for a in aufg if ist_sprachwerkstatt(a)]
    abfrage = [a for a in aufg if a.get("typ") in ABFRAGE_TYPEN and not ist_sprachwerkstatt(a)]
    return {"n": n, "forschen": len(forschen), "sprach": len(sprach), "abfrage": len(abfrage),
            "mit_modell": len([a for a in forschen if arbeitet_mit_modell(a)]),
            "stationen": n + (1 if tab.get("lese") else 0)}


def gewichtung_probleme(inh):
    """Liste aller Verstöße gegen die Gewichtung. Abschluss ist von den Quoten ausgenommen (nur ≤ 6 Stationen)."""
    p = []
    vermutungen = {a.get("id") for t in inh["tabs"] for a in t["aufgaben"] if a.get("typ") == "vermutung"}
    for tab in inh["tabs"]:
        key = tab["key"]
        g = gewichtung(tab)
        if key == "abschluss":
            if g["stationen"] > STATIONEN_MAX_ABSCHLUSS:
                p.append(f"{key}: {g['stationen']} Stationen (höchstens {STATIONEN_MAX_ABSCHLUSS})")
            continue
        if not g["n"]:
            p.append(f"{key}: keine Stationen")
            continue
        if g["forschen"] < min_forschen(key) * g["n"] - 1e-9:
            p.append(f"{key}: nur {g['forschen']} von {g['n']} Stationen forschend (mindestens {int(min_forschen(key) * 100)} %)")
        if g["forschen"] < min_forschen_anzahl(key):
            p.append(f"{key}: nur {g['forschen']} echte Forschen-Stationen (mindestens {min_forschen_anzahl(key)}; zählen: {', '.join(sorted(ECHT_FORSCHEN_TYPEN))}, "
                     f"Diagramm mit auswertung, sonst nur mit forschen: true)")
        if g["sprach"] < SPRACHWERKSTATT_MIN:
            p.append(f"{key}: {g['sprach']} Sprachwerkstatt-Stationen (mindestens {SPRACHWERKSTATT_MIN}; eyebrow beginnt mit „Sprachwerkstatt“)")
        if g["abfrage"] > QUOTE_ABFRAGE_MAX * g["n"] + 1e-9:
            p.append(f"{key}: {g['abfrage']} von {g['n']} Stationen sind reine Abfrage/Sicherung (höchstens {int(QUOTE_ABFRAGE_MAX * 100)} %)")
        if g["stationen"] > max_stationen(key):
            p.append(f"{key}: {g['stationen']} Stationen inklusive Lesestrecke (höchstens {max_stationen(key)})")
        if vermutung_pflicht(key):                    # „nutztier“ (OHNE_VERMUTUNG) braucht weder Forscherfrage noch Prüfen
            if not any(a.get("typ") == "vermutung" for a in tab["aufgaben"]):
                p.append(f"{key}: keine Forscherfrage (Station vom Typ vermutung)")
            if not any(a.get("typ") == "pruefen" or a.get("erkenntnis") for a in tab["aufgaben"]):
                p.append(f"{key}: die Forschungsphase endet nicht mit einem pruefen oder einem Erkenntnissatz (Feld erkenntnis)")
        if tab.get("lese") and not tab.get("leseNach"):
            p.append(f"{key}: die Lesestrecke steht an erster Stelle (leseNach fehlt) – sie kommt erst nach der ersten Erkundung")
        if key in ("koerper", "volk") and g["forschen"] and g["mit_modell"] < 0.5 * g["forschen"]:
            p.append(f"{key}: nur {g['mit_modell']} von {g['forschen']} Forschen-Stationen arbeiten mit Modell oder Film (mindestens die Hälfte)")
        for a in tab["aufgaben"]:
            if a.get("typ") == "pruefen" and a.get("vermutung") not in vermutungen:
                p.append(f"{key}/{a.get('nr')}: pruefen.vermutung „{a.get('vermutung')}“ verweist auf keine vermutung.id")
    return p
