# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:06:53 2019

@author: Joel Miller

learning from this website:
https://realpython.com/python-gui-with-wxpython/

"""
import os,wx
from automate import objTrack
 
wildcard = "mp4 source (*.mp4)|*.mp4|" \
            "All files (*.*)|*.*"


class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Cascade Trainer")
        panel = wx.Panel(self, wx.ID_ANY)
        self.currentDirectory = os.getcwd()

        # Title Text
        titleText = wx.StaticText(panel,label='Location of video files to train')
        
        # create text box
        self.textBox = wx.TextCtrl(panel,size = (200,100), style=wx.TE_MULTILINE)
        
        # create the buttons and bindings
        openFileDlgBtn = wx.Button(panel, label="Select Files")
        openFileDlgBtn.Bind(wx.EVT_BUTTON, self.onOpenFile)
        
        startTrain = wx.Button(panel, label="Start Training")
        startTrain.Bind(wx.EVT_BUTTON, self.startTraining)
        
        # Status Box
        self.statusBox = wx.TextCtrl(panel,size = (200,100), style=wx.TE_MULTILINE)

        # put the buttons in a sizer
        vSize = wx.BoxSizer(wx.VERTICAL)
        hSize = wx.BoxSizer(wx.HORIZONTAL)
        vSize.Add(titleText,0, wx.ALL|wx.CENTER)
        vSize.Add(self.textBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        
        hSize.Add(openFileDlgBtn, 0, wx.ALL|wx.CENTER, 5)
        hSize.Add(startTrain, 0, wx.ALL|wx.CENTER, 5)
        vSize.Add(hSize)
        
        vSize.Add(self.statusBox,0, wx.ALL|wx.CENTER|wx.EXPAND, 5)
        panel.SetSizer(vSize)


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
    
    def startTraining(self, event):
        print(self.filePaths)
        objTrack(self.filePaths)

#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()
