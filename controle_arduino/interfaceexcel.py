import serial
import time
import ids_peak.ids_peak as ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl
import sys
import cv2
import os
import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Global pour stocker le planning extrait d'Excel
planning = []

def charger_excel(log_callback):
    global planning
    filepath = filedialog.askopenfilename(filetypes=[("Fichiers Excel", "*.xlsx *.xls")])
    if not filepath:
        return
    try:
        df = pd.read_excel(filepath)
        if not {'temps', 'intensite'}.issubset(df.columns):
            log_callback("Le fichier doit contenir les colonnes 'temps' et 'intensite'.")
            return
        
        intensites = df['intensite'].values
        max_intensite = max(intensites)
        
        # Normalisation
        intensites_pwm = [int((val / max_intensite) * 255) for val in intensites]
        planning = list(zip(df['temps'].values, intensites_pwm))
        
        log_callback(f"Fichier chargé : {filepath}")
        log_callback(f"Planning : {planning}")
    except Exception as e:
        log_callback(f"Erreur lors du chargement du fichier Excel : {e}")

def start_acquisition(log_callback):
    global planning
    if not planning:
        log_callback("Erreur : Aucun fichier Excel chargé.")
        return

    port_arduino = "/dev/ttyACM0"
    baudrate_arduino = 9600
    dossier_images = "/home/administrateur/Documents/Ingrid/distribution_z/images/Timelapse"

    try:
        ser = serial.Serial(port_arduino, baudrate_arduino, timeout=1)
    except serial.SerialException as e:
        log_callback(f"Erreur d'ouverture du port série : {e}")
        return
    time.sleep(2)

    ids_peak.Library.Initialize()
    device_manager = ids_peak.DeviceManager.Instance()
    device_manager.Update()
    device_descriptors = device_manager.Devices()

    if len(device_descriptors) == 0:
        log_callback("Aucune caméra IDS détectée.")
        ser.close()
        ids_peak.Library.Close()
        return

    try:
        device = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
    except ids_peak.Exception as e:
        log_callback(f"Erreur lors de l'ouverture de la caméra : {e}")
        ser.close()
        ids_peak.Library.Close()
        return

    remote_device_nodemap = device.RemoteDevice().NodeMaps()[0]

    try:
        remote_device_nodemap.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        remote_device_nodemap.FindNode("TriggerSource").SetCurrentEntry("Software")
        remote_device_nodemap.FindNode("TriggerMode").SetCurrentEntry("On")

        datastream = device.DataStreams()[0].OpenDataStream()
        payload_size = remote_device_nodemap.FindNode("PayloadSize").Value()

        for i in range(datastream.NumBuffersAnnouncedMinRequired()):
            buffer = datastream.AllocAndAnnounceBuffer(payload_size)
            datastream.QueueBuffer(buffer)

        datastream.StartAcquisition()
        remote_device_nodemap.FindNode("AcquisitionStart").Execute()
    except ids_peak.Exception as e:
        log_callback(f"Erreur lors de la configuration de l'acquisition : {e}")
        device.Close()
        ids_peak.Library.Close()
        ser.close()
        return

    os.makedirs(dossier_images, exist_ok=True)

    try:
        t0 = time.time()
        for i, (t_sec, pwm_val) in enumerate(planning):
            # Attend le bon timing
            while time.time() - t0 < t_sec:
                time.sleep(0.1)
            
            # Envoi lumière
            commande = f"LUM={pwm_val}\n"
            ser.write(commande.encode())
            log_callback(f"[{t_sec}s] Capture {i+1}, lumière PWM={pwm_val}")

            time.sleep(0.5)  # Petit délai pour stabiliser la lumière

            # Capture image
            remote_device_nodemap.FindNode("TriggerSoftware").Execute()
            buffer = datastream.WaitForFinishedBuffer(1000)

            raw_image = ids_ipl.Image.CreateFromSizeAndBuffer(
                buffer.PixelFormat(),
                buffer.BasePtr(),
                buffer.Size(),
                buffer.Width(),
                buffer.Height()
            )
            color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_RGB8)
            datastream.QueueBuffer(buffer)

            picture = color_image.get_numpy_3D()
            filename = os.path.join(dossier_images, f"timelapse{i}.jpg")
            cv2.imwrite(filename, picture)
            log_callback(f"Image enregistrée : {filename}")

    except KeyboardInterrupt:
        log_callback("\nInterruption par l'utilisateur (Ctrl+C). Nettoyage des ressources...")
    except Exception as e:
        log_callback(f"Erreur inattendue : {e}")
    finally:
        try:
            remote_device_nodemap.FindNode("AcquisitionStop").Execute()
            datastream.StopAcquisition()
        except ids_peak.Exception as e:
            log_callback(f"Erreur lors de l'arrêt de l'acquisition : {e}")

        ids_peak.Library.Close()
        ser.close()
        log_callback("Ressources libérées. Fin du script.")

def main():
    root = tk.Tk()
    root.title("Interface Timelapse Synchronisée")

    frame_controls = ttk.Frame(root, padding=10)
    frame_controls.pack(side=tk.LEFT, fill=tk.Y)

    log_text = tk.Text(frame_controls, height=20, width=50)
    log_text.pack()

    def log_callback(message):
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)

    ttk.Button(frame_controls, text="Charger fichier Excel", command=lambda: charger_excel(log_callback)).pack(pady=5)
    ttk.Button(frame_controls, text="Démarrer acquisition", command=lambda: start_acquisition(log_callback)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()