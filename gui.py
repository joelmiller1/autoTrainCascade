import cv2,os,subprocess,shlex,shutil,glob,re,wx
from threading import Thread
from selector import areaSelector, mask2Rect, box2Rect, mask2Box, box2Mask

pathCount = lambda path: len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

class TrainingClass():
    def __init__(self, trainingTabVars):
        # Initialize thread to be run
        self.tcVars = trainingTabVars

        
    def makeDirs(self):
        self.tcVars.statusBox.AppendText("Creating Temporary Directories\n")
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
        videoLocation = self.tcVars.filePaths
        cap = cv2.VideoCapture(videoLocation[0])
        vidNum = 0
        init = 1
        initScale = 1
        posCount = 0
        negCount = 0
        posList = []
        negList = []
        self.tcVars.statusBox.AppendText('Space -- to Pause/Play video\n')
        self.tcVars.statusBox.AppendText('w -- to select object to train on\n')
        self.tcVars.statusBox.AppendText('s -- to stop obj tracking (if it starts tracking something weird)\n')
        self.tcVars.statusBox.AppendText('a -- rewind 3 seconds\n')
        self.tcVars.statusBox.AppendText('d -- fast foward 3 seconds\n')
        self.tcVars.statusBox.AppendText('n -- to move on to next video in list\n')
        self.tcVars.statusBox.AppendText('q or Esc -- to quit\n\n')
        
        class Found(Exception): pass
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    self.tcVars.statusBox.AppendText('didnt find video\n')
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
                            self.tcVars.statusBox.AppendText('Only one video loaded\n')
                        else:
                            self.tcVars.statusBox.AppendText('Last video in list\n')
                    
                    
                # Quit Video Playback by pressing 'q' or ESC
                if key == 113 or key == 27:
                    break
    
                if success:
                    cv2.imshow('Video',frame)
                
        except Found:
            self.tcVars.statusBox.AppendText('Finished making Pictures. Now review positives and delete false positives\n')
            
        def reviewPics(posCount):
            self.tcVars.statusBox.AppendText('a -- to go to previous picture\n')
            self.tcVars.statusBox.AppendText('d -- to go to next picture\n')
            self.tcVars.statusBox.AppendText('x -- to delete picture from training arena\n')
            self.tcVars.statusBox.AppendText('q or Esc -- to skip review\n\n')
            count = posCount
            i = 1
            self.tcVars.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
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
                                self.tcVars.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
                        except:
                            break
                    
                    if key == ord('d'):
                        if i <= count:
                            i += 1
                            frame = cv2.imread(f'data/pos/pos{i}.jpg')
                            self.tcVars.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
                            break
                        
                    if key == ord('x'):
                        if i <= count:
                            os.remove(f'data/pos/pos{i}.jpg')
                            posList.remove(f'pos/pos{posCount}.jpg  1  0 0 {w} {h}\n')
                            posCount -= 1
                            i += 1
                            if i <= count:
                                frame = cv2.imread(f'data/pos/pos{i}.jpg')
                            self.tcVars.statusBox.AppendText('image: '+str(i)+'/'+str(count)+'\n')
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
        self.tcVars.statusBox.AppendText("Positive Count: "+str(posCount)+'\n')
        self.tcVars.statusBox.AppendText("Negative Count: "+str(negCount)+'\n')
        cap.release()
        cv2.destroyAllWindows()
        try:
            self.tcVars.w = w
            self.tcVars.h = h
        except:
            pass
        #return w,h
            
    def selectPosNeg(self):
        self.makeDirs()
        #video_location = self.filePaths
        
        '''relocating bgList'''
        vidPath = self.tcVars.filePaths
        if os.path.isdir('data/raw') == False:
            os.mkdir('data/raw')
        count = pathCount('data/raw')
        # it will capture image in each 5 seconds
        try:
            frameRate = int(self.tcVars.frameRateInput.GetValue())
        except:
            frameRate = 3
            self.tcVars.statusBox.AppendText("Error reading frame rate, defaulting to 3\n")
        
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
                    self.tcVars.statusBox.AppendText("converting images...\n")
                    
        vidcap.release()
        cv2.destroyAllWindows()
        self.tcVars.statusBox.AppendText("Finished making pictures\n")
        
        count = pathCount('data/raw')
        i = 1
        posCount = 1
        negCount = 1
        posList = []
        negList = []
        init = 1
        yRatio = 1
        self.tcVars.statusBox.AppendText('a -- to go to previous picture\n')
        self.tcVars.statusBox.AppendText('d -- to go to next picture\n')
        self.tcVars.statusBox.AppendText('s -- to skip picture from training arena\n')
        self.tcVars.statusBox.AppendText('q or Esc -- to skip review\n\n')
        
        while i <= count:
            self.tcVars.statusBox.AppendText('Image: '+ str(i)+'/' + str(count)+'\n')
            refImg = cv2.imread(f'data/raw/img{i}.jpg')
            modImg = refImg.copy()
            box = areaSelector(modImg,yRatio,init)
            
            if box[0] == -1:
                cv2.imwrite(f'data/neg/img{i}.jpg',modImg)
                negList.append(f'neg/img{i}.jpg\n')
                negCount += 1
                i += 1
            elif box[0] == -9: # previous picturew
                if i > 1:
                    i -= 1
            elif box[0] == -21: # next picture
                cv2.imwrite(f'data/neg/img{i}.jpg',modImg)
                negList.append(f'neg/img{i}.jpg\n')
                negCount += 1
                i += 1
            elif box[0] == -41: # skip picture
                i += 1
                continue
            elif box[0] == -31:  # quit
                break
            else:
                if init == 1:
                    ratioInit = mask2Rect(box)
                    h = ratioInit[1][1] - ratioInit[0][1]
                    w = ratioInit[1][0] - ratioInit[0][0]
                    yRatio = round(h/w,2)
                    init = 2
                    self.tcVars.statusBox.AppendText('height = '+str(h)+'\n')
                    self.tcVars.statusBox.AppendText('width = '+str(w)+'\n')
                
                modImg = modImg[box]
                if init == 1:
                    cv2.imwrite(f'data/pos/img{i}.jpg',modImg)
                    w = modImg.shape[1]
                    h = modImg.shape[0]
                else:
                    resizedModImg = cv2.resize(modImg,(w,h))
                    cv2.imwrite(f'data/pos/img{i}.jpg',resizedModImg)
                posList.append(f'pos/img{i}.jpg  1  0 0 {w} {h}\n')
                posCount += 1
                temp = mask2Rect(box)
                refImg = cv2.rectangle(refImg,temp[0],temp[1],(0,0,0),cv2.FILLED)
                cv2.imwrite(f'data/neg/img{i}.jpg',refImg)
                negList.append(f'neg/img{i}.jpg\n')
                negCount += 1
                i += 1
        
        # Negative file list creation
        bgFile = open('data/bg.txt','w+')
        [bgFile.write(i) for i in negList]
        bgFile.close()
        self.tcVars.statusBox.AppendText('Background text file written\n')
        
        # Positive file list creation
        datFile = open('data/info.dat','w+')
        [datFile.write(i) for i in posList]
        datFile.close()
        self.tcVars.statusBox.AppendText('info.dat file written\n')
        
        negCount = pathCount('data/neg')
        self.tcVars.statusBox.AppendText('Number of Negative pics: '+str(negCount)+'\n')
        posCount = pathCount('data/pos')
        self.tcVars.statusBox.AppendText('Number of Positive pics: '+str(posCount)+'\n')
        self.tcVars.w = w
        self.tcVars.h = h
        
    def createSamples(self):
        self.tcVars.statusBox.AppendText('Beginning vec file creation\n')
        posCount = pathCount('data/pos')
        width = self.tcVars.w
        height = self.tcVars.h
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
        self.tcVars.statusBox.AppendText(program.stdout.read().decode())
        self.tcVars.statusBox.AppendText('\n')
        program.wait()
        self.tcVars.statusBox.AppendText('Vector files created\n')
        self.tcVars.trainedWidth = trainedWidth
        self.tcVars.trainedHeight = trainedHeight


