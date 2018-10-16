import tkinter
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import Tunneler

HEIGHT = 300
WIDTH = 750
menu = ['local        |   self->self->redirector->dest',
        'remote    |   {any}->origin->self->dest',
        'dynamic |   self->self->redirecter->{any}']
needed = [['redir','dest'],
          ['orig','dest'],
          ['redir']]
'''
Things to keep track of:
    input boxes / textboxes - dictionary?
    userlist for easy repeat input - set
    

--------------------------------------------------------------------------
| label: self.userbox                         |                          |
| label: self.entry[1] label: self.ports[0]   |                          |
| label: self.entry[2] label: self.ports[0]   |                          |
| label: self.entry[3] label: self.ports[0]   |                          |
|                                             |                          |
|                                             |                          |
|                                             |                          |
|                                             |                          |
|                                             |                          |
|                                             |                          |
|                                             |                          |
|                                             |                          |
|_____________________________________________|__________________________|
'''

class TunnGui(object):
    def __init__(self):
        self.host={}
        self.userlist = set()
        
        self.top = tkinter.Tk()
        self.top.bind_class("Text","<Tab>", self.focus_next_window)
        self.top.bind_class("Text","<Shift-Tab>",self.focus_prev_window)
        self.top.bind_class("Text","<Return>",self.enter_createTunnel)    
        
        self.top.bind_class("Combobox","<Tab>", self.focus_next_window)
        self.top.bind_class("Combobox","<Shift-Tab>",self.focus_prev_window)
        self.top.bind_class("Combobox","<Return>",self.enter_createTunnel)        

        
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
        '''Currently handles enabling/disabling ip text boxes. Still needs improvement - mostly in how we track which inputs we need'''
        ind = needed[self.dropdown.current()]
        for i in self.host.values():
            for j in i.values():
                j.config(state=tkinter.DISABLED,background='lightgrey')
        
        for i in ind:
            for j in self.host[i].values():
                j.config(state=tkinter.NORMAL,background='white')

    
    def createLeftSide(self):
        '''Currently the gui is split into two major halves, this handles the left'''
        
        left_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL)
        left_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        
        label =tkinter.Label(text="User:",justify=tkinter.RIGHT,anchor=tkinter.E)
        self.userbox = ttk.Combobox(textvariable=self.user,justify='left',width=30)
        
        left_horiz_frame.paneconfig(label,minsize=55)
        left_horiz_frame.paneconfig(self.userbox,minsize=200)        
        left_horiz_frame.add(label,pady=5,stretch="never")
        left_horiz_frame.add(self.userbox,pady=5,stretch="last")
        left_horiz_frame.add(tkinter.Frame())
        left_frame.add(left_horiz_frame)
        
        self.host['orig'] = self.createIPLine(left_frame,"Origin ip:",port=True)
        self.host['dest'] = self.createIPLine(left_frame,"Dest ip:",port=True) 
        self.host['redir'] = self.createIPLine(left_frame,"Redir ip:",port=True)
        
        horiz_frame = tkinter.Frame() # necessary to format the button correctly for some reason
        creator = tkinter.Button(horiz_frame,command=self.createTunnel,text="Create!",width=10,height=2)
        creator.grid(row=0,column=0,pady=(10,0))
        left_frame.add(horiz_frame)
        self.rootFrame.paneconfig(left_frame,minsize=350)
        self.rootFrame.add(left_frame,padx=5,width=2*WIDTH/3,stretch="always")
        
    def createIPLine(self,frame,msg,port=False,disabled=True):
        '''Creates a text box with a label in a specified frame'''
        left_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        
        label = tkinter.Label(text=msg,justify=tkinter.RIGHT,anchor=tkinter.E)
        ip = tkinter.Text(wrap=tkinter.WORD,height=1,width=25,state=(tkinter.DISABLED if disabled else tkinter.NORMAL),background=('lightgrey' if disabled else 'white'))

        left_horiz_frame.paneconfig(label,minsize=55)
        left_horiz_frame.paneconfig(ip,minsize=200)        
        left_horiz_frame.add(label,pady=5,stretch="never")
        left_horiz_frame.add(ip,pady=5,stretch="always")
                
        label = tkinter.Label(text="Port:",justify=tkinter.RIGHT,anchor=tkinter.E)
        port = tkinter.Text(wrap=tkinter.WORD,height=1,width=6,state=(tkinter.DISABLED if disabled else tkinter.NORMAL),background=('lightgrey' if disabled else 'white'))
      

        left_horiz_frame.paneconfig(label,minsize=27)
        left_horiz_frame.paneconfig(port,minsize=27)            
        left_horiz_frame.add(label,pady=5,stretch="never")
        left_horiz_frame.add(port,pady=5,stretch="never")

        
        frame.add(left_horiz_frame,stretch='last')     
        return {'ip':ip,'port':port}
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
                tunnel = Tunneler.Tunnel(user=self.user.get().strip(),ssh_port=self.getter(self.host['redir']['port']),origin_port=self.getter(self.host['orig']['port']),destination_port=self.getter(self.host['dest']['port']),**tuntype)
                tunnel.origin=self.getter(self.host['orig']['ip'])
                tunnel.destination=self.getter(self.host['dest']['ip'])
                tunnel.redirector=self.getter(self.host['redir']['ip'])
                cmd = tunnel.establish() # Eventually we want to return the pid of the process and track tunnel start/end instead of command
                self.userlist.add(self.user.get().strip())
                self.userbox.config(values=list(self.userlist)) # If successful update user list 
                self.setText(self.text,cmd)
        except Exception as e:
            self.setText(self.text,str(e))
             
if __name__=='__main__':  
    x = TunnGui()