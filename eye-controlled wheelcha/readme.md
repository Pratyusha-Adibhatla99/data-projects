# Eye-Movement Based Electronic Wheelchair System 👁️♿

**Archive Date:** May 2020  
**Institution:** ANITS (Anil Neerukonda Institute of Technology and Sciences)   
**Platform:** Raspberry Pi 3B+ | Python 3 | OpenCV 3.3.0  
**Developer:** Pratyusha Adibhatla  


## 📌 Project Overview
This project is an assistive technology designed as a mobility solution for individuals with **Quadriplegia**, a condition where extreme paralysis leaves eye movement as the primary motor function. 

By utilizing edge computing on a **Raspberry Pi 3B+**, this system replaces bulky, expensive laptop-based MATLAB setups with a portable, cost-effective alternative. The system captures real-time eye movements via a head-mounted IR camera and translates them into actionable directional commands to drive a motorized wheelchair.

---

## ⚙️ Methodology & Algorithms

The system processes every video frame using a low-latency, two-stage algorithm to ensure real-time responsiveness.

### 1. IRIS Detection (Centroid Algorithm)
* **Face & Eye Detection:** The system utilizes the **Viola-Jones Algorithm** to detect the user's face and accurately locate the eye region.
* **Pre-processing:** The detected eye is dynamically cropped, converted to grayscale, and then thresholded into a binary image.
* **Centroid Calculation:** The algorithm traverses the binary image (where the pupil is represented by black pixels `0` and the sclera/skin by white pixels `1`) and averages the coordinates to find the **Centroid Point** of the pupil.



### 2. Directional Logic (Threshold Algorithm)
The binary eye image is segmented into three vertical sections to map physical movement to motor control:
* **Left / Right:** If the pupil centroid concentration is higher in the left or right threshold divisions, the wheelchair initiates a turn in that corresponding direction.
* **Front / Back:** If the pupil is centered, the system evaluates the vertical regions. A high pixel concentration in the **Top** region moves the chair forward; concentration in the **Lower** region triggers a reverse or stop.



---

## 🛠️ Hardware Integration

* **Processing Unit:** Raspberry Pi 3B+.
* **Vision Interface:** A head-mounted IR web camera, positioned approximately 12–15 cm from the user's eye to capture high-contrast frames regardless of ambient lighting.
* **Actuation:** DC Motors driven by an **L293D / L298N motor driver**.
* **Power Management:** The processing unit is powered by portable power banks, utilizing shell scripts to ensure the OpenCV program runs automatically upon startup.

### GPIO Pin Mapping (Board Numbering)
The Raspberry Pi sends TTL logic signals (3.3V) to the motor driver through the following GPIO configuration:
* **Motor 1 (Left Wheel):** Pins 16, 18 (Direction) & Pin 22 (Enable).
* **Motor 2 (Right Wheel):** Pins 23, 21 (Direction) & Pin 19 (Enable).



---

## 🛡️ Safety Mechanisms

To ensure user autonomy and safety, the system relies on native blink detection:
* **Emergency Stop:** If no black pixels (the pupil) are detected for **five consecutive frames**, a continuous blink or closed eyes is assumed, and all motors immediately halt.
* **System Toggle:** Four intentional, consecutive blinks act as a hardware interrupt, toggling the system state between ON and OFF to prevent accidental movement when the user is resting.

---

## 🚀 Setup & Execution

### Prerequisites
Ensure your Raspberry Pi is running Raspbian and is updated.
```bash
sudo apt update
sudo apt install python3-pip
