import os
import sys
import time
import datetime
import subprocess

#This is a part of kairon APP that runs in background and is not visible to user.
#This service is used to elevate the user to admin level 
#create a new file and write new line to it
def write_to_file(file_name, text):
    with open(file_name, 'a') as f:
        f.write( str(datetime.datetime.now()) +  ' :: ' + text + '\n')	

#create a new variable in windows env
def set_env_variable(key, value):
    os.environ[key] = value

def verify():
    return True

CURRENT_USER = "test"

if __name__ == '__main__':
    try:
        command = f"""
            $nusnm = \"{CURRENT_USER}\"
            Add-LocalGroupMember -Group "Administrateurs" -Member $nusnm
            """
        write_to_file('C:\\Kairos\\logs.txt', 'Kairos App as been launched by user: ' + CURRENT_USER)
        if verify() == True: 
            exec = subprocess.Popen(["powershell","& {" + command + "}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exec.communicate()
            if exec.returncode == 0:
                write_to_file('C:\\Kairos\\logs.txt', CURRENT_USER + ' has been added to Admin group')
            else:
                write_to_file('C:\\Kairos\\logs.txt', CURRENT_USER + ' has not been added to Admin group')
        else:
            write_to_file('C:\\Kairos\\logs.txt', 'Verification failed')
    except:
        write_to_file('C:\\Kairos\\logs.txt', 'An error occured')
        sys.exit()