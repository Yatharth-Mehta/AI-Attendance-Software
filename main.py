import cv2
import os
import numpy as np
import sqlite3
import mediapipe as mp
import time
from datetime import datetime

DATASET_PATH = "faces"
CONFIDENCE_THRESHOLD = 140
ABSENCE_GRACE = 5
BREAK_LIMIT = 10

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
date TEXT,
entry_time TEXT,
exit_time TEXT,
break_seconds INTEGER
)
""")

conn.commit()

mp_face = mp.solutions.face_detection
detector = mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.6)

faces = []
labels = []
label_map = {}
label_id = 0

for person in os.listdir(DATASET_PATH):

    person_path = os.path.join(DATASET_PATH, person)

    if not os.path.isdir(person_path):
        continue

    label_map[label_id] = person

    for img_name in os.listdir(person_path):

        path = os.path.join(person_path, img_name)

        img = cv2.imread(path)

        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray,(200,200))

        faces.append(gray)
        labels.append(label_id)

    label_id += 1

if len(faces) == 0:
    raise Exception("Dataset empty")

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(labels))

sessions = {}
warning_text = ""
warning_time = 0

def start_session(name):

    now = datetime.now()

    cursor.execute("""
    INSERT INTO attendance
    (name,date,entry_time,exit_time,break_seconds)
    VALUES (?,?,?,?,?)
    """,(
        name,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        None,
        0
    ))

    conn.commit()

    sessions[name] = {
        "row_id": cursor.lastrowid,
        "last_seen": time.time(),
        "break_start": None,
        "break_seconds": 0
    }

def update_exit(name):

    now = datetime.now()

    session = sessions[name]

    if session["break_start"] is not None:
        session["break_seconds"] += int(time.time() - session["break_start"])

    cursor.execute("""
    UPDATE attendance
    SET exit_time=?, break_seconds=?
    WHERE id=?
    """,(
        now.strftime("%H:%M:%S"),
        session["break_seconds"],
        session["row_id"]
    ))

    conn.commit()

cap = cv2.VideoCapture(0)

while True:

    start_time = time.time()

    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape

    cv2.putText(frame,"AI ATTENDANCE",(20,50),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,220,255),2)

    cv2.line(frame,(20,70),(250,70),(70,70,70),2)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = detector.process(rgb)

    detected = set()

    if results.detections:

        for detection in results.detections:

            bbox = detection.location_data.relative_bounding_box

            x1 = max(0,int(bbox.xmin*width))
            y1 = max(0,int(bbox.ymin*height))
            x2 = min(width,int((bbox.xmin+bbox.width)*width))
            y2 = min(height,int((bbox.ymin+bbox.height)*height))

            face = frame[y1:y2,x1:x2]

            if face.size == 0:
                continue

            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray,(200,200))

            label, conf = recognizer.predict(gray)

            name = "Unknown"

            if conf < CONFIDENCE_THRESHOLD:
                name = label_map[label]

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,200,255),2)

            cv2.putText(frame,name,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,200,255),2)

            if name != "Unknown":

                detected.add(name)

                if name not in sessions:
                    start_session(name)

                session = sessions[name]

                session["last_seen"] = time.time()

                if session["break_start"] is not None:

                    duration = int(time.time()-session["break_start"])

                    session["break_seconds"] += duration

                    session["break_start"] = None

    now = time.time()

    for name in list(sessions.keys()):

        session = sessions[name]

        if name in detected:
            continue

        gap = now - session["last_seen"]

        if gap > ABSENCE_GRACE and session["break_start"] is None:
            session["break_start"] = now

        if session["break_start"] is not None:

            break_time = now - session["break_start"]

            if break_time > BREAK_LIMIT:

                warning_text = f"{name} exited"
                warning_time = time.time()

                update_exit(name)

                del sessions[name]

    cv2.putText(frame,"ACTIVE USERS",(20,110),
                cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,200,200),2)

    y = 150

    for name in sessions:

        cv2.circle(frame,(25,y-5),6,(0,255,120),-1)

        cv2.putText(frame,name,(45,y),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(240,240,240),2)

        y += 40

    cv2.putText(frame,"BREAK TIME",(20,y+20),
                cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,200,200),2)

    y += 60

    for name,session in sessions.items():

        seconds = session["break_seconds"]

        cv2.putText(frame,f"{name}: {seconds}s",(20,y),
                    cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,200,0),2)

        y += 30

    fps = int(1/(time.time()-start_time))

    cv2.putText(frame,f"FPS: {fps}",(width-120,40),
                cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)

    if warning_text != "":

        if time.time() - warning_time < 3:

            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            x = int((width - text_size[0]) / 2)

            cv2.putText(
                frame,
                warning_text,
                (x, height - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,120,255),
                3
            )
        else:
            warning_text = ""

    cv2.imshow("AI Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for name in list(sessions.keys()):
    update_exit(name)

cap.release()
cv2.destroyAllWindows()
conn.close()
