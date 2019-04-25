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

        frame1 = Frame(self.master,bg="blue")
        # frame1.pack(fill=X)
        frame1.columnconfigure(0,weight=0)
        frame1.columnconfigure(1,weight=1)
        frame1.grid(column=0,row=0,sticky='nsew')


        lbl1 = Label(frame1, text="First")
        lbl1.grid(row=0,column=0,sticky='w')

        e1 = Entry(frame1)
        e1.grid(row=0,column=1,sticky='we')
        # filebutton = Button(   self, text="Select Input File",
        #                             command=None    )
        # filebutton.grid(row=0,column=1,sticky="we")


        lbl2 = Label(frame1, text="Second")
        lbl2.grid(row=1,column=0,sticky='w')

        e2 = Entry(frame1)
        e2.grid(row=1,column=1,sticky='we')





## Create the window
app = Window()

app.mainloop()

