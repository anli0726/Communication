# The class create a self-defined multithrading server to receive from and send messages to clients
import sys, os # to solve TimsStamp import problme
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import socket
import numpy as np
from colorama import *
from TimeStamp import TimeStamp
from datetime import datetime, timedelta

class Server:

    def __init__(self, channel_name, ip, port, timeout=10.0, latency_threshold=1000):
        '''
        The constructor of the server. It takes ip and port number from user input
        '''
        self.channel_name = channel_name
        self.name = channel_name + "_server"
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.latency_threshold = latency_threshold # latency threshold in millyseconds
        self.comm_dict = {} # a look up table linking client name and corresponding communication channel
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initiate basic socket
        self.server_socket.bind((self.ip, self.port)) # bind the server socket to the host ip and the corresponding port
        self.server_socket.listen(5) # let the socket listening on the network
        self.ts = TimeStamp(self.name)
        self.rrt = 0
        self.clients = []

    def estabish_connection(self):

        try:
            print(f"[{self.ts.time()}][estabish_connection] Number of connected client(s): {len(self.comm_dict)}. Listening to estabish connection...")
            conn2client, client_address = self.server_socket.accept() # block until server accept the connection to client
            client_ip = client_address[0]
            print(f"[{self.ts.time()}][estabish_connection] client_ip = {client_ip}")
            self.comm_dict[client_ip] = conn2client
            print(f"[{self.ts.time()}][estabish_connection] Connectted by {client_address}. Number of connected client(s): {len(self.comm_dict)}")
            return True, conn2client, client_address

        except socket.error as msg: # if the initial sever socket encouter an error
            print('\033[91m' + f"[{self.ts.time()}][estabish_connection] Error when establish connection: {msg}. Closing the server..." + '\033[39m')
            self.server_socket.close() # close the initial sever socket
            return False, None, None

    def comm_quality_check(self, client_ip):

        conn2client = self.comm_dict[client_ip]
        server_check_msg = f"{self.channel_name}#{self.ts.time()}#{self.name}#".ljust(128, ' ')
        conn2client.sendall(bytes(server_check_msg, 'utf-8')) # first sending
        rrt_start = datetime.now()
        try:
            data = conn2client.recv(128) # first receiving (block)
            self.rrt = (datetime.now() - rrt_start)/timedelta(milliseconds=1)
            received_time = self.ts.time()
            client_msgs = str(data, 'utf-8').split('#')[:-1]
            print(f"[{self.ts.time()}][Server] client_msgs = {client_msgs}")
            client_name = client_msgs[0]
            client_ts = client_msgs[1]
            print(f"[{self.ts.time()}][{self.name}] Checking communication qulity to {client_name}...")

            reply_msg = f"{self.channel_name}#{self.ts.time()}#{received_time}#{self.rrt}#".ljust(128, ' ')
            conn2client.sendall(bytes(reply_msg, 'utf-8')) # second sending
            print(f"[{self.ts.time()}][{self.name}] Round trip time (rrt) = {self.rrt}")
            if self.rrt >= self.latency_threshold:
            # show in yellow string if the latency exceeds the threshold
                print('\033[93m' + f'[{self.ts.time()}][Server] The conneciton delay to {client_name} is over {self.latency_threshold} ms' + '\033[39m')
            return True, client_name
        except socket.error as msg: # if error happens
            print('\033[91m' + f"[{self.ts.time()}] Error when checking communication quality: {msg} ..." + '\033[39m')
            return False, None

    def recv(self, client_ip):
        '''
        recv+
        '''
        commObj = self.comm_dict[client_ip]
        data = commObj.recv(128)
        server_min, server_sec, server_msec = self.ts.time(["minute", "second", "msec"])
        result = [None, (server_min, server_sec), None, None]
        if data: # if there is message sent by client

            client_msgs = str(data, 'utf-8').split('#')[:-1] # received and decode the message
            client_name = client_msgs[0]
            client_TimeStamp = client_msgs[1] # extract the local time of the server when sending message
            result[0] = client_name
            detect_result = client_msgs[2:]

            if len(detect_result) == 2: 
            # which means there should be position and orientation info
            # return [client_name, (server_min, server_sec), detect_position, detect_orientation]

                ## convert the time the client send the message and the time server received the message
                ## to seconds, then subtracting them to find the latency
                # client_min = int(client_TimeStamp[-9:-7])
                # client_sec = int(client_TimeStamp[-6:-4])
                # client_msec = int(client_TimeStamp[-3:])
                # client_t = (client_min*60 + client_sec)*1000 + client_msec
                # server_t = (server_min*60 + server_sec)*1000 + server_msec
                # latency = abs(client_t - server_t)
                # if (latency - self.rrt/2) >= self.latency_threshold: # show in yellow string if the latency exceeds the threshold
                #     print('\033[93m' +
                #     f'[{self.ts.time()}][recv] The conneciton delay to {client_name} is over {self.latency_threshold} second(s)'
                #     + '\033[39m')

                detect_position, detect_orientation = detect_result[0], detect_result[1]
                detect_position = np.fromstring(detect_position[1:-1], dtype=float, sep=" ")
                result[2] = detect_position
                detect_orientation = np.fromstring(detect_orientation[1:-1], dtype=float, sep=" ")
                result[3] = detect_orientation

            else:
                # print(f"[{self.ts.time()}][recv] No detect result")
                result[2] = detect_result 

        else: # return [None, (server_min, server_sec), None, None]
            print('\033[91m' +
                  f'[{self.ts.time()}][recv] The conneciton to has been closed'
                  + '\033[39m')
        
        # print(f"[{self.ts.time()}][recv] {client_name} result = {result}")
        return result

    def send(self, message):
        msg2client = f"{self.channel_name}#{self.ts.time()}#{message}#".ljust(128, ' ')
        print(f"[{self.ts.time()}][send] Send instruction {msg2client}")
        for client in self.comm_dict:
            self.comm_dict[client].send(bytes(msg2client, 'utf-8'))

    def request_close_client(self, conn2client, client_address, reason):
        request_close_client_msg = \
          f"Server requests client {client_address} to close due to {reason}"
        print(request_close_client_msg)
        conn2client.sendall(bytes(request_close_client_msg, 'utf-8'))

if __name__ == "__main__": # test case
    myServer = Server("Mobile Comm Server", '', 12345, 10.0)
    res, conn, addr = myServer.estabish_connection()
    while res:
        res, conn, addr = myServer.estabish_connection()
