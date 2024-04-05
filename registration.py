import easygui
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from easygui import multenterbox
import hashlib
import time
from imutils import paths
import face_recognition
# import argparse
import pickle
import cv2
import os
import shutil


# name = 'darshan' #replace with your name

def connect():
    uri = "<Your MongoDB url>"
    # Set the Stable API version when creating a new client
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)


con = connect()
fieldNames = ["Name:", "Phone Number", "Password"]
title = "Registration"
msg = "Please Fill the Details"
fieldValues = multenterbox(msg, title, fieldNames)
while 1:
    if fieldValues is None: break
    errmsg = ""
    for i in range(len(fieldNames)):
        if fieldNames[i] == 'Phone Number':
            if fieldValues[i].strip() == "" or len(fieldValues[i]) < 10:
                errmsg += "please enter valid phone number"
        if fieldValues[i].strip() == "":
            errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "":
        break  # no problems found
    fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
name = fieldValues[0]
phoneNo = fieldValues[1]
password = hashlib.sha256(bytes(fieldValues[2], encoding='utf-8')).hexdigest()
print(name, phoneNo, password)
db = con['test']
col = db['SGBUSers']
try:
    data = col.find_one({"userID": phoneNo})
    if data is None or data == "":
        col.insert_one({"userID": phoneNo, "name": name, "password": password, "rewardPoints": 0})
        print('Data Inserted Successfully')
    else:
        print('Already Registered')
        exit()
except Exception as e:
    print(e)

cam = cv2.VideoCapture(0)
os.chdir('E:/face attendence/face attendence/dataset')
if phoneNo in os.listdir('E:/face attendence/face attendence/dataset'):
    shutil.rmtree(f'E:/face attendence/face attendence/dataset/{phoneNo}')
os.mkdir(phoneNo)
os.chdir(f'E:/face attendence/face attendence/dataset/{phoneNo}')
cv2.namedWindow("Face Registration", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Face Registration", 500, 300)

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Face Registration", frame)


    if img_counter <= 20:
        cv2.waitKey(1)
        time.sleep(0.25)
        img_name = "image_{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
    if img_counter > 20:
        break


cam.release()

cv2.destroyAllWindows()

print("[INFO] start processing faces...")
os.chdir("E:/face attendence/face attendence/")
imagePaths = list(paths.list_images("dataset"))

# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
    print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
    name = imagePath.split(os.path.sep)[-2]

    # load the input image and convert it from RGB (OpenCV ordering)
    # to dlib ordering (RGB)
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input image
    boxes = face_recognition.face_locations(rgb,
                                            model="hog")

    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(rgb, boxes)

    # loop over the encodings
    for encoding in encodings:
        # add each encoding + name to our set of known names and
        # encodings
        knownEncodings.append(encoding)
        knownNames.append(name)

# dump the facial encodings + names to disk
os.chdir("E:/face attendence/face attendence/")
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "phoneNo": knownNames}
f = open("encodings.pickle", "wb")
f.write(pickle.dumps(data))
f.close()
easygui.msgbox("Face Registered Successfully", "Success")
