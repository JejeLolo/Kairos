import string
import tkinter as tk
from tkinter import Entry, StringVar, ttk
from installer import install, init_server,uninstall

DEFAULT_SIZE = (400, 500)


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.set_metadata()
        self.set_install_button()
        self.set_uninstall_button()
        self.name_var = tk.StringVar()
        self.create_widgets()
        self.grid()
        
        # progress_bar = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=280)
        # progress_bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
    
    def set_metadata(self):
        #img = tk.PhotoImage(file='../asset/logo.png')
        #self.iconphoto(False, img)
        ##make titlebar transparent
        # self.overrideredirect(True)
        self.geometry('x'.join(map(str, DEFAULT_SIZE)))
        self.title('kairos')

    def create_widgets(self):
        self.description_label = tk.Label(self, text="Clé de licence:")
        self.description_label.place( x = 10 , y = 10 ) 
        self.token = tk.Entry(self)
        self.token.place( x = 100 , y = 10 , width = 250)

    def set_install_button(self):
        ttk.Button(self, text='Install', command=self.press_install).place(x =(DEFAULT_SIZE[1]//2-45), y = 70)

    def set_uninstall_button(self):
        ttk.Button(self, text='Uninstall', command=self.press_uninstall).place(x =(DEFAULT_SIZE[1]//2-120) , y = 70) #TODO fonction de suppression de l'application
    
    def press_install(self):
        token = self.token.get()
        user=init_server(token)
        install(user[1])
        self.destroy()
    
    def press_uninstall(self):
        uninstall()
        pass