Système d’acquisition et d’analyse d’images time-lapse synchronisé

## Description du projet

**PRONTO** est un système d’imagerie time-lapse développé à l’**IMT Atlantique** pour l’**IUEM**, visant à observer des **diatomées au microscope**.  
Le dispositif combine :
- une **caméra IDS** pour la capture d’images haute fréquence,  
- une **carte Arduino** pour le pilotage de l’éclairage (LED),  
- des **scripts Python** pour la synchronisation, l’acquisition et le traitement des images.

Trois modes d’acquisition sont disponibles :
1. **Éclairage ON/OFF fixe**  
2. **Éclairage sinusoïdal**  
3. **Éclairage contrôlé via un fichier Excel**

Les images sont ensuite **traitées et analysées** (détection, création de vidéos, suivi d’objets, etc.).

---

## Architecture du projet

Structure des dossiers :
- `controle_arduino/` : scripts d’acquisition et de contrôle Arduino  
  - `codefinalenpy.py` : acquisition avec lumière ON/OFF  
  - `codefinalsinus.py` : acquisition avec lumière sinusoïdale  
  - `interfaceexcel.py` : acquisition via un fichier Excel (planning d’intensité)  
  - `codefinal.ino` : Arduino ON/OFF  
  - `codefinalsinus.ino` : Arduino sinus  
  - `interfaceexcel.ino` : Arduino Excel  
- `traitement_image/` : scripts de traitement et d’analyse  
  - `vid_detection.py` : détection et traitement des images  
  - `creation_videos.py` : création de vidéos timelapse  
- `README.md` : documentation du projet  

---

## Installation

### 1. Dépendances Python

pip install opencv-python numpy matplotlib pandas pyserial ids-peak ids-peak-ipl

Les bibliothèques `ids_peak` et `ids_peak_ipl` proviennent du SDK IDS Peak (caméras IDS).  
Téléchargez-les depuis : https://fr.ids-imaging.com/ids-peak.html

---

### 2. Matériel nécessaire

Caméra IDS Imaging (compatible SDK Peak)  
Carte Arduino Uno/Nano reliée à la LED  
Câble USB pour la communication série  
Source de lumière et support de montage  

---

## Utilisation

### 🔹 Mode 1 : Lumière ON/OFF

Scripts :
Python → codefinalenpy.py  
Arduino → codefinal.ino

Étapes :
1. Téléverser le code Arduino codefinal.ino  
2. Lancer le script Python :
   python3 codefinalenpy.py  
3. Les images sont enregistrées dans :
   /home/administrateur/Documents/Ingrid/distribution_z/images/Timelapse

---

### 🔹 Mode 2 : Lumière sinusoïdale

Scripts :
Python → codefinalsinus.py  
Arduino → codefinalsinus.ino

Étapes :
1. Téléverser le code Arduino correspondant  
2. Lancer le script :
   python3 codefinalesinus.py  
3. Une interface graphique s’ouvre pour définir :
   - Le nombre d’images à capturer  
   - L’intervalle entre deux captures (en secondes)  


---

### 🔹 Mode 3 : Lumière contrôlée par fichier Excel

Scripts :
Python → interfaceexcel.py  
Arduino → interfaceexcel.ino

Étapes :
1. Téléverser le code Arduino  
2. Lancer le script :
   python3 interfaceexcel.py  
3. Charger un fichier Excel contenant deux colonnes :
   temps (s) | intensite  
   -----------|-----------  
   0          | 100  
   10         | 200  
   20         | 255  
4. L’acquisition suit le planning temporel et envoie les intensités PWM correspondantes à l’Arduino.

---

## Traitement des images

### 📹 Création de vidéo timelapse
Script : creation_videos.py  
Combine les images capturées en une vidéo.

### Détection d’objets (ex. diatomées)
Script : vid_detection.py  
- Recherche un template (image de référence) dans chaque frame  
- Supporte la rotation du template pour une détection plus robuste  
- Génère une vidéo annotée (output_video.avi) avec les détections  


---

## Auteurs

Projet PRONTO — IMT Atlantique x IUEM  
Développé par Cyril Saad, Molka Jabbeur, Thomas De Saint Savin, Anycia Raulet et Anatole Perbene.
Encadré par l’équipe IUEM — projet d’acquisition et d’analyse d’images time-lapse pour l’observation de diatomées.

---

## Licence

Ce projet est distribué sous licence MIT.  
Vous êtes libres de le réutiliser, modifier et redistribuer avec attribution.
