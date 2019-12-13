# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 10:38:16 2019

@author: Joel Miller
"""
import cv2,os,subprocess,shlex,shutil,glob,re
from selector import areaSelector, mask2Rect, box2Rect, mask2Box, box2Mask

pathCount = lambda path: len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

#TODO: add argparse for command line operation

def main():
    '''video_location = ['../vids/mario1.mp4',
                      '../vids/mario3.mp4']'''
    #width,height = selectPosNeg(video_location)
    width, height = objTrack(video_location)
    #trainedWidth,trainedHeight = createSamples(width,height)
    #trainCascade(trainedWidth,trainedHeight)
    #playVids(video_location)

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
    makeDirs()
    cap = cv2.VideoCapture(videoLocation[0])
    vidNum = 0
    init = 1
    initScale = 1
    posCount = 0
    negCount = 0
    posList = []
    negList = []
    class Found(Exception): pass
    try:
        while True:
            success, frame = cap.read()
            if not success:
                print('didnt find video')
                break
            refFrame = frame.copy()
            refFrame2 = frame.copy()
            key = cv2.waitKey(1) & 0xFF
    
            # Pause the Video
            if key == 32:
                while True:
                    key2 = cv2.waitKey(1) or 0xFF
                    # Start obj tracking
                    if key2 == ord('w'):
                        if initScale:
                            yRatio = 1
                            box = areaSelector(frame,yRatio,initScale)
                            ratioInit = mask2Rect(box)
                            h = ratioInit[1][1] - ratioInit[0][1]
                            w = ratioInit[1][0] - ratioInit[0][0]
                            yRatio = round(h/w,2)
                            initScale = 0
                            objFrame = refFrame[box]
                            w = objFrame.shape[1]
                            h = objFrame.shape[0]
                        else:
                            box = areaSelector(frame,yRatio,initScale)
                            objFrame = refFrame[box]
                            objFrame = cv2.resize(objFrame,(w,h))
                            
                        init = 2
                        tracker = cv2.TrackerMedianFlow_create()
                        tracker.init(frame,mask2Box(box))
                        posCount += 1
                        cv2.imwrite(f'data/pos/pos{posCount}.jpg',objFrame)
                        posList.append(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                        temp = mask2Rect(box)
                        refFrame = cv2.rectangle(refFrame,temp[0],temp[1],(0,0,0),cv2.FILLED)
                        negCount += 1
                        cv2.imwrite(f'data/neg/neg{negCount}.jpg',refFrame)
                        negList.append(f'neg/neg{negCount}.jpg\n')
                        break
                        
                    cv2.imshow('Video',frame)
                    # Play the Video
                    if key2 == 32:
                        break
                    if key2 == ord('s'):
                        init = 1
                        break
                    if key2 == ord('n'):
                        vidNum += 1
                        if len(videoLocation) > 1 and vidNum < len(videoLocation):
                            cap.release()
                            cap = cv2.VideoCapture(videoLocation[vidNum])
                            break
                        else:
                            if len(videoLocation) == 1:
                                print('Only one video loaded')
                            else:
                                print('Last video in list')
                            
                    if key2 == 27 or key2 == 113:
                        raise Found


            if success and init == 2:
                trackSuccess, box = tracker.update(frame)
                if trackSuccess:
                    rectPts = box2Rect(box)
                    objFrame = refFrame2[box2Mask(box)]
                    cv2.rectangle(frame,rectPts[0],rectPts[1],(255,0,0),2,1)
                    posCount += 1
                    resizedModImg = cv2.resize(objFrame,(w,h))
                    cv2.imwrite(f'data/pos/pos{posCount}.jpg',resizedModImg)
                    posList.append(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                    refFrame = cv2.rectangle(refFrame,rectPts[0],rectPts[1],(0,0,0),cv2.FILLED)
                    negCount += 1
                    cv2.imwrite(f'data/neg/neg{negCount}.jpg',refFrame)
                    negList.append(f'neg/neg{negCount}.jpg\n')
                else:
                    init = 1
            
            if key ==ord('s'):
                init = 1
                        
            # Skip forward 3 seconds
            if key == ord('d'):
                skip = cap.get(cv2.CAP_PROP_POS_MSEC) + 3000
                cap.set(cv2.CAP_PROP_POS_MSEC,skip)
                success, frame = cap.read()
            
            # Skip Back 3 seconds
            if key == ord('a'):
                skip = cap.get(cv2.CAP_PROP_POS_MSEC) - 3000
                cap.set(cv2.CAP_PROP_POS_MSEC,skip)
                success, frame = cap.read()
                
            if key == ord('n'):
                vidNum += 1
                if len(videoLocation) > 1 and vidNum <  len(videoLocation):
                    cap.release()
                    cap = cv2.VideoCapture(videoLocation[vidNum])
                else:
                    if len(videoLocation) == 1:
                        print('Only one video loaded')
                    else:
                        print('Last video in list')
                
                
            # Quit Video Playback by pressing 'q' or ESC
            if key == 113 or key == 27:
                break

            if success:
                cv2.imshow('Video',frame)
            
    except Found:
        print('Finished making Pictures. Now review positives and delete false positives')
        
    def reviewPics(posCount):
        count = posCount
        i = 1
        print('image: '+str(i)+'/'+str(count))
        while i <= count:
            frame = cv2.imread(f'data/pos/pos{i}.jpg')
            while True:
                key = cv2.waitKey(1) or 0xFF
                cv2.imshow('Video',frame)

                if key == ord('a'):
                    try:
                        if i > 1:
                            i -= 1
                            frame = cv2.imread(f'data/pos/pos{i}.jpg')
                            print('image: '+str(i)+'/'+str(count))
                    except:
                        break
                
                if key == ord('d'):
                    if i <= count:
                        i += 1
                        frame = cv2.imread(f'data/pos/pos{i}.jpg')
                        print('image: '+str(i)+'/'+str(count))
                        break
                    
                if key == ord('x'):
                    if i <= count:
                        os.remove(f'data/pos/pos{i}.jpg')
                        posList.remove(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                        posCount -= 1
                        i += 1
                        if i <= count:
                            frame = cv2.imread(f'data/pos/pos{i}.jpg')
                        print('image: '+str(i)+'/'+str(count))
                        break

                             
                if key == 113 or key == 27:
                    i = count + 9000
                    break
        
        cv2.destroyAllWindows()
        retPath = os.getcwd()
        os.chdir('data/pos')
        renameList = [file for file in glob.glob('*.jpg')] 
        def posSort(name):
            a = re.search('pos(\d+).jpg',name)
            return int(a.groups(0)[0])
    
        renameList.sort(key=posSort)
        
        renameNum = 1
        for j in renameList:
            os.rename(j,f'pos{renameNum}.jpg')
            renameNum += 1
        os.chdir(retPath)
        return posCount
                    
    posCount = reviewPics(posCount)
    
    # write out background file
    bgFile = open('data/bg.txt','w+')
    [bgFile.write(i) for i in negList]
    bgFile.close()
    # write out dat file
    datFile = open('data/info.dat','w+')
    [datFile.write(i) for i in posList]
    datFile.close()
    print("Positive Count: "+str(posCount))
    print("Negative Count: "+str(negCount))
    cap.release()
    cv2.destroyAllWindows()
    return w,h


def bgList(vidPath):
    if os.path.isdir('data/raw') == False:
        os.mkdir('data/raw')
    count = pathCount('data/raw')
    # it will capture image in each 5 seconds
    frameRate = 3
    
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
    init = 1
    yRatio = 1
    while i <= count:
        refImg = cv2.imread(f'data/raw/img{i}.jpg')
        modImg = refImg.copy()
        box = areaSelector(modImg,yRatio,init)
    
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
            if init == 1:
                ratioInit = mask2Rect(box)
                h = ratioInit[1][1] - ratioInit[0][1]
                w = ratioInit[1][0] - ratioInit[0][0]
                yRatio = round(h/w,2)
                init = 2
                print('height = '+str(h))
                print('width = '+str(w))
            
            modImg = modImg[box]
            if init == 1:
                cv2.imwrite(f'data/pos/pos{posCount}.jpg',modImg)
                w = modImg.shape[1]
                h = modImg.shape[0]
            else:
                resizedModImg = cv2.resize(modImg,(w,h))
                cv2.imwrite(f'data/pos/pos{posCount}.jpg',resizedModImg)
            posList.append(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
            posCount += 1
            temp = mask2Rect(box)
            refImg = cv2.rectangle(refImg,temp[0],temp[1],(0,0,0),cv2.FILLED)
            cv2.imwrite(f'data/neg/neg{negCount}.jpg',refImg)
            negList.append(f'neg/neg{negCount}.jpg\n')
            negCount += 1
        print('Image: '+ str(i)+'/' + str(count))
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
    return w,h
    
def createSamples(width,height):
    print('Beginning vec file creation')
    posCount = pathCount('data/pos')
    if width and height < 60:
        trainedWidth = width
        trainedWidth = height
    elif width > height:
        trainedWidth = 60
        trainedHeight = int(60*(height/width))
    elif width < height:
        trainedHeight = 60
        trainedWidth = int(60*(width/height))
    
    createSamples = f'../opencv/opencv_createsamples.exe -vec ./data/output.vec -info ./data/info.dat -bg ./data/bg.txt -num {posCount} -w {trainedWidth} -h {trainedHeight}'
    program = subprocess.Popen(shlex.split(createSamples),stdout=subprocess.PIPE)
    print(program.stdout.read().decode())
    program.wait()
    print('Vector files created')
    return trainedWidth, trainedHeight

def trainCascade(trainedWidth,trainedHeight):
    print('Cascade training has started, this might take awhile...')
    posCount = pathCount('data/pos')
    negCount = pathCount('data/neg')
    retPath = os.getcwd()
    os.chdir('data')
    trainCascade = f'../../opencv/opencv_traincascade.exe -data ./ -vec ./output.vec -bg ./bg.txt -numPos {posCount} -numNeg {negCount} -numStages 20 -precalcValBufSize 2048 -precalcIdxBufSize 2048 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -w {trainedWidth} -h {trainedHeight}'
    program2 = subprocess.Popen(shlex.split(trainCascade),stdout=subprocess.PIPE)
    print(program2.stdout.read().decode())
    program2.wait()
    os.chdir(retPath)
    print('Finished Training')

def playVids(video_location):
    obj_cascade = cv2.CascadeClassifier('data/cascade.xml')
    cap = cv2.VideoCapture(video_location[0])
    ret, frame = cap.read()
    
    while(cap.isOpened()):
        success, frame = cap.read()
    
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        usps = obj_cascade.detectMultiScale(gray, 1.3, 5)
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