class playVidClass():
    def __init__(self,pvClass):
        self.pvClass = pvClass
        
    def playVids(self):
        self.pvClass.statusBox.AppendText('starting to play videos.\n')
        cascadeLoc = self.pvClass.cascadeLoc
        print(cascadeLoc)
        obj_cascade = cv2.CascadeClassifier(cascadeLoc)
        video_location = self.pvClass.videoLoc
        cap = cv2.VideoCapture(video_location)
        
        self.pvClass.statusBox.AppendText('Space -- to Pause/Play video\n')
        self.pvClass.statusBox.AppendText('a -- rewind 3 seconds\n')
        self.pvClass.statusBox.AppendText('d -- fast foward 3 seconds\n')
        self.pvClass.statusBox.AppendText('q or Esc -- to quit\n\n')
        
        class Found(Exception): pass

        try:
            while True:
                success, frame = cap.read()
                key = cv2.waitKey(1) & 0xFF
                if not success:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                objCascade = obj_cascade.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in objCascade:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)

                # Pause the Video (space)
                if key == 32:
                    while True:
                        key2 = cv2.waitKey(1) or 0xFF
                        vidTime = int(round(cap.get(cv2.CAP_PROP_POS_MSEC)/1000,0))
                        cv2.putText(frame,str(vidTime)+' seconds',(5,10),cv2.FONT_HERSHEY_DUPLEX,0.4,(0,0,0),1)
                        cv2.imshow('Video',frame)
                        # Play the Video
                        if key2 == 32:
                            break
                        if key2 == 27 or key2 == 113:
                            raise Found

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

                # Quit Video Playback by pressing 'q' or ESC
                if key == 113 or key == 27:
                    break

                vidTime = int(round(cap.get(cv2.CAP_PROP_POS_MSEC)/1000,0))
                cv2.putText(frame,str(vidTime)+' seconds',(5,10),cv2.FONT_HERSHEY_DUPLEX,0.4,(0,0,0),1)
                cv2.imshow('Video',frame)
                
        except Found:
            self.pvClass.statusBox.AppendText('Done.\n')
        
        cap.release()
        cv2.destroyAllWindows()


