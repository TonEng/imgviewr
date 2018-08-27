#!/usr/bin/python
import sys, datetime, subprocess, glob, os, random
import Tkinter as tk
reload(sys)
sys.setdefaultencoding('utf8')
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
from functools import partial

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

## note: image_raw is changed inside the button handler and thus a global variable.
## note: list_of_filenames_pointer points to the current loaded/displayed image and is
##       changed in several helpers - therefore is this also a global variable.


class Application(tk.Frame) :
    
    def __init__(self, parent, image_raw):
##      establish the frame, buttons, canvas and put the first picture on the canvas      
        tk.Frame.__init__(self,parent)
        self.pack(fill=tk.BOTH, expand=1)
# get screen size of user and make the window fill approx. 3/4 of the screen.
        self.screen_w=root.winfo_screenwidth()
        self.screen_h=root.winfo_screenheight()
        self.screen_w = int(self.screen_w * 0.75)
        self.screen_h = int(self.screen_h * 0.75)
        self.canvas=tk.Canvas(self,bg='black', width=str(self.screen_w), height=str(self.screen_h))
#  configure the grid rows/columns
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.columnconfigure(4,weight=1)
        self.quit=tk.Button(self, text='Quit', command=self.quit)
        self.quit.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W)
        self.canvas.grid(row=1,column=0,columnspan=5,sticky=tk.N+tk.S+tk.E+tk.W)
#  the "Next","previous" and "random" buttons require more arguments - apply this trick to get that done.
        action_with_arg=partial(self.show_pic,self.canvas,"n")
        self.anders=tk.Button(self, text='Next', command=action_with_arg, activebackground='yellow')
        self.anders.grid(row=0, column=1, sticky=tk.N+tk.W+tk.E)
        action_with_arg=partial(self.show_pic,self.canvas,"p")
        self.anders=tk.Button(self, text='Previous', command=action_with_arg, activebackground='yellow')
        self.anders.grid(row=0, column=2, sticky=tk.N+tk.W+tk.E)
        action_with_arg=partial(self.show_pic,self.canvas,"r")
        self.anders=tk.Button(self, text='Random', command=action_with_arg, activebackground='yellow')
        self.anders.grid(row=0, column=3, sticky=tk.N+tk.W+tk.E)
        self.slideshow_state=tk.IntVar()
        action_with_arg=partial(self.but_slideshow,self.canvas)
        l_txt="Slideshow "+str(timedelay/float(1000))+"s."
        self.Chkbut=tk.Checkbutton(self,text=l_txt,variable=self.slideshow_state,command=action_with_arg,activebackground='red')
        self.Chkbut.grid(row=0, column=4, sticky=tk.N+tk.W+tk.E)
        
##        def handler(event,self=self,img=image_raw):  
##            return self.configure(event,img)
#  this is to bind a handler when the main window is changed ("configured")
        self.canvas.bind("<Configure>", self.configure)
        self.canvas.bind("<Button-1>", self.canvas_onclick)
       
#  use update_idletasks() in ubuntu, update() in MacOS, needed to ensure the winfo_ calls do not return zero
#       root.update_idletasks()
        root.update()
        self.w_window=self.canvas.winfo_width()
        self.h_window=self.canvas.winfo_height()
        img_s=self.adjust_image(self.canvas,image_raw)
        img=ImageTk.PhotoImage(img_s)
        self.keeper = img
        ids=self.canvas.create_image(self.w_window/2,self.h_window/2,image=img)

