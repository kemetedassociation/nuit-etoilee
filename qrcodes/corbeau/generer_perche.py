"""Corbeau KEMETED perché sur le QR code de la Nuit Étoilée.

Reprend le visuel corbeau-perche-source.png : le corbeau (avec ses griffes et sa
queue) est gardé tel quel et vectorisé ; le cadre est redessiné parfaitement carré
et le faux QR du visuel est remplacé par le vrai, avec une marge claire suffisante.

Fichiers produits :
  corbeau-perche-qr-xtool.svg  une seule couleur, sans objet blanc : pour la graveuse
  corbeau-perche-qr-site.svg   sur fond clair arrondi : pour le site et les écrans

Usage : python3 generer_perche.py [URL] [LARGEUR_MM]
"""
import os, sys
import numpy as np
import potrace, segno
from PIL import Image, ImageDraw, ImageFilter

URL = sys.argv[1] if len(sys.argv) > 1 else "https://kemetedassociation.github.io/nuit-etoilee/"
LARGEUR_MM = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
ICI = os.path.dirname(os.path.abspath(__file__))
K = 3                                  # tracé sur l'image agrandie 3 fois
FOND_SITE = "#f6efe0"

# Repères mesurés sur le visuel (en px de l'image 1254 x 1254)
CADRE_G, CADRE_D, CADRE_H = 300, 951, 607     # bords extérieurs gauche, droit, haut
EP = 25                                       # épaisseur du cadre
COTE = CADRE_D - CADRE_G                      # le cadre devient un carré de ce côté
MARGE_QR = 3                                  # zone claire autour du QR, en modules

src = Image.open(os.path.join(ICI, "corbeau-perche-source.png")).convert("L")
H0 = CADRE_H + COTE + 40
W, H = src.width * K, H0 * K
gris = Image.new("L", (src.width, H0), 255); gris.paste(src, (0, 0))
grand = gris.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(K * .7))
encre = np.array(grand) < 128

# 1. Corbeau : tout ce qui est au-dessus du cadre, plus la queue qui dépasse à droite
yy, xx = np.mgrid[0:H, 0:W]
corbeau = encre & ((yy < CADRE_H * K) | (xx > CADRE_D * K + 2 * K))
corbeau &= yy < (CADRE_H + 120) * K           # rien du faux QR

# 2. Cadre carré à coins arrondis (anneau : extérieur moins intérieur)
cadre = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(cadre)
x0, y0, x1, y1 = CADRE_G * K, CADRE_H * K, CADRE_D * K, (CADRE_H + COTE) * K
d.rounded_rectangle([x0, y0, x1, y1], radius=30 * K, fill=255)
d.rounded_rectangle([x0 + EP * K, y0 + EP * K, x1 - EP * K, y1 - EP * K], radius=10 * K, fill=0)
dessin = corbeau | (np.array(cadre) > 0)

# 3. Vectorisation (potracer prend « faux » pour l'encre)
trace = potrace.Bitmap(~dessin).trace(turdsize=25, alphamax=1.0, opticurve=True, opttolerance=0.25)
def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")
chemin = []
for cb in trace:
    p = cb.start_point
    chemin.append(f"M{f(p.x)} {f(p.y)}")
    for s in cb.segments:
        if s.is_corner: chemin.append(f"L{f(s.c.x)} {f(s.c.y)}L{f(s.end_point.x)} {f(s.end_point.y)}")
        else: chemin.append(f"C{f(s.c1.x)} {f(s.c1.y)} {f(s.c2.x)} {f(s.c2.y)} {f(s.end_point.x)} {f(s.end_point.y)}")
    chemin.append("Z")

# 4. Vrai QR code, correction H (30 %), centré dans le cadre
qr = segno.make(URL, error="h", micro=False)
n = len(qr.matrix)
interieur = (COTE - 2 * EP) * K
mod = interieur / (n + 2 * MARGE_QR)
qx, qy = x0 + EP * K + MARGE_QR * mod, y0 + EP * K + MARGE_QR * mod
mods = []
for y, ligne in enumerate(qr.matrix):
    x = 0
    while x < n:
        if ligne[x]:
            a = x
            while x < n and ligne[x]: x += 1
            mods.append(f"M{f(qx + a*mod)} {f(qy + y*mod)}h{f((x-a)*mod)}v{f(mod)}h{f(-(x-a)*mod)}z")
        else: x += 1

# 5. Cadrage serré autour du dessin
lignes, colonnes = np.where(dessin)
m = 20 * K
vx, vy = colonnes.min() - m, lignes.min() - m
vw, vh = colonnes.max() + m - vx, lignes.max() + m - vy
haut_mm = LARGEUR_MM * vh / vw

def svg(site):
    fond = f'<rect x="{f(vx)}" y="{f(vy)}" width="{f(vw)}" height="{f(vh)}" rx="{f(60*K)}" fill="{FOND_SITE}"/>\n' if site else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(LARGEUR_MM)}mm" height="{f(haut_mm)}mm" viewBox="{f(vx)} {f(vy)} {f(vw)} {f(vh)}">\n'
            f'<title>Corbeau KEMETED &amp; ASSOCIATION — QR Nuit Étoilée</title>\n<desc>{URL}</desc>\n'
            f'{fond}<path fill="#000000" fill-rule="evenodd" d="{"".join(chemin)}"/>\n'
            f'<path fill="#000000" shape-rendering="crispEdges" d="{"".join(mods)}"/>\n</svg>\n')

open(os.path.join(ICI, "corbeau-perche-qr-xtool.svg"), "w", encoding="utf-8").write(svg(False))
open(os.path.join(ICI, "corbeau-perche-qr-site.svg"), "w", encoding="utf-8").write(svg(True))
qr_mm = n * mod * LARGEUR_MM / vw
print(f"{LARGEUR_MM:.0f} x {haut_mm:.0f} mm · QR version {qr.version}-{qr.error} · {n} modules · QR {qr_mm:.1f} mm · module {qr_mm/n:.2f} mm")
