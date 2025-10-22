import serial
import time
import ids_peak.ids_peak as ids_peak
import ids_peak_ipl.ids_peak_ipl as ids_ipl
import sys
import cv2
import os
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def start_acquisition(nb_images, intervalle, log_callback):
    port_arduino = "/dev/ttyACM0"  # Modifier si besoin
    baudrate_arduino = 9600
    dossier_images = "/home/administrateur/Documents/PRONTO/PRONTO/PRONTO/PHOTOSX4"

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
        ser.write(b'ON\n')
        time.sleep(5)

        for i in range(nb_images):
            log_callback(f"Capture {i+1}/{nb_images}")
            ser.write(b'ON\n')
            time.sleep(2)
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
            ser.write(b'OFF\n')
            time.sleep(intervalle)
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

def update_plot(ax, canvas, data):
    ax.clear()
    ax.plot(range(len(data)), data, marker='o')
    ax.set_title("Évolution des captures")
    ax.set_xlabel("Capture")
    ax.set_ylabel("Valeur arbitraire")
    canvas.draw()

def main():
    root = tk.Tk()
    root.title("Interface de Contrôle du Timelapse")
    
    frame_controls = ttk.Frame(root, padding=10)
    frame_controls.pack(side=tk.LEFT, fill=tk.Y)
    
    ttk.Label(frame_controls, text="Nombre d'images").pack()
    nb_images_var = tk.IntVar(value=10)
    nb_images_entry = ttk.Entry(frame_controls, textvariable=nb_images_var)
    nb_images_entry.pack()
    
    ttk.Label(frame_controls, text="Intervalle (s)").pack()
    intervalle_var = tk.IntVar(value=5)
    intervalle_entry = ttk.Entry(frame_controls, textvariable=intervalle_var)
    intervalle_entry.pack()
    
    log_text = tk.Text(frame_controls, height=10, width=40)
    log_text.pack()
    
    def log_callback(message):
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)
    
    data = []
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def start():
        nb_images = nb_images_var.get()
        intervalle = intervalle_var.get()
        start_acquisition(nb_images, intervalle, log_callback)
        data.append(nb_images)
        update_plot(ax, canvas, data)
    
    ttk.Button(frame_controls, text="Démarrer", command=start).pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()
