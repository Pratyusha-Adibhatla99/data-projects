# Eye-Movement Based Electronic Wheelchair

This project is an assistive technology designed for individuals with Quadriplegia, a condition where extreme paralysis leaves eye movement as the primary motor function. We developed a portable, cost-effective system using a Raspberry Pi 3B+ and OpenCV to replace bulky, expensive laptop-based MATLAB setups. The system captures real-time eye movements via a head-mounted IR camera to drive a motorized wheelchair.

## Methodology: How it was Done

## Hardware Setup: A Raspberry Pi 3B+ interfaces with an IR web camera and an L293D/L298N motor driver.


## Camera Mounting: The camera is positioned approximately 12–15 cm from the user's eye to capture high-contrast frames.


## Motor Control: The Pi sends logic signals to DC motors through specific GPIO pins (16, 18, 22 for Motor 1; 23, 21, 19 for Motor 2).


## Power: The system is powered by portable power banks, and shell scripts are used to ensure the program runs automatically upon startup.

## The Algorithms
The system processes every frame using a two-stage approach to ensure low latency.

## 1. IRIS Detection (Centroid Algorithm)

Face & Eye Detection: The system uses the Viola-Jones Algorithm to detect the face and then locates the eye region.


Pre-processing: The detected eye is cropped, converted to grayscale, and then into a binary image.


Centroid Calculation: The algorithm traverses the binary image (where black is 0 and white is 1) and averages the coordinates of all black pixels to find the Centroid Point (the pupil center).

## 2. Directional Logic (Threshold Algorithm)
The binary eye image is divided into three vertical sections:


Left/Right: If the centroid (pupil) concentration is higher in the left or right threshold divisions, the wheelchair turns in that direction.

Front/Back: If the pupil is in the middle section, the system evaluates vertical regions. High black pixel concentration in the Top moves the chair forward; concentration in the Lower region triggers a stop or reverse.


## Safety (Blink Detection): If no black pixels are detected for five consecutive frames, a blink is assumed, and the motors stop.
