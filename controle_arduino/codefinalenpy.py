def main():
    device = None
    datastream = None
    remote_device_nodemap = None
    ser = None

    try:
        # Connexion série
        ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
        time.sleep(2)

        # Initialisation bibliothèque IDS
        ids_peak.Library.Initialize()

        device_manager = ids_peak.DeviceManager.Instance()
        device_manager.Update()
        device_descriptors = device_manager.Devices()

        if len(device_descriptors) == 0:
            print("Aucune caméra IDS détectée.")
            return

        device = device_descriptors[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
        remote_device_nodemap = device.RemoteDevice().NodeMaps()[0]

        # Configuration, etc.
        remote_device_nodemap.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        remote_device_nodemap.FindNode("TriggerSource").SetCurrentEntry("Software")
        remote_device_nodemap.FindNode("TriggerMode").SetCurrentEntry("On")

        datastream = device.DataStreams()[0].OpenDataStream()
        payload_size = remote_device_nodemap.FindNode("PayloadSize").Value()

        for _ in range(datastream.NumBuffersAnnouncedMinRequired()):
            buffer = datastream.AllocAndAnnounceBuffer(payload_size)
            datastream.QueueBuffer(buffer)

        datastream.StartAcquisition()
        remote_device_nodemap.FindNode("AcquisitionStart").Execute()

        # ... votre code de capture ici ...

    except Exception as e:
        print(f"Une erreur s’est produite : {e}")

    finally:
        # Arrêter l’acquisition si la caméra est ouverte
        if remote_device_nodemap is not None:
            try:
                remote_device_nodemap.FindNode("AcquisitionStop").Execute()
            except Exception as e:
                print(f"Impossible d'arrêter l'acquisition : {e}")

        if datastream is not None:
            try:
                datastream.StopAcquisition()
                datastream.FlushQueue(ids_peak.DataStreamFlushMode_DiscardAll)
                datastream.RevokeAllBuffers()
            except Exception as e:
                print(f"Impossible d'arrêter le flux d'acquisition : {e}")

        if device is not None:
            try:
                device.Close()
            except Exception as e:
                print(f"Impossible de fermer la caméra : {e}")

        if ser is not None and ser.is_open:
            try:
                ser.close()
            except Exception as e:
                print(f"Impossible de fermer la liaison série : {e}")

        # Fermer la bibliothèque IDS
        ids_peak.Library.Close()

        # Sortie du script
        sys.exit()
