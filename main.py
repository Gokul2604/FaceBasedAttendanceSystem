import datetime
import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import re
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://facebasedattendancesystem-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'facebasedattendancesystem.appspot.com'
})

bucket = storage.bucket()

# def crop_image_with_face_alignment(image_path, crop_width, crop_height):
#     # Load the image
#     image = face_recognition.load_image_file(image_path)
#
#     # Find all the faces in the image
#     face_locations = face_recognition.face_locations(image)
#
#     if len(face_locations) == 0:
#         print("No faces found in the image.")
#         return
#
#     # Choose the first face detected (you can modify this logic if needed)
#     face_location = face_locations[0]
#
#     # Extract the coordinates of the face bounding box
#     top, right, bottom, left = face_location
#
#     # Calculate the width and height of the face bounding box
#     face_width = right - left
#     face_height = bottom - top
#
#     # Calculate the center coordinates of the face bounding box
#     face_center_x = (left + right) // 2
#     face_center_y = (top + bottom) // 2
#
#     # Calculate the scaling factor for zooming out
#     scaling_factor = max(face_width / crop_width, face_height / crop_height)
#
#     # Calculate the new dimensions for cropping (zoomed out)
#     new_crop_width = int(face_width / scaling_factor)
#     new_crop_height = int(face_height / scaling_factor)
#
#     # Calculate the new cropping boundaries (zoomed out)
#     left = max(face_center_x - new_crop_width // 2, 0)
#     top = max(face_center_y - new_crop_height // 2, 0)
#     right = min(left + new_crop_width, image.shape[1])
#     bottom = min(top + new_crop_height, image.shape[0])
#
#     # Crop the image (zoomed out)
#     cropped_image = image[top:bottom, left:right]
#
#     # Resize the cropped image to the required dimensions (216 x 216)
#     resized_image = Image.fromarray(cropped_image).resize((crop_width, crop_height))
#
#     # Save the resized image
#     resized_image.save(image_path)

cap = cv2.VideoCapture(0) # argument can be changed to 1 or more if u have multiple cameras

# setting the dimensions for the webcam display screen
cap.set(3, 640) # width
cap.set(4, 480) # height



# # cropping all the images to the dimensions 216 x 216 and saving it
# folderImagePath = 'Images'
# imagePath = os.listdir(folderImagePath)
#
# for img in imagePath:
#     crop_image_with_face_alignment(os.path.join(folderImagePath,img), 640, 640)



# setting up the background
imgBackground = cv2.imread("Resources/background.png")

# importing the mode images into a list
folderPathMode = 'Resources/Modes'
modePath = os.listdir(folderPathMode)
imgModeList = []

for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderPathMode,path)))
# print(len(imgModeList))

# loading the encodings
print("Loading the encodings...")
file = open("Encodefile.p", "rb")
encodeListWithId = pickle.load(file)
file.close()
encodeList, studentId = encodeListWithId
# print(studentId)

modeType = 0
counter = 0
imgStudent = []
id = -1

# basic template code for running the webcam
while True:
    success, img = cap.read()

    # scaling down the image to increase computation speed
    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    face_currFrame = face_recognition.face_locations(imgS)
    encode_currFrame = face_recognition.face_encodings(imgS, face_currFrame)

    #overlaying the webcam screen on top of the imgBackground
    imgBackground[162:642,55:695] = img
    imgBackground[44:677,808:1222] = imgModeList[modeType]

    if face_currFrame:
        # looping through the encodings to detect the most similar one
        for encodeFace, faceLoc in zip(encode_currFrame, face_currFrame):
            matches = face_recognition.compare_faces(encodeList, encodeFace)
            faceDist = face_recognition.face_distance(encodeList, encodeFace)
            # print("Matches", matches)
            # print("Distance", faceDist)

            matchIdx = np.argmin(faceDist)

            if matches[matchIdx]:
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)

                # retrieving matched student data for displaying
                id = studentId[matchIdx]

                if counter == 0 :
                    cvzone.putTextRect(imgBackground, "Loading", (275,400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            # saving the student data the very first time
            if counter == 1:
                studentData = db.reference(f'Students/{id}').get()
                # print(studentData)
                # getting the image from storage

                folderPath = 'Images'
                imgPath = os.listdir(folderPath)
                imgid = id
                for path in imgPath:
                    pattern = str(id)+'\.(jpg|JPG|jpeg|JPEG|png|PNG)'

                    if(re.match(pattern,path)):
                        imgid = path

                blob = bucket.get_blob(f'Images/{imgid}')
                arr = np.frombuffer(blob.download_as_string(), np.uint8)
                studentImg = cv2.imdecode(arr, cv2.COLOR_BGRA2BGR)

                # updating attendance of student
                dateTimeObj = datetime.strptime(studentData['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secElapsed = (datetime.now() - dateTimeObj).total_seconds()
                # print(secElapsed)

                # setting a time limit to 60s after which the attendance can be taken again
                # this is similar to real life where attendance in schools are taken only once every day
                # where we can change the time limit below if needed
                if(secElapsed > 60):
                    ref = db.reference(f'Students/{id}')
                    studentData['total_attendance'] += 1
                    ref.child('total_attendance').set(studentData['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    studentData = []
                    imgStudent = []
                    imgBackground[44:677, 808:1222] = imgModeList[modeType]

            if modeType != 3:
                if 10 <= counter < 20:
                    modeType = 2

                imgBackground[44:677, 808:1222] = imgModeList[modeType]

                if counter < 10:
                    cv2.putText(imgBackground, str(studentData['total_attendance']), (861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground, str(studentData['dept']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentData['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentData['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentData['batch']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w,h),_ = cv2.getTextSize(studentData['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414 - w ) // 2
                    cv2.putText(imgBackground, str(studentData['name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175+216,909:909+216] = studentImg

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentData = []
                    imgStudent = []
                    imgBackground[44:677, 808:1222] = imgModeList[modeType]
    else:
        counter = 0
        modeType = 0

    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)