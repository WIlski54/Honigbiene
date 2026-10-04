"""Prüfungen am Stylesheet, die aus echten Darstellungsfehlern entstanden sind.

Hintergrund: Um ein Touch-Ziel auf 44 px zu bringen, war der Glossarlink im
Fließtext mit `padding: 9px 6px; margin: -9px 0` aufgeblasen worden. Der gelbe
Hintergrund ragte dadurch 5–6 px in die Zeilen darüber und darunter und verdeckte
dort Buchstaben. Inline-Ziele in einem Satz sind von der 44-px-Regel ausgenommen
(WCAG 2.5.8, „inline exception“) – sie werden durch die Zeilenhöhe begrenzt.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = open(os.path.join(ROOT, "static", "css", "app.css"), encoding="utf-8").read()


def regel(selektor: str) -> str:
    """Erste Regel zu genau diesem Selektor (ohne Kommentare davor)."""
    m = re.search(re.escape(selektor) + r"\s*\{([^}]*)\}", CSS)
    assert m, f"Regel {selektor} nicht gefunden"
    return m.group(1)


def wert(block: str, eigenschaft: str):
    m = re.search(rf"(?:^|;)\s*{eigenschaft}\s*:\s*([^;]+)", block)
    return m.group(1).strip() if m else None


def _px(s):
    m = re.match(r"^(-?[\d.]+)px$", (s or "").strip())
    return float(m.group(1)) if m else None


def test_glossarlink_bleibt_in_seiner_zeile():
    """Der Kasten darf nicht höher werden als die Zeile – sonst verdeckt er Text."""
    block = regel(".glossar-link")

    # Kein negativer vertikaler Rand: Genau damit war der Kasten aus der Zeile gewachsen.
    rand = (wert(block, "margin") or "0").split()
    oben = _px(rand[0]) if rand else 0
    assert oben is None or oben >= 0, f"negativer oberer Rand: {rand}"
    assert wert(block, "margin-top") is None or (_px(wert(block, "margin-top")) or 0) >= 0

    # Vertikales Padding moderat halten.
    padding = (wert(block, "padding") or "0").split()
    senkrecht = _px(padding[0])
    assert senkrecht is not None and senkrecht <= 5, f"vertikales Padding zu groß: {padding}"

    # Eigene, kompakte Zeilenhöhe – „inherit“ übernähme die 2.0 des Lesetexts,
    # und der Kasten wäre wieder höher als die Zeile.
    lh = wert(block, "line-height")
    assert lh and lh != "inherit", "line-height fehlt oder erbt"
    assert float(lh) <= 1.4, f"line-height zu groß: {lh}"


def test_lesetext_hat_luft_zwischen_den_zeilen():
    """Genug Zeilenabstand für die Markierung – und besser lesbar für schwache Leser."""
    lh = wert(regel(".lese-text"), "line-height")
    assert lh and float(lh) >= 1.9, f"Zeilenabstand zu klein: {lh}"


def test_kasten_passt_rechnerisch_in_die_zeile():
    """Kastenhöhe = Schriftgröße · line-height + 2 · Padding ≤ Zeilenhöhe des Textes."""
    link = regel(".glossar-link")
    text = regel(".lese-text")
    schrift_rem = float(re.match(r"([\d.]+)rem", wert(text, "font-size")).group(1))
    schrift_px = schrift_rem * 16
    kasten = schrift_px * float(wert(link, "line-height")) + 2 * _px((wert(link, "padding") or "0").split()[0])
    zeile = schrift_px * float(wert(text, "line-height"))
    assert kasten <= zeile, f"Kasten {kasten:.1f}px > Zeile {zeile:.1f}px"


def test_kein_inline_element_wird_mit_negativem_rand_aufgeblasen():
    """Dasselbe Muster darf an keiner anderen Stelle im Stylesheet stehen."""
    treffer = []
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", CSS):
        selektor, block = m.group(1).strip().splitlines()[-1].strip(), m.group(2)
        if "display: inline" not in block:
            continue
        padding = (wert(block, "padding") or "0").split()
        rand = (wert(block, "margin") or "0").split()
        p_oben, m_oben = _px(padding[0]), _px(rand[0]) if rand else 0
        if p_oben and p_oben > 5 and m_oben is not None and m_oben < 0:
            treffer.append(selektor)
    assert not treffer, f"Inline-Elemente mit aufgeblasener Trefferfläche: {treffer}"
