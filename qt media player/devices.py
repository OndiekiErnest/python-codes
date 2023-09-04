""" AUDIO and VIDIO DEVICES """
from PyQt6.QtMultimedia import (
    QMediaDevices,
)
# List of Audio Input Devices
speakers = QMediaDevices.audioOutputs()
mics = QMediaDevices.audioInputs()
cameras = QMediaDevices.videoInputs()

for inputs in (speakers, mics, cameras):
    #
    for device in inputs:
        print("Is default:", device.isDefault(), "--->", device.description())
