#pip install numpy opencv-python, dependencies for mediapipe
#pip install mediapipe
import cv2
import time
import mediapipe as mp

# MediaPipe Tasks imports
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load face landmark model
base_options = python.BaseOptions(
    model_asset_path="face_landmarker.task"  # face_landmarker.task is in the same directory, literally an image used to build
) # Model from: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker#models


# Update the options for the face landmarker, use base options, don't bother with blend and transformations
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1 # Only 1 face 
)

landmarker = vision.FaceLandmarker.create_from_options(options) # Marker variable for face mapping

# Open camera
capture = cv2.VideoCapture(1)

if not capture.isOpened(): # Safety check
    print("Could not open camera.")
    exit()

last_time = time.time() # Get the time of the computer, for running a while loop while counting
current_time = last_time

print("Normalizing human in 10 seconds!")

while (current_time - last_time) < 10: # Time is needed for person to adjust 

    current_time = time.time() # Update time

    ret, frame = capture.read() # Get a picture from camera
    if not ret:
        print("Failed to capture frame.")
        exit()

    frame = cv2.resize(frame, (800, 600)) # Sizing
    
    seconds_left = int(10 - (current_time - last_time)) # Update the time

    cv2.putText(frame, "Seconds Left: " + str(seconds_left), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 5) # Put time on display

    # Create an rgb frame from the bgr picture
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Update the media pipe image with the data
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Facemapping is detected and put into result
    result = landmarker.detect(mp_image)

    # Draw the landmarks over the person's face
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1]) # Get the normalized x and y values for each landmark
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 255, 0), -1) # Draw a circle at each landmark

    cv2.imshow("Mediapipe Feed", frame) #Outut camera feed

    if cv2.waitKey(1) & 0xFF == ord('q'): # Break early if 'q' is pressed, mask out last 8 bits for ASCII input
        break                             # waitKey for 1 millisecond


ret, frame = capture.read() # Then actually read the camera for the capture image
if not ret:
    print("Failed to capture")
    capture.release()
    cv2.destroyAllWindows()
    exit()

frame = cv2.resize(frame, (800, 600))

rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

result = landmarker.detect(mp_image)

total_yBase = 0

if result.face_landmarks: # Grab all of the face_landmarks, get their non-normalized y value, and update the base
    for face_landmarks in result.face_landmarks:
        for landmark in face_landmarks:
            total_yBase += int(landmark.y * 600)

baseline_y = int(total_yBase / len(face_landmarks)) # Get the average y value for base line, based off number of face_landmarks

if total_yBase == 0: # Safety check if human not in frame
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

    frame = cv2.resize(frame, (800, 600)) # same process as image capture

    # Create an rgb frame from the bgr picture
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Update the media pipe image with the data
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Facemapping is detected and put into result
    result = landmarker.detect(mp_image)

    total_yNew = 0

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                total_yNew += int(landmark.y * 600)
    
    ratio = total_yNew / total_yBase # Compare new overall y-position with the base
    
    # Signal timing threshold of 0.5 seconds, creates a 0.5 second delay for game input
    # ^ People's avg jump time is apparently 0.5 - 0.9 seconds

    if ratio < 0.78 and (update_time - start_time) > 0.5: # Offset of 0.2 
        # Jump signal
        print("Jump")
        start_time = time.time()
    elif ratio > 1.22 and (update_time - start_time) > 0.5:
        #Crouch signal
        print("Crouch")
        start_time = time.time()

    # print(ratio)

    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)
    
    cv2.line(frame, (200, baseline_y), (600, baseline_y), (0, 255, 0), 2) # Draw a horizontal line at the y base value

    cv2.imshow("Mediapipe Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): # Input signal needed for if the player dies to break the loop
        break

capture.release()
cv2.destroyAllWindows()