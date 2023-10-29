import numpy as np
import cv2
import cvlib as cv
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model

# Load the pre-trained gender detection model
gender_model = load_model('gender_detection.model')

# Open the default camera (webcam)
camera = cv2.VideoCapture(0)

# Define the gender classes
gender_classes = ['man', 'woman']

# Continuously capture frames from the webcam
while camera.isOpened():
    # Read a frame from the camera
    success, frame = camera.read()

    # Detect faces in the frame
    detected_faces, confidences = cv.detect_face(frame)

    # Process each detected face
    for face_coordinates in detected_faces:
        (startX, startY, endX, endY) = face_coordinates

        # Draw a rectangle around the detected face
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

        # Extract the face region from the frame
        face_region = frame[startY:endY, startX:endX]

        # Skip small detected regions
        if face_region.shape[0] < 10 or face_region.shape[1] < 10:
            continue

        # Preprocess the face region for gender detection
        face_region = cv2.resize(face_region, (96, 96))
        face_region = face_region.astype("float") / 255.0
        face_region = img_to_array(face_region)
        face_region = np.expand_dims(face_region, axis=0)

        # Predict the gender using the model
        predictions = gender_model.predict(face_region)[0]

        # Determine the gender with the highest confidence
        gender_index = np.argmax(predictions)
        gender_label = gender_classes[gender_index]
        confidence_text = "{}: {:.2f}%".format(gender_label, predictions[gender_index] * 100)

        # Position for the label text
        text_position = (startX, startY - 10) if startY - 10 > 10 else (startX, startY + 10)

        # Display the gender label and confidence on the frame
        cv2.putText(frame, confidence_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show the frame with the detected faces and predictions
    cv2.imshow("Gender Detection", frame)

    # Exit the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
camera.release()
cv2.destroyAllWindows()
