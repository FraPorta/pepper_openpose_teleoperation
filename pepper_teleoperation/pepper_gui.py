from Tkconstants import RIGHT
import Tkinter as tk
import argparse
import qi
# import time
import sys
from PIL import ImageTk, Image



from GUI_material.image_label import ImageLabel
from speech_thread import SpeechThread
from pepper_approach_control_thread import PepperApproachControl
from Queue import Queue

# Colors
red = '#d63d41'
dark_red = '#c82b2e'
darkest_red = '#52373b' 
light_red = '#eb9ea0'
orange = '#ec5633'

class PepperGui:
    def __init__(self, master, session):
        #create buttons,entries,etc
        self.master = master
        self.session = session
        
        self.teleop = tk.IntVar()
        self.approach = tk.IntVar()
        
        # Instantiate queue and class for speech recognition
        self.q_speech = Queue()
        self.q_record = Queue()
        
        self.q_pepper = Queue()
        self.q_appr_teleop = Queue()
        self.st = None
        
        font='Lucida Sans'
        btn_txt_size = 12
        
        # Colors
        red = '#d63d41'
        dark_red = '#c82b2e'
        darkest_red = '#52373b' 
        light_red = '#eb9ea0'
        orange = '#ec5633'

        
        # Master init
        self.master.title("Pepper Control")
        self.master.geometry("1000x562")
        self.master.configure(bg=red)
        self.master.resizable(False, False)
        # Background
        # image = Image.open('GUI_material/background.png')
        IMAGE_PATH = 'GUI_material/background.png'
        WIDTH, HEIGTH = 1000, 562

        self.canvas = tk.Canvas(self.master, width=WIDTH, height=HEIGTH)
        self.canvas.pack()

        img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((WIDTH, HEIGTH), Image.ANTIALIAS))
        self.canvas.background = img  # Keep a reference in case this code is put in a function.
        bg = self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
       
        # BUTTONS
        # Button start recording
        self.btn_rec = tk.Button(self.master,
                                 text="Start Talking",
                                 bg=darkest_red,
                                 fg='white',
                                 font=(font, btn_txt_size),
                                 activebackground=dark_red,
                                 activeforeground='white',
                                 width=20,
                                 height=2,
                                 disabledforeground=light_red,
                                 relief=tk.FLAT,
                                 state=tk.DISABLED,
                                 command=self.start_talk)        
        self.btn_rec.pack()
        self.btn_rec.place(x=20, y=80)
        
        # Button start pepper approach and teleoperation
        self.btn_pepper = tk.Button(self.master, 
                                    text="Start Search/Teleoperation",
                                    bg=darkest_red,
                                    fg='white',
                                    font=(font, btn_txt_size),
                                    activebackground=dark_red,
                                    activeforeground='white',
                                    width=20,
                                    height=2,
                                    disabledforeground=light_red,
                                    relief=tk.FLAT,
                                    state=tk.DISABLED,
                                    command=self.start_pepper)        
        self.btn_pepper.pack()
        self.btn_pepper.place(x=20, y=245)
        
        # Button connect to Pepper
        self.btn_connect = tk.Button(self.master, 
                                    text="Connect to Pepper",
                                    bg=orange,
                                    fg='white',
                                    font=(font, btn_txt_size),
                                    activebackground=dark_red,
                                    activeforeground='white',
                                    width=20,
                                    height=2,
                                    disabledforeground="grey",
                                    anchor=tk.CENTER,
                                    relief=tk.FLAT,
                                    command=self.connect_pepper)        
        self.btn_connect.pack()
        self.btn_connect.place(relx=0.4, y=450)
        
        # Gifs
        self.gif = ImageLabel(self.master)
        self.gif.config(relief="flat", borderwidth=0)
        self.gif.pack()
        self.gif.place(x=257, y=74)
        self.gif.load('GUI_material/voice_transp_frame.gif')
        
        gif_path = 'GUI_material/load_white_frame.gif'
        self.gif_load = ImageLabel(self.master)
        self.gif_load.config(relief="flat", borderwidth=0)
        self.gif_load.pack()
        self.gif_load.place(x=257, y=240)
        self.gif_load.load(gif_path)
        
        # Labels
        self.txt_1 = tk.Label(self.master,
                              bg=red,
                              fg='white',
                              font=(font,12,'bold'))
        self.txt_1.place(x=350, y=50)
        self.txt_1.configure(text="Recognized text:")
        
        self.txt = tk.Label(self.master,
                            bg=dark_red,
                            bd=3,
                            fg='white',
                            font=(font,12),
                            width=62,
                            height=2,
                            relief=tk.FLAT)
        self.txt.place(x=350, y=83)
        self.txt.configure(text="The recognized text will appear here...")
        
        self.txt_pepper_1 = tk.Label(self.master,
                                     bg=red,
                                     fg='white',
                                     font=(font,12,'bold'))
        self.txt_pepper_1.place(x=350, y=215)
        self.txt_pepper_1.configure(text="Feedback:")
        
        self.txt_pepper = tk.Label(self.master,
                                   bg=dark_red,
                                   bd=3,
                                   fg='white',
                                   font=(font,12),
                                   width=62,
                                   height=2,
                                   relief=tk.FLAT)

        self.txt_pepper.place(x=350, y=248)
        self.txt_pepper.configure(text="Feedback from Pepper will appear here...")
        
        self.lbl_conn = tk.Label(self.master,
                                 bg=darkest_red,
                                 fg=light_red,
                                 font=(font,11))
        self.lbl_conn.place(relx=0.4, y=520)
        self.lbl_conn.configure(text="Press the button to connect!")
        
        # CheckBoxes
        y=305
        self.c_approach = tk.Checkbutton(self.master,
                                         text = "Approach",
                                         variable = self.approach,
                                         onvalue = 1,
                                         offvalue = 0,
                                         font=(font,12,'bold'),
                                         bg=red,
                                         fg='white',
                                         selectcolor=darkest_red,
                                         activebackground=red,
                                         activeforeground='white')
        self.c_approach.place(x=20, y=y)
        
        self.c_teleop = tk.Checkbutton(self.master,
                                       text = "Teleoperation",
                                       variable = self.teleop,
                                       onvalue = 1, 
                                       offvalue = 0,
                                       font=(font,12,'bold'), 
                                       bg=red,
                                       fg='white',
                                       selectcolor=darkest_red,
                                       activebackground=red,
                                       activeforeground='white',
                                       relief=tk.FLAT)
        self.c_teleop.place(x=20, y=y+30)
        
        # Entries
        self.text_ip = tk.Entry(self.master,
                                bg=red,
                                fg='white',
                                font=(font,12),
                                insertbackground='white',
                                disabledbackground=darkest_red,
                                width=15,
                                relief=tk.FLAT)
        self.text_ip.insert(tk.END, "130.251.13.134")
        self.text_ip.place(x=580-135, y=405-10)
        
        self.lbl_ip = tk.Label(self.master,
                               bg=darkest_red,
                               fg='white',
                               font=(font,12))
        self.lbl_ip.place(x=554-135, y=405-10)
        self.lbl_ip.configure(text="IP:")
        
        self.text_port = tk.Entry(self.master,
                                  bg=red,
                                  fg='white',
                                  font=(font,12),
                                  insertbackground='white',
                                  disabledbackground=darkest_red,
                                  width=15,
                                  relief=tk.FLAT)
        self.text_port.insert(tk.END, "9559")
        self.text_port.place(x=580-135, y=425-10)
        
        self.lbl_port = tk.Label(self.master,
                                 bg=darkest_red,
                                 fg='white',
                                 font=(font,12))
        self.lbl_port.place(x=540-135, y=425-10)
        self.lbl_port.configure(text="Port:")  
    
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
                self.btn_rec.configure(state=tk.NORMAL, bg=orange)
                self.btn_pepper.configure(state=tk.NORMAL, bg=orange)
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
        show_plot = True
        gif_path = 'GUI_material/load_white.gif'
        
        if self.approach.get() == 1 and self.teleop.get() ==1:
            # Show gif
            self.gif_load = ImageLabel(self.master)
            self.gif_load.config(relief="flat", borderwidth=0)
            self.gif_load.pack()
            self.gif_load.place(x=257, y=240)
            self.gif_load.load(gif_path)
            
            approach_requested = True
            approach_only = False
            
            self.pac = PepperApproachControl(self.session, show_plot, approach_requested, approach_only, self.q_pepper, self.q_appr_teleop)
            self.pac.start()
            
            # Change button text and command
            self.btn_pepper.configure(text="Stop Pepper", command=self.stop_pepper)
            
        elif self.approach.get() == 0 and self.teleop.get() == 1:
            # Show gif
            self.gif_load = ImageLabel(self.master)
            self.gif_load.config(relief="flat", borderwidth=0)
            self.gif_load.pack()
            self.gif_load.place(x=257, y=240)
            self.gif_load.load(gif_path)
            
            approach_requested = False
            approach_only = False
            
            self.pac = PepperApproachControl(self.session, show_plot, approach_requested, approach_only, self.q_pepper, self.q_appr_teleop)
            self.pac.start()
            
            # Change button text and command
            self.btn_pepper.configure(text="Stop Pepper", command=self.stop_pepper)
            
        elif self.approach.get() == 1 and self.teleop.get() == 0:
            # Show gif
            self.gif_load = ImageLabel(self.master)
            self.gif_load.config(relief="flat", borderwidth=0)
            self.gif_load.pack()
            self.gif_load.place(x=257, y=240)
            self.gif_load.load(gif_path)
            
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
        # self.gif_load.place_forget()
        # self.gif_load.pack_forget()
        self.q_pepper.put(True)
        
        gif_path = 'GUI_material/load_white_frame.gif'
        self.gif_load = ImageLabel(self.master)
        self.gif_load.config(relief="flat", borderwidth=0)
        self.gif_load.pack()
        self.gif_load.place(x=257, y=240)
        self.gif_load.load(gif_path)
        
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
        self.gif.place(x=257, y=74)
        self.gif.load('GUI_material/voice_transp.gif')
        
        # Change button text and command
        self.btn_rec.configure(text="Stop Talking", command=self.stop_talk)
        
        # Start recording for Speech to text   
        self.q_record.put("Rec")  

    ## method stop_talk
    #
    #  Stop recognizing voice and hide microphone gif
    def stop_talk(self):
        self.q_record.put("StopRec")
        self.gif = ImageLabel(self.master)
        self.gif.config(relief="flat", borderwidth=0)
        self.gif.pack()
        self.gif.place(x=257, y=74)
        self.gif.load('GUI_material/voice_transp_frame.gif')
        # self.gif.place_forget()
        # self.gif.grid_forget()
        # self.gif.pack_forget()
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
    # Start naoqi session
    session = qi.Session()
    
    # Start GUI
    root = tk.Tk()
    app = PepperGui(root, session)
    app.start()