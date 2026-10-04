"""Stachelapparat der Honigbiene (Glossar Stachel) und Facetten-Lupe (Glossar Facettenauge).

`stachel_gross()`: lokale Koordinaten, Spitze links bei x ≈ −160, Giftblase rechts bis x ≈ +215, Mitte y = 0.
"""
import math
import random

from bienen_zeichnen import *  # noqa: F401,F403
import bienen_zeichnen as _bz

_bz.DEFS_EXTRA.append(
    "<linearGradient id='bStachel' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#e2a455'/><stop offset='.45' stop-color='#a8641c'/><stop offset='1' stop-color='#4a2808'/></linearGradient>"
    "<radialGradient id='bGiftBlase' cx='.4' cy='.3' r='.9'><stop offset='0' stop-color='#ffffff' stop-opacity='.95'/><stop offset='.35' stop-color='#d7eefb'/><stop offset='1' stop-color='#6fb0d6'/></radialGradient>"
    "<radialGradient id='bGiftInhalt' cx='.4' cy='.4' r='.8'><stop offset='0' stop-color='#fff6c8'/><stop offset='1' stop-color='#f2cf63'/></radialGradient>"
)


def stachel_gross(tropfen=True):
    """Stachelapparat mit Giftblase, Stachelbasis, Stachelrinne und Widerhaken."""
    o = []
    # Giftdrüse (feine Fäden) und Giftblase
    o.append("<path d='M200,-18 C222,-40 236,-30 230,-14 M202,10 C226,24 240,10 232,-4' fill='none' stroke='#a9d0e6' stroke-width='3.2' stroke-linecap='round'/>"
             "<path d='M200,-18 C222,-40 236,-30 230,-14 M202,10 C226,24 240,10 232,-4' fill='none' stroke='#eaf6ff' stroke-width='1.1' stroke-linecap='round'/>")
    sack = "M96,-8 C100,-34 140,-46 176,-34 C206,-24 214,0 204,20 C192,42 150,46 120,34 C100,26 94,10 96,-8 Z"
    o.append(f"<path d='{sack}' fill='url(#bGiftBlase)' stroke='#3d7fa8' stroke-width='2.2' stroke-linejoin='round'/>")
    o.append("<g transform='translate(150 2) scale(.74 .7) translate(-150 -2)'>"
             f"<path d='{sack}' fill='url(#bGiftInhalt)' opacity='.65'/></g>")
    o.append("<ellipse cx='140' cy='-22' rx='26' ry='7' fill='#fff' opacity='.85' transform='rotate(-10 140 -22)'/>"
             "<circle cx='188' cy='14' r='3.6' fill='#fff' opacity='.7'/><circle cx='170' cy='26' r='2.4' fill='#fff' opacity='.6'/>")
    # Giftgang zur Stachelbasis
    o.append("<path d='M104,6 C92,6 84,4 74,2' fill='none' stroke='#3d7fa8' stroke-width='9' stroke-linecap='round'/>"
             "<path d='M104,6 C92,6 84,4 74,2' fill='none' stroke='#d7eefb' stroke-width='6' stroke-linecap='round'/>")
    # Stachelbasis (Wulst) mit Platten
    o.append("<path d='M82,-24 C58,-30 34,-22 28,-6 C26,10 44,24 70,24 C86,24 94,10 90,-6 Z' fill='url(#bStachel)' stroke='#2a1404' stroke-width='2' stroke-linejoin='round'/>"
             "<path d='M44,-14 C56,-20 70,-18 80,-12' fill='none' stroke='#f0c88a' stroke-width='2.2' stroke-linecap='round' opacity='.7'/>"
             "<path d='M36,2 C50,10 70,12 84,6' fill='none' stroke='#2a1404' stroke-width='1.4' opacity='.55'/>"
             "<path d='M60,-26 L76,-44 L88,-22 Z M64,24 L82,40 L90,18 Z' fill='#8a5214' stroke='#2a1404' stroke-width='1.6' stroke-linejoin='round'/>")
    # Stachelrinne (Schaft) zur Spitze links: kurz und kräftig, damit die Widerhaken sichtbar werden
    schaft = "M34,-13 C0,-12 -52,-7 -128,5 C-54,9 0,15 34,15 Z"
    o.append(f"<path d='{schaft}' fill='url(#bStachel)' stroke='#2a1404' stroke-width='2' stroke-linejoin='round'/>")
    o.append("<path d='M28,-7 C-8,-6 -62,-2 -118,5' fill='none' stroke='#f6dca8' stroke-width='2.6' stroke-linecap='round' opacity='.7'/>")
    # Lanzetten mit Widerhaken (zeigen nach hinten = zur Giftblase)
    barbs = ""
    for i in range(8):
        x = -118 + i * 12.4
        y = 6.2 + (x + 128) * .052
        barbs += f"M{x:.1f},{y:.1f} l13,{9 + i * .3:.1f} l-3.5,-9.4 z "
    o.append(f"<path d='{barbs}' fill='#d9a04c' stroke='#2a1404' stroke-width='1.5' stroke-linejoin='round'/>")
    ob = ""
    for i in range(5):
        x = -110 + i * 15
        y = 5.2 + (x + 128) * .028
        ob += f"M{x:.1f},{y:.1f} l9,-6 l-1,7 z "
    o.append(f"<path d='{ob}' fill='#b9772c' stroke='#2a1404' stroke-width='1.2' stroke-linejoin='round'/>")
    if tropfen:
        o.append("<g><ellipse cx='-138' cy='12' rx='7' ry='8' fill='url(#bNektar)' stroke='#c47500' stroke-width='1' opacity='.95'/>"
                 "<ellipse cx='-140.5' cy='9' rx='2' ry='3' fill='#fff' opacity='.85'/></g>")
    return "".join(o)
