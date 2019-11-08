# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 09:11:30 2019

@author: Joel Miller
"""
import cv2
from selector import areaSelector, mask2Box, box2Rect

video_location = '../vids/f15.mp4'
cap = cv2.VideoCapture(video_location)
success, refFrame = cap.read()

bbox = mask2Box(areaSelector(refFrame))
vidWIndow = "Video Window"

tracker_types = ['BOOSTING','MIL','KCF','TLD','MEDIANFLOW','GOTURN','MOSSE','CSRT']
tracker_type = tracker_types[7]

if tracker_type == 'BOOSTING':
    tracker = cv2.TrackerBoosting_create()
if tracker_type == 'MIL':
    tracker = cv2.TrackerMIL_create()
if tracker_type == 'KCF':
    tracker = cv2.TrackerKCF_create()
if tracker_type == 'TLD':
    tracker = cv2.TrackerTLD_create()
if tracker_type == 'MEDIANFLOW':
    tracker = cv2.TrackerMedianFLow_create()
if tracker_type == 'GOTURN':
    tracker = cv2.TrackerGOTURN_create()
if tracker_type == 'MOSSE':
    tracker = cv2.TrackerMOSSE_create()
if tracker_type == 'CSRT':
    tracker = cv2.TrackerCSRT_create()
    
tracker.init(refFrame,bbox)

while True:
    success, frame = cap.read()
    if not success:
        break
    success, bbox = tracker.update(frame)

    if success:
        rectPts = box2Rect(bbox)
        cv2.rectangle(frame, rectPts[0], rectPts[1],(255,0,0), 2,1)
    else:
        print("Tracking Failed")
    
    cv2.imshow("Tracking",frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
        
