from Tkconstants import RIGHT
import Tkinter as tk
import argparse
import qi
# import time
import sys


from GUI_material.image_label import ImageLabel
from speech_thread import SpeechThread
from pepper_approach_control_thread import PepperApproachControl
from Queue import Queue

class PepperGui:
    def __init__(self, master, session):
        #create buttons,entries,etc
        self.master = master
        self.session = session
        self.btn_txt_size = 10
        self.teleop = tk.IntVar()
        self.approach = tk.IntVar()
        
        # Instantiate queue and class for speech recognition
        self.q_speech = Queue()
        self.q_record = Queue()
        
        self.q_pepper = Queue()
        self.q_appr_teleop = Queue()
        self.st = None
        
        # Master init
        self.master.title("Talk through Pepper")
        self.master.geometry("960x480")
        self.master.configure(bg='black')
        self.frame = tk.Frame(self.master)
        
        # Gif init
        self.gif = ImageLabel(self.master)
        self.gif.config(relief="flat", borderwidth=0)
       
        # BUTTONS
        # Button start recording
        self.btn_rec = tk.Button(self.master,
                                 text="Start Talking",
                                 bg='#d62f2f',
                                 fg='white',
                                 font=('MS Sans Serif',self.btn_txt_size),
                                 activebackground='#ce4d33',
                                 width=20,
                                 height=2,
                                 state=tk.DISABLED,
                                 command=self.start_talk)        
        self.btn_rec.pack()
        self.btn_rec.place(x=20,y=40)
        
        # Button start pepper approach and teleoperation
        self.btn_pepper = tk.Button(self.master, 
                                    text="Start Search/Teleoperation",
                                    bg='#d62f2f',
                                    fg='white',
                                    font=('MS Sans Serif',self.btn_txt_size),
                                    activebackground='#ce4d33',
                                    activeforeground='white',
                                    width=20,
                                    height=2,
                                    state=tk.DISABLED,
                                    command=self.start_pepper)        
        self.btn_pepper.pack()
        self.btn_pepper.place(x=20,y=160)
        
        # Button connect to Pepper
        self.btn_connect = tk.Button(self.master, 
                                    text="Connect to Pepper",
                                    bg='#d62f2f',
                                    fg='white',
                                    font=('MS Sans Serif',self.btn_txt_size),
                                    activebackground='#ce4d33',
                                    activeforeground='white',
                                    width=20,
                                    height=2,
                                    disabledforeground="white",
                                    command=self.connect_pepper)        
        self.btn_connect.pack()
        self.btn_connect.place(x=750,y=400)
        
        # Labels init
        self.txt = tk.Label(self.master, bg='black', fg='white', font=('MS Sans Serif',12))
        self.txt.place(x=325, y=50)
        self.txt.configure(text="The recognized text will appear here...")
        
        self.txt_pepper = tk.Label(self.master, bg='black', fg='white', font=('MS Sans Serif',12))
        self.txt_pepper.place(x=325, y=170)
        self.txt_pepper.configure(text="Feedback from Pepper will appear here...")
        
        self.lbl_conn = tk.Label(self.master, bg='black', fg='white', font=('MS Sans Serif',11))
        self.lbl_conn.place(x=750,y=370)
        self.lbl_conn.configure(text="Press the button to connect!")
        
        # CheckBoxes
        y=230
        self.c_approach = tk.Checkbutton(self.master, text = "Approach", variable = self.approach,\
                                         onvalue = 1, offvalue = 0, font=('MS Sans Serif',12,'bold'), bg='black', fg='#d62f2f',\
                                         selectcolor='white', activebackground="black", activeforeground='#d62f2f')
        self.c_approach.place(x=20,y=y)
        
        self.c_teleop = tk.Checkbutton(self.master, text = "Teleoperation", variable = self.teleop,\
                                       onvalue = 1, offvalue = 0, font=('MS Sans Serif',12,'bold'), bg='black', fg='#d62f2f',\
                                       selectcolor='white', activebackground="black", activeforeground='#d62f2f')
        self.c_teleop.place(x=20,y=y+30)
        
        # Texts
        self.text_ip = tk.Entry(self.master, bg='black', fg='white', font=('MS Sans Serif',12),insertbackground='white',disabledbackground="#333333", width=15)
        self.text_ip.insert(tk.END, "130.251.13.134")
        self.text_ip.place(x=600,y=400)
        
        self.lbl_ip = tk.Label(self.master, bg='black', fg='white', font=('MS Sans Serif',12))
        self.lbl_ip.place(x=574,y=400)
        self.lbl_ip.configure(text="IP:")
        
        self.text_port = tk.Entry(self.master, bg='black', fg='white', font=('MS Sans Serif',12),insertbackground='white',disabledbackground="#333333", width=15)
        self.text_port.insert(tk.END, "9559")
        self.text_port.place(x=600,y=420)
        
        self.lbl_port = tk.Label(self.master, bg='black', fg='white', font=('MS Sans Serif',12))
        self.lbl_port.place(x=560,y=420)
        self.lbl_port.configure(text="Port:")
        
        self.frame.pack()
        
        
    
    ## method connect_pepper
    #
    #  Starts the Session with given Ip and Port
    def connect_pepper(self):
        self.lbl_conn.configure(text="Trying to connect...")
        
        session_connected = True
        value_err = False
 
        try:
            self.ip = self.text_ip.get()
            self.port = int(self.text_port.get())
        except ValueError:
            value_err = True
        
        if value_err:
            self.lbl_conn.configure(text="Check the port number")
        else:
            # Try to connect to the robot
            try:
                self.session.connect("tcp://" + self.ip + ":" + str(self.port))
            except RuntimeError:
                session_connected = False
                self.lbl_conn.configure(text="Can't connect, please change ip")
                
            # If the connection was successfull, unlock the other buttons and start the speech recognition thread
            if session_connected:
                self.btn_rec.configure(state=tk.NORMAL)
                self.btn_pepper.configure(state=tk.NORMAL)
                self.btn_connect.configure(state=tk.DISABLED, bg="#57aa03", text="Connected!")
                self.text_ip.configure(state=tk.DISABLED)
                self.text_port.configure(state=tk.DISABLED)
                self.lbl_conn.place_forget()
                
                # Create Speech Thread
                self.st = SpeechThread(self.session, self.q_speech, self.q_record)
                # Start Speech recognition Thread
                self.st.start()
        
    ## method start_pepper
    #
    #  Start Pepper approach/teleoperation
    def start_pepper(self):
        show_plot = False
        
        if self.approach.get() == 1 and self.teleop.get() ==1:
            approach_requested = True
            approach_only = False
            
            self.pac = PepperApproachControl(self.session, show_plot, approach_requested, approach_only, self.q_pepper, self.q_appr_teleop)
            self.pac.start()
            
            # Change button text and command
            self.btn_pepper.configure(text="Stop Pepper", command=self.stop_pepper)
            
        elif self.approach.get() == 0 and self.teleop.get() == 1:
            approach_requested = False
            approach_only = False
            
            self.pac = PepperApproachControl(self.session, show_plot, approach_requested, approach_only, self.q_pepper, self.q_appr_teleop)
            self.pac.start()
            
            # Change button text and command
            self.btn_pepper.configure(text="Stop Pepper", command=self.stop_pepper)
            
        elif self.approach.get() == 1 and self.teleop.get() == 0:
            approach_requested = True
            approach_only = True
            
            self.pac = PepperApproachControl(self.session, show_plot, approach_requested, approach_only, self.q_pepper, self.q_appr_teleop)
            self.pac.start()
            
            # Change button text and command
            self.btn_pepper.configure(text="Stop Pepper", command=self.stop_pepper)
        else:
            self.txt_pepper.configure(text="Please select Approach or Teleoperation or both")
            

    
    ## method stop_pepper
    #
    #  Stop Pepper approach/teleoperation
    def stop_pepper(self):
        self.q_pepper.put(True)
        # if self.pac.approach_requested or self.pac.approach_only:
            # self.pac.au.is_stopped = True
            # self.pac.loop_interrupted = True
            
        # Change button text and command
        self.btn_pepper.configure(text="Start Search/Teleoperation", command=self.start_pepper)
    
    ## method start_talk
    #
    #  Button callback to start talking
    def start_talk(self):
        # Show gif
        self.gif = ImageLabel(self.master)
        self.gif.config(relief="flat", borderwidth=0)
        self.gif.pack()
        self.gif.place(x=202, rely=0.01)
        self.gif.load('GUI_material/voice_rec.gif')
        
        # Change button text and command
        self.btn_rec.configure(text="Stop Talking", command=self.stop_talk)
        
        # Start recording for Speech to text   
        self.q_record.put("Rec")  
        # self.st.rec = True

    ## method stop_talk
    #
    #  Stop recognizing voice and hide microphone gif
    def stop_talk(self):
        self.q_record.put("StopRec")
        # self.st.rec = False
        
        self.gif.place_forget()
        self.gif.grid_forget()
        self.gif.pack_forget()
        self.btn_rec.configure(text="Start Talking", command=self.start_talk)

    ## method on_closing
    #
    #  Stop speech recognition thread and close the window
    def on_closing(self):
        self.q_record.put("StopRun")
        # self.st.is_running = False
        if self.st is not None:
            if self.st.is_alive():
                self.st.join()
        self.master.destroy()
    
    ## method start
    #
    #  Start the mainloop
    def start(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.after(500, func=self.check_queue)
        self.master.mainloop()
    
    ## method check_queue
    #
    #  Check every half a second if there is an entry in the queue
    def check_queue(self):
        # if self.st.is_running:
        # If the queue is not empty get the recognized text
        if not self.q_speech.empty():
            text = self.q_speech.get(block=False, timeout=None) 
            # Show recognized text
            if text is not None:
                self.txt.configure(text=text)
        
        if not self.q_appr_teleop.empty():
            string = self.q_appr_teleop.get(block=False, timeout=None)
            if string is not None:
                self.txt_pepper.configure(text=string)
                    
        self.master.after(500, func=self.check_queue)

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
    
    root = tk.Tk()
    app = PepperGui(root, session)
    app.start()