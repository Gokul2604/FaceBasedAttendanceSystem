import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://facebasedattendancesystem-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('Students')

data = {
    '1036': {
        "name": "Anvesh C H",
        "dept": "CSE",
        "batch": 2024,
        "total_attendance": 5,
        "standing": "A",
        "year": 3,
        "last_attendance_time": "2022-06-06 00:00:00"
    },
    '1040': {
        "name": "Gokul Prakash R",
        "dept": "CSE",
        "batch": 2024,
        "total_attendance": 4,
        "standing": "A",
        "year": 3,
        "last_attendance_time": "2022-06-06 00:00:00"
    },
    '2143': {
        "name": "Robert Downey Jr",
        "dept": "ECE",
        "batch": 2025,
        "total_attendance": 7,
        "standing": "O",
        "year": 2,
        "last_attendance_time": "2022-06-06 00:00:00"
    }
}

for key,value in data.items():
    ref.child(key).set(value)