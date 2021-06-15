import Tkinter as tk
import tkFileDialog as filedialog
import ttk

root = tk.Tk()

label = tk.Label(root, text="Hello World!") # Create a text label
label.pack(padx=20, pady=20) # Pack it into the window

root.mainloop()