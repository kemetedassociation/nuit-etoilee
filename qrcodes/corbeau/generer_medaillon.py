"""Médaillon KEMETED & ASSOCIATION avec le QR code de la Nuit Étoilée dans le corbeau.

Reprend le visuel du médaillon (double anneau, corbeau, arc de lune, KEMETED,
& ASSOCIATION, trait), dessiné en vectoriel, avec un vrai QR code.

Fichiers produits :
  medaillon-kemeted-xtool.svg  une seule couleur, sans objet blanc : pour la graveuse
  medaillon-kemeted-site.svg   même dessin sur fond bois clair : pour le site et l'écran

Usage : python3 generer_medaillon.py [URL] [DIAMETRE_MM]
"""
import os, sys
import numpy as np
import potrace, segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

URL = sys.argv[1] if len(sys.argv) > 1 else "https://kemetedassociation.github.io/nuit-etoilee/"
DIAMETRE_MM = float(sys.argv[2]) if len(sys.argv) > 2 else 180.0
ICI = os.path.dirname(os.path.abspath(__file__))
POLICES = os.path.join(ICI, "polices")

N = 4000                 # dessin sur une toile de 4000 px, centre en (2000, 2000)
C = N / 2
RW = 2520                # largeur du corbeau
OX, OY = C - RW / 2 + 50, 420
MARGE_QR = 3             # zone claire autour du QR, en modules
BOIS, ENCRE = "#efe3cb", "#16120d"

encre = Image.new("L", (N, N), 0)
d = ImageDraw.Draw(encre)

# 1. Anneaux (un épais, un fin)
for r_ext, r_int in ((1985, 1925), (1888, 1868)):
    d.ellipse([C - r_ext, C - r_ext, C + r_ext, C + r_ext], fill=255)
    d.ellipse([C - r_int, C - r_int, C + r_int, C + r_int], fill=0)

# 2. Corbeau officiel, agrandi et lissé
src = Image.open(os.path.join(ICI, "corbeau-source.png")).convert("RGBA")
k = RW / src.width
RH = round(src.height * k)
alpha = src.getchannel("A").resize((RW, RH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(k * .9))
noir = np.array(alpha) > 128

# Corps plein (trait de l'aile refermé) pour trouver la plus grande fenêtre carrée
ferme = src.getchannel("A").point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.MinFilter(11))
ferme = np.array(ferme.resize((RW, RH), Image.NEAREST)) > 0
fond = Image.fromarray(np.pad((~ferme).astype(np.uint8) * 255, 2, constant_values=255)).convert("L")
ImageDraw.floodfill(fond, (0, 0), 128)
plein = (np.array(fond)[2:-2, 2:-2] != 128) & (ferme | noir)
r = 8
petit = plein[::r, ::r]
h, w = petit.shape
dp = np.zeros((h, w), dtype=np.int32)
best = by = bx = 0
for y in range(h):
    for x in range(w):
        if petit[y, x]:
            dp[y, x] = 1 if (y == 0 or x == 0) else 1 + min(dp[y-1, x], dp[y, x-1], dp[y-1, x-1])
            if dp[y, x] > best: best, by, bx = dp[y, x], y, x
cote = (best - 1) * r
bord = .022 * RW
fx, fy, fc = (bx - best + 1) * r + bord, (by - best + 1) * r + bord, cote - 2 * bord

# QR : correction M (15 %), assez robuste pour une gravure et avec de plus gros modules
qr = segno.make(URL, error="m", micro=False)
n = len(qr.matrix)
mod = fc / (n + 2 * MARGE_QR)
fen = Image.new("L", (RW, RH), 0)
ImageDraw.Draw(fen).rounded_rectangle([fx, fy, fx + fc, fy + fc], radius=mod * 1.2, fill=255)
corbeau = noir & ~(np.array(fen) > 0)

