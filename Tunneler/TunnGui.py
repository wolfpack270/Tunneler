import tkinter
from tkinter import ttk
import Tunneler

menu = ['local | self->redirector->dest','remote | {any}->origin->self->dest','dynamic | self->redirecter->{any}']
class TunnGui(object):
    def __init__(self):
        self.buttons = []
        self.entries = []
        
        self.top = tkinter.Tk()
        self.top.title("Tunneler")
        self.top.tk.call('wm', 'iconphoto', self.top._w, tkinter.PhotoImage(file='wormhole.png'))
        self.top.resizable(width=True,height=True)
        
        # Currently text input in the first column can be set up with createInput. This may change.
        self.createInput(0,"Username:")
        self.createInput(1,"Src ip:")      
        self.createInput(2,"Dest ip:")
        self.createInput(3,"Redir ip:")
        
        # Paned Window is a resizeable frame that can be "packed" by adding frames/child widgets. They get added in the orient direction.
        self.right_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        self.right_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        
        label = tkinter.Label(text="Tunnel Type:",justify=tkinter.LEFT)
        self.right_horiz_frame.add(label,stretch="always")
        
        self.choice = tkinter.StringVar()
        self.dropdown = ttk.Combobox(values=menu,textvariable=self.choice,state='readonly')
        self.right_horiz_frame.add(self.dropdown)
        
        self.right_frame.add(self.right_horiz_frame,padx=20,pady=20,stretch="always")
        
        
        # Currently self.text can be used for feedback to the user. Eventually this should be split to show feedback as well as contain
        # a list of tunnels
        
        self.text = tkinter.Text(self.right_frame,wrap=tkinter.WORD,width=60,height=10)
        self.right_frame.add(self.text,padx=20,pady=20,stretch="always")
        self.right_frame.grid(row=0,rowspan=4,column=4,padx=10,sticky=tkinter.NSEW)
        
        creator = tkinter.Button(command=self.createTunnel,text="Create!")
        creator.grid(row=5,column=1)
        
        
        # Because we have a grid layout, in order for user resizing to work we have to configure row/column weights
        self.top.grid_rowconfigure(0,weight=1)
        self.top.grid_rowconfigure(1,weight=1)
        self.top.grid_rowconfigure(2,weight=1)
        self.top.grid_rowconfigure(3,weight=1)
        self.top.grid_rowconfigure(4,weight=1)
        self.top.grid_rowconfigure(5,weight=1)
        
        self.top.grid_columnconfigure(0,weight=1)
        self.top.grid_columnconfigure(1,weight=1)
        self.top.grid_columnconfigure(2,weight=2)
        self.top.grid_columnconfigure(3,weight=1)
        self.top.grid_columnconfigure(4,weight=1)
        self.top.mainloop()
    
    def getter(self,entry):
        '''Method for returning the contents of a Text widget'''
        val = entry.get("1.0",tkinter.END)
        return val
    
    
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
                self.text.insert(tkinter.END,cmd+'\n')
        except Exception as e:
            print(e)
            self.text.insert(tkinter.END,"Something went wrong\n")
        
    def createInput(self,row=1,column=1,label):
        '''Creates a text box with a label that can then be used to get user input'''
        inplabel = tkinter.Label(text=label,justify=tkinter.LEFT)
        inplabel.grid(row=row,column=1,sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
        
        inpbox = tkinter.Text(self.top,wrap=tkinter.WORD,height=2,width=25)
        inpbox.config()
        inpbox.grid(row=row,column=2,padx=5,pady=(20,10),sticky=tkinter.E+tkinter.W)           
        self.entries.append(inpbox)
             
if __name__=='__main__':  
    x = TunnGui()