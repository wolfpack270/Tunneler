import tkinter
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import Tunneler

HEIGHT = 300
WIDTH = 750
menu = ['local        |   self->self->redirector->dest','remote    |   {any}->origin->self->dest','dynamic |   self->self->redirecter->{any}']
class TunnGui(object):
    def __init__(self):
        self.ports = []
        self.entries = []
        self.userlist = set()
        
        self.top = tkinter.Tk()
        self.top.minsize(width=WIDTH,height=HEIGHT)
        self.top.title("Tunneler")
        
        self.top.tk.call('wm', 'iconphoto', self.top._w, tkinter.PhotoImage(file='wormhole.png'))
        self.top.resizable(width=True,height=True)
        
        # Paned Window is a resizeable frame that can be "packed" by adding frames/child widgets. They get added in the orient direction.
        self.rootFrame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL,borderwidth=3)
        
        self.user = tkinter.StringVar()
        self.createLeftSide()
        self.createRightSide()
        self.rootFrame.grid(row=0,column=0,sticky=tkinter.NSEW)
        
        # Because we have a grid layout, in order for user resizing to work we have to configure row/column weights
        rows,cols = self.top.grid_size()
        for i in range(rows):
            self.top.grid_rowconfigure(i,weight=1)
        for i in range(cols):
            self.top.grid_columnconfigure(i,weight=1)
        
        
        self.top.mainloop()
        
    def _config_text(self,event):
        '''Currently handles enabling/disabling ip text boxes. Once I change how entities are stored
        this can be improved and cleaned up'''
        ind = self.dropdown.current()
        if ind == -1:
            for i in self.entries[1:]:
                self.entries.config(state=tkinter.DISABLED,background='lightgrey')
        if ind==0: # Local
            self.entries[1].config(state=tkinter.DISABLED,background='lightgrey')
            self.ports[0].config(state=tkinter.DISABLED,background='lightgrey')
            for i in self.entries[2:]:
                i.config(state=tkinter.NORMAL,background='white')
            for i in self.ports[1:]:
                i.config(state=tkinter.NORMAL,background='white')            
        elif ind==1: # Remote
            self.entries[3].config(state=tkinter.DISABLED,background='lightgrey')
            self.ports[2].config(state=tkinter.DISABLED,background='lightgrey')
            for i in self.entries[1:3]:
                i.config(state=tkinter.NORMAL,background='white')
            for i in self.ports[0:2]:
                i.config(state=tkinter.NORMAL,background='white')            
        elif ind==2: # Dynamic
            self.entries[3].config(state=tkinter.NORMAL,background='white')
            self.ports[2].config(state=tkinter.NORMAL,background='white')
            for i in self.entries[1:3]:
                i.config(state=tkinter.DISABLED,background='lightgrey')
            for i in self.ports[0:2]:
                i.config(state=tkinter.DISABLED,background='lightgrey')            
            pass
    
    def createLeftSide(self):
        '''Currently the gui is split into two major halves, this handles the left'''
        
        left_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL)
        left_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        
        label =tkinter.Label(text="User:",justify=tkinter.RIGHT,anchor=tkinter.E)
        self.userbox = ttk.Combobox(textvariable=self.user,justify='left',width=30)
        self.userbox.bind("<Tab>", self.focus_next_window)
        self.userbox.bind("<Shift-Tab>",self.focus_prev_window)
        self.userbox.bind("<Return>",self.enter_createTunnel)
        left_horiz_frame.paneconfig(label,minsize=55)
        left_horiz_frame.paneconfig(self.userbox,minsize=200)        
        left_horiz_frame.add(label,pady=5,stretch="never")
        left_horiz_frame.add(self.userbox,pady=5,stretch="last")
        left_horiz_frame.add(tkinter.Frame())
        left_frame.add(left_horiz_frame)
        self.entries.append(self.userbox)
        
        self.createInput(left_frame,"Origin ip:",port=True)
        self.createInput(left_frame,"Dest ip:",port=True) 
        self.createInput(left_frame,"Redir ip:",port=True)
        
        horiz_frame = tkinter.Frame() # necessary to format the button correctly for some reason
        creator = tkinter.Button(horiz_frame,command=self.createTunnel,text="Create!",width=10,height=2)
        creator.grid(row=0,column=0,pady=(10,0))
        left_frame.add(horiz_frame)
        self.rootFrame.paneconfig(left_frame,minsize=350)
        self.rootFrame.add(left_frame,padx=5,width=2*WIDTH/3,stretch="always")
        
    def createInput(self,frame,msg,port=False,disabled=True):
        '''Creates a text box with a label in a specified frame'''
        left_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        
        label = tkinter.Label(text=msg,justify=tkinter.RIGHT,anchor=tkinter.E)
        text = tkinter.Text(wrap=tkinter.WORD,height=1,width=25,state=(tkinter.DISABLED if disabled else tkinter.NORMAL),background=('lightgrey' if disabled else 'white'))
        text.bind("<Tab>", self.focus_next_window)
        text.bind("<Shift-Tab>",self.focus_prev_window)
        text.bind("<Return>",self.enter_createTunnel)
        self.entries.append(text)
        left_horiz_frame.paneconfig(label,minsize=55)
        left_horiz_frame.paneconfig(text,minsize=200)        
        left_horiz_frame.add(label,pady=5,stretch="never")
        left_horiz_frame.add(text,pady=5,stretch="always")
                
        if port:
            label = tkinter.Label(text="Port:",justify=tkinter.RIGHT,anchor=tkinter.E)
            text2 = tkinter.Text(wrap=tkinter.WORD,height=1,width=6,state=(tkinter.DISABLED if disabled else tkinter.NORMAL),background=('lightgrey' if disabled else 'white'))
            text2.bind("<Tab>", self.focus_next_window)
            text2.bind("<Shift-Tab>",self.focus_prev_window)
            text2.bind("<Return>",self.enter_createTunnel)            
            self.ports.append(text2)
            left_horiz_frame.paneconfig(label,minsize=27)
            left_horiz_frame.paneconfig(text2,minsize=27)            
            left_horiz_frame.add(label,pady=5,stretch="never")
            left_horiz_frame.add(text2,pady=5,stretch="never")

        
        frame.add(left_horiz_frame,stretch='last')     
   
    def createRightSide(self):
        '''Creating the right half'''
        
        
        right_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        right_horiz_frame = tkinter.Frame()
        right_horiz_frame_2 = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
    
        ### Label and dropdown ####
        label = tkinter.Label(right_horiz_frame,text="Tunnel Type:",justify=tkinter.RIGHT)
        label.grid(row=0,column=0)
    
        self.choice = tkinter.StringVar()
        self.dropdown = ttk.Combobox(right_horiz_frame,values=menu,textvariable=self.choice,state='readonly',justify=tkinter.LEFT,width=35)
        self.dropdown.bind("<<ComboboxSelected>>", self._config_text)
        self.dropdown.grid(row=0,column=1)
        right_frame.add(right_horiz_frame,stretch="first")
        
        ### Next row is just a single element so no frame *really* needed currently ###
        self.text = ScrolledText(right_frame,wrap=tkinter.WORD,height=10,state='disabled')
        right_frame.add(self.text,stretch='always')
        
        ### Clear button in its own frame to allow resizing ###
        self.text_button = tkinter.Button(right_horiz_frame_2,text="Clear",command=lambda: self.clear(self.text))
        self.text_button.grid(row=0,column=0,padx=(10,0))
        right_frame.add(right_horiz_frame_2)
        self.rootFrame.paneconfig(right_frame,minsize=3*WIDTH/5)
        self.rootFrame.add(right_frame,padx=10,pady=10, width=400,stretch="always")
    
        
    # Since we don't want user to be able to control the feedback textbox, we have to enable/disable
    # every time we change it.
    def setText(self,entry,text):
        '''Method for setting the contents of a Text Widget'''
        entry.config(state='normal')
        entry.insert(tkinter.END,text+'\n')
        entry.config(state='disabled')
    def clear(self,entry):
        '''Method for deleting contents of a Text Widget'''
        entry.config(state='normal')
        entry.delete("1.0",tkinter.END)
        entry.config(state='disabled')
        return
    def getter(self,entry):
        '''Method for returning the contents of a Text widget'''
        val = entry.get("1.0",tkinter.END).strip()
        return val
    def focus_next_window(self,event):
        '''Method to make tab change textboxes'''
        event.widget.tk_focusNext().focus()
        return("break")
    def focus_prev_window(self,event):
        '''Method to make tab change textboxes'''
        event.widget.tk_focusPrev().focus()
        return("break")        
    def enter_createTunnel(self,event):
        '''Method to make Return attempt to create a tunnel'''
        self.createTunnel()
        return("break")
    
    
    def createTunnel(self):
        '''Get user input from tkinter app and create a Tunneler class. Validation of Tunnel information should be handled in it's class'''
        try:
            ind = self.dropdown.current()
            if ind==-1:
                self.setText(self.text,'Please select a tunnel type.')
            else:
                tuntype= {"local":(True if ind==0 else False),"remote":(True if ind==1 else False),"dynamic":(True if ind==2 else False)}
                # **tuntype makes the dictionary convert to keywords. i.e. {"local":True} converts to local=True
                tunnel = Tunneler.Tunnel(user=self.user.get().strip(),ssh_port=22,origin_port=self.getter(self.ports[0]),destination_port=self.getter(self.ports[1]),**tuntype)
                tunnel.origin=self.getter(self.entries[1])
                tunnel.destination=self.getter(self.entries[2])
                tunnel.redirector=self.getter(self.entries[3])
                cmd = tunnel.establish() # Eventually we want to return the pid of the process and track tunnel start/end instead of command
                self.userlist.add(self.user.get().strip())
                self.userbox.config(values=list(self.userlist))
                self.setText(self.text,cmd)
        except Exception as e:
            self.setText(self.text,str(e))
        
             
if __name__=='__main__':  
    x = TunnGui()