class trainCascadeThread(Thread):
    def __init__(self, trainingTabVars,btn):
        # Initialize thread to be run
        Thread.__init__(self)
        self.trainingTabVars = trainingTabVars
        self.btn = btn
        self.start()    # start the thread

    def run(self):
        # Code to be run in new thread
        self.trainingTabVars.statusBox.AppendText('Cascade training has started, this might take awhile...\n')
        trainedWidth = self.trainingTabVars.trainedWidth
        trainedHeight = self.trainingTabVars.trainedHeight
        posCount = pathCount('data/pos')
        negCount = pathCount('data/neg')
        retPath = os.getcwd()
        os.chdir('data')
        trainCascade = f'../../opencv/opencv_traincascade.exe -data ./ -vec ./output.vec -bg ./bg.txt -numPos {posCount} -numNeg {negCount} -numStages 20 -precalcValBufSize 2048 -precalcIdxBufSize 2048 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -w {trainedWidth} -h {trainedHeight}'
        program2 = subprocess.Popen(shlex.split(trainCascade),stdout=subprocess.PIPE)
        self.trainingTabVars.statusBox.AppendText(program2.stdout.read().decode())
        self.trainingTabVars.statusBox.AppendText('\n')
        program2.wait()
        os.chdir(retPath)
        
        # Post training cleanup
        os.chdir(self.trainingTabVars.currentDirectory)
        if os.path.isdir('\\cascade.xml') == True:
            os.remove("\\cascade.xml")
            
        self.trainingTabVars.statusBox.AppendText('Cascade training finished.\n')
        self.trainingTabVars.statusBox.AppendText('Cleaning Files....\n')
        temp = self.trainingTabVars.filePaths[0]
        temp2 = re.findall('(.*)\\\.*$',temp)
        cascadeLoc1 =  temp2[0] + "\\data\\cascade.xml"
        cascadeLoc2 = self.trainingTabVars.currentDirectory + "\\cascade.xml"
        self.trainingTabVars.cascadeLoc = cascadeLoc2
        try:
            os.rename(cascadeLoc1,cascadeLoc2)
        except:
            self.trainingTabVars.statusBox.AppendText('no cascade classifier found\n')
        self.trainingTabVars.statusBox.AppendText('done.\n')
        self.btn.Enable()
        playVideo = playVidClass(self.trainingTabVars)
        playVideo.playVids()
    
    def postTime(self,i):
        self.trainingTabVars.statusBox.AppendText('here?\n')


class TrainingTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        vSize = wx.BoxSizer(wx.VERTICAL)
        self.currentDirectory = os.getcwd()
        
        # create Title and file viewer       
        titleText = wx.StaticText(self,wx.ID_ANY,label='Location of video files to train')
        self.textBox = wx.TextCtrl(self,wx.ID_ANY,size = (200,50), style=wx.TE_MULTILINE)
        
        # create the buttons and bindings
        selectFilesBtn = wx.Button(self,wx.ID_ANY, label="Select Video")
        selectFilesBtn.Bind(wx.EVT_BUTTON, self.onOpenFile)
        
        # Button for video obj track training
        vidTrainBtn = wx.Button(self,wx.ID_ANY, label="Video Obj Track Training")
        vidTrainBtn.Bind(wx.EVT_BUTTON, self.startVidTraining)
        
        # Button for vid to pic training
        picTrainBtn = wx.Button(self,wx.ID_ANY, label="Vid2Pic Training")
        picTrainBtn.Bind(wx.EVT_BUTTON, self.startPicTraining)
        frameRateInfo = wx.StaticText(self,wx.ID_ANY,label='Enter Frame Rate to save pictures from video:')
        self.frameRateInput = wx.TextCtrl(self,wx.ID_ANY)
        
        # Status Box
        statusText = wx.StaticText(self,wx.ID_ANY,label='Status:')
        self.statusBox = wx.TextCtrl(self,wx.ID_ANY,size = (200,250), style=wx.TE_MULTILINE)
        
        vSize = wx.BoxSizer(wx.VERTICAL)
        hSize = wx.BoxSizer(wx.HORIZONTAL)
        vSize.Add(titleText,0, wx.ALL|wx.CENTER)
        vSize.Add(self.textBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        vSize.Add(selectFilesBtn, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(vidTrainBtn, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(picTrainBtn, 0, wx.ALL|wx.CENTER, 5)
        hSize.Add(frameRateInfo, 0, wx.ALL|wx.CENTER, 5)
        hSize.Add(self.frameRateInput, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(hSize)
        vSize.Add(statusText,0, wx.ALL|wx.CENTER)
        vSize.Add(self.statusBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        self.SetSizer(vSize)
        
    def onOpenFile(self, event):
        # create and run dialog box
        wildcard = "mp4 source (*.mp4)|*.mp4|" \
            "All files (*.*)|*.*"
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
            self.videoLoc = a[0]
        dlg.Destroy()
        
    def startVidTraining(self, event):
        # Start training through video
        btn = event.GetEventObject()
        btn.Disable()
        vidTrainClass = TrainingClass(self)
        if self.filePaths:
            vidTrainClass.objTrack()
            if self.w:
                vidTrainClass.createSamples()
                trainCascadeThread(self,btn)
            else:
                self.statusBox.AppendText('Nothing to Train\n')
        else:
            self.statusBox.AppendText('No video Selected\n')
        
    def startPicTraining(self, event):
        btn = event.GetEventObject()
        btn.Disable()
        vidTrainClass = TrainingClass(self)
        if self.filePaths:
            vidTrainClass.selectPosNeg()
            if self.w:
                vidTrainClass.createSamples()
                trainCascadeThread(self,btn)
            else:
                self.statusBox.AppendText('Nothing to Train\n')
        else:
            self.statusBox.AppendText('No video Selected\n')


class PlaybackTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        vSize = wx.BoxSizer(wx.VERTICAL)
        self.currentDirectory = os.getcwd()
        
        # create the buttons and bindings
        self.cascadeTextBox = wx.TextCtrl(self,wx.ID_ANY)
        loadCascadeBtn = wx.Button(self,wx.ID_ANY, label="Load Cascade")
        loadCascadeBtn.Bind(wx.EVT_BUTTON, self.loadCascade)
        
        # Button for video obj track training
        self.videoTextBox = wx.TextCtrl(self,wx.ID_ANY)
        selectVideoBtn = wx.Button(self,wx.ID_ANY, label="Select Video")
        selectVideoBtn.Bind(wx.EVT_BUTTON, self.selectVideo)
        
        # Play video with obj detection 
        playVideoBtn = wx.Button(self,wx.ID_ANY, label="Play Video")
        playVideoBtn.Bind(wx.EVT_BUTTON, self.playVideo)
        
        # Status Box
        statusText = wx.StaticText(self,wx.ID_ANY,label='Status:')
        self.statusBox = wx.TextCtrl(self,wx.ID_ANY,size = (200,250), style=wx.TE_MULTILINE)
        
        # Add Cascade Selection Sizers
        vSize = wx.BoxSizer(wx.VERTICAL)
        cascadeBox = wx.StaticBox(self,-1,"Load Cascade Filter:")
        cascadeSizer = wx.StaticBoxSizer(cascadeBox,wx.HORIZONTAL)
        cascadeSizer.Add(self.cascadeTextBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 3)
        cascadeSizer.Add(loadCascadeBtn, 0, wx.ALL|wx.CENTER, 3)
        vSize.Add(cascadeSizer)
        
        # Add Video Selection Sizers
        videoBox = wx.StaticBox(self,-1,"Load Video to Play:")
        videoSizer = wx.StaticBoxSizer(videoBox,wx.HORIZONTAL)
        videoSizer.Add(self.videoTextBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 3)
        videoSizer.Add(selectVideoBtn, 0, wx.ALL|wx.CENTER, 3)
        vSize.Add(videoSizer)
        
        # Play button Sizer
        vSize.Add(playVideoBtn, 0, wx.ALL|wx.CENTER, 15)
        
        # Status Box Sizer
        vSize.Add(statusText,0, wx.ALL|wx.CENTER,5)
        vSize.Add(self.statusBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        self.SetSizer(vSize)
        
    def loadCascade(self, event):
        # create and run dialog box
        wildcard = "xml source (*.xml)|*.xml|" \
            "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Select a xml cascade filter",
            defaultDir=self.currentDirectory, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.cascadePath = dlg.GetPaths()
            a = dlg.GetPaths()
            self.cascadeTextBox.Clear()
            self.cascadeTextBox.AppendText(a[0])
            self.cascadeLoc = a[0]
        dlg.Destroy()
        
    def selectVideo(self, event):
        # create and run dialog box
        wildcard = "xml source (*.mp4)|*.mp4|" \
            "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Select a video to play",
            defaultDir=self.currentDirectory, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.videoPath = dlg.GetPaths()
            a = dlg.GetPaths()
            self.videoTextBox.Clear()
            self.videoTextBox.AppendText(a[0])
            self.videoLoc = a[0]
        dlg.Destroy()
    
    def playVideo(self,event):
        playVideo = playVidClass(self)
        playVideo.playVids()

class TrackingTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        vSize = wx.BoxSizer(wx.VERTICAL)
        self.currentDirectory = os.getcwd()
        
        # create the Radio Box
        panel = wx.Panel(self,wx.VERTICAL)
        self.rBoxList = ['Video','Webcam','IP']
        self.radioBox1 = wx.RadioBox(panel,label="Video Source",choices=self.rBoxList,majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.radioBox1.Bind(wx.EVT_RADIOBOX,self.onRadioBox)
        # source label and text
        self.sourceLabel = wx.StaticText(self,wx.ID_ANY,label="Video Location: ")
        self.sourceText = wx.TextCtrl(self,wx.ID_ANY)
        self.selectVideoBtn = wx.Button(self,wx.ID_ANY,label="Select Video")
        self.selectVideoBtn.Bind(wx.EVT_BUTTON, self.onSelectVideoBtn)

        
        # Load Cascade Filter
        loadCascadeBtn = wx.Button(self,wx.ID_ANY,label="Load Cascade Filter")
        loadCascadeBtn.Bind(wx.EVT_BUTTON,self.onLoadCascadeBtn)
        
        # Start Tracking Button 
        startBtn = wx.Button(self,wx.ID_ANY, label="Start Tracking")
        startBtn.Bind(wx.EVT_BUTTON, self.onStartBtn)
        
        # Status Box
        statusText = wx.StaticText(self,wx.ID_ANY,label='Status:')
        self.statusBox = wx.TextCtrl(self,wx.ID_ANY,size = (200,250), style=wx.TE_MULTILINE)
        
        # Add Cascade Selection Sizers
        vSize = wx.BoxSizer(wx.VERTICAL)
        vSize.Add(panel, 0, wx.ALL|wx.CENTER,5)
        hSize = wx.BoxSizer(wx.HORIZONTAL)
        hSize.Add(self.sourceLabel,wx.CENTER,5)
        hSize.Add(self.sourceText,wx.CENTER,5)
        hSize.Add(self.selectVideoBtn)
        vSize.Add(hSize,0,wx.ALL|wx.CENTER|wx.EXPAND,5)
        vSize.Add(loadCascadeBtn, 0, wx.ALL|wx.CENTER,5)
        vSize.Add(startBtn, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(statusText,0, wx.ALL|wx.CENTER,5)
        vSize.Add(self.statusBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        self.SetSizer(vSize)
        
    def onSelectVideoBtn(self,event):
        # create and run dialog box
        wildcard = "mp4 source (*.mp4)|*.mp4|" \
            "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Select a video file",
            defaultDir=self.currentDirectory, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.cascadePath = dlg.GetPaths()
            a = dlg.GetPaths()
            self.sourceText.Clear()
            self.sourceText.AppendText(a[0])
            self.videoLoc = a[0]
        dlg.Destroy()
    
    def onLoadCascadeBtn(self, event):
        # create and run dialog box
        wildcard = "xml source (*.xml)|*.xml|" \
            "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Select a xml cascade filter",
            defaultDir=self.currentDirectory, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.cascadePath = dlg.GetPaths()
            a = dlg.GetPaths()
            self.sourceText.Clear()
            self.sourceText.AppendText(a[0])
            self.cascadeLoc = a[0]
        dlg.Destroy()
        
    def onRadioBox(self,event):
        self.statusBox.AppendText(self.radioBox1.GetStringSelection() + '\n')
        if(self.radioBox1.GetStringSelection() == 'Video'):
            self.sourceLabel.SetLabel('Video Location: ')
            self.selectVideoBtn.Enable()
            self.sourceText.Enable()
            self.sourceText.Clear()
        elif(self.radioBox1.GetStringSelection() == 'Webcam'):
            self.sourceLabel.SetLabel('(default is 0)')
            self.sourceText.Disable()
            self.selectVideoBtn.Disable()
            self.sourceText.Clear()
        else:
            self.sourceLabel.SetLabel('IP Address: ')
            self.selectVideoBtn.Disable()
            self.sourceText.Enable()
            self.sourceText.Clear()
        
    def onStartBtn(self,event):
        self.statusBox.AppendText('start button pressed\n')


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Cascade Traininer",size=(400, 550))

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # Create the tab windows
        tab1 = TrainingTab(nb)
        tab2 = PlaybackTab(nb)
        tab3 = TrackingTab(nb)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Training")
        nb.AddPage(tab2, "Playback")
        nb.AddPage(tab3, "Tracking")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
    

if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()