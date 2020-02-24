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
Download and install/extract files from https://github.com/opencv/opencv/releases/tag/3.4.8 . If you are on windows then get the 
vc-14/15 files. It downloads an exe file. Run the exe file which basically is a 7zip extracter that unzips all the files you need.
Pretty sketchy, but yolo. The files you need to run the programs are located in the extracted_files_loc/build/x64/vc15/bin/. You really only need the files in that bin folder, so you can copy the entire contents of the folder to wherever directory you want or reference that folder's location. 

The code also requires additional libraries that must be installed via pip or conda. Most of them are standard for python but here is the list of all required libraries:

`import cv2,os,subprocess,shlex,shutil,glob,re,wx`


__Step 2__ - 
Run the gui.py program. On the gui, you can click on the "Select Files" button which will open up a file browser that you can use to point to one or more video files. After the videos are selected click "open". The video file locations should appear in the top text box. 

__Step 3__ - 

The "Video Track Training" button will allow you to play the videos (w/ pause, foward, reverse skipping), and select an object that you want to train. The script will track the object you select and will train on that object. You can select an object multiple times throughout the video (or subsequent videos), but you can only do one object at a time. For example, you can not select two objects on the same frame.

The "Vid2Pic Training" button will convert all the videos in your list to pictures. You will then have to go through each picture and either use that image as a negative, select an object to train as a positive, or skip the frame entirely.

__Step 4__ - 

When the program starts the training, the gui will freeze. This is because I need to implement multi-threading on the program in order for it to run smoothly. Training time depends on many factors, but mostly on how many samples you have. 

After training is complete, the cascade filter will appear in a new folder where the video is located. You can then use that to track on object with your new cascade classifier!

