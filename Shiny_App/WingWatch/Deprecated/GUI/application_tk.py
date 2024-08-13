import tkinter as tk 
from tkinter.messagebox import showinfo

root = tk.Tk()

def show_message():
    showinfo("Hello World!")

btn = tk.Button(root,text='Click Me!', command = show_message)
btn.pack()

root.mainloop()


#Dealt with the error of not being able to connect to the xserver on windows using this link:
#https://stackoverflow.com/questions/49169055/docker-tkinter-tclerror-couldnt-connect-to-display
#Need to find a solution for mac and windows


# i needed to add /tmp/.X11-unix as a shared volume
#docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --name gui_container wingwatch