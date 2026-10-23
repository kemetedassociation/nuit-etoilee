"""Génère les QR codes des contes (SVG pour la graveuse laser + PNG).
Usage : python3 generer.py [URL_DE_BASE]
Si le site change d'adresse, relancer avec la nouvelle URL."""
import sys, os, segno
from PIL import Image, ImageDraw, ImageFont

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://claude.ai/artifact/KtyVzxwcx2NUoTFc5EXXmF"
ICI = os.path.dirname(os.path.abspath(__file__))
CONTES = [
 ("accueil", "Accueil", "Nuit Étoilée · Contes du monde"),
 ("conte-1", "Conte I · Mali", "Le secret de Sigui"),
 ("conte-2", "Conte II · Sahel", "Le chemin de lait"),
 ("conte-3", "Conte III · Maghreb", "Les noms donnés aux étoiles"),
 ("conte-4", "Conte IV · Grèce antique", "Le chasseur et le scorpion"),
 ("conte-5", "Conte V · Chine", "La tisserande et le bouvier"),
 ("conte-6", "Conte VI · Australie", "Les ombres du fleuve céleste"),
 ("conte-7", "Conte VII · Égypte ancienne", "Le corps étoilé de Nout"),
 ("conte-8", "Conte VIII · Scandinavie", "La poursuite éternelle"),
 ("conte-9", "Conte IX · Amérique du Nord", "La grande chasse à l'ours céleste"),
 ("conte-10", "Conte X · Inde", "Chandra et les vingt-sept épouses"),
]
TAILLE_MM = 40      # taille du QR (zone de silence comprise) dans le SVG
MARGE = 4           # zone de silence en modules (norme : 4)

for d in ("svg", "png", "png-avec-titre"): os.makedirs(os.path.join(ICI, d), exist_ok=True)
def police(t):
    for f in ("/System/Library/Fonts/Supplemental/Georgia.ttf", "/Library/Fonts/Georgia.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try: return ImageFont.truetype(f, t)
        except OSError: pass
    return ImageFont.load_default()

for i, (ancre, kicker, titre) in enumerate(CONTES):
    url = f"{BASE}#{ancre}"
    qr = segno.make(url, error="h", micro=False)
    nom = f"{i:02d}-{ancre}" if ancre != "accueil" else "00-accueil"
    m = qr.matrix; n = len(m); tot = n + 2*MARGE
    # SVG : un seul tracé noir, carrés fusionnés par lignes, dimension en mm
    segs = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]: x += 1
                segs.append(f"M{x0+MARGE} {y+MARGE}h{x-x0}v1h-{x-x0}z")
            else: x += 1
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{TAILLE_MM}mm" height="{TAILLE_MM}mm" viewBox="0 0 {tot} {tot}" shape-rendering="crispEdges">\n'
           f'<title>{kicker} — {titre}</title>\n<path fill="#000000" d="{"".join(segs)}"/>\n</svg>\n')
    open(os.path.join(ICI, "svg", nom + ".svg"), "w", encoding="utf-8").write(svg)
    # PNG nu : 2048 px environ, noir et blanc pur
    echelle = 2048 // tot
    qr.save(os.path.join(ICI, "png", nom + ".png"), scale=echelle, border=MARGE, dark="#000000", light="#ffffff")
    # PNG avec titre (impression)
    img = Image.open(os.path.join(ICI, "png", nom + ".png")).convert("RGB")
    W = img.width; H = img.height + 300
    fond = Image.new("RGB", (W, H), "white"); fond.paste(img, (0, 0))
    d = ImageDraw.Draw(fond)
    for txt, t, y in ((kicker.upper(), 56, img.height + 10), (titre, 92, img.height + 100)):
        f = police(t)
        while d.textlength(txt, font=f) > W - 120: t -= 4; f = police(t)
        d.text((W/2, y), txt, font=f, fill="black", anchor="ma")
    fond.save(os.path.join(ICI, "png-avec-titre", nom + ".png"), dpi=(600, 600))
    print(nom, "→", url)
