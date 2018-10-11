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
        '''Verifies ssh settings'''
        if not all(map(lambda x : (isinstance(x,bool) or x==0 or x==1),[self.remote,self.local,self.dynamic])):
            print("remote,local and dynamic must be boolean values")
            raise ValueError
        
        if sum([self.remote,self.local,self.dynamic])>1:
            print("You must select only one type of tunnel")
            raise AttributeError    
    
    def _validate_ports(self):
        if not (isinstance(self.ssh_port,int) and isinstance(self.dest_port,int) and isinstance(self.orig_port,int)):
            if self.ssh_port<0 or self.ssh_port>65535:
                print("SSH port must be between 0 and 65535, not {}".format(self.ssh_port))
            if self.dest_port<0 or self.dest_port>65535:
                print("Destination port must be between 0 and 65535, not {}".format(self.dest_port))
            if self.orig_port<0 or self.orig_port>65535:
                print("Origin port must be between 0 and 65535, not {}".format(self.orig_port))
            print("Something went wrong with your port values.\nMake sure they are all integers 0 < x <= 65535")
            raise ValueError
    
    def _validate_user(self):
        if self.user.strip() == '':
            print("Username can not be blank")
            raise ValueError
        if self.user[0] not in string.ascii_letters:
            print("Username must start with a letter")
            raise ValueError
        if not all(map(lambda x : x in string.ascii_letters+string.digits,self.user)):
            print("Username {} invalid".format(self.user))
            raise ValueError
        
    def _validate_ip(self,ip):
        if not isinstance(ip,str):
            print("ip {} must be string".format(ip))
            raise TypeError
        if ip is "":
            raise ValueError
        if ip == 'localhost':
            return
        octs = ip.split('.')
        try:
            if not all(map(lambda x: x.isdigit(),octs)):        
                if socket.gethostbyname(ip):
                    return
        except:
            print("IP could not resolve")
            raise ValueError
        
        
        if len(octs) != 4:
            print("Invalid number of octets in ip {}".format(ip))
            raise IndexError
        
        
        if octs[0] == '127':
            return
          
        if int(octs[0]) <=0 or int(octs[0])>=255:
            print("ip address can not start with {}".format(octs[0]))
            raise ValueError
        
        for i in octs[1:]:
            if int(i)<0 or int(i)>255:
                print("Invalid ip {}".format(ip))
                raise ValueError
        
    
    def changeUser(self,user):
        '''Changes the user the ssh tunnel is established through'''
        self.user=user
        

    def establish(self):
        '''Sets up the ssh connection. Will still require user input for the password if necessary
        
        returns pid of ssh tunnel'''
        self._validate_type()
        self._validate_user()
        
        if self.dynamic or self.local:
            self._validate_ip(self.redirector)
            
        if self.dynamic:
            
            cmd = 'ssh -p {} -NfD {} {}@{}'.format(self.ssh_port,self.dest_port,self.user,self.redirector)
            #print(cmd)
            #return
        
        else:
            self._validate_ip(self.destination)
        
        if self.local:
            if self.destination == 'localhost' or self.destination[0:len('127.0.0.')] == '127.0.0.':
                self.destination = self.redirector
            cmd = 'ssh -p {} -NfL {}:{}:{} {}@{}'.format(self.ssh_port,self.orig_port,self.destination,self.dest_port,self.user,self.redirector)
            #print(cmd)
            #return
        
        if self.remote:
            self._validate_ip(self.origin)
            cmd = 'ssh -p {} -NfR {}:{}:{} {}@{}'.format(self.ssh_port,self.orig_port,self.destination,self.dest_port,self.user,self.origin)
            #print(cmd)
            #return
            
        print(cmd)

        if not DEBUG:
            x = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            result = x.stderr.readline()
            if 'fail' in result:
                self._shell()
                print("You need to manually ssh and accept the host key")
                raise KeyError
            else:
                print(x.stdout.readline())
        
        return cmd
        
    def _shell(self):
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