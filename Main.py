import os
import tkinter as tk
from tkinter import messagebox
from imutils.video import VideoStream
import face_recognition
import cv2
import pickle
import datetime
import numpy as np
import serial
from pymongo.mongo_client import MongoClient
from pymongo.server_api import  ServerApi

import time

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")

        self.reward_points = {}  # Dictionary to store reward points for each face
        self.serial_port = serial.Serial("COM6", 115200, timeout=1)  # Change COM6 to your ESP8266 port

        self.title_label = tk.Label(root, text="Face Recognition System", font=("Helvetica", 20))
        self.title_label.pack(pady=10)

        self.start_camera_button = tk.Button(root, text="Start Camera", command=self.start_camera)
        self.start_camera_button.pack(pady=20)

        self.con = self.connect()['SGBUSers']

        self.camera = None

        self.last_face_detected_time = None
        self.camera_status = False  # To keep track of camera status

        self.check_servo_timeout()  # Initial call

    def connect(self):
        uri = "<your MongoDB url>"
        # Set the Stable API version when creating a new client
        client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            return client['test']
        except Exception as e:
            print(e)

    def start_camera(self):
        self.camera = VideoStream(src=0, framerate=10).start()

        self.start_camera_button.config(state=tk.DISABLED)  # Disable the button after starting the camera
        self.camera_status = True  # Set camera status to True when the camera is started

        self.capture_button_list = []  # Reset the capture buttons

        # Main loop for face recognition
        while self.camera_status:
            frame = self.camera.read()
            frame = cv2.resize(frame, (640, 480))  # Resize the frame

            faces = face_recognition.face_locations(frame)
            if faces:
                for face in faces:
                    self.process_face(frame, face)
            else:
                # No face detected, check servo timeout
                self.check_servo_timeout()

            cv2.imshow("Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()
        self.camera.stop()
        self.start_camera_button.config(state=tk.NORMAL)  # Enable the button after stopping the camera

    def process_face(self, frame, face_location):
        encoding = face_recognition.face_encodings(frame, [face_location])[0]

        # Load the known faces and embeddings
        data = pickle.loads(open("encodings.pickle", "rb").read())
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        userID = "1010101010"

        face_distances = face_recognition.face_distance(data["encodings"], encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            userID = data["phoneNo"][best_match_index]

            if self.last_face_detected_time is None or userID != self.last_face_name:
                # Different face detected or first detection, update reward points
                self.last_face_name = userID
                self.last_face_detected_time = datetime.datetime.now()
                self.reward_points[userID] = self.reward_points.get(userID, 0) + 1
                print(f"Points are: {self.reward_points[userID]}")
                dataMongo = self.con.find_one({"userID": userID})
                if dataMongo is None or data == "":
                   tk.messagebox.showinfo("Face Not Registered", "Your Face is Not Registered")
                   print('face not registered')
                else:
                    points = dataMongo.get('rewardPoints')+1
                    self.con.update_one({"userID":userID},{"$set": {"rewardPoints":points}})
                    self.reward_points[userID] = points
                    # tk.messagebox.showinfo("Face Recognised", f"Your Points are:{points}")
                    print(f"Points are: {points}")

                # Send command to ESP8266 to open the servo
                self.serial_port.write(b'O')

    def check_servo_timeout(self):
        if self.last_face_detected_time is not None and self.camera_status:
            current_time = datetime.datetime.now()
            elapsed_time = (current_time - self.last_face_detected_time).total_seconds()

            # Check if 5 seconds have passed since the last face detection
            if elapsed_time >= 10:
                # Send command to ESP8266 to close the servo
                self.serial_port.write(b'C')
                self.last_face_detected_time = None

        # Schedule the function call after 1000 milliseconds (1 second)
        self.root.after(1000, self.check_servo_timeout)

    def stop_camera(self):
        self.camera_status = False

if __name__ == "__main__":
    root = tk.Tk()
    os.chdir("E:/face attendence/face attendence/")
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_camera)  # Handle window close event
    root.mainloop()
