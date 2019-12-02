# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 10:06:53 2019

@author: Joel Miller

learning from this website:
https://realpython.com/python-gui-with-wxpython/

"""
import wx,glob


class videoListPanel(wx.Panel):    
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 100), 
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.InsertColumn(0, 'Video(s) Name', width=200)
        self.list_ctrl.InsertColumn(1, 'Path', width=140)
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)        
        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)        
        self.SetSizer(main_sizer)

    def on_edit(self, event):
        print('in on_edit')

    def updateVideoList(self, folder_path):
        print(folder_path)
        
        

class MyFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='Hello World')
        # Windows needs this for Tab traversal
        panel = wx.Panel(self)        
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add Text Input to panel -- first arg is where text goes on
        self.text_ctrl = wx.TextCtrl(panel)
        # Have text box dynamically sized
        my_sizer.Add(self.text_ctrl, 0, wx.ALL | wx.EXPAND, 10)
        
        # Add Button to do something -- first arg is where btn goes
        my_btn = wx.Button(panel, label='Press Me')
        my_btn.Bind(wx.EVT_BUTTON, self.btnpress)
        # Button is located beneath text box, centered
        my_sizer.Add(my_btn, 0, wx.ALL | wx.CENTER, 10)
        
        panel.SetSizer(my_sizer)        
        self.Show()
        
    def btnpress(self, event):
        value = self.text_ctrl.GetValue()
        value = int(value)
        a = [print(i) for i in list(range(0,value))]
    
    
class mainFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None,
                         title='Cascade Trainer')
        self.panel = videoListPanel(self)
        self.Show()
        
        def create_menu(self):
            menu_bar = wx.MenuBar()
            file_menu = wx.Menu()
            open_folder_menu_item = file_menu.Append(
                wx.ID_ANY, 'Open Folder', 
                'Open a folder with MP3s'
            )
            menu_bar.Append(file_menu, '&File')
            self.Bind(
                event=wx.EVT_MENU, 
                handler=self.on_open_folder,
                source=open_folder_menu_item,
            )
            self.SetMenuBar(menu_bar)
    
        def on_open_folder(self, event):
            title = "Choose a directory:"
            dlg = wx.DirDialog(self, title, 
                               style=wx.DD_DEFAULT_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                self.panel.update_mp3_listing(dlg.GetPath())
            dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = mainFrame()
    app.MainLoop()