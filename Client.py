import sys, os # to solve TimsStamp import problme
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import socket
from TimeStamp import TimeStamp
from datetime import datetime, timedelta

class Client:
    
    def __init__(self, name, ip, port, timeout=10.0):
        self.name = name
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.Client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.channel_name = None
        self.ts = TimeStamp(self.name)
        self._rrt = 0

    def connect2Server(self):
        try:
            self.Client_socket.connect((self.ip, self.port))
            time_connected = self.ts.datetime()
            
            self.channel_name, _, _ = self.recv()
            receive_time = self.ts.datetime()

             # = channel_name
            print(f"[{self.ts.datetime()}][Client][connect2Server] Connection to '{self.channel_name}' server is established at time {time_connected}")
            self.send(receive_time)
            rrt_start = datetime.now()
            
            _, _, server_rrt = self.recv()
            print(f"[{self.ts.datetime()}][Client][connect2Server] server_rrt = {server_rrt}")
            self.rrt = (datetime.now() - rrt_start)/timedelta(milliseconds=1)

            self.connected = True

        except socket.error as err_msg:
            print('\033[91m' + f"[{self.ts.datetime()}] Connection to ({self.ip}: {self.port}) cannot establish: {err_msg}" + '\033[39m')

    def send(self, message, show_msg=False):
        try:
            # self.Client_socket.sendall(bytes(self.ts.datetime()+message, 'utf-8'))
            msg2send = f"{self.name}#{self.ts.datetime()}#{message}#".ljust(128, ' ')
            self.Client_socket.sendall(bytes(msg2send, 'utf-8'))
            if show_msg:
                print(f"[{self.ts.datetime()}] Sent message \"{message}\"")
            return True
        except socket.error as err_msg:
            print('\033[91m' + f"[{self.ts.datetime()}] Cannot send message to ({self.ip}: {self.port}): {err_msg}" + '\033[39m')
                # self.Client_socket.close() # directly closing due to unavailablility to communicate
            return False
        
    def recv(self):
        data = self.Client_socket.recv(128)
        if data:
            # msg = f"[{self.ts.datetime()}]" + str(data, 'utf-8')
            msgs = str(data, 'utf-8').split('#')[:-1]
            channel_name = msgs[0]
            sent_time = msgs[1]
            if len(msgs) >= 2:
                msg = msgs[2:]
                if len(msg) == 1 and msg[0] == "END":
                    msg = "END"
            print(f"[{self.ts.datetime()}][Client][recv] msg = {msg}")

            if self.channel_name is not None and channel_name != self.channel_name:
                print(f"[{self.ts.datetime()}][Client][recv] Error: Receive from channel {channel_name}")
                
            return channel_name, sent_time, msg
        else:
            print(f"{self.ts.datetime()}][Client][recv] No raw data receive, return END...")
            return self.channel_name, None, "END"
    
    def close_connection(self):
        # self.Client_socket.sendall(bytes(f"{self.ts.datetime()}Connection closed from Client", "utf-8"))
        print(f"[{self.ts.datetime()}][Client] Connection close notified")
        self.Client_socket.close()

if __name__ == "__main__":
    host_ip = '192.168.1.147'
    port = 12345
    Client = Client(host_ip, port)
    Client.connect2Server()
    for i in range(10):
        Client.communication(f"{i} time send the message")
        time.sleep(1)
    Client.close_connection()