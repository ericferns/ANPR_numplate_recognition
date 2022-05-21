# ANPR_numplate_recognition

## Introduction
A piece of python script, that detects an Indian number plate using the haarcascade `indian_license_plate.xml` from the video feed, crops the ROI, and then runs an OCR on the returned image, to give the letters and numbers on the same.
The returned string of letters is then used to validate with respect to a database, which can be stored elsewhere, AKA on a server. The method of communication used her is socket communication.

## How to use
- Clone the repo on your local machine
- Install Google's Application for OCR support, called `Tesseract OCR`
- In the terminal, run the command `pip install -r requirements.txt`
- Open the file `VehLicensePlatecheck.py` and on the `line 21`, change the value of the variable `host` to the IP address or domain name of your server.
- In the same file, check for `line 24`, specify the port number as well, in the variable `server_address`. On `lines 65-66`, in the variable `cap=cv2.VideoCapture(0)`, the '0' stands for using the webcam on your local machine. You can change the values to 1,2 etc., to use other cameras connected to your port. Or, if you are using an IP camera, then replace it with the `rtsp` protocol IP addres for the same.
- Open the file `server.py` and on the `line 18` replace the value of that variable to the server name or IP address, and on `line 23`, change the value to the your port number.
