import math
import pytesseract
import cv2
import pandas as pd
import serial
import time
import numpy as np
from skimage.filters import threshold_local
import imutils
import skimage
from imutils.object_detection import non_max_suppression
import os
import socket
import time
from imutils.video import FPS
from imutils.video import VideoStream

#Client side config

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'vvf.co.in'# ip of server
local_fqdn = socket.getfqdn()
print('Your device is:',local_fqdn)
server_address = (host, 8001)
print('You are connected to:',server_address)

try:
    sock.connect(server_address)
except Exception as msg: #socket.error, exc:
    print("Caught exception socket.error : %s" % msg)

#config for xml decode
def decode_predictions(scores, geometry):
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []
    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
    for x in range(0, numCols):
        if scoresData[x] < 60:
        	continue
    (offsetX, offsetY) = (x * 4.0, y * 4.0)
    angle = anglesData[x]
    cos = np.cos(angle)
    sin = np.sin(angle)
    h = xData0[x] + xData2[x]
    w = xData1[x] + xData3[x]
    endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
    endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
    startX = int(endX - w)
    startY = int(endY - h)
    rects.append((startX, startY, endX, endY))
    confidences.append(scoresData[x])
    return (rects, confidences)

#tesseract config
config = ('-l eng --oem 3 --psm 13')

#Open Camera
#cap = cv2.VideoCapture('rtsp://admin:VOCIAL@192.168.1.100:554/h264_stream', cv2.CAP_FFMPEG)
cap = cv2.VideoCapture(0)
cap.open('rtsp://admin:VOCIAL@192.168.1.100:554/h264_stream', cv2.CAP_FFMPEG)

if not cap.isOpened():
    raise IOError("Cannot open Webcam")

#frame processing
while True:

    if cap.isOpened():
        try:
            (ret, frame) = cap.read()

        except cv2.error as e:
            print('Caught CV error')
            pass
        while ret:
            frame = cv2.resize(frame, (640, 480))
            #cv2.imshow('frame', frame) #use for frames related debug
            plate_img = frame.copy()
            #open xml
            plate_cascade = cv2.CascadeClassifier('./indian_license_plate.xml')
            plate_rect = plate_cascade.detectMultiScale(frame, scaleFactor = 1.3, minNeighbors = 7)

            possible_plates = plate_img
            for (x,y,w,h) in plate_rect:
                a,b = (int(0.02*frame.shape[0]), int(0.025*frame.shape[1])) #parameter tuning
                plate = plate_img[y+a:y+h-a, x+b:x+w-b, :]
                cv2.rectangle(plate_img, (x,y), (x+w, y+h), (51,51,255), 3)

                if plate is not None:
                    #call tesseract
                    try:
                        tesser_out = pytesseract.image_to_string(plate, config=config)
                        if tesser_out is not None:
                            current_license = tesser_out
                            #write junk in tesseract.txt
                            file1 = open("tesserout.txt", "a")
                            file1.write(tesser_out)
                            file1.close()
                            vveh_letter = []
                            vvehexists = ''
                            str_plt = ''
	           #Convert Junk to alphanumeric
                            alpha = pd.read_csv('alpha.csv')
                            for V in current_license:
                                vletter_exist = V in alpha.values
                                if vletter_exist:
                                    vveh_letter.append(V)
                                str_plt = ''.join(vveh_letter)
                            print('Number Plate:', str_plt)
                            #Connecting with server to send data
                            print ("connecting to (%s) with %s" % (local_fqdn, host))
                            number_plate = [str_plt]
                            for entry in number_plate:
                                #Sending data
                                print ("data: %s" % entry)
                                new_data = str("number_plate: %s\n" % entry).encode("utf-8")
                                sock.sendall(new_data)
                                time.sleep(1)
                            #validation with license plate database
                            database = pd.read_csv('pltnumbers.csv')
                            vvehexists = str_plt in database.values

                            if vvehexists is True:
                                vvhdata = database[database['vehno'] == str_plt]
                                with open("./archive/registered/registered.txt", "w") as outfile:
                                    print (outfile, 'Plate retrieved at:', input['header']['timestamp'].time())
                                #file1.write(str_plt)
                                #file1.close()
                                starttime = time.time()
                                timestamp = time.time() - starttime
                                path = './archive/registered'
                                cv2.imwrite(os.path.join(path, str_plt+starttime+'.jpg'), frame)
                                print('vvhdata', vvhdata.vehowner)

                            if vvehexists is not True:
                                file1 = open("./archive/unregistered/unregistered.txt", "a")  # append mode
                                file1.write(str_plt)
                                file1.close()
                            break

                    except ValueError as msg:
                        print("Caught tesseract error : %s" % msg)
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
