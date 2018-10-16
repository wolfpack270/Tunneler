import string,os,signal
import subprocess
import types
import socket

DEBUG = True

  

class Tunnel(object):
    '''Tunnel object with tunnel from origin to destination
    
    remote is equivalent to ssh -NfR origin:port:destination:port
    local is equivalent to ssh -NfL localhost:port:destination:port
    dynamic is equivalent to ssh -NfD port'''
    def __init__(self,user='root',ssh_port=22,origin_port=9000,destination_port=9000,remote=False,local=False,dynamic=False):
        self.local=local
        self.remote=remote
        self.dynamic=dynamic        
        self._validate_type()

        self.user= user
        self._validate_user()
        
        self.origin = ''
        self.orig_port=origin_port
        self.destination = ''
        self.dest_port=destination_port
        self.redirector = ''
        self.pid = ''
        self.ssh_port = ssh_port
        self._validate_ports()
    
    def _validate_type(self):
        '''Verifies a tunnel type is selected'''
        if not all(map(lambda x : (isinstance(x,bool) or x==0 or x==1),[self.remote,self.local,self.dynamic])):
            raise ValueError("remote,local and dynamic must be boolean values")
        
        if sum([self.remote,self.local,self.dynamic])>1:
            raise AttributeError("You must select only one type of tunnel")
    
    def _validate_ports(self):
        '''Makes sure ports are numbers and inside a valid range (0,65535]'''
        if not (isinstance(self.ssh_port,int) and isinstance(self.dest_port,int) and isinstance(self.orig_port,int)):
            try:
                self.ssh_port=int(self.ssh_port) # Everyone is gonna need to ssh, so always check
                if self.ssh_port<0 or self.ssh_port>65535:
                    raise ValueError("SSH port must be between 0 and 65535, not {}".format(self.ssh_port))
                
                if self.local or self.remote: 
                    # If doing a local forward, we need a destination port to send to and a port to listen on
                    self.dest_port=int(self.dest_port)
                    if self.dest_port<0 or self.dest_port>65535:
                        raise ValueError("Destination port must be between 0 and 65535, not {}".format(self.dest_port))
                    self.orig_port=int(self.orig_port)
                    if self.orig_port<0 or self.orig_port>65535:
                        raise ValueError("Origin port must be between 0 and 65535, not {}".format(self.orig_port))                
            except Exception as e:
                print(e)
                raise ValueError("Something went wrong with your port values.\nMake sure they are all integers 0 < x <= 65535")
        

        
    
    def _validate_user(self):
        '''Ensures usernames start with a character and consist of only alpha numeric values'''
        if self.user.strip() == '':
            raise ValueError("Username can not be blank")
        if self.user[0] not in string.ascii_letters:
            raise ValueError("Username must start with a letter")
        if not all(map(lambda x : x in string.ascii_letters+string.digits,self.user)):
            raise ValueError("Username {} invalid".format(self.user))
        
    def _validate_ip(self,ip):
        '''Ensures the ip is a string, but not empty.
        Checks to see if hostname/url resolves
        or
        Checks if the input is a valid ip (4 octets, not starting with 0 or 255)'''
        ip=ip.strip()
        if not isinstance(ip,str):
            raise TypeError("ip {} must be string".format(ip))
        
        for i in string.whitespace:
            if i in ip:
                raise ValueError("ip can not contain whitespace")
            
        if ip is "":
            raise ValueError("ip field can not be empty")
        if ip == 'localhost':
            return
        octs = ip.split('.')
        try:
            if not all(map(lambda x: x.isdigit(),octs)):        
                if socket.gethostbyname(ip):
                    return
        except:
            raise ValueError("Could not resolve {}".format(ip))
        
        
        if len(octs) != 4:
            raise IndexError("Invalid number of octets in ip {}".format(ip))
        
        
        if octs[0] == '127':
            # if it starts with 127, let them do their own loopback validation
            return
          
        if int(octs[0]) <=0 or int(octs[0])>=255:
            raise ValueError("ip address can not start with {}".format(octs[0]))
        
        for i in octs[1:]:
            if int(i)<0 or int(i)>255:
                raise ValueError("Invalid ip {}".format(ip))
        
    
    def changeUser(self,user):
        '''Changes the user the ssh tunnel is established through'''
        self.user=user
        

    def establish(self):
        '''Sets up the ssh connection. Will still require user input for the password if necessary
        
        returns the command it would have run
        ---Future----returns pid of ssh tunnel'''
        
        self._validate_type()
        self._validate_user()
        
        if self.dynamic or self.local:
            self._validate_ip(self.redirector)
            
        if self.dynamic:
            
            cmd = 'ssh -p {} -NfD {} {}@{}'.format(self.ssh_port,self.dest_port,self.user,self.redirector)
        
        else:
            self._validate_ip(self.destination)
        
        if self.local:
            if self.destination == 'localhost' or self.destination[0:len('127.0.0.')] == '127.0.0.':
                self.destination = self.redirector
            cmd = 'ssh -p {} -NfL {}:{}:{} {}@{}'.format(self.ssh_port,self.orig_port,self.destination,self.dest_port,self.user,self.redirector)
        
        if self.remote:
            self._validate_ip(self.origin)
            cmd = 'ssh -p {} -NfR {}:{}:{} {}@{}'.format(self.ssh_port,self.orig_port,self.destination,self.dest_port,self.user,self.origin)

        if not DEBUG:
            x = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            result = x.stderr.readline()
            if 'fail' in result:
                self._shell()
                print("You need to manually ssh and accept the host key")
                raise KeyError("You need to manually ssh and accept the host key")
            else:
                print(x.stdout.readline())
        
        return cmd
        
    def _shell(self):
        '''Hopefully this will spawn a mini shell if needed for host key validation issues'''
        desktop = os.environ.get('XDG_CURRENT_DESKTOP')
        if desktop is not None:
            desktop = desktop.lower()
        
        if 'gnome' in desktop:
            TERMINAL = ['gnome-terminal', '--']
        elif desktop == 'kde':
            TERMINAL = ['konsole', '-e']
        elif desktop == 'xfce':
            TERMINAL = ['xfce4-terminal', '-x']
        else:
            TERMINAL = ['xterm', '-e']
            
        x = subprocess.Popen(TERMINAL + cmd.split(),stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        
        
    def kill(self):
        '''Attempts to terminate the tunnel'''
        os.kill(self.pid, signal.SIGTERM)
    
    def __repr__(self):
        if self.local:
            return "Your machine is listening on {}:{} and forwarding the traffic through {}@{} to {}:{}".format(self.origin,\
                                                                                                                      self.orig_port,\
                                                                                                                      self.user,\
                                                                                                                      self.redirector,\
                                                                                                                      self.destination,\
                                                                                                                      self.dest_port)
        if self.remote:
            return "Remote machine {} is listening on port {} and forwarding the traffic through your machine to {}:{}".format(self.origin,\
                                                                                                                               self.orig_port,\
                                                                                                                               self.destination,\
                                                                                                                               self.dest_port)
        if self.dynamic:
            return "Port {} is acting as a socks proxy for traffic through {}@{}".format(self.orig_port,self.user,self.redirector)
        
        
  
if __name__=='__main__':  
    x = Tunnel(dynamic=True)
    x.origin='127.0.0.1'
    x.orig_port=9000
    x.destination="10.10.10.93"
    x.dest_port=9999
    x.redirector='bandit.labs.overthewire.org'
    x.user='bandit0'
    x.establish()