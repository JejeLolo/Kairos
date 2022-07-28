from gui.gui import GUI
from tkinter import Tk

def main():
    gui = GUI()
    gui.mainloop()
    
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        pass
