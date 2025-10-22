
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Chemins des fichiers
video_path = '/home/administrateur/Documents/PRONTO/PRONTO/PRONTO/timelapse_video.mp4'
template_path = '/home/administrateur/Documents/PRONTO/PRONTO/PRONTO/codes/photos/diatomee.png'

# Charger le modèle de la diatomée
template = cv2.imread(template_path)
gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
gray_template = cv2.GaussianBlur(gray_template, (3, 3), 0)

# Fonction pour faire tourner un template sans rogner
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
    return rotated

# Ouverture de la vidéo
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Erreur lors de l'ouverture de la vidéo")
    exit()

# Paramètres de détection
threshold = 0.5
angles = [i for i in range(0, 91, 10)]
fps = cap.get(cv2.CAP_PROP_FPS)

# Création d'un objet VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (640, 480))

# Variables pour stocker les positions et les données
previous_positions = []
data_records = []
frame_idx = 0

# Affichage interactif avec matplotlib
plt.ion()
fig, ax = plt.subplots()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rectangles = []
    w, h = gray_template.shape[::-1]

    for angle in angles:
        rotated_template = rotate_image(gray_template, angle)
        result = cv2.matchTemplate(gray_frame, rotated_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        for pt in zip(*locations[::-1]):
            rect = [int(pt[0]), int(pt[1]), int(w), int(h)]
            rectangles.append(rect)
            rectangles.append(rect)

    rectangles, _ = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
    current_positions = []

    # Récupérer les dimensions de l'image
    height, width = frame.shape[:2]

    # Tracer les axes à l'origine en bas à gauche
    cv2.line(frame, (0, height - 1), (width, height - 1), (255, 0, 0), 2)  # Axe X bleu
    cv2.line(frame, (0, 0), (0, height), (255, 0, 0), 2)  # Axe Y bleu
    cv2.putText(frame, '(0,0)', (5, height - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    for i, (x, y, w, h) in enumerate(rectangles):
        center_x, center_y = x + w // 2, y + h // 2
        current_positions.append((center_x, center_y))

        if frame_idx > 0 and i < len(previous_positions):
            prev_x, prev_y = previous_positions[i]
            dx = center_x - prev_x
            dy = center_y - prev_y
            distance = np.sqrt(dx**2 + dy**2)
            speed = distance * fps
            angle_rad = np.arctan2(dy, dx)
            angle_deg = np.degrees(angle_rad)

            text = f"Diatomee {i+1}\nVitesse: {speed:.2f} px/s\nAngle: {angle_deg:.1f} degres"
            y_offset = 15
            for k, line in enumerate(text.split('\n')):
                cv2.putText(frame, line, (x + w + 5, y + k * y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)

            data_records.append({
                'Frame': frame_idx,
                'Diatomee': i + 1,
                'X': center_x,
                'Y': center_y,
                'Speed (px/s)': speed,
                'Angle (deg)': angle_deg
            })

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.drawMarker(frame, (center_x, center_y), (0, 0, 255), markerType=cv2.MARKER_STAR, markerSize=10, thickness=1)

    previous_positions = current_positions
    frame_idx += 1

    ax.clear()
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    ax.axis('off')
    plt.draw()
    plt.pause(0.03)

    out.write(frame)
    print(f"{frame_idx} image(s) analysée(s).")

# Enregistrement des données
cap.release()
out.release()
df = pd.DataFrame(data_records)
df.to_excel('vitesses_diatomees.xlsx', index=False)
plt.ioff()
plt.close(fig)
print("Traitement terminé ✅")
