import Tkinter as tk
from GUI_material.image_label import ImageLabel
from speech_thread import SpeechThread
import argparse
import qi

class Window1:
    def __init__(self, master, session):
        #create buttons,entries,etc
        self.master = master
        self.session = session
        
        # Instantiate class for speech recognition
        self.st = SpeechThread(session)
        
        # Master init
        self.master.title("Talk through Pepper")
        self.master.geometry("960x480")
        self.master.configure(bg='black')
        self.frame = tk.Frame(self.master)
        # Gif init
        self.gif = ImageLabel(self.master)
        self.gif.config(relief="flat", borderwidth=0)
        # self.gif.pack()
        # self.gif.place(relx=0.3,rely=0.02)
        # self.gif.load('GUI_material/voice_rec.jpg')
        
        # Button init
        self.btn_rec = tk.Button(self.master, text="Start Talking", bg='#d62f2f',fg='white', activebackground='#56aaff',width=20, height=2, command=self.show_gif)        
        self.btn_rec.pack()
        self.btn_rec.place(x=20,y=40)
        
        # Text init
        self.txt = tk.Text(self.master, bg='black', fg='white')
        self.txt.place(x=100, y=40)
        
        self.frame.pack()
        
    def show_gif(self):
        # self.lbl = ImageLabel(self.master)
        # self.lbl.grid(row=0,column=1,sticky='nwes')
        # self.lbl.config(width=400, height=600)
        
        # Start Speech recognition Thread
        self.st.start()
        # Show gif
        self.gif.pack()
        self.gif.place(relx=0.2,rely=0.01)
        self.gif.load('GUI_material/voice_rec.gif')
        self.btn_rec.configure(text="Stop Talking", command=self.hide_gif)
        
        # Wait for the thread to end and show recognized text
        self.st.join()
        rec_text = self.st.text
        self.txt.insert(tk.END, rec_text)
    
    def hide_gif(self):
        # self.gif.pack()
        # self.gif.place(relx=0.3,rely=0.02)
        # self.gif.load('GUI_material/voice_rec.jpg')
        self.gif.place_forget()
        self.gif.grid_forget()
        self.gif.pack_forget()
        self.btn_rec.configure(text="Start Talking", command=self.show_gif)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="130.251.13.134",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    

    # Parse arguments
    args = parser.parse_args()
    ip_addr = args.ip 
    port = args.port
    session = qi.Session()
    
    # Try to connect to the robot
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
            "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    
    root = tk.Tk()
    app = Window1(root, session)
    root.mainloop()