# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 10:38:16 2019

@author: Joel Miller
"""
import cv2,os,subprocess,shlex,shutil
from selector import areaSelector, mask2Rect, box2Rect, mask2Box, box2Mask

pathCount = lambda path: len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

def main():
    video_location = ['../vids/mario1.mp4',
                      '../vids/mario3.mp4']
    #selectPosNeg(video_location)
    #objTrack(video_location)
    #createSamples()
    #trainCascade()
    playVids(video_location)

def makeDirs():
    print("Creating Temporary Directories")
    if os.path.isdir('data') == False:
        os.mkdir('data')
        os.mkdir('data/pos')
        os.mkdir('data/neg')
    else:
        shutil.rmtree('data')
        os.mkdir('data')
        os.mkdir('data/pos')
        os.mkdir('data/neg')
        
def objTrack(videoLocation):
    cap = cv2.VideoCapture(videoLocation)
    cap.set(cv2.CAP_PROP_POS_MSEC,90*1000)
    success, refFrame = cap.read()
    box = mask2Box(areaSelector(refFrame))
    tracker = cv2.TrackerMedianFlow_create()
    tracker.init(refFrame,box)
    posCount = 0
    negCount = 0
    makeDirs()
    dat = []
    bg = []
    
    while True:
        success,frame = cap.read()
        refFrame = frame.copy()
        if not success:
            break
        success, box = tracker.update(frame)
        success, box = tracker.update(refFrame)
        
        if success:
            rectPts = box2Rect(box)
            cv2.rectangle(frame,rectPts[0],rectPts[1],(255,0,0),2,1)
            mask = box2Mask(box)
            posCount += 1
            cv2.imwrite(f'data/pos/pos{posCount}.jpg',refFrame[mask])
            dat.append(f'pos/pos{posCount}.jpg  1  0 0 {int(box[2])} {int(box[3])}\n')
            refFrame = cv2.rectangle(refFrame,rectPts[0],rectPts[1],(0,0,0),cv2.FILLED)
            negCount += 1
            cv2.imwrite(f'data/neg/neg{negCount}.jpg',refFrame)
            bg.append(f'neg/neg{negCount}.jpg\n')
        else:
            box = mask2Box(areaSelector(refFrame))
            tracker = cv2.TrackerMedianFlow_create()
            tracker.init(refFrame,box)
        
        cv2.imshow('Tracking',frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    # write out background file
    bgFile = open('data/bg.txt','w+')
    [bgFile.write(i) for i in bg]
    bgFile.close()
    # write out dat file
    datFile = open('data/info.dat','w+')
    [datFile.write(i) for i in dat]
    datFile.close()
    
    cap.release()
    cv2.destroyAllWindows()
    f'Positive Count: {posCount} Negative Count: {negCount}'

def bgList(vidPath):
    if os.path.isdir('data/raw') == False:
        os.mkdir('data/raw')
    count = pathCount('data/raw')
    # it will capture image in each 5 seconds
    frameRate = 1
    
    for i in list(range(0,len(vidPath))):
        sec = 2
        vidcap = cv2.VideoCapture(vidPath[i])   
        success,image = vidcap.read()
        while success:
            vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
            success,image = vidcap.read()
            if success:
                cv2.imwrite(f'data/raw/img{count+1}.jpg', image)
                count += 1
            sec += frameRate
            if (count%50) == 0:
                print("converting images...")
                
    vidcap.release()
    cv2.destroyAllWindows()
    print("Finished making pictures")
        
def selectPosNeg(video_location):
    makeDirs()
    bgList(video_location)
    count = pathCount('data/raw')
    i = 1
    posCount = 1
    negCount = 1
    posList = []
    negList = []
    
    while i <= count:
        refImg = cv2.imread(f'data/raw/img{i}.jpg')
        modImg = refImg.copy()
        box = areaSelector(modImg)
        if box[0] == -1:
            cv2.imwrite(f'data/neg/neg{negCount}.jpg',modImg)
            negList.append(f'neg/neg{negCount}.jpg\n')
            negCount += 1
        elif box[0] == -9:
            i -= 2
        elif box[0] == -21:
            i += 1
            continue
        elif box[0] == -31:
            break
        else:
            modImg = modImg[box]
            cv2.imwrite(f'data/pos/pos{posCount}.jpg',modImg)
            width = modImg.shape[1]
            height = modImg.shape[0]
            posList.append(f'pos/pos{posCount}.jpg  1  0 0 {width} {height}\n')
            posCount += 1
            temp = mask2Rect(box)
            refImg = cv2.rectangle(refImg,temp[0],temp[1],(0,0,0),cv2.FILLED)
            cv2.imwrite(f'data/neg/neg{negCount}.jpg\n',refImg)
            negList.append('neg/neg{negCount}.jpg\n')
            negCount += 1
        f'Image {i}/{count}'
        i += 1
    
    # Negative file list creation
    bgFile = open('data/bg.txt','w+')
    [bgFile.write(i) for i in negList]
    bgFile.close()
    print('Background text file written')
    
    # Positive file list creation
    datFile = open('data/info.dat','w+')
    [datFile.write(i) for i in posList]
    datFile.close()
    print('info.dat file written')
    
    negCount = pathCount('data/neg')
    print('Number of Negative pics: '+str(negCount))
    posCount = pathCount('data/pos')
    print('Number of Positive pics: '+str(posCount))
    
def createSamples():
    print('Beginning vec file creation')
    posCount = pathCount('data/pos')
    createSamples = f'../opencv/opencv_createsamples.exe -vec ./data/output.vec -info ./data/info.dat -bg ./data/bg.txt -num {posCount} -w 60 -h 40'
    program = subprocess.Popen(shlex.split(createSamples),stdout=subprocess.PIPE)
    print(program.stdout.read().decode())
    program.wait()
    print('Vector files created')

def trainCascade():
    print('Cascade training has started, this might take awhile...')
    posCount = pathCount('data/pos')
    negCount = pathCount('data/neg')
    tempPath = os.getcwd()
    os.chdir('data')
    trainCascade = f'../../opencv/opencv_traincascade.exe -data ./ -vec ./output.vec -bg ./bg.txt -numPos {posCount} -numNeg {negCount} -numStages 20 -precalcValBufSize 2048 -precalcIdxBufSize 2048 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -mode ALL -featureType LBP -w 60 -h 40'
    program2 = subprocess.Popen(shlex.split(trainCascade),stdout=subprocess.PIPE)
    print(program2.stdout.read().decode())
    program2.wait()
    os.chdir(tempPath)
    print('Finished Training')

def playVids(video_location):
    usps_cascade = cv2.CascadeClassifier('data/cascade.xml')
    cap = cv2.VideoCapture(video_location[0])
    ret, frame = cap.read()
    
    while(cap.isOpened()):
        success, frame = cap.read()
    
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        usps = usps_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in usps:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
    
        if success:
            cv2.imshow('Video',frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

