import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://facebasedattendancesystem-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'facebasedattendancesystem.appspot.com'
})

# importing the student images into a list
folderPath = 'Images'
imgPath = os.listdir(folderPath)
imgList = []
studentId = []

for path in imgPath:
    fileName = os.path.join(folderPath,path)
    imgList.append(cv2.imread(fileName))
    studentId.append(os.path.splitext(path)[0])

    # creating a storage bucket and uploading images to the firebase storage
    bucket = storage.bucket()
    blob = bucket.blob(f'{folderPath}/{path}')
    blob.upload_from_filename(f'{folderPath}/{path}')
    print("Images uploaded...")
# print(len(imgList))
# print(studentId)

def getEncoding(imageList):
    encodeList = []
    for img in imageList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # opencv uses BGR colorspace. Changing it to RGB to suit face_recognition lib
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding started...")
knownEncodeList = getEncoding(imgList)
knownEncodeListWithId = [knownEncodeList, studentId]
print("Encoding complete...")

# generating a pickle file
file = open("Encodefile.p", "wb")
pickle.dump(knownEncodeListWithId, file)
file.close()
print("File saved...")