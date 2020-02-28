import wx,time
from threading import Thread

class finished():
    def __init__(self,val1,val2):
        self.val1 = val1
        self.val2 = val2
        
    def printFunction(self):
        print("thread finished, val1 is: " + str(self.val1))


class TestThread(Thread):
    def __init__(self):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.start()    # start the thread

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        for i in range(2):
            time.sleep(2)
            wx.CallAfter(self.postTime, i)
        #time.sleep(2)
        f = finished("john", 32)
        wx.CallAfter(f.printFunction,)
    
    def postTime(self,i):
        # send time to gui
        print("postTime was executed, val:" + str(i))


class TrainingTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        panel = wx.Panel(self)
        
        t = wx.StaticText(self, -1, "This is the first tab", (200,20))
        
        self.btn = btn = wx.Button(panel, label="Start Thread")
        btn.Bind(wx.EVT_BUTTON, self.onButton)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizer(sizer)
    
    def onButton(self, event):
        # Run thread
        TestThread()
        print("Thread started!")
        btn = event.GetEventObject()
        btn.Disable()


class PlaybackTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the second tab", (20,20))

class TrackingTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the third tab", (20,20))


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Cascade Traininer")

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