# Nuit Étoilée · Contes du monde

Plateforme de l'événement **Nuit Étoilée** de KEMETED & Association (Salle Battant, Besançon) :
dix contes et mythes sur les étoiles, venus d'Afrique de l'Ouest, du Maghreb, de Grèce, de Chine,
d'Australie, d'Égypte, de Scandinavie, d'Amérique du Nord et d'Inde. Chaque conte est à lire et
à écouter avec son fond musical, puis à prolonger par des défis.

## Contenu
- **10 contes** avec texte complet, audio narré et musique, et « À observer ce soir ».
- **Défis** par conte : quiz, constellations à relier, puzzle, mémoire, cadenas, devinettes,
  jeux d'adresse (pont des pies, bouclier contre le loup Sköll, étoile invisible).
- **Deux modes** : *Petite étoile* (7–11 ans) et *Astronome* (12 ans et plus).
- **Énigme finale** : chaque conte réussi donne une lettre du mot secret.
- **Roue des contes** en 3D et **frise du voyage** animée au défilement (GSAP).
- Fonctionne sur téléphone, progression enregistrée sur l'appareil, hors ligne après la première visite.

Liens directs vers un conte : `…/#conte-1` à `…/#conte-10`.

## Structure
| Chemin | Rôle |
|---|---|
| `page.html` | Source de la page (styles, contenu et jeux) |
| `index.html` | Page publiée, générée par `./build.sh` à partir de `page.html` |
| `audio/` | Introduction et dix contes musicaux (MP3, volume harmonisé) |
| `img/` | Affiches des contes |
| `qrcodes/` | QR codes par conte : `svg/` pour la graveuse laser, `png/`, `png-avec-titre/` |
| `manifest.json`, `sw.js` | Installation sur téléphone et mode hors ligne |

## Modifier le site
1. Modifier `page.html`.
2. Lancer `./build.sh` pour régénérer `index.html`.
3. Committer et pousser : GitHub Pages republie automatiquement.

## Régénérer les QR codes
```sh
pip3 install segno pillow
python3 qrcodes/generer.py https://kemetedassociation.github.io/nuit-etoilee/
```

---
KEMETED & Association · *Sous le même ciel* · Salle Battant, 48 rue Battant, 25000 Besançon
