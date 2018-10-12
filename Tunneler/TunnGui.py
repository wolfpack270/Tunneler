import tkinter
from tkinter import ttk
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
        
        self.createLeftSide()
        self.createRightSide()
        
        self.rootFrame.grid(row=0,column=0)
        

        # Because we have a grid layout, in order for user resizing to work we have to configure row/column weights
        self.top.grid_rowconfigure(0,weight=1)
        self.top.grid_rowconfigure(1,weight=1)
        self.top.grid_rowconfigure(2,weight=1)
        self.top.grid_rowconfigure(3,weight=1)
        self.top.grid_rowconfigure(4,weight=1)
        self.top.grid_rowconfigure(5,weight=1)

        self.top.grid_columnconfigure(0,weight=1)
        self.top.grid_columnconfigure(1,weight=1)
        self.top.grid_columnconfigure(2,weight=1)
        self.top.grid_columnconfigure(3,weight=1)
        self.top.grid_columnconfigure(4,weight=1)
        self.top.mainloop()
    
    def createLeftSide(self):
        left_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        # Currently text input in the first column can be set up with createInput. This may change.
        
        self.createInput(left_frame,"User:       ")
        self.createInput(left_frame,"Src ip:     ")
        self.createInput(left_frame,"Dest ip:  ") 
        self.createInput(left_frame,"Redir ip: ")
        
        horiz_frame = tkinter.Frame()
        creator = tkinter.Button(horiz_frame,command=self.createTunnel,text="Create!",width=10,height=2)
        creator.grid(row=0,column=0,pady=(10,0))
        left_frame.add(horiz_frame)
        self.rootFrame.add(left_frame,width=300)
        #left_frame.grid(row=0,column=0,padx=10,sticky=tkinter.NSEW)
        
    def createRightSide(self):
        # Paned Window is a resizeable frame that can be "packed" by adding frames/child widgets. They get added in the orient direction.
        right_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        right_horiz_frame = tkinter.Frame()
        right_horiz_frame_2 = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
    
    
        label = tkinter.Label(right_horiz_frame,text="Tunnel Type:",justify=tkinter.RIGHT)
        label.grid(row=0,column=0)
        #right_horiz_frame.add(label)
    
        self.choice = tkinter.StringVar()
        self.dropdown = ttk.Combobox(right_horiz_frame,values=menu,textvariable=self.choice,state='readonly',justify=tkinter.LEFT,width=30)
        self.dropdown.grid(row=0,column=1)
   
        right_frame.add(right_horiz_frame,padx=10,pady=10,stretch="always")
    
    
        # Currently self.text can be used for feedback to the user. Eventually this should be split to show feedback as well as contain
        # a list of tunnels
    
        self.text = tkinter.Text(right_frame,wrap=tkinter.WORD,width=60,height=10,state='disabled')
        right_frame.add(self.text,padx=10,pady=10,stretch="always")
    
        self.text_button = tkinter.Button(text="Clear",command=lambda: self.clear(self.text))
        right_horiz_frame_2.add(self.text_button,height=30,width=50,padx=20)
        right_horiz_frame_2.add(tkinter.Frame(width=5))
        right_frame.add(right_horiz_frame_2)
        self.rootFrame.add(right_frame,width=400)
        #right_frame.grid(row=0,column=1,padx=10,sticky=tkinter.NSEW)
    
    
        
    # Since we don't want user to be able to control the feedback textbox, we have to enable/disable
    # every time we change it.
    def setText(self,entry,text):
        entry.config(state='normal')
        entry.insert(tkinter.END,text+'\n')
        entry.config(state='disabled')
        
    def getter(self,entry):
        '''Method for returning the contents of a Text widget'''
        val = entry.get("1.0",tkinter.END)
        return val
    
    def clear(self,entry):
        '''Method for deleting contents of a Text Widget'''
        entry.config(state='normal')
        entry.delete("1.0",tkinter.END)
        entry.config(state='disabled')
        return
    
    def createTunnel(self):
        '''Get user input from tkinter app and create a Tunneler class. Validation of Tunnel information should be handled in it's class'''
        try:
            ind = self.dropdown.current()
            if ind==-1:
                self.text.insert(tkinter.END,'Please select a tunnel type.\n')
            else:
                tuntype= {"local":(True if ind==0 else False),"remote":(True if ind==1 else False),"dynamic":(True if ind==2 else False)}
                tunnel = Tunneler.Tunnel(user=self.getter(self.entries[0]).strip(),ssh_port=22,origin_port=9000,destination_port=80,**tuntype)
                tunnel.origin=self.getter(self.entries[1]).strip()
                tunnel.destination=self.getter(self.entries[2]).strip()
                tunnel.redirector=self.getter(self.entries[3]).strip()
                cmd = tunnel.establish() # Eventually we want to return the pid of the process and track tunnel start/end instead of command
                self.setText(self.text,cmd)
        except Exception as e:
            print(e)
            self.setText(self.text,"Something went wrong")
        
    def createInput(self,frame,label):
        '''Creates a text box with a label'''
        
            
        left_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        label = tkinter.Label(text=label,justify=tkinter.LEFT)
        text = tkinter.Text(wrap=tkinter.WORD,height=2,width=20)
        self.entries.append(text)
        left_horiz_frame.add(label,pady=10)
        left_horiz_frame.add(text,pady=10)
        frame.add(left_horiz_frame)        
        
        return
             
if __name__=='__main__':  
    x = TunnGui()