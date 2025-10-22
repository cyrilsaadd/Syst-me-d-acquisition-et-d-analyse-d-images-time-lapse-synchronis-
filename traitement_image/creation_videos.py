import os
import cv2
from natsort import natsorted  # trie naturel : timelapse1, timelapse2, ..., timelapse10
import matplotlib.pyplot as plt

def create_video_from_images(image_folder, output_video_path, frame_rate=10):
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    images = natsorted(images)  # pour bien les trier dans l'ordre

    if not images:
        print("Aucune image trouvée.")
        return

    first_image_path = os.path.join(image_folder, images[0])
    first_frame = cv2.imread(first_image_path)

    if first_frame is None:
        print("Erreur : impossible de lire la première image.")
        return

    height, width, _ = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (width, height))

    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"Erreur lecture image : {img_path}")
            continue
        video.write(frame)

    video.release()
    print(f"✅ Vidéo créée avec succès à : {output_video_path}")

def afficher_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erreur : impossible d'ouvrir la vidéo.")
        return

    plt.ion()  # mode interactif
    fig, ax = plt.subplots()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ax.imshow(frame_rgb)
        ax.axis('off')
        plt.pause(0.03)  # pause entre les images
        ax.cla()  # clear axes

    cap.release()
    plt.ioff()
    plt.close()

# --------- LANCEMENT DU CODE ------------
# Ton dossier "photos" est dans le même répertoire que ton script :
image_folder = "/home/administrateur/Documents/PRONTO/PRONTO/PRONTO/PHOTOSX4"
video_name = "/home/administrateur/Documents/PRONTO/PRONTO/PRONTO/timelapse_video4.mp4"  # nom de sortie de la vidéo
frame_rate = 10 # images par seconde
#frame_rate entre 10 et 30 est souvent utilisé

create_video_from_images(image_folder, video_name, frame_rate)
afficher_video(video_name)