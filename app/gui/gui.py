import re
import os
import subprocess as sub
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename


DEFAULT_SIZE = (380, 300)
CURRENT_USER = os.environ['USERNAME']

def verify_mail(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)

def verify_password(password):
    return True

def write_to_file(file_name, text):
    with open(file_name, 'a') as f:
        f.write( str(datetime.datetime.now()) +  ' :: ' + text + '\n')	

#launch 
    
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.entry_email = None
        self.entry_password = None
        self.pathname = tk.StringVar()
        self.text_description = None
        self.attributes('-toolwindow', True)
        self.set_metadata()
        self.close_button()
        self.input_user()

    def set_metadata(self):
        screensize = self.winfo_screenwidth(), self.winfo_screenheight()
        width = DEFAULT_SIZE[0]
        height = DEFAULT_SIZE[1]
        x = (screensize[0] - width) // 2
        y = (screensize[1] - height) // 2

        self.geometry(f'{width}x{height}+{x}+{y}')
        self.title('kairos')
        self.resizable(False, False)
        self.overrideredirect(True)
    
    def close_button(self):
        btn_close = tk.Button(self, text='X', command=self.destroy)
        btn_close.place(x=350, y=5, width=20, height=20)

    def email_field(self):
        label_email = tk.Label(self, text='Email')
        label_email.place(x=10, y=30) 

        self.entry_email = tk.Entry(self)
        self.entry_email.place(x=120, y=30, width=250)

    def password_field(self):
        label_password = tk.Label(self, text='Mot de passe')
        label_password.place(x=10, y=70)

        self.entry_password = tk.Entry(self, show='*')
        self.entry_password.place(x=120, y=70, width=250)

    def application_field(self):
        label_application = tk.Label(self, text='Application')
        label_application.place(x=10, y=100)

        entry_application = tk.Entry(self, state='disabled', textvariable=self.pathname)
        entry_application.place(x=120, y=100, width=180, height=25)

        btn_application = ttk.Button(self, text='Ouvrir', command=self.get_path)
        btn_application.place(x=310, y=100, width=60, height=25)
    
    def description_field(self):
        label_description = tk.Label(self, text='Remarque')
        label_description.place(x=10, y=130)

        self.text_description = tk.Text(self)
        self.text_description.place(x=120, y=130, width=250, height=100)

        btn_description = tk.Button(self, text='Connect', command=self.user_authent)
        btn_description.place(x=180, y=250)

    def input_user(self):
        self.email_field()
        self.password_field()
        self.application_field()
        self.description_field()

    def get_path(self):
        path = askopenfilename(title='Ouvrir un fichier')
        self.pathname.set(path)
    
    def user_authent(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        pathname = self.pathname.get()
        mark = self.text_description.get('1.0', 'end')[:-1]

        if all((verify_mail(email), verify_password(password), mark, pathname)):
            sub.Popen(f"C:\\Kairos\\RunasCs.exe kairos fmi@fmi.FR {pathname}", shell=True)
            write_to_file("C:\\Kairos\\logs.txt", f"{CURRENT_USER} launched :: {pathname} with mark :: {mark}")
            self.destroy()
        else:
            write_to_file("C:\\Kairos\\logs.txt", f"{CURRENT_USER} failed to launch")

if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
