# ️PWA Asset Generator

Script Python permettant de générer automatiquement un set complet d’icônes pour vos PWA (manifest icons, favicon, logo) à partir d’une image source.

Résultat :
- Un fichier `manifest.json` prêt à être complété et déployé.
- Des icônes carrées et centrées (optimales pour l’affichage de votre logo sur smartphone), générées pour le dossier `manifest/`
- Un `logo.png` et un `favicon.ico` non centrés, conservant l’image originale pour une utilisation optimale dans vos headers, footers et onglets de navigateur.

## Prérequis
- Python 3.9+
- pip (gestionnaire de paquets Python)

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation
```bash
python main.py <nom_image> <nom_du_projet> [center]
```

Exemple :
python main.py great_logo.png nakas false

## Licence
Programme placé dans le domaine public.
