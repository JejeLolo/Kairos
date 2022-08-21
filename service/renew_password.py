import os
import hvac
import subprocess
from secrets import token_urlsafe

#This is a part of kairon APP that runs in background and is not visible to user.
#This servise is used to change the password of the admin user every day

#define vault server
vault_server = 'jeremy-degano.fr'
DEFAULT_PATH = "C:/Kairos/"
SERVICE_FOLDER = os.path.join(DEFAULT_PATH, 'Service')
#set path for ping and net user
def set_path():
    os.environ['PATH'] = 'C:\\Windows\\System32;C:\\Windows;C:\\Windows\\System32\\Wbem;C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\;C:\\Windows\\System32\\OpenSSH\\;C:\\Program Files\\Git\\bin;C:\\Program Files\\Git\\mingw64\\bin;C:\\Program Files\\Git\\usr\\bin;C:\\Program Files\\Git\\mingw64\\usr\\bin;C:\\Program Files\\Git\\mingw64\\libexec\\git-core;C:\\Program Files\\Git\\mingw64\\share\\git-core;C:\\Program Files\\Git\\mingw64\\share\\git-core\\templates;C:\\Program Files\\Git\\mingw64\\share\\git-gui;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates;C:\\Program Files\\Git\\mingw64\\share\\gitk;C:\\Program Files\\Git\\mingw64\\share\\gitk\\templates;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor\\16x16;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor\\22x22;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor\\'

def read_token():
    with open(os.path.join(SERVICE_FOLDER,'token.txt'), 'r') as f:
        return f.read()

def init_server(token):
    #authenticate with tls certificate
    client = hvac.Client(url='https://jeremy-degano.fr', token=token)
    return client.is_authenticated(), client

def insert_secret(client, passwd):
    passwd = {str(os.environ["COMPUTERNAME"]): str(passwd)}
    client.secrets.kv.v2.create_or_update_secret(mount_point='kairos', path='entreprise/{}'.format(os.environ["COMPUTERNAME"]), secret=passwd)

def is_connected(vault_server):
    try:
        #verify if one of the ip is reachable
        subprocess.check_output("ping -n 1 " + vault_server, shell=True)
        return True
    except:
        return False

#verify if user kairos exist
def is_user_exist():
    try:
        subprocess.check_output("net user kairos", shell=True)
        return True
    except:
        return False


      
if __name__ == '__main__':
    try:
        if is_user_exist() == True and is_connected(vault_server) == True:
            #create a new password
            password = token_urlsafe(15)
            #set path for ping and net user
            set_path()
            #change password

            exec = subprocess.run("net user kairos {}".format(password), shell=True)
            #verif if password is changed
            if exec.returncode == 1:
                #Send mail to admin
                pass
            else:
                #insert password in vault
                client = init_server(read_token())
                insert_secret(client[1], password)
        
    except Exception as e:
        print(e)
    finally:
        pass
    
