import cv2 
import numpy as np
import matplotlib.pyplot as plt

# Chemins des fichiers
video_path = 'c:/Users/lenovo1/OneDrive/Documents/IMT/PRONTO/timelapse_video.mp4' 
template_path = 'c:/Users/lenovo1/OneDrive/Documents/IMT/PRONTO/codes/photos/diatomee.png'

# Charger le modèle de la diatomée
template = cv2.imread(template_path)
gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
gray_template = cv2.GaussianBlur(gray_template, (3, 3), 0)  # Filtrage flou léger

# Fonction pour faire tourner un template sans rogner
def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
    return rotated

# Ouverture de la vidéo
cap = cv2.VideoCapture(video_path)

# Vérification si la vidéo s'ouvre correctement
if not cap.isOpened():
    print("Erreur lors de l'ouverture de la vidéo")
    exit()

# Seuil de détection
threshold = 0.5
angles = [0, 15, 30, 45, 60, 75, 90]

# Création d'un objet VideoWriter pour sauvegarder la vidéo (optionnel)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (640, 480))  # Change la taille si nécessaire

# Affichage interactif avec matplotlib
plt.ion()  # Active le mode interactif pour que plt.draw() fonctionne
fig, ax = plt.subplots()  # Crée la figure et l'axe pour matplotlib

while True:
    ret, frame = cap.read()
    
    if not ret:
        break  # Fin de la vidéo
    
    # Convertir en niveaux de gris pour la détection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Appliquer le template matching pour plusieurs angles
    rectangles = []
    w, h = gray_template.shape[::-1]
    
    for angle in angles:
        rotated_template = rotate_image(gray_template, angle)
        result = cv2.matchTemplate(gray_frame, rotated_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        for pt in zip(*locations[::-1]):
            rect = [int(pt[0]), int(pt[1]), int(w), int(h)]
            rectangles.append(rect)
            rectangles.append(rect)  # Nécessaire pour groupRectangles

    # Grouper les rectangles proches
    rectangles, _ = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

    # Dessiner les rectangles rouges fins et ajouter la croix '*' au centre
    for (x, y, w, h) in rectangles:
        # Calculer le centre du rectangle
        center_x, center_y = x + w // 2, y + h // 2
        
        # Dessiner la croix '*' au centre
        cv2.putText(frame, '*', (center_x - 10, center_y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # Dessiner le rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Affichage de la vidéo avec les rectangles (remplacement de cv2.imshow par matplotlib)
    ax.clear()  # Efface l'ancienne image
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Convertir de BGR à RGB pour l'affichage
    ax.axis('off')  # Désactiver les axes
    plt.draw()  # Actualiser la figure
    plt.pause(0.1)  # Pause pour donner le temps à l'affichage de se mettre à jour

    # Sauvegarder la vidéo avec les rectangles (optionnel)
    out.write(frame)

# Libérer la vidéo et fermer les fenêtres
cap.release()
out.release()
plt.ioff()  # Désactiver le mode interactif
plt.close(fig)  # Fermer la figure matplotlib
