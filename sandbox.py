from Tkinter import *


class Window(Frame):
    """Creates and manipulates the GUI"""

    def __init__(self, master=None):
        
        ## This just builds the window 
        self.root = Tk()
        Frame.__init__(self, master)
        self.initWindow()


    def initWindow(self):
        self.master.title("sandbox")
        self.root.geometry("400x200")

        # self.root.columnconfigure(0, weight=1)
        # self.root.rowconfigure(0, weight=1)
        # self.grid(column=0,row=0)
        self.master.grid()
        self.master.columnconfigure(0,weight=1)
        self.master.rowconfigure(0,weight=1)


        helptext_frame = LabelFrame(  self.master, 
                                      text="Description of Selected Script"  )
        helptext_frame.grid(row=0, column=0, sticky='nsew')
        helptext_frame.columnconfigure(0,weight=1)
        helptext_frame.rowconfigure(0,weight=1)
     

        msg_text = """
This shows how to make a simple script. The script:
  - looks at people in ECE Dept.
  - returns # of duespayers and membership %
"""
        msg = Label(helptext_frame, text=msg_text, justify='left', bg='cyan')
        msg.grid(sticky="nw")





## Create the window
app = Window()

app.mainloop()

