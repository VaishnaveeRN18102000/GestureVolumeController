import cv2
import numpy as np
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTracker as ht
wc, hc = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, wc)
cam.set(4, hc)
pt = 0
boundbox = []
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volrange = volume.GetVolumeRange()
minvol = volrange[0]
maxvol = volrange[1]
volbar = 400
sysvol = 0
volper = 0
ar = 0
colsysvol = (255, 0, 0)
detector = ht.handDetector(detectionCon=0.75, maxHands=1)
while True:
    suc, img = cam.read()
    img = detector.findHands(img)
    lmList, boundbox = detector.findPosition(img)
    if len(lmList) != 0:
        ar = (boundbox[2] - boundbox[0]) * (boundbox[3] - boundbox[1]) // 100
        if 250 <= ar <= 1500:
            length, img, liList = detector.findLength(4, 8, img)
            fingers = detector.checkFingersUp()
            print(fingers)
            volbar = np.interp(length, [30, 250], [400, 150])
            volper = np.interp(length, [30, 250], [0, 100])
            incr = 5
            volper = incr * round(volper / incr)
            if not fingers[4]:
                cv2.circle(img, (liList[4], liList[5]), 9, (255, 0, 0), cv2.FILLED)
                volume.SetMasterVolumeLevelScalar(volper/100, None)
                colsysvol = (0, 255, 0)
            else:
                colsysvol = (255, 0, 0)
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 2)
    cv2.rectangle(img, (50, int(volbar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volper)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
    sysvol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Volume Set: {int(sysvol)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 1, colsysvol, 2)
    ct = time.time()
    fps = 1 / (ct - pt)
    pt = ct
    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
    cv2.imshow("Camera", img)
    cv2.waitKey(1)
