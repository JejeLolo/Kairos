from http import client
from pydoc import cli
import subprocess as sub
import command_runner
import sys
from secrets import token_urlsafe
import os
import uuid
import zipfile
import hvac
import requests
from tkinter import *
import ctypes

DEFAULT_PATH = "C:/Kairos/"
xml_task = os.path.join(DEFAULT_PATH, "RenewPass.XML")

# entreprise = sys.argv[1] if len(sys.argv) > 1 else None
entreprise = "jejelolo"

def set_path():
    os.environ['PATH'] = 'C:\\Windows\\System32;C:\\Windows;C:\\Windows\\System32\\Wbem;C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\;C:\\Windows\\System32\\OpenSSH\\;C:\\Program Files\\Git\\bin;C:\\Program Files\\Git\\mingw64\\bin;C:\\Program Files\\Git\\usr\\bin;C:\\Program Files\\Git\\mingw64\\usr\\bin;C:\\Program Files\\Git\\mingw64\\libexec\\git-core;C:\\Program Files\\Git\\mingw64\\share\\git-core;C:\\Program Files\\Git\\mingw64\\share\\git-core\\templates;C:\\Program Files\\Git\\mingw64\\share\\git-gui;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates;C:\\Program Files\\Git\\mingw64\\share\\gitk;C:\\Program Files\\Git\\mingw64\\share\\gitk\\templates;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor\\16x16;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor\\22x22;C:\\Program Files\\Git\\mingw64\\share\\git-gui\\templates\\common\\images\\icons\\hicolor\\'

#init VAULT SERVER
def init_server(token):
    client = hvac.Client(url='https://jeremy-degano.fr', token=token)
    return client.is_authenticated(), client

def read_secret(client):
    secret = client.kv.read_secret(mount_point='kairos', path=f'{entreprise}/{os.environ["COMPUTERNAME"]}')
    return secret

def get_mac():
  mac_num = hex(uuid.getnode()).replace('0x', '').upper()
  mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
  return mac


def insert_secret(client):
    passwd = {str(os.environ["COMPUTERNAME"]): str(passwd)}
    client.secrets.kv.v2.create_or_update_secret(mount_point='kairos', path=f'{entreprise}/{os.environ["COMPUTERNAME"]}', secret=passwd)

def create_user(client):
    """Create Admin User with secrets password
    
    exec : 
        $nusnm = <username>
        $nuspss = ConvertTo-SecureString <password> -AsPlainText -Force
        New-LocalUser -Name $nusnm -Password $nuspss
        Add-LocalGroupMember -Group "Administrateurs" -Member $nusnm
    """ 
    username = 'kairos'
    passwd = token_urlsafe(15)
    command = f"""
    $nusnm = \"{username}\"
    $nuspss = ConvertTo-SecureString \"{passwd}\" -AsPlainText -Force
    New-LocalUser -Name $nusnm -Description "Kairos app user" -Password $nuspss
    Add-LocalGroupMember -Group "Administrateurs" -Member $nusnm
    """
    exec = sub.Popen(["powershell","& {" + command + "}"], stdout=sub.PIPE)
    passwd = {str(os.environ["COMPUTERNAME"]): str(passwd)}
    client.secrets.kv.v2.create_or_update_secret(mount_point='kairos', path=f'{entreprise}/{os.environ["COMPUTERNAME"]}', secret=passwd)
    exec.communicate()
    return True if exec.returncode == 0 else False

def is_user_admin():
    return (False, True)[ctypes.windll.shell32.IsUserAnAdmin()]

def is_user_exist():
    command = """
    Get-LocalUser kairos
    """
    exec = sub.Popen(f"powershell & {command}".split(), stdout=sub.PIPE)
    exec.communicate()
    return True if exec.returncode == 0 else False

def download_files():
    directory = DEFAULT_PATH
    try:
        os.mkdir(directory)
        path = 'https://github.com/JejeLolo/Kairos/archive/refs/heads/main.zip'
        filename = path.split('/')[-1]
        files = requests.get(path, stream=True)
        with open( directory + filename, "wb") as f:
            f.write(files.content)
        with zipfile.ZipFile(directory + filename, 'r') as zip_ref:
            zip_ref.extractall(directory)
        os.remove(directory + filename)
    except:
        pass


def import_shedul_task():
    sub.Popen(f"SCHTASKS /Create /XML {xml_task} /TN KairosApp /F")
    return True if exec.returncode == 0 else False

def delete_shedul_task():
    sub.Popen(f"SCHTASKS /Delete /TN KairosApp /F")
    return True if exec.returncode == 0 else False

def remove_user():
    command = "net user kairos /delete"
    exec = sub.Popen(f"powershell & {command}".split(), stdout=sub.PIPE)
    exec.communicate()
    return True if exec.returncode == 0 else False

def remove_files():
    directory = DEFAULT_PATH
    try:
        os.rmdir(directory)
    except:
        pass

def install(user):
    set_path()
    print(is_user_admin())
    if is_user_exist() or os.path.isdir(DEFAULT_PATH):
        remove_user()
        remove_files()
    create_user(user)
    download_files()
    import_shedul_task()
    return True

def uninstall():
    remove_user()
    remove_files()
    delete_shedul_task()
    return True