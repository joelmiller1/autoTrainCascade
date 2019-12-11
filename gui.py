# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:06:53 2019

@author: Joel Miller


"""

import cv2,os,subprocess,shlex,shutil,glob,re,wx
from selector import areaSelector, mask2Rect, box2Rect, mask2Box, box2Mask

wildcard = "mp4 source (*.mp4)|*.mp4|" \
            "All files (*.*)|*.*"

pathCount = lambda path: len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

       

class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,"Cascade Trainer",size=(400, 350))
        #wx.Frame.CenterOnScreen
        panel = wx.Panel(self, wx.ID_ANY)
        self.currentDirectory = os.getcwd()
        self.filePaths = 0
        self.w = 0
        # Title Text
        titleText = wx.StaticText(panel,label='Location of video files to train')
        
        # create text box
        textBox = wx.TextCtrl(panel,size = (200,50), style=wx.TE_MULTILINE)
        
        # create the buttons and bindings
        selectFilesBtn = wx.Button(panel, label="Select Files")
        selectFilesBtn.Bind(wx.EVT_BUTTON, self.onOpenFile)
        
        # Button for video obj track training
        vidTrainBtn = wx.Button(panel, label="Video Track Training")
        vidTrainBtn.Bind(wx.EVT_BUTTON, self.startVidTraining)
        
        # Button for vid to pic training
        picTrainBtn = wx.Button(panel, label="Vid2Pic Training")
        picTrainBtn.Bind(wx.EVT_BUTTON, self.startPicTraining)
        frameRateInfo = wx.StaticText(panel,label='Enter Frame Rate to save pictures from video:')
        self.frameRateInput = wx.TextCtrl(panel)
        
        # Status Box
        statusText = wx.StaticText(panel,label='Status:')
        self.statusBox = wx.TextCtrl(panel,size = (200,150), style=wx.TE_MULTILINE)

        # put the buttons in a sizer
        vSize = wx.BoxSizer(wx.VERTICAL)
        hSize = wx.BoxSizer(wx.HORIZONTAL)
        vSize.Add(titleText,0, wx.ALL|wx.CENTER)
        vSize.Add(textBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        vSize.Add(selectFilesBtn, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(vidTrainBtn, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(picTrainBtn, 0, wx.ALL|wx.CENTER, 5)
        hSize.Add(frameRateInfo, 0, wx.ALL|wx.CENTER, 5)
        hSize.Add(self.frameRateInput, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(hSize)
        vSize.Add(statusText,0, wx.ALL|wx.CENTER)
        vSize.Add(self.statusBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        panel.SetSizer(vSize)
        
    def makeDirs(self):
        self.statusBox.AppendText("Creating Temporary Directories\n")
        if os.path.isdir('data') == False:
            os.mkdir('data')
            os.mkdir('data/pos')
            os.mkdir('data/neg')
        else:
            shutil.rmtree('data')
            os.mkdir('data')
            os.mkdir('data/pos')
            os.mkdir('data/neg')
            
    def objTrack(self):
        self.makeDirs()
        videoLocation = self.filePaths
        cap = cv2.VideoCapture(videoLocation[0])
        vidNum = 0
        init = 1
        initScale = 1
        posCount = 0
        negCount = 0
        posList = []
        negList = []
        self.statusBox.AppendText('Space -- to Pause/Play video\n')
        self.statusBox.AppendText('w -- to select object to train on\n')
        self.statusBox.AppendText('s -- to stop obj tracking (if it starts tracking something weird)\n')
        self.statusBox.AppendText('a -- rewind 3 seconds\n')
        self.statusBox.AppendText('d -- fast foward 3 seconds\n')
        self.statusBox.AppendText('n -- to move on to next video in list\n')
        self.statusBox.AppendText('q or Esc -- to quit\n')
        
        class Found(Exception): pass
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    self.statusBox.AppendText('didnt find video\n')
                    break
                refFrame = frame.copy()
                refFrame2 = frame.copy()
                key = cv2.waitKey(50) & 0xFF
        
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
                            posPath = os.path.abspath('data/pos')
                            cv2.imwrite(f'{posPath}\\pos{posCount}.jpg',objFrame)
                            posList.append(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                            temp = mask2Rect(box)
                            refFrame = cv2.rectangle(refFrame,temp[0],temp[1],(0,0,0),cv2.FILLED)
                            negCount += 1
                            negPath = os.path.abspath('data/neg')
                            cv2.imwrite(f'{negPath}\\neg{negCount}.jpg',refFrame)
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
                                    self.statusBox.AppendText('Only one video loaded\n')
                                else:
                                    self.statusBox.AppendText('Last video in list\n')
                                
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
                        cv2.imwrite(f'{posPath}\\pos{posCount}.jpg',resizedModImg)
                        posList.append(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                        refFrame = cv2.rectangle(refFrame,rectPts[0],rectPts[1],(0,0,0),cv2.FILLED)
                        negCount += 1
                        cv2.imwrite(f'{negPath}\\neg{negCount}.jpg',refFrame)
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
                            self.statusBox.AppendText('Only one video loaded\n')
                        else:
                            self.statusBox.AppendText('Last video in list\n')
                    
                    
                # Quit Video Playback by pressing 'q' or ESC
                if key == 113 or key == 27:
                    break
    
                if success:
                    cv2.imshow('Video',frame)
                
        except Found:
            self.statusBox.AppendText('Finished making Pictures. Now review positives and delete false positives\n')
            
        def reviewPics(posCount):
            self.statusBox.AppendText('a -- to go to previous picture\n')
            self.statusBox.AppendText('d -- to go to next picture\n')
            self.statusBox.AppendText('x -- to delete picture from training arena\n')
            self.statusBox.AppendText('q or Esc -- to skip review\n')
            count = posCount
            i = 1
            self.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
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
                                self.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
                        except:
                            break
                    
                    if key == ord('d'):
                        if i <= count:
                            i += 1
                            frame = cv2.imread(f'data/pos/pos{i}.jpg')
                            self.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
                            break
                        
                    if key == ord('x'):
                        if i <= count:
                            os.remove(f'data/pos/pos{i}.jpg')
                            posList.remove(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                            posCount -= 1
                            i += 1
                            if i <= count:
                                frame = cv2.imread(f'data/pos/pos{i}.jpg')
                            self.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
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
        self.statusBox.AppendText("Positive Count: "+str(posCount)+'\n')
        self.statusBox.AppendText("Negative Count: "+str(negCount)+'\n')
        cap.release()
        cv2.destroyAllWindows()
        try:
            self.w = w
            self.h = h
        except:
            pass
        #return w,h
    
    
    def bgList(self):
        vidPath = self.filePaths
        if os.path.isdir('data/raw') == False:
            os.mkdir('data/raw')
        count = pathCount('data/raw')
        # it will capture image in each 5 seconds
        try:
            frameRate = int(self.frameRateInput.GetValue())
        except:
            frameRate = 3
            self.statusBox.AppendText("Error reading frame rate, defaulting to 3\n")
        
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
                    self.statusBox.AppendText("converting images...\n")
                    
        vidcap.release()
        cv2.destroyAllWindows()
        self.statusBox.AppendText("Finished making pictures\n")
            
    def selectPosNeg(self):
        self.makeDirs()
        #video_location = self.filePaths
        self.bgList()
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
                    self.statusBox.AppendText('height = '+str(h)+'\n')
                    self.statusBox.AppendText('width = '+str(w)+'\n')
                
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
            self.statusBox.AppendText('Image: '+ str(i)+'/' + str(count)+'\n')
            i += 1
        
        # Negative file list creation
        bgFile = open('data/bg.txt','w+')
        [bgFile.write(i) for i in negList]
        bgFile.close()
        self.statusBox.AppendText('Background text file written\n')
        
        # Positive file list creation
        datFile = open('data/info.dat','w+')
        [datFile.write(i) for i in posList]
        datFile.close()
        self.statusBox.AppendText('info.dat file written\n')
        
        negCount = pathCount('data/neg')
        self.statusBox.AppendText('Number of Negative pics: '+str(negCount)+'\n')
        posCount = pathCount('data/pos')
        self.statusBox.AppendText('Number of Positive pics: '+str(posCount)+'\n')
        self.w = w
        self.h = h
        
    def createSamples(self):
        self.statusBox.AppendText('Beginning vec file creation\n')
        posCount = pathCount('data/pos')
        width = self.w
        height = self.h
        if width and height < 60:
            trainedWidth = width
            trainedHeight = height
        elif width > height:
            trainedWidth = 60
            trainedHeight = int(60*(height/width))
        elif width < height:
            trainedHeight = 60
            trainedWidth = int(60*(width/height))
        
        createSamples = f'../opencv/opencv_createsamples.exe -vec ./data/output.vec -info ./data/info.dat -bg ./data/bg.txt -num {posCount} -w {trainedWidth} -h {trainedHeight}'
        program = subprocess.Popen(shlex.split(createSamples),stdout=subprocess.PIPE)
        self.statusBox.AppendText(program.stdout.read().decode())
        self.statusBox.AppendText('\n')
        program.wait()
        self.statusBox.AppendText('Vector files created\n')
        self.trainedWidth = trainedWidth
        self.trainedHeight = trainedHeight
    
    def trainCascade(self):
        self.statusBox.AppendText('Cascade training has started, this might take awhile...\n')
        trainedWidth = self.trainedWidth 
        trainedHeight = self.trainedHeight
        posCount = pathCount('data/pos')
        negCount = pathCount('data/neg')
        retPath = os.getcwd()
        os.chdir('data')
        trainCascade = f'../../opencv/opencv_traincascade.exe -data ./ -vec ./output.vec -bg ./bg.txt -numPos {posCount} -numNeg {negCount} -numStages 20 -precalcValBufSize 2048 -precalcIdxBufSize 2048 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -w {trainedWidth} -h {trainedHeight}'
        program2 = subprocess.Popen(shlex.split(trainCascade),stdout=subprocess.PIPE)
        self.statusBox.AppendText(program2.stdout.read().decode())
        self.statusBox.AppendText('\n')
        program2.wait()
        os.chdir(retPath)
        self.statusBox.AppendText('Finished Training\n')
    
    def playVids(self):
        obj_cascade = cv2.CascadeClassifier('data/cascade.xml')
        video_location = self.filePaths
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


    #----------------------------------------------------------------------
    def onOpenFile(self, event):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentDirectory, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.filePaths = dlg.GetPaths()
            a = dlg.GetPaths()
            self.textBox.Clear()
            for i in list(range(0,len(self.filePaths))):
                self.textBox.AppendText(a[i]+'\n')
        dlg.Destroy()
    
    def startVidTraining(self, event):
        if self.filePaths:
            self.objTrack()
            if self.w:
                self.createSamples()
                self.trainCascade()
                self.playVids()
            else:
                self.statusBox.AppendText('Nothing to Train\n')
        else:
            self.statusBox.AppendText('No video Selected\n')
        
    def startPicTraining(self, event):
        if self.filePaths:
            self.selectPosNeg()
            if self.w:
                self.createSamples()
                self.trainCascade()
                self.playVids()
            else:
                self.statusBox.AppendText('Nothing to Train\n')
        else:
            self.statusBox.AppendText('No video Selected\n')
        

#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()
    
    
