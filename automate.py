# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 10:38:16 2019

@author: Joel Miller
"""
import cv2,glob,os,subprocess,shlex,shutil
from selector import areaSelector, mask2Rect

try:
    file.close()
    file2.close()
except:
    print("Train Start")

def picList(picPath):
    imgList = []
    currentDir = os.getcwd()
    os.chdir(picPath)   
    for file in glob.glob('*.jpg'):
        imgList.append(file)
    os.chdir(currentDir)
    count = len(imgList)
    return count, imgList


def bgList(vidPath):
    vidcap = cv2.VideoCapture(vidPath)
    if os.path.isdir('data/raw') == False:
        os.mkdir('data/raw')
    count, imgList = picList('data/raw')
    
    def getFrame(sec):
        vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
        hasFrames,image = vidcap.read()
        if hasFrames:
            cv2.imwrite("data/raw/img"+str(count+1)+".jpg", image)     # save frame as JPG file
        return hasFrames,image
    
    sec = 2
    frameRate = 1 #//it will capture image in each 0.5 second
    success,image  = getFrame(sec)
    
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success,image = getFrame(sec)
        
        """if success:
            cv2.imshow("video",image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break"""
        if (count%20) == 0:
            print("converting images...")
    vidcap.release()
    cv2.destroyAllWindows()
    print("Finished making pictures")


if os.path.isdir('data') == False:
    os.mkdir('data')
else:
    shutil.rmtree('data')    
bgList('../vids/usps.mp4')
count, imgList = picList('data/raw')
file = open('data/bg.txt','w+')
file2 = open('data/info.dat','w+')
    
if os.path.isdir('data/pos') == False:
    os.mkdir('data/pos')
if os.path.isdir('data/neg') == False:
    os.mkdir('data/neg')
i = 0
posCount = 1

while i < (count):
    refImg = cv2.imread('data/raw/'+imgList[i])
    modImg = refImg.copy()
    box = areaSelector(modImg)
    if box[0] == -1:
        cv2.imwrite('data/neg/'+imgList[i],modImg)
        file.write('neg/'+imgList[i]+'\n')
    elif box[0] == -9:
        i -= 2
    elif box[0] == -21:
        i += 1
        continue
    else:
        modImg = modImg[box]
        cv2.imwrite('data/pos/pos'+str(posCount)+'.jpg',modImg)
        width = modImg.shape[1]
        height = modImg.shape[0]
        file2.write(f'pos/pos{posCount}.jpg  1  0 0 {width} {height}\n')
        posCount += 1
        temp = mask2Rect(box)
        refImg = cv2.rectangle(refImg,temp[0],temp[1],(0,0,0),cv2.FILLED)
        cv2.imwrite('data/neg/'+imgList[i],refImg)
        file.write('neg/'+imgList[i]+'\n')
    i += 1

file.close()
file2.close()
print('Background text file written')
print('info.dat file written')
negCount,qq = picList('data/neg')
print('Number of Negative pics: '+str(negCount))
posCount,qq = picList('data/pos')
print('Number of Positive pics: '+str(posCount))

createSamples = '../cascade_classifier/opencv_createsamples.exe'
args = f' -vec ./data/output.vec -info ./data/info.dat -bg ./data/bg.txt -num {posCount} -w 60 -h 40'
program = subprocess.Popen(shlex.split(createSamples+args))
program.wait()
print('Vector files created')

currentDir = os.getcwd()
os.chdir('data')   
trainCascade = f'../opencv/opencv_traincascade.exe -data ./ -vec ./output.vec -bg ./bg.txt -numPos {posCount} -numNeg {negCount} -numStages 20 -precalcValBufSize 2048 -precalcIdxBufSize 2048 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -mode ALL -featureType LBP -w 60 -h 40'
program2 = subprocess.Popen(shlex.split(trainCascade))
program2.wait()
print('Finished Training')

os.chdir(currentDir)

usps_cascade = cv2.CascadeClassifier('data/cascade.xml')
cap = cv2.VideoCapture('../vids/usps.mp4')
cap.set(1,24*30)

ret, frame = cap.read()

while(cap.isOpened()):
    success, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    usps = usps_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in usps:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

    if success:
        cv2.imshow('Video',frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