## called when 'Next', 'Previous' or 'Random' button is pressed, display next image: f=canvas, type = n,p,r
## note that we close the 'old' image here to not keep memory use growing
## note that image_raw is changed here, so it is a global variable.
## s_show contains the return handle from re-scheduling the show_pic method to achieve a slideshow. It is global as to be
##   able to cancel a re-schedule if the type has changed.
## old_selection is to remember the last type selection and compare it with the current, if they are not equal, there is likely a
##  re-schedule set-up of the previous type which needs to get canceled.  old_selection is global and is initilized to ""
##  it is set every time show_pic is scheduled. It is reset to "" when show_pic reschedule is canceled.
    def show_pic(self,f,type) :
        global s_show
        self.canvas.after_cancel(s_show)   ## cancel whenever there is possibly a second one scheduled.
        ww=f.winfo_width()
        hw=f.winfo_height()
        global image_raw
        global list_of_filenames_pointer
        
        global old_selection
        global timedelay
        image_raw.close()
        if type == "n" :
            list_of_filenames_pointer=list_of_filenames_pointer+1
            if list_of_filenames_pointer >= len(list_of_filenames) :
                list_of_filenames_pointer = 0
        if type == "p" :
            list_of_filenames_pointer=list_of_filenames_pointer-1
            if list_of_filenames_pointer < 0 :
                list_of_filenames_pointer=len(list_of_filenames)-1
        if type == "r" :
            list_of_filenames_pointer = random.randint(0,len(list_of_filenames)-1)
        
        image_raw=Image.open(list_of_filenames[list_of_filenames_pointer])
        self.set_title(list_of_filenames_pointer)
        img_s=self.adjust_image(f,image_raw)
        img=ImageTk.PhotoImage(img_s)
        self.keeper = img
        ids=f.create_image(ww/2,hw/2,image=img)
        
        if ( (self.slideshow_state.get() == 0)):
            if (s_show != 0) :
            ##  slideshow status off, but there is still some s_show scheduled -> cancel s_show
                self.canvas.after_cancel(s_show)
                s_show=0
                old_selection=""
            else:
                old_selection=""
        else:
            ##  slideshow status on.
            if (s_show == 0) :
               ##  slideshow on, but no scheduled -> schedule on
                s_show =self.canvas.after(timedelay,self.show_pic,f,type)
                old_selection = type
            else :  ##  s_show is on, check if type is still the same...
                if (old_selection != type) :
                    ##  if old type is not the same, cancel old slideshow, always start new one:
                    self.canvas.after_cancel(s_show)
            old_selection = type
            s_show=self.canvas.after(timedelay,self.show_pic,f,type)
                

##  called when slideshow button changed
    def but_slideshow(self,f) :
        if ( self.slideshow_state.get() == 0 and s_show !=0) :
            self.canvas.after_cancel(s_show)
            old_selection=""


##  called when clicked on th screen... upper half: increase speed, lower half: decrease speed
    def canvas_onclick(self, event):
        global timedelay
        if (event.y > (self.canvas.winfo_height()/2)) :
            timedelay = timedelay+500
        else :
            if (timedelay > 1000) : timedelay = timedelay - 500
        self.Chkbut["text"] = "Slideshow "+str(timedelay/float(1000))+"s."
            

## called when the window with the canvas is being resized...
    def configure(self,event) :
        img_s=self.adjust_image(self.canvas,image_raw)
        img=ImageTk.PhotoImage(img_s)
        self.keeper = img
        ids=self.canvas.create_image(event.width/2,event.height/2,image=img)


## helper to size the image to the canvas: window=canvas, image_in= image
    def adjust_image(self,window,image_in) :
        ww=window.winfo_width()
        hw=window.winfo_height()
        w_image,h_image=image_in.size
        factor_w=float(ww)/float(w_image)
        factor_h=float(hw)/float(h_image)
        factor=min(float(factor_w),float(factor_h))
        w=int(w_image*float(factor))
        h=int(h_image*float(factor))
        img_out = image_in.resize((w,h),Image.BICUBIC)
        return img_out

## helper to set the title:
    def set_title(self,image_ptr) :
        l_title= "Image Viewer: " + str(list_of_filenames[image_ptr])
        l_title= l_title + " Image " + str(image_ptr+1)
        l_title= l_title + " of " + str(len(list_of_filenames))
        root.title(l_title)


##  main:  ******************************************************************************
supported_names = set(['.JPG','.JPEG','.PNG','.GIF'])
list_of_filenames=[]
random.seed()
for file_name in sorted(glob.iglob(os.getcwd()+"/*"), key=os.path.getmtime) :
    if os.path.isfile(file_name) :
        file_extension=os.path.splitext(file_name)
        if file_extension[-1].upper() in supported_names :
            list_of_filenames.append(file_name)

if len(list_of_filenames) <= 0 :
    print "No files found, program exits"
else :
    list_of_filenames_pointer=0
    s_show=0
    old_selection=""
    timedelay = 2000
    ## list_of_filenames_pointer points to the CURRENT / displayed image.
    image_raw=Image.open(list_of_filenames[list_of_filenames_pointer])
    root=tk.Tk()
    y=Application(root,image_raw)
    y.set_title(list_of_filenames_pointer)
    root.mainloop()
