import cv2
import time

import easygui

cam = cv2.VideoCapture(0)
cv2.namedWindow("Face Registration", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Face Registration", 500, 300)

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Face Registration", frame)
    key = cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord("s"):
        easygui.msgbox("Face Not Detected","Error")


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cv2.destroyAllWindows()