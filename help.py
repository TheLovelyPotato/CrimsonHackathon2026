import cv2
import time
import mediapipe as mp
import numpy as np

# MediaPipe Tasks imports
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load face landmark model
base_options = python.BaseOptions(
    model_asset_path="face_landmarker.task"  # You must download this file
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1
)

landmarker = vision.FaceLandmarker.create_from_options(options)

# Open camera
capture = cv2.VideoCapture(1)

if not capture.isOpened():
    print("Could not open camera.")
    exit()

last_time = time.time()
current_time = last_time

print("Normalizing human in 10 seconds!")

while (current_time - last_time) < 10:

    current_time = time.time()

    ret, frame = capture.read()
    if not ret:
        print("Failed to capture frame.")
        exit()

    frame = cv2.resize(frame, (800, 600))
    
    seconds_left = int(10 - (current_time - last_time))

    cv2.putText(frame, "Seconds Left: " + str(seconds_left), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 5)

    cv2.imshow("Mediapipe Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


ret, frame = capture.read()
if not ret:
    print("Failed to capture")
    capture.release()
    cv2.destroyAllWindows()
    exit()

frame = cv2.resize(frame, (800, 600))

# Convert BGR to RGB
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Convert to MediaPipe Image
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

# Run detection
result = landmarker.detect(mp_image)

total_yBase = 0

if result.face_landmarks:
    for face_landmarks in result.face_landmarks:
        for landmark in face_landmarks:
            total_yBase += int(landmark.y * 600)

if total_yBase == 0:
    print("No face detected. Please try again.")
    capture.release()
    cv2.destroyAllWindows()
    exit()

# Game loop chunk

start_time = time.time()

while True:

    update_time = time.time()

    ret, frame = capture.read()
    if not ret:
        break

    frame = cv2.resize(frame, (800, 600))

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Run detection
    result = landmarker.detect(mp_image)

    total_yNew = 0

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                total_yNew += int(landmark.y * 600)
    
    ratio = total_yNew / total_yBase
    
    # Signal timing threshold of 0.5 seconds

    if ratio < 0.85 and (update_time - start_time) > 0.5:
        # Jump signal
        print("Jump")
        start_time = time.time()
    elif ratio > 1.15 and (update_time - start_time) > 0.5:
        #Crouch signal
        print("Crouch")
        start_time = time.time()

    print(ratio)

    # Draw landmarks
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)

    cv2.imshow("Mediapipe Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()