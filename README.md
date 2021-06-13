# SmartHomeDoor
## Overview
Smart Home Door (SHD) is my Bachelor Project, The objective of the research is to implement a smart system that can interact without human intervention, to capture the bill, extract the needed Arabic words and numbers from it, then use the extracted information to pay the money, even when users are not at home.

Initially, OpenCV is used to detect the bill from the image and filter out the unnecessary noise from it. Then, the detected bill is passed to Tesseract-OCR engine, which is an Optical Character Recognition engine. Tesseract is used to extract and read the needed information from the bill. A cash dispenser is simulated to pay the amount of money extracted.

## Hardware
1) RaspberryPi: It is supposed to be connected to a camera to capture the bill, the code is uploaded on RaspberryPi where the system starts working after capturing the bill.
2) Arduino: Connected to RaspberryPi and Servomotors, when the bill is validated, RaspberryPi sends a signal to Arduino to start the motors.
3) Servomotors: Each servomotor indicating the dispensing of a certain money bill (i.e. 200s, 100s, 50s, 20s, 10s and 5s).

## Software and Servers
1) Python
2) OpenCV: To detect the bill from the captured image.
3) Tesseract-OCR: To read the needed Arabic words and numbers from the detected bill.
4) MongoDB: To deploy the system onto the cloud, to save the paid bills and compare the new bills with the ones paid for validation.

## Link
This is the link to the demo video along with the Bachelor Thesis: https://drive.google.com/drive/folders/1y_Fm2Q_TTKkrp4RltfToBdfwINKgkNhw
