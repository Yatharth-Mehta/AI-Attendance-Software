# AI Face Recognition Attendance System

---

## **Introduction**

Traditional attendance systems rely on manual processes such as signing registers, swiping ID cards, or entering credentials into digital systems. These methods are often inefficient, susceptible to human error, and vulnerable to misuse such as proxy attendance.

Advances in **computer vision** and **artificial intelligence** now allow systems to automatically identify individuals using facial recognition. Facial recognition enables automated identity verification through visual data captured from cameras.

This project implements a **real time AI based attendance monitoring system** that detects and recognizes faces from a webcam feed and automatically records attendance. The system logs **entry time, exit time, and break duration** in a database.

The entire system runs **locally on a computer**, ensuring fast performance and privacy without relying on cloud services.

---

# **Project Objectives**

The main objectives of this project are:

- Automate attendance using **facial recognition**
- Eliminate manual attendance recording
- Track **entry and exit times** automatically
- Measure **break durations** when users leave the camera
- Store attendance records in a **structured database**
- Provide a **real time monitoring interface**

---

# **Rationale**

Manual attendance systems have several limitations:

- Human errors in recording attendance  
- Administrative overhead  
- Possibility of **fraudulent attendance marking**

Face recognition based systems provide a **contactless and automated solution**. Once trained with facial images of users, the system can instantly recognize individuals through a camera feed without requiring any physical interaction.

### Technology Choices

**OpenCV**  
Used for camera handling and image processing.

**MediaPipe**  
Provides fast and accurate **deep learning based face detection**.

**LBPH Face Recognition**  
A lightweight and efficient algorithm suitable for **small datasets and real time systems**.

**SQLite Database**  
A serverless database used to store attendance records locally.

The overall design focuses on **simplicity, speed, and reliability**.

---

# **System Logic**

The system operates through the following stages:

1. Face dataset loading  
2. Face recognition model training  
3. Webcam video capture  
4. Face detection using MediaPipe  
5. Face recognition using LBPH  
6. Attendance session management  
7. Break time monitoring  
8. Database storage of records  

Each webcam frame is processed in real time. When a known face appears, the system starts an **attendance session**. When the face disappears temporarily, the system marks a **break period**. If the absence continues beyond a defined threshold, the system records an **exit time** and ends the session.

---

# **System Architecture**

The system consists of five major components:

- **Dataset Management**
- **Face Detection**
- **Face Recognition**
- **Session Management**
- **Database Storage**

---

# **Dataset Management**

The system loads facial images from a dataset folder where **each folder represents a person**.

Example dataset structure:

```
faces/
   yatharth/
      img1.jpg
      img2.jpg

   aman/
      img1.jpg
```

Each image is converted to **grayscale** and resized before training the recognition model.

This ensures **consistent input data** for the algorithm.

---

# **Face Detection**

Face detection is performed using **MediaPipe**.

The detector scans each frame from the webcam and identifies **bounding boxes containing faces**. These regions are extracted and passed to the recognition system.

MediaPipe uses **deep learning based detection**, which provides higher accuracy than traditional methods such as Haar cascades.

---

# **Face Recognition**

The system uses the **Local Binary Pattern Histogram (LBPH)** algorithm.

LBPH works by:

1. Dividing the face image into small regions  
2. Extracting texture patterns  
3. Generating histograms of facial features  
4. Comparing these histograms with trained images

If the similarity score passes a threshold, the face is classified as a **known user**.

---

# **Session Management**

A **session** represents the period during which a user is present in front of the camera.

When a recognized face appears:

- A new session is created
- **Entry time is recorded**
- The user is added to the active session list

Each session tracks:

- Last time the user was seen
- Break start time
- Total break duration
- Database row ID

This data is stored in memory to enable **fast real time updates**.

---

# **Break Detection Logic**

The system differentiates between **temporary absence** and **actual exit**.

Two parameters control this behavior:

**Absence Grace Period**

Short duration where the system assumes the face detection temporarily failed.

**Break Limit**

If the absence exceeds this limit, the system concludes the user has exited.

This prevents accidental exits due to **brief occlusions or camera glitches**.

---

# **Database Design**

Attendance data is stored using **SQLite**.

### Table Structure

| Field | Description |
|------|------|
| id | Unique record ID |
| name | Name of the recognized user |
| date | Attendance date |
| entry_time | Time when user first appears |
| exit_time | Time when user leaves |
| break_seconds | Total break duration |

Each time a person appears, a **new record is created**.  
When they leave, the system updates the **exit time and break duration**.

---

# **User Interface**

The application displays a **live camera feed** with real time overlays.

The interface shows:

- System title
- Active users list
- Break durations
- Face bounding boxes
- Recognized names
- FPS indicator

This allows operators to **monitor attendance visually**.

---

# **Program Workflow**

```
Dataset Images
      ↓
Model Training
      ↓
Webcam Capture
      ↓
Face Detection
      ↓
Face Recognition
      ↓
Session Tracking
      ↓
Break Monitoring
      ↓
Database Storage
```

---

# **Technologies Used**

**Programming Language**  
Python

**Computer Vision Library**  
OpenCV

**Face Detection Framework**  
MediaPipe

**Machine Learning Algorithm**  
LBPH Face Recognizer

**Database**  
SQLite

---

# **Advantages**

- Fully automated attendance recording
- Contactless identification
- Real time monitoring
- Break duration tracking
- Low computational requirements
- Works **offline without cloud services**

---

# **Limitations**

- Recognition accuracy depends on lighting conditions
- Performance depends on training dataset quality
- LBPH struggles with very large datasets
- Currently supports **single camera input**

---

# **Future Improvements**

Possible enhancements include:

- Deep learning face recognition models such as **FaceNet or ArcFace**
- **Multi person tracking** algorithms
- Web dashboard for attendance analytics
- Anti spoofing detection
- Multi camera support

---

# **How to Run the Project**

### Install Dependencies

```
pip install opencv-python opencv-contrib-python mediapipe numpy
```

### Prepare Dataset

```
faces/
   person_name/
      image1.jpg
      image2.jpg
```

### Run the Program

```
python main.py
```

Press **Q** to exit the application.

---

# **Conclusion**

This project demonstrates how **computer vision and machine learning** can be used to automate attendance monitoring. By combining face detection, face recognition, and real time video processing, the system can accurately identify individuals and record attendance without manual intervention.

The architecture is designed to be **lightweight, efficient, and easy to deploy**. With further enhancements such as deep learning models and multi camera support, the system could evolve into a **scalable enterprise level attendance system**.
