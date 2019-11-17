# objectDetect
### Motivation and Background 
The purpose of this python project is to take most of the work out of training so you can use the standard opencv object tracking
examples to track your own custom object. The problem with the whole training process is that it is tedious and the end result may
not work. I created this (for Windows users) in order to try and automate some of the process.... this is still far from perfect, but
it can be easily modified/built upon to train faster. Changing the training parameters will help deliver better results for what you 
are trying to achieve, changing things like using more positive and negative images will produce better results. Most of the 
documentation is located in the following link: 
https://docs.opencv.org/3.4/dc/d88/tutorial_traincascade.html

### Instructions
__Step 1__ -
Download and install/extract files from https://github.com/opencv/opencv/releases/tag/3.4.8 . If you are on windows then get the 
vc-14/15 files. It downloads an exe file. Run the exe file which basically is a 7zip extracter that unzips all the files you need.
Pretty sketchy, but yolo. The files you need to run the programs are located in the extracted_files_loc/build/x64/vc15/bin/. You really only need those files, so you can copy the entire contents of the folder to wherever directory you want or reference that
folder's location. 

__Step 2__ - 
Put your video into a folder named vids and then run the automate.py program. ///finish later///

