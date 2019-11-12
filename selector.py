# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:22:52 2019

@author: Joel Miller
"""

import cv2


def pts4Rect(points):
    (xa,ya) = points[0]
    (xb,yb) = points[1]
    (x1,x2) = (xa,xb) if xa < xb else (xb,xa)
    (y1,y2) = (ya,yb) if ya < yb else (yb,ya)
    return [(x1,y1), (x2,y2)]

def mask2Rect(mask):
    y1 = mask[0].start
    y2 = mask[0].stop
    x1 = mask[1].start
    x2 = mask[1].stop
    return pts4Rect([(x1,y1),(x2,y2)])

def mask2Box(mask):
    y1 = mask[0].start
    y2 = mask[0].stop
    x1 = mask[1].start
    x2 = mask[1].stop
    return (x1,y1,abs(x1-x2),abs(y1-y2))

def box2Rect(bbox):
    x1 = int(bbox[0])
    y1 = int(bbox[1])
    w = int(bbox[2])
    h = int(bbox[3])
    return ((x1,y1), (x1+w,y1+h))

def box2Mask(bbox):
    pts = box2Rect(bbox)
    mask = (slice(pts[0][1],pts[1][1]),slice(pts[0][0],pts[1][0]))
    return mask

def areaSelector(refFrame):
    selectWindow = "Select Region"
    cv2.namedWindow(selectWindow)
    
    clickParams = {
            'refPt': [(0,0),(0,0)],
            'cropping': False,
            'selectFrame': refFrame.copy()}
    
    def click(event,x,y,flags,params):
        frame = params['selectFrame']
        if event == cv2.EVENT_LBUTTONDOWN:
            params['refPt'][0] = (x,y)
            params['refPt'][1] = (x,y)
            params['cropping'] = True
        elif event == cv2.EVENT_LBUTTONUP:
            params['refPt'][1] = (x,y)
            params['refPt'] = pts4Rect(params['refPt'])
            params['cropping'] = False
            params['selectFrame'] = refFrame.copy()
            
            frame = params['selectFrame']
            pts = params['refPt']
            cv2.rectangle(frame,pts[0],pts[1],(0,255,0),2)
        elif params['cropping'] == True:
            pts = params['refPt']
            params['refPt'][1] = (x,y)
            plotPts = pts4Rect(params['refPt'])
            frame[:] = refFrame[:]
            cv2.rectangle(frame,plotPts[0],plotPts[1],(0,255,0),2)
    
        cv2.imshow(selectWindow, frame)
    
    cv2.setMouseCallback(selectWindow,click,clickParams)
    mask = ()
    while True:
        cv2.imshow(selectWindow,clickParams['selectFrame'])
        key = cv2.waitKey(1) & 0xFF
        if(key == ord("r")):
            clickParams['selectFrame'] = refFrame.copy()
            
        elif(key == 13): #enter key
            pts = clickParams['refPt']
            if (len(pts) == 2):
                if(pts[0] == pts[1]):
                    mask = (-1,)
                else:
                    mask = (slice(pts[0][1],pts[1][1]),slice(pts[0][0],pts[1][0]))
                break
            else:
                break
        elif(key == ord("b")):
            mask = (-9,)
            break
        
        elif(key == ord("s")):
            mask = (-21,)
            break
        
        elif(key == ord("q") or cv2.getWindowImageRect(selectWindow)[0] < 0):
            mask = (-31,)
            break
    cv2.destroyWindow(selectWindow)
    return mask
        

