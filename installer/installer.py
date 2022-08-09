from pydoc import cli
import shutil
import subprocess as sub
import winreg
import datetime
import windows_tools
import windows_tools.file_utils
import command_runner
import ofunctions.platform
from ofunctions import file_utils
from secrets import token_urlsafe
import os
import uuid
import zipfile
import hvac
import requests
from tkinter import *
import ctypes

DEFAULT_PATH = "C:/Kairos/"
ROOT_PATH = os.path.join(os.environ.get('SYSTEMDRIVE', '/'), os.sep, 'Kairos')
LOG_DIRECTORY = os.path.join(ROOT_PATH, 'logs')
CACERT_FOLDER = os.path.join(DEFAULT_PATH, 'CaCerts')
APP_NAME = "kairos"
APP_VERSION = "0.0.1"

xml_task = os.path.join(DEFAULT_PATH, "RenewPass.XML")

# entreprise = sys.argv[1] if len(sys.argv) > 1 else None
entreprise = "jejelolo"

def set_acls(acl_type, path):
    """
    :param type:
    :param path:
    :return:
    Well known SIDS are
    S-1-1-0 : Everyone
    S-1-5-32-544 : Local administrator
    In order to work, we first need to set rights on all folders and files, then
    set again rights with (OI)(CI) which applies only on folders, in order for new files to have correct rights
    so /grant sid:F works for all folders / files
    second run /grant sid:(OI)(CI):F will enable inheritance on folders
    restricted = System has full rights, admins have full right (core app), everyone has no rights at all (core app)
    read       = System has full rights, everyone has read right (logs)
    """

    # not to use only system ACLs anymore
    # TODO: Remove npexec since it looks like a ransomware to MalwareBytes and probably others
    npexec = os.path.join(DEFAULT_PATH, 'NPExec.exe')

    if acl_type == 'restricted':
        commands = [
            # '"%s" -accepteula -s takeown /F "%s" %s' % (npexec, path, takeown_opt),
            '"%s" -accepteula -s icacls "%s" /inheritance:r /grant:R System:F ' \
            '/grant *S-1-5-32-544:F /remove:gd *S-1-1-0 /T /C /Q' % (npexec, path),
            '"%s" -accepteula -s icacls "%s" /inheritance:r /grant:R System:(OI)(CI)F ' \
            '/grant *S-1-5-32-544:(OI)(CI)F /T /C /Q' % (npexec, path)
        ]
    elif acl_type == 'read':
        commands = [
            # '"%s" -accepteula -s takeown /F "%s" %s' % (npexec, path, takeown_opt),
            '"%s" -accepteula -s icacls "%s" /inheritance:r /grant:R System:F ' \
            '/grant *S-1-5-32-544:F /grant *S-1-1-0:RX /T /C /Q' % (npexec, path),
            '"%s" -accepteula -s icacls "%s" /inheritance:r /grant:R System:(OI)(CI)F ' \
            '/grant *S-1-5-32-544:(OI)(CI)F /grant *S-1-1-0:(OI)(CI)RX /T /C /Q' % (npexec, path)
        ]
    elif acl_type == 'traverse':
        commands = [
            # '"%s" -accepteula -s takeown /F "%s" %s' % (npexec, path, takeown_opt),
            '"%s" -accepteula -s icacls "%s" /grant *S-1-1-0:RX /C /Q' % (npexec, path),
        ]
    elif acl_type == 'traverse-inherit':
        commands = [
            # '"%s" -accepteula -s takeown /F "%s" %s' % (npexec, path, takeown_opt),
            '"%s" -accepteula -s icacls "%s" /grant *S-1-1-0:RX /T /C /Q' % (npexec, path),
            '"%s" -accepteula -s icacls "%s" /grant *S-1-1-0:(OI)(CI)RX /T /C /Q' % (npexec, path)
        ]
    else:
        commands = []

    # First transfer file ownership of every directory and file
    admins_sid = windows_tools.file_utils.get_pysid('S-1-5-32-544')
    try:
        windows_tools.file_utils.take_ownership_recursive(path, owner=admins_sid)
    except OSError:
        pass

    for command in commands:
        result, output = command_runner.command_runner(command, timeout=1800, windows_no_window=True, encoding='cp437')
        if result != 0:
            try:
                temp_log_file = os.path.join(os.environ.get('TMP', False), APP_NAME + '.log')
                tmp_logger = ofunctions.logger_utils.logger_get_logger(temp_log_file, debug= False)
                tmp_logger.critical('Cannot prepare ACLs. %s' % command)
                tmp_logger.critical(output)
            except:
                pass
            return result
    return 0

