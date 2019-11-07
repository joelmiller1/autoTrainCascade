# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 08:18:23 2019
@author: Joel Miller
"""

import cv2
from selector import areaSelector

usps_cascade = cv2.CascadeClassifier('data/cascade.xml')
cap = cv2.VideoCapture('../vids/usps.mp4')
cap.set(1,24*30)

ret, frame = cap.read()
box = areaSelector(frame)
if box is not None:
    frame = frame[box]


while(cap.isOpened()):
    ret, frame = cap.read()
    if box is not None:
        frame = frame[box]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    usps = usps_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in usps:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

    
    cv2.imshow('Video',frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

