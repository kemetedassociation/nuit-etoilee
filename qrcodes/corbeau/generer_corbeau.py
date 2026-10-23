"""QR code dans le corbeau KEMETED & ASSOCIATION.

Vectorise le corbeau officiel (corbeau-source.png), ouvre une fenêtre carrée dans
la plus grande zone libre du corps et y place le QR code. Le SVG est d'une seule
couleur, sans objet blanc : la fenêtre est un vrai trou dans la silhouette, donc
la graveuse grave le corbeau et les modules du QR, et rien d'autre.

Usage : python3 generer_corbeau.py [URL] [LARGEUR_MM]
"""
import os, sys
import numpy as np
import potrace, segno
from PIL import Image, ImageDraw, ImageFilter

URL = sys.argv[1] if len(sys.argv) > 1 else "https://kemetedassociation.github.io/nuit-etoilee/"
LARGEUR_MM = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
ICI = os.path.dirname(os.path.abspath(__file__))
ECHELLE = 4          # le contour est tracé sur l'image agrandie 4 fois, pour des courbes lisses
MARGE_QR = 3         # zone claire autour du QR, en modules
BORD = 0.022         # épaisseur de corbeau gardée autour de la fenêtre, en fraction de la largeur

# 1. Silhouette (le corbeau est défini par la transparence du PNG)
src = Image.open(os.path.join(ICI, "corbeau-source.png")).convert("RGBA")
alpha = src.getchannel("A").resize((src.width * ECHELLE, src.height * ECHELLE), Image.LANCZOS)
# léger flou avant le seuil : efface les marches de pixels de la petite image source
alpha = alpha.filter(ImageFilter.GaussianBlur(ECHELLE * 0.9))
noir = np.array(alpha) > 128
H, W = noir.shape

# 2. Corps « plein » : la silhouette avec l'œil et le trait de l'aile bouchés
# bordure claire autour de l'image : le corbeau touche les bords, sans elle le fond serait coupé en morceaux
# Le trait de l'aile rejoint le contour : on le referme d'abord (fermeture morphologique sur
# l'image source), sinon il couperait le corps en deux et la fenêtre irait se loger dans la tête.
ferme = src.getchannel("A").point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.MinFilter(11))
ferme = np.array(ferme.resize((W, H), Image.NEAREST)) > 0
fond = Image.fromarray(np.pad((~ferme).astype(np.uint8) * 255, 2, constant_values=255)).convert("L")
ImageDraw.floodfill(fond, (0, 0), 128)
plein = (np.array(fond)[2:-2, 2:-2] != 128) & (ferme | noir)

# 3. Plus grand carré dans le corps (calculé sur une grille réduite, puis remis à l'échelle)
r = 4
petit = plein[::r, ::r]
h, w = petit.shape
dp = np.zeros((h, w), dtype=np.int32)
best, by, bx = 0, 0, 0
for y in range(h):
    for x in range(w):
        if petit[y, x]:
            dp[y, x] = 1 if (y == 0 or x == 0) else 1 + min(dp[y-1, x], dp[y, x-1], dp[y-1, x-1])
            if dp[y, x] > best:
                best, by, bx = dp[y, x], y, x
cote = (best - 1) * r
x0, y0 = (bx - best + 1) * r, (by - best + 1) * r
bord = BORD * W
fx, fy, fc = x0 + bord, y0 + bord, cote - 2 * bord      # la fenêtre

# 4. QR code : on prend la meilleure correction d'erreur qui garde des modules lisibles
qr = segno.make(URL, error="h", micro=False)
n = len(qr.matrix)
if fc / (n + 2 * MARGE_QR) < W / 140:                   # modules trop fins : on repasse en niveau Q
    qr = segno.make(URL, error="q", micro=False); n = len(qr.matrix)
mod = fc / (n + 2 * MARGE_QR)
rayon = mod * 1.2

# 5. Silhouette percée de la fenêtre, puis vectorisation
fen = Image.new("L", (W, H), 0)
ImageDraw.Draw(fen).rounded_rectangle([fx, fy, fx + fc, fy + fc], radius=rayon, fill=255)
masque = noir & ~(np.array(fen) > 0)
# potracer considère « faux » comme l'encre : on lui passe donc le négatif
trace = potrace.Bitmap(~masque).trace(turdsize=40, alphamax=1.15, opticurve=True, opttolerance=0.4)

def f(v): return f"{v:.2f}".rstrip("0").rstrip(".")
d = []
for courbe in trace:
    p = courbe.start_point
    d.append(f"M{f(p.x)} {f(p.y)}")
    for s in courbe.segments:
        if s.is_corner:
            d.append(f"L{f(s.c.x)} {f(s.c.y)}L{f(s.end_point.x)} {f(s.end_point.y)}")
        else:
            d.append(f"C{f(s.c1.x)} {f(s.c1.y)} {f(s.c2.x)} {f(s.c2.y)} {f(s.end_point.x)} {f(s.end_point.y)}")
    d.append("Z")

# 6. Modules du QR, fusionnés par lignes
qx, qy = fx + MARGE_QR * mod, fy + MARGE_QR * mod
mods = []
for y, ligne in enumerate(qr.matrix):
    x = 0
    while x < n:
        if ligne[x]:
            x1 = x
            while x < n and ligne[x]: x += 1
            mods.append(f"M{f(qx + x1*mod)} {f(qy + y*mod)}h{f((x-x1)*mod)}v{f(mod)}h{f(-(x-x1)*mod)}z")
        else:
            x += 1

haut_mm = LARGEUR_MM * H / W
svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{f(LARGEUR_MM)}mm" height="{f(haut_mm)}mm" viewBox="0 0 {W} {H}">
<title>Corbeau KEMETED &amp; ASSOCIATION — QR Nuit Étoilée</title>
<desc>{URL}</desc>
<path fill="#000000" fill-rule="evenodd" d="{"".join(d)}"/>
<path fill="#000000" shape-rendering="crispEdges" d="{"".join(mods)}"/>
</svg>
'''
sortie = os.path.join(ICI, "corbeau-qr-nuit-etoilee.svg")
open(sortie, "w", encoding="utf-8").write(svg)
qr_mm = n * mod * LARGEUR_MM / W
print(f"SVG : {sortie}")
print(f"Corbeau {LARGEUR_MM:.0f} x {haut_mm:.0f} mm · QR version {qr.version}-{qr.error} · {n} modules · "
      f"QR {qr_mm:.1f} mm · module {qr_mm/n:.2f} mm")
