import tkinter
from tkinter import ttk
import Tunneler

menu = ['self->redirector->dest','{any}->origin->self->dest','self->redirecter->{any}']
class TunnGui(object):
    def __init__(self):
        self.buttons = []
        self.entries = []
        
        self.top = tkinter.Tk()
        self.top.title("Tunneler")
        self.top.tk.call('wm', 'iconphoto', self.top._w, tkinter.PhotoImage(file='wormhole.png'))
        self.top.resizable(width=True,height=True)
        
        self.createInput(0,"Username:")
        self.createInput(1,"Src ip:")      
        self.createInput(2,"Dest ip:")
        self.createInput(3,"Redir ip:")
        
        self.right_frame = tkinter.PanedWindow(self.top,orient=tkinter.VERTICAL,borderwidth=3)
        self.right_horiz_frame = tkinter.PanedWindow(orient=tkinter.HORIZONTAL)
        label = tkinter.Label(text="Tunnel Type:",justify=tkinter.LEFT)
        self.choice = tkinter.StringVar()

        self.dropdown = ttk.Combobox(values=menu,textvariable=self.choice,state='readonly')     
        self.right_horiz_frame.add(label,stretch="always")
        self.right_horiz_frame.add(self.dropdown)
        self.right_frame.add(self.right_horiz_frame,padx=20,pady=20,stretch="always")
        
        
        
        self.text = tkinter.Text(self.right_frame,wrap=tkinter.WORD,width=60,height=10)
        self.right_frame.add(self.text,padx=20,pady=20,stretch="always")
        self.right_frame.grid(row=0,rowspan=4,column=4,padx=10,sticky=tkinter.NSEW)
        
        creator = tkinter.Button(command=self.createTunnel,text="Create!")
        creator.grid(row=5,column=1)
        
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
        val = entry.get("1.0",tkinter.END)
        #print("Returning {}".format(val))
        return val
    
    def printer(self,entry):
        print("box says {}".format(entry.get("1.0",tkinter.END)))
    
    def createTunnel(self):
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
                cmd = tunnel.establish()
                self.text.insert(tkinter.END,cmd+'\n')
        except Exception as e:
            print(e)
            self.text.insert(tkinter.END,"Something went wrong\n")
        
    def createInput(self,row,label,buttonText="Print!"):
        inplabel = tkinter.Label(text=label,justify=tkinter.LEFT)
        inplabel.grid(row=row,column=1,sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
        
        inpbox = tkinter.Text(self.top,wrap=tkinter.WORD,height=2,width=25)
        inpbox.config()
        inpbox.grid(row=row,column=2,padx=5,pady=(20,10),sticky=tkinter.E+tkinter.W)           
    
        #button = tkinter.Button(self.top,height=2,width=5,text=buttonText)
        #button.config(command= lambda: self.printer(inpbox))
        #button.grid(row=row,column=3)
        #self.buttons.append(button)
        self.entries.append(inpbox)
             
if __name__=='__main__':  
    x = TunnGui()