import Tkinter as tk
from GUI_material.image_label import ImageLabel
from speech_thread import SpeechThread
import argparse
import qi

from Queue import Queue

class Window1:
    def __init__(self, master, session):
        #create buttons,entries,etc
        self.master = master
        self.session = session
        
        # Instantiate class for speech recognition
        self.q = Queue()
        self.st = SpeechThread(self.session, self.q)
        
        # Master init
        self.master.title("Talk through Pepper")
        self.master.geometry("800x160")
        self.master.configure(bg='black')
        self.frame = tk.Frame(self.master)
        # Gif init
        self.gif = ImageLabel(self.master)
        self.gif.config(relief="flat", borderwidth=0)
        # self.gif.pack()
        # self.gif.place(relx=0.3,rely=0.02)
        # self.gif.load('GUI_material/voice_rec.jpg')
        
        # Button init
        self.btn_rec = tk.Button(self.master, text="Start Talking", bg='#d62f2f',fg='white', activebackground='#56aaff',width=20, height=2, command=self.start_talk)        
        self.btn_rec.pack()
        self.btn_rec.place(x=20,y=40)
        
        self.btn_stop = tk.Button(self.master, text="Exit", bg='#d62f2f',fg='white', activebackground='#56aaff',width=20, height=2, command=self.stop_thread)        
        self.btn_stop.pack()
        self.btn_stop.place(relx=0.75,y=40)
        
        # Text init
        # self.txt = tk.Label(self.master, bg='black', fg='white', height=4, width=50)
        # self.txt.place(x=400, y=40)
        
        self.frame.pack()
        
        # Start Speech recognition Thread
        self.st.start()
        
    ## method stop_thread
    #
    #  Stop speech recognition thread and close the window
    def stop_thread(self):
        self.st.is_running = False
        self.st.join()
        self.master.destroy()
    
    ## method start_talk
    #
    #  Button callback to start talking
    def start_talk(self):
        # Show gif
        self.gif.pack()
        self.gif.place(relx=0.2,rely=0.01)
        self.gif.load('GUI_material/voice_rec.gif')
        self.btn_rec.configure(text="Stop Talking", command=self.stop_talk)
        
        # # Start Speech recognition
        # if not self.st.is_running:
        #     self.st = SpeechThread(session)
        #     self.st.start()
            
        self.st.rec = True
        
        # txt = self.q.get(block=True, timeout=None) 
        
        # # Show recognized text
        # if txt is not None:
        #     rec_text = self.st.text
        # self.txt.configure(text=rec_text)
    
    ## method stop_talk
    #
    #  Stop recognizing voice and hide microphone gif
    def stop_talk(self):
        self.st.rec = False
        
        self.gif.place_forget()
        self.gif.grid_forget()
        self.gif.pack_forget()
        self.btn_rec.configure(text="Start Talking", command=self.start_talk)
        

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