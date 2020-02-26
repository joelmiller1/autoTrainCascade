# Make your own Cascade Classifier easily
## Motivation and Background 
The purpose of this python project is to take most of the work out of training so you can use the standard opencv object tracking
examples to track your own custom object. The problem with the whole training process is that it is tedious and the end result may
not work. I created this (for Windows users) in order to try and automate some of the process.... this is still far from perfect, but
it can be easily modified/built upon to train faster. Changing the training parameters will help deliver better results for what you 
are trying to achieve, changing things like using more positive and negative images will produce better results. It doesn't work well for objects that change a lot (i.e. different shapes, aspect viewing angles, etc). But for something that doesn't change much, like logos, it can do well on. 

https://docs.opencv.org/3.4/dc/d88/tutorial_traincascade.html

## Instructions
__Step 1__ -
Make a new folder somewhere and rename to what you please (For this example, I will name the folder __Train__). cd into __Train__ and clone the [autoTrainCascade](https://github.com/joelmiller1/autoTrainCascade.git) repo into the __Train__ folder. Next, download and install/extract files from https://github.com/opencv/opencv/releases/tag/3.4.8 . If you are on windows then get the vc-14/15 files. It downloads an exe file. Run the exe file which basically is a 7zip extracter that unzips all the files you need. The files you need to run the program are located in the extracted_files_loc/build/x64/vc15/bin/. Copy the entire contents of that bin folder into a new folder called __opencv__, and place the __opencv__ folder in the __Train__ folder.  You don't need any of the other contents of the extracted files, so you can delete the other stuff if you wish.

The file structure should look like this:

```bash
├── Train
│   ├── autoTrainCascade
│   │   ├── gui.py
│   │   ├── selector.py
│   ├── opencv
│   │   ├── opencv_annotation.exe
│   │   ├── opencv_createsamples.exe
│   │   ├── opencv__ffmgeg348_64.dll
│   │   ├── opencv_interactive-calibration.exe
│   │   ├── opencv_traincascade.exe
│   │   ├── opencv_version.exe
│   │   ├── opencv_version_win32.exe
│   │   ├── opencv_visualisation.exe
│   │   ├── opencv_world348.dll
│   │   ├── opencv_world348.pdb
│   │   ├── opencv_world348d.dll
│   │   ├── opencv_world348d.dll
│   ├── vids
│   │   ├── vid1.mp4
│   │   ├── vid2.mp4
```

__Step 2__ -

The code also requires additional libraries that can be installed via pip, conda, or other. Most of them are standard for python but here is the list of all required libraries:

`import cv2,os,subprocess,shlex,shutil,glob,re,wx`

Run the gui.py program. On the gui, you can click on the "Select Files" button which will open up a file browser that you can use to point to one or more video files. After the videos are selected click "open". The video file locations should appear in the top text box. 

![gui](/gui.jpg)

__Step 3__ - 

The "Video Track Training" button will allow you to play the videos (w/ pause, foward, reverse skipping) and select an object that you want to train. In order to track/train an object, first pause the video with the object in frame and press "w". This will allow you to draw a box around the object you want to train. The very first time you draw the box is important because the script will save the aspect ratio of the box you created in order to resize/reshape future images you wish to train as well as constrain any future boxes you draw to that aspect ratio. The script will then track that object until the tracker fails. You can select an object multiple times throughout the video (or subsequent videos), but you can only do one object at a time. For example, you can not select two objects on the same frame; but it will allow you to train an object that only appears a few times throughout the video.

If you lose track on the object, or it starts tracking something other than the object you selected, you can press "s" to stop tracking the object. You will be able to go back and delete the false objects it was tracking later. Once you are done with the video, you can press "n" for the next video in your playlist. You will then be able to pause, select the object you want to train again, and continue on.

Once you are finished with your video playlist, the script will then have you review all the pictures it tracked in order to train with. If you lost track or started tracking something strange in the previous stage, you can now go through and delete the objects you don't want to train with. You can go forward or backwards with the "a" and "d" keys. The "x" key will discard the image. You can either review all the pictures or press "q" and it will start the training process. 

The "Vid2Pic Training" button will convert all the videos in your list to pictures. You will then have to go through each picture and either use that image as a negative, select an object to train as a positive, or skip the frame entirely. Very tedious, but you have a lot more control

__Step 4__ - 

When the program starts the training, the gui will freeze. This is because I need to implement multi-threading on the program in order for it to run smoothly. Training time depends on many factors, but mostly on how many samples you have. 

After training is complete, the cascade filter will appear in the folder where gui.py is located. You can then use that to track on object with your new cascade classifier!

```bash
├── Train
│   ├── autoTrainCascade
│   │   ├── gui.py
│   │   ├── selector.py
│   │   ├── **cascade.xml**
│   ├── opencv
│   │   ├── opencv_annotation.exe
│   │   ├── opencv_createsamples.exe
│   │   ├── opencv__ffmgeg348_64.dll
│   │   ├── opencv_interactive-calibration.exe
│   │   ├── opencv_traincascade.exe
│   │   ├── opencv_version.exe
│   │   ├── opencv_version_win32.exe
│   │   ├── opencv_visualisation.exe
│   │   ├── opencv_world348.dll
│   │   ├── opencv_world348.pdb
│   │   ├── opencv_world348d.dll
│   │   ├── opencv_world348d.dll
│   ├── vids
│   │   ├── vid1.mp4
│   │   ├── vid2.mp4
```

