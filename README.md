# FaceBasedAttendanceSystem
An attendance system that updates attendance based on face recognition using Computer Vision. Uses Firebase as it's database which holds the student info and the student images

Displays the following details on the popup GUI:
  1. Student ID
  2. Student Name
  3. Year of study
  4. Batch
  5. No of attendances registered
  6. Grade

It registers the attendance for a student only if 60s has passed after the previous attendance of the student was taken
This can be changed to 1 hr or even 1 day depending on the use of application

Screenshots of the application being used:

1. Default screen of the attendance system (mode 0)
![image](https://github.com/Gokul2604/FaceBasedAttendanceSystem/assets/64155771/a39a9721-463a-48cd-86fe-34cff28ce982)

2. Showing the student details when marking attendace (mode 1)
![image](https://github.com/Gokul2604/FaceBasedAttendanceSystem/assets/64155771/d5c4b3bf-4f26-4362-99e8-ccd2ac7c6cdb)

3. Showing a Marked screen (mode 2)
![image](https://github.com/Gokul2604/FaceBasedAttendanceSystem/assets/64155771/b7a942db-8212-4a75-b156-6cd924722727)

4. "Already Marked" Screen when the particular student marked his/her attendace before 60s had elapsed from his/her prev attendance (mode 3)
![image](https://github.com/Gokul2604/FaceBasedAttendanceSystem/assets/64155771/1d55c27c-db98-4a16-a044-4462126c032f)
