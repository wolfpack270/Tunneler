import tkinter
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import Tunneler

menu = ['local        |   self->self->redirector->dest','remote    |   {any}->origin->self->dest','dynamic |   self->self->redirecter->{any}']
class TunnGui(object):
    def __init__(self):
        self.buttons = []
        self.entries = []
        
        self.top = tkinter.Tk()
        self.top.title("Tunneler")
        
        self.top.tk.call('wm', 'iconphoto', self.top._w, tkinter.PhotoImage(file='wormhole.png'))
        self.top.resizable(width=True,height=True)
        
        self.rootFrame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL,borderwidth=3)
        self.rootFrame.configure(background='darkgrey')
        
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
        ind = self.dropdown.current()
        if ind == -1:
            for i in self.entries[1:]:
                self.entries.config(state=tkinter.DISABLED,background='lightgrey')
        if ind==0:
            self.entries[1].config(state=tkinter.DISABLED,background='lightgrey')
            for i in self.entries[2:]:
                i.config(state=tkinter.NORMAL,background='white')
        elif ind==1:
            self.entries[3].config(state=tkinter.DISABLED,background='lightgrey')
            for i in self.entries[1:3]:
                i.config(state=tkinter.NORMAL,background='white')
        elif ind==2:
            self.entries[3].config(state=tkinter.NORMAL,background='white')
            for i in self.entries[1:3]:
                i.config(state=tkinter.DISABLED,background='lightgrey')
            pass
    
    def createLeftSide(self):
        left_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        
        self.createInput(left_frame,"User:         ",disabled=False)
        self.createInput(left_frame,"Origin ip: ")
        self.createInput(left_frame,"Dest ip:    ") 
        self.createInput(left_frame,"Redir ip:   ")
        
        horiz_frame = tkinter.Frame()
        creator = tkinter.Button(horiz_frame,command=self.createTunnel,text="Create!",width=10,height=2)
        creator.grid(row=0,column=0,pady=(10,0))
        left_frame.add(horiz_frame)
        self.rootFrame.add(left_frame,padx=5,width=300,stretch="always")
        
   
    def createRightSide(self):
        # Paned Window is a resizeable frame that can be "packed" by adding frames/child widgets. They get added in the orient direction.
        right_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        right_horiz_frame = tkinter.Frame()
        right_horiz_frame_2 = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
    
    
        label = tkinter.Label(right_horiz_frame,text="Tunnel Type:",justify=tkinter.RIGHT)
        label.grid(row=0,column=0)
    
        self.choice = tkinter.StringVar()
        self.dropdown = ttk.Combobox(right_horiz_frame,values=menu,textvariable=self.choice,state='readonly',justify=tkinter.LEFT,width=40)
        self.dropdown.bind("<<ComboboxSelected>>", self._config_text)
        self.dropdown.grid(row=0,column=1)
   
        right_frame.add(right_horiz_frame)
        self.text = ScrolledText(right_frame,wrap=tkinter.WORD,height=10,state='disabled')
        right_frame.add(self.text,stretch='always')
        
    
        self.text_button = tkinter.Button(right_horiz_frame_2,text="Clear",command=lambda: self.clear(self.text))
        self.text_button.grid(row=0,column=0,padx=(10,0))
        right_frame.add(right_horiz_frame_2)
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
        val = entry.get("1.0",tkinter.END)
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
                tunnel = Tunneler.Tunnel(user=self.getter(self.entries[0]).strip(),ssh_port=22,origin_port=9000,destination_port=80,**tuntype)
                tunnel.origin=self.getter(self.entries[1]).strip()
                tunnel.destination=self.getter(self.entries[2]).strip()
                tunnel.redirector=self.getter(self.entries[3]).strip()
                cmd = tunnel.establish() # Eventually we want to return the pid of the process and track tunnel start/end instead of command
                self.setText(self.text,cmd)
        except Exception as e:
            self.setText(self.text,str(e))
        
    def createInput(self,frame,label,disabled=True):
        '''Creates a text box with a label in a specified frame'''
        left_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        label = tkinter.Label(text=label,justify=tkinter.LEFT)
        text = tkinter.Text(wrap=tkinter.WORD,height=1,width=20,state=(tkinter.DISABLED if disabled else tkinter.NORMAL),background=('lightgrey' if disabled else 'white'))
        text.bind("<Tab>", self.focus_next_window)
        text.bind("<Shift-Tab>",self.focus_prev_window)
        text.bind("<Return>",self.enter_createTunnel)
        self.entries.append(text)
        left_horiz_frame.add(label,pady=10)
        left_horiz_frame.add(text,pady=10)
        frame.add(left_horiz_frame)        
        
        return
             
if __name__=='__main__':  
    x = TunnGui()