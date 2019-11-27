# objectDetect
<<<<<<< HEAD
### Motivation and Background 
The purpose of this python project is to take most of the work out of training so you can use the standard opencv object tracking
examples to track your own custom object. The problem with the whole training process is that it is tedious and the end result may
not work. I created this (for Windows users) in order to try and automate some of the process.... this is still far from perfect, but
it can be easily modified/built upon to train faster. Changing the training parameters will help deliver better results for what you 
are trying to achieve, changing things like using more positive and negative images will produce better results. Most of the 
documentation is located in the following link: 
https://docs.opencv.org/3.4/dc/d88/tutorial_traincascade.html

### Instructions
=======
## Background
How to train and create your own Cascade Classifier: This script is used to make your own cascade classifier. I built this for Windows, and will not work on other OSs. You can use the script on a video to select, track, and train an object. The script will output a xml file that can be used to track an object using the standard opencv example. It doesn't work well for objects that change a lot (i.e. different shapes, aspect viewing angles, etc). But for something that doesn't change much, like logos, it can do well on. 

https://docs.opencv.org/3.4/dc/d88/tutorial_traincascade.html

## Instructions
>>>>>>> Added readme instructions --still needs more work
__Step 1__ -
Download and install/extract files from https://github.com/opencv/opencv/releases/tag/3.4.8 . If you are on windows then get the 
vc-14/15 files. It downloads an exe file. Run the exe file which basically is a 7zip extracter that unzips all the files you need.
Pretty sketchy, but yolo. The files you need to run the programs are located in the extracted_files_loc/build/x64/vc15/bin/. You really only need those files, so you can copy the entire contents of the folder to wherever directory you want or reference that
folder's location. 

__Step 2__ - 
You can input the location of where the video is located on your computer into the script. I will eventually make an argument parser so you can command line run the script. You can input multiple videos into the list, and it will script will grab each one. There are two functions that can be used in the script:

The "objTrack" function will allow you to play the videos (w/ pause, foward, reverse skipping), and select an object that you want to train. The script will track the object you select and will train on that object. You can select an objects multiple times throughout the video (or subsequent videos).

The "selectPosNeg" function will convert all the videos in your list to pictures. You will then have to go through each picture and either use that image as a negative, select an object to train as a positive, or skip the frame entirely. 

Currently the script can only do one object at a time. If the object you want to train appears multiple times in the same frame, it will not work properly. This can be adjusted later, but will not work in the "objTrack" function.