def fix_acl():
    res = set_acls('restricted', ROOT_PATH)
    if res != 0:
        pass
    res = set_acls('traverse', ROOT_PATH)
    if res != 0:
        pass
    res = set_acls('read', os.path.join(ROOT_PATH, 'logs.txt'))
    if res != 0:
        pass
    #hide cacerts
    file_utils.make_path(CACERT_FOLDER)
    res = set_acls('restricted', CACERT_FOLDER)
    if res != 0:
        pass


def write_to_file(file_name, text):
    with open(file_name, 'a') as f:
        f.write( str(datetime.datetime.now()) +  ' :: ' + text + '\n')	

def set_path():
    os.mkdir(DEFAULT_PATH)
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

    if exec.returncode == 0 :
        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "User Kairos created")
        return True
    else:
        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "User Kairos not created")
        return False

def is_user_admin():
    return (False, True)[ctypes.windll.shell32.IsUserAnAdmin()]

def is_user_exist():
    command = """
    Get-LocalUser kairos
    """
    exec = sub.Popen(f"powershell & {command}".split(), stdout=sub.PIPE)
    exec.communicate()

    if exec.returncode == 0:
        return True
    else:
        return False

def download_files():
    try:
        path = 'https://github.com/JejeLolo/Kairos/archive/refs/heads/main.zip'
        filename = path.split('/')[-1]
        r = requests.get(path, allow_redirects=True)
        open(os.path.join(DEFAULT_PATH, filename), 'wb').write(r.content)
        with zipfile.ZipFile(os.path.join(DEFAULT_PATH, filename), 'r') as zip_ref:
            zip_ref.extractall(DEFAULT_PATH)
        os.remove(os.path.join(DEFAULT_PATH, filename))
        folder = os.listdir(DEFAULT_PATH)[0]
        for file in os.listdir(os.path.join(DEFAULT_PATH, folder)):
            shutil.move(os.path.join(DEFAULT_PATH, folder, file), DEFAULT_PATH)
        os.rmdir(os.path.join(DEFAULT_PATH, folder))

        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "Files downloaded successfully")
        return True
    except:
        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "Files not downloaded something went wrong")
        pass

#reg HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA to 0 --> Allow to launch App without UAC
def reg():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_READ)
    value, regtype = winreg.QueryValueEx(key, "EnableLUA")
    if value != 0:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "EnableLUA modified successfully")
    else:
        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "EnableLUA was already set to 0")
    return True

def remove_reg():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        pass

def import_shedul_task():
    exec = sub.Popen(f"SCHTASKS /Create /XML {xml_task} /TN KairosApp /F")
    exec.communicate()
    if exec.returncode == 0:
        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "Shedul task created")
        return True
    else:
        write_to_file(os.path.join(DEFAULT_PATH,"logs.txt"), "Shedul task not created")
        return False

def delete_shedul_task():
    exec = sub.Popen(f"SCHTASKS /Delete /TN KairosApp /F")
    exec.communicate()
    return True if exec.returncode == 0 else False

def remove_user():
    if is_user_exist():
        command = "net user kairos /delete"
        exec = sub.Popen(f"powershell & {command}".split(), stdout=sub.PIPE)
        exec.communicate()
        if exec.returncode == 0:
            return True
        else:
            return False
    else : 
        pass

def remove_files():
    directory = DEFAULT_PATH
    try:
        os.rmdir(directory)
    except:
        pass

def install(user):
    if is_user_exist() or os.path.isdir(DEFAULT_PATH):
        delete_shedul_task()
        remove_user()
        remove_files()
    set_path()
    create_user(user)
    download_files()
    import_shedul_task()
    reg()
    fix_acl()
    return True

def uninstall():
    remove_user()
    remove_files()
    delete_shedul_task()
    remove_reg()
    return True