# 3. Arc de lune derrière le corbeau, interrompu autour de lui et en bas à gauche
ACX, ACY, AR, AE = C + 80, 1590, 1100, 24
yy, xx = np.mgrid[0:N, 0:N]
dist = np.hypot(xx - ACX, yy - ACY)
ang = (np.degrees(np.arctan2(yy - ACY, xx - ACX)) + 360) % 360
arc = (np.abs(dist - AR) <= AE / 2) & ~((ang > 18) & (ang < 140))
# écart autour du corbeau : silhouette élargie (calculée en petit puis remise à l'échelle)
halo = Image.fromarray((ferme | noir).astype(np.uint8) * 255).resize((RW // 4, RH // 4), Image.BILINEAR)
halo = np.array(halo.filter(ImageFilter.MaxFilter(23)).resize((RW, RH), Image.BILINEAR)) > 60
place = np.zeros((N, N), dtype=bool)
place[OY:OY + RH, int(OX):int(OX) + RW] = halo
arc &= ~place

e = np.array(encre) > 0
e |= arc
zone = np.zeros((N, N), dtype=bool)
zone[OY:OY + RH, int(OX):int(OX) + RW] = corbeau
e |= zone
encre = Image.fromarray(e.astype(np.uint8) * 255)
d = ImageDraw.Draw(encre)

# 4. Textes
cinzel = ImageFont.truetype(os.path.join(POLICES, "Cinzel.ttf"), 400)
try: cinzel.set_variation_by_axes([700])
except Exception: pass
d.text((C, 2985), "KEMETED", font=cinzel, fill=255, anchor="mm")

poppins = ImageFont.truetype(os.path.join(POLICES, "Poppins-Medium.ttf"), 170)
texte, espace = "& ASSOCIATION", 22
largeurs = [d.textlength(ch, font=poppins) for ch in texte]
total = sum(largeurs) + espace * (len(texte) - 1)
x, ys = C - total / 2, 3290
for ch, lw in zip(texte, largeurs):
    d.text((x, ys), ch, font=poppins, fill=255, anchor="lm")
    x += lw + espace
for sens in (-1, 1):                          # tirets de part et d'autre
    x0 = C + sens * (total / 2 + 60)
    x1 = x0 + sens * 150
    d.rectangle([min(x0, x1), ys - 9, max(x0, x1), ys + 9], fill=255)
d.rectangle([C - 620, 3500, C + 620, 3520], fill=255)   # trait du bas

# 5. Vectorisation (potracer prend « faux » pour l'encre)
trace = potrace.Bitmap(~(np.array(encre) > 127)).trace(turdsize=30, alphamax=1.0, opticurve=True, opttolerance=0.25)
def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")
chemin = []
for cb in trace:
    p = cb.start_point
    chemin.append(f"M{f(p.x)} {f(p.y)}")
    for s in cb.segments:
        if s.is_corner: chemin.append(f"L{f(s.c.x)} {f(s.c.y)}L{f(s.end_point.x)} {f(s.end_point.y)}")
        else: chemin.append(f"C{f(s.c1.x)} {f(s.c1.y)} {f(s.c2.x)} {f(s.c2.y)} {f(s.end_point.x)} {f(s.end_point.y)}")
    chemin.append("Z")

qx, qy = OX + fx + MARGE_QR * mod, OY + fy + MARGE_QR * mod
mods = []
for y, ligne in enumerate(qr.matrix):
    x = 0
    while x < n:
        if ligne[x]:
            x1 = x
            while x < n and ligne[x]: x += 1
            mods.append(f"M{f(qx + x1*mod)} {f(qy + y*mod)}h{f((x-x1)*mod)}v{f(mod)}h{f(-(x-x1)*mod)}z")
        else: x += 1

def svg(fond_bois):
    couleur = ENCRE if fond_bois else "#000000"
    disque = f'<circle cx="{f(C)}" cy="{f(C)}" r="1985" fill="{BOIS}"/>\n' if fond_bois else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(DIAMETRE_MM)}mm" height="{f(DIAMETRE_MM)}mm" viewBox="0 0 {N} {N}">\n'
            f'<title>KEMETED &amp; ASSOCIATION — médaillon QR Nuit Étoilée</title>\n<desc>{URL}</desc>\n'
            f'{disque}<path fill="{couleur}" fill-rule="evenodd" d="{"".join(chemin)}"/>\n'
            f'<path fill="{couleur}" shape-rendering="crispEdges" d="{"".join(mods)}"/>\n</svg>\n')

open(os.path.join(ICI, "medaillon-kemeted-xtool.svg"), "w", encoding="utf-8").write(svg(False))
open(os.path.join(ICI, "medaillon-kemeted-site.svg"), "w", encoding="utf-8").write(svg(True))
qr_mm = n * mod * DIAMETRE_MM / N
print(f"Médaillon Ø {DIAMETRE_MM:.0f} mm · QR version {qr.version}-{qr.error} · {n} modules · QR {qr_mm:.1f} mm · module {qr_mm/n:.2f} mm")
