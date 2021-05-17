import time
import socket
import sys
import zlib
import socket
import numpy as np
import cv2

class SocketReceiveVideo:
    ## method init
    # 
    # class initialization 
    def __init__(self):
       
        hostname = socket.gethostname()
        UDP_IP = socket.gethostbyname(hostname) 
        UDP_PORT = 5005
        print("IP: ", UDP_IP)
        # Init socket
        self.sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
        self.sock.bind((UDP_IP, UDP_PORT))

        print("Start receiving video...")

    
    ## method receive_image
    #
    # start receiving images
    def receive_image(self):
        img = ''
        try:
            while True:
                # receive image
                chunk_img, addr = self.sock.recv(4096) # buffer size is 4096 bytes
                img = img + chunk_img 

                if not chunk_img:
                    break

            im_decompressed = zlib.decompress(img)
            img_str = str(bytearray(im_decompressed))
            
            return img_str

        except Exception as e:
            print(e)
            sys.exit(-1)
        except KeyboardInterrupt:
            self.close()
            sys.exit(1)
    
    

    ## method close
    # 
    # close socket
    def close(self):
        self.sock.close()


if __name__ == '__main__':
    # Init class
    srv = SocketReceiveVideo()
    # VGA resolution
    imageHeight = 480
    imageWidth = 640
    try:
        # Start receiving images
        while True:
            img_str = srv.receive_image()

            # Reshape array and show the image 
            nparr = np.fromstring(img_str, np.uint8)
            img_np = nparr.reshape(((imageHeight, imageWidth, 3))).astype(np.uint8)
            cv2.imshow("Pepper front camera", img_np)

    except KeyboardInterrupt:
        print("Stop receiving video.")
        sys.exit(1)


    