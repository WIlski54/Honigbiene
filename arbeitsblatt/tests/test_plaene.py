"""Stationspläne (plan_<reiter>.py): Format, Eindeutigkeit und die frei platzierbare Lesestrecke."""
import config
from config import ABSCHNITTE, ALLE_AUFGABEN, AUFGABE_ZU_ABSCHNITT, AUFGABEN_TYPEN, LESE_NACH, LESESTRECKEN, ist_lesestrecke, lese_nach, nr_von_typ
from plan import AUFGABEN_PLAN, PLAENE


def test_plaene_sind_in_ordnung():
    assert config.pruefe_plaene() == []


def test_abschnitte_werden_aus_den_plan_dateien_gebaut():
    assert [a["key"] for a in ABSCHNITTE] == list(PLAENE)
    for a in ABSCHNITTE:
        assert a["aufgaben"] == list(PLAENE[a["key"]].STATIONEN)
        assert a["titel"] and a["kurz"]
    assert AUFGABEN_PLAN == AUFGABEN_TYPEN
    assert ALLE_AUFGABEN == [str(n) for a in ABSCHNITTE for n in a["aufgaben"]]
    assert all(AUFGABE_ZU_ABSCHNITT[str(n)] == a["key"] for a in ABSCHNITTE for n in a["aufgaben"])


def test_lesestrecke_darf_an_beliebiger_stelle_stehen():
    assert lese_nach(["L1", 1, 2]) is None            # oben
    assert lese_nach([1, 2, "L1", 3]) == 2            # nach Aufgabe 2
    assert lese_nach(["F1", "F2", "L2"]) == "F2"      # Zeichenketten-Nummern, ganz am Ende
    assert lese_nach([1, 2, 3]) == ""                 # Reiter ohne Lesestrecke
    assert [ist_lesestrecke(n) for n in ("L1", "L12", "T", "LX", 1, "l1")] == [True, True, False, False, False, False]


def test_lese_nach_passt_zu_den_plaenen():
    for a in ABSCHNITTE:
        erwartet = lese_nach(a["aufgaben"])
        if erwartet == "":
            assert a["key"] not in LESE_NACH
        else:
            assert LESE_NACH[a["key"]] == erwartet
    assert set(LESESTRECKEN.values()) == set(LESE_NACH)


def test_nr_von_typ_in_planreihenfolge():
    for typ in set(AUFGABEN_TYPEN.values()):
        nrs = nr_von_typ(typ)
        assert nrs and all(AUFGABEN_TYPEN[n] == typ for n in nrs)
    assert nr_von_typ("gibt-es-nicht") == []


def test_fehlerhafte_plaene_werden_gemeldet(monkeypatch):
    """pruefe_plaene() findet doppelte Nummern, fehlende Typen, kleine Buchstaben und zwei Lesestrecken."""
    import plan_nutztier
    monkeypatch.setattr(plan_nutztier, "STATIONEN", ["L1", "L2", 1, 1, "f1", "LX", 99, True])
    monkeypatch.setattr(plan_nutztier, "TYPEN", {1: "mc", 5: "mc"})
    probleme = " | ".join(config.pruefe_plaene())
    assert "mehr als eine Lesestrecke" in probleme
    assert "Nummer 1 steht in plan_nutztier und in plan_nutztier" in probleme       # doppelt
    assert "'f1' muss in GROSSBUCHSTABEN" in probleme and "'LX' muss in GROSSBUCHSTABEN" in probleme
    assert "99" in probleme and "nicht in TYPEN" in probleme
    assert "TYPEN kennt 5" in probleme
    assert "muss eine Zahl oder Zeichenkette sein" in probleme                       # True ist keine Nummer
