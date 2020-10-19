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
			
			data = self.Client_socket.recv
			(128) # first receiving (block)
			receive_time = self.ts.datetime()
			server_check_msgs = str(data, 'utf-8').split('#')[:-1]
			# print(f"[{self.ts.datetime()}] server_check_msgs = {server_check_msgs}")
			self.channel_name = server_check_msgs[0]
			server_TimeStamp = server_check_msgs[1]
			print(f"[{self.ts.datetime()}][connect2Server]" \
				+ f" Connection to '{self.channel_name}' server is established at time {time_connected}")
			client_check_msg = f"{self.name}#{self.ts.datetime()}#{receive_time}#".ljust(128, ' ')
			self.Client_socket.sendall(bytes(client_check_msg, 'utf-8')) # first sending
			rrt_start = datetime.now()
			
			data = self.Client_socket.recv(128) # second receiveing (block)

			server_reply_msgs = str(data, 'utf-8').split('#')[:-1]
			server_TimeStamp = server_check_msgs[0]
			server_rrt = server_check_msgs[1]
			self.rrt = (datetime.now() - rrt_start)/timedelta(milliseconds=1)

			self.connected = True

		except socket.error as err_msg:
			print('\033[91m' + f"[{self.ts.datetime()}] Connection to ({self.ip}: {self.port}) cannot establish: {err_msg}" + '\033[39m')

	def connect2Server_test(self):
		try:
			self.Client_socket.connect((self.ip, self.port))
			time_connected = self.ts.datetime()
			
			channel_name, server_TimeStamp, _ = self.recv_test()
			receive_time = self.ts.datetime()

			self.channel_name = channel_name
			print(f"[{self.ts.datetime()}][connect2Server] Connection to '{self.channel_name}' server is established at time {time_connected}")
			self.send_test(receive_time)
			rrt_start = datetime.now()
			
			channel_name, server_TimeStamp, server_rrt = self.recv_test()
			print(f"[Client] server_rrt = {server_rrt}")
			self.rrt = (datetime.now() - rrt_start)/timedelta(milliseconds=1)

			self.connected = True

		except socket.error as err_msg:
			print('\033[91m' + f"[{self.ts.datetime()}] Connection to ({self.ip}: {self.port}) cannot establish: {err_msg}" + '\033[39m')

	def send_test(self, message, show_msg=False):
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
		data = self.Client_socket.recv(8)
		if data:
			# msg = f"[{self.ts.datetime()}]" + str(data, 'utf-8')
			msg = str(data, 'utf-8')
			return msg
		else:
			print("[Client][recv] No raw data receive, return END...")
			return "END"

	def recv_test(self):
		data = self.Client_socket.recv(128)
		if data:
			# msg = f"[{self.ts.datetime()}]" + str(data, 'utf-8')
			msgs = str(data, 'utf-8').split('#')[:-1]
			channel_name = msgs[0]
			sent_time = msgs[1]
			if len(msgs) >= 2:
				msg = msgs[2:]
			if channel_name is not None and channel_name != self.channel_name:
				print(f"[client] Error: Receive from channel {msg}")

			return channel_name, sent_time, msg
		else:
			print("[Client][recv] No raw data receive, return END...")
			return self.channel_name, None, "END"
	
	def close_connection(self):
		# self.Client_socket.sendall(bytes(f"{self.ts.datetime()}Connection closed from client", "utf-8"))
		print(f"[{self.ts.datetime()}] Connection close notified")
		self.Client_socket.close()

if __name__ == "__main__":
		host_ip = '192.168.1.147'
		port = 12345
		client = Client(host_ip, port)
		client.connect2Server()
		for i in range(10):
				client.communication(f"{i} time send the message")
				time.sleep(1)
		client.close_connection()