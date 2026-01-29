# Project: Eye-Movement Controlled Wheelchair
# Date: 2020
# Author: Adibhatla Pratyusha
# Platform: Raspberry Pi 3B+ / OpenCV 3.3.0

import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep

# --- GPIO Setup ---
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Motor 1 Pins
Motor1A = 16
Motor1B = 18
Motor1E = 22

# Motor 2 Pins
Motor2A = 23
Motor2B = 21
Motor2E = 19

GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1E, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(Motor2E, GPIO.OUT)

# --- OpenCV Classifiers ---
# Note: Ensure these XML files are in the same directory or update paths
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

cap = cv2.VideoCapture(0)

print("System Initialized. Press ESC to exit.")

try:
    while True:
        ret, img = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(roi_gray)

            for (ex, ey, ew, eh) in eyes:
                crop_img = roi_color[ey: ey + eh, ex: ex + ew]
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                # Image processing for pupil detection
                eye_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
                # Apply threshold to isolate pupil
                ret, thresh = cv2.threshold(eye_gray, 75, 255, cv2.THRESH_BINARY)
                
                rows, cols = thresh.shape
                p = q = z = 0 # Left, Center, Right counters

                # Directional Logic based on pupil position (Horizontal)
                for i in range(rows):
                    for j in range(cols):
                        if np.any(thresh[i, j] == 0): # Black pixels (Pupil)
                            if j < cols/3:
                                p += 1 # Left
                            elif j > (2*cols)/3:
                                z += 1 # Right
                            else:
                                q += 1 # Center

                # Vertical logic counters
                a = b = c = 0 # Top, Middle, Bottom

                # --- Decision Logic & Motor Control ---
                if p < z and q < z:
                    # Move Right
                    GPIO.output(Motor1A, GPIO.HIGH)
                    GPIO.output(Motor1B, GPIO.LOW)
                    GPIO.output(Motor1E, GPIO.HIGH)
                    GPIO.output(Motor2A, GPIO.LOW)
                    GPIO.output(Motor2B, GPIO.HIGH)
                    GPIO.output(Motor2E, GPIO.HIGH)
                    print("Action: Right")

                elif z < q and p < q:
                    # Vertical analysis for Front/Back/Stop
                    for i in range(rows):
                        for j in range(cols):
                            if np.any(thresh[i, j] == 0):
                                if i < rows/3:
                                    a += 1 # Top
                                elif i > (2*rows)/3:
                                    c += 1 # Bottom
                                else:
                                    b += 1 # Middle

                    if b < a and c < a:
                        # Move Front
                        GPIO.output(Motor1A, GPIO.LOW)
                        GPIO.output(Motor1B, GPIO.HIGH)
                        GPIO.output(Motor1E, GPIO.HIGH)
                        GPIO.output(Motor2A, GPIO.LOW)
                        GPIO.output(Motor2B, GPIO.HIGH)
                        GPIO.output(Motor2E, GPIO.HIGH)
                        print("Action: Front")

                    elif a < b and c < b:
                        # Stop
                        GPIO.output(Motor1E, GPIO.LOW)
                        GPIO.output(Motor2E, GPIO.LOW)
                        print("Action: Stop")

                    elif a < c and b < c:
                        # Move Back
                        GPIO.output(Motor1A, GPIO.HIGH)
                        GPIO.output(Motor1B, GPIO.LOW)
                        GPIO.output(Motor1E, GPIO.HIGH)
                        GPIO.output(Motor2A, GPIO.HIGH)
                        GPIO.output(Motor2B, GPIO.LOW)
                        GPIO.output(Motor2E, GPIO.HIGH)
                        print("Action: Back")

                elif q < p and z < p:
                    # Move Left
                    GPIO.output(Motor1A, GPIO.LOW)
                    GPIO.output(Motor1B, GPIO.HIGH)
                    GPIO.output(Motor1E, GPIO.HIGH)
                    GPIO.output(Motor2A, GPIO.HIGH)
                    GPIO.output(Motor2B, GPIO.LOW)
                    GPIO.output(Motor2E, GPIO.HIGH)
                    print("Action: Left")

        cv2.imshow('Wheelchair Control Feed', img)
        
        if cv2.waitKey(1) == 27: # ESC key
            break

finally:
    # Proper cleanup for GitHub-ready code
    print("Cleaning up GPIO and closing...")
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()