import socket
import time
import sys
import json
from MessageReceiver import MessageReceiver
#from WebServer import WebServer
from ClientState import ClientState

def encode_doLogin(username):
	return json.dumps({"request": "login",
	                   "content": username})

def encode_doLogout():
	return json.dumps({"request": "logout",
	                   "content": None})

def encode_sendMessage(message):
	return json.dumps({"request": "msg",
	                  "content": message})

def encode_getNames():
	return json.dumps({"request": "names",
	                   "content": None})

def encode_getHelp():
	return json.dumps({"request": "help",
	                   "content": None})

def parse(payload):
	payload = json.loads(payload)

	if payload["response"] in validResponses:
		return validResponses[payload["response"]](payload)
	else:
		return None

def parse_error(payload):
	return {"timestamp": payload["timestamp"],
	        "error": payload["content"]}

def parse_info(payload):
	return {"timestamp": payload["timestamp"],
	        "info": payload["content"]}

def parse_message(payload):
	return {"timestamp": payload["timestamp"],
	        "message": payload["content"],
			"sender": payload["sender"]}

def parse_history(payload):
	history = []
	for json_message in payload["content"]:
		history.append(parse(json_message))
	return {"timestamp": payload["timestamp"],
	        "history": history}
	
validResponses = {
	"error": parse_error,
	"info": parse_info,
	"message": parse_message,
	"history": parse_history,
}

class Client:
	def __init__(self, host, server_port):
		self.clientState = ClientState()
		self.host = host
		self.server_port = server_port
		self.clientState.state = "loggedOut";

		self.run()
		
	def connectToServer(self):
		try:
			self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connection.connect((self.host, self.server_port))
			messageReceiver = MessageReceiver(self, self.connection)
			messageReceiver.start()
			self.clientState.state = "loggedOut"
			print("Connection successful.")
		except socket.error as e:
			sys.exit("Unable to connect to server.")
			self.clientState.state = "disconnected"

	def run(self):
		print("Client started. Attempting to connect to server.")
		self.connectToServer()
		while True:
			while not self.connection._closed:
				if self.clientState.state == "disconnected":
					break
				else:
					if self.clientState.state == "loggedOut":
						cmd = input("\rInput: ")
						if cmd == "login":
							self.clientState.userName = input("Username: ")
							self.sendPayload(encode_doLogin(self.clientState.userName))
							# assume login succeeds; will be set to "loggedOut" later if login fails
							self.clientState.state = "chat"
						elif cmd == "help":
							self.sendPayload(encode_getHelp())
						else:
							print("Invalid input. Valid commands: login, help")
					elif self.clientState.state == "chat":
						message = input()
						# the state may change while we're waiting for the input.
						if self.clientState.state == "chat":
							print("\rYou: ", end="")
							if message == "logout":
								self.sendPayload(encode_doLogout())
								self.clientState.state = "disconnected"
							elif message == "names":
								self.sendPayload(encode_getNames())
							elif message == "help":
								self.sendPayload(encode_getHelp())
							else:
								self.sendPayload(encode_sendMessage(message))
								
				# give the server a moment to respond
				time.sleep(0.1) 

			self.clientState.state = "disconnected"
			print("\rDisconnected from server.")
			if input("\rInput: ") == "connect":
				self.connectToServer()
			else:
				print("\rInvalid input. Valid commands: connect")
	def disconnect(self):
		self.connection.close()

	def receiveMessage(self, msg):
		message = parse(msg)
		if "error" in message.keys():
			print("\rError: " + message["error"]+"\nInput: ", end ="")
			self.clientState.state = "loggedOut"
		elif "info" in message.keys():
			if self.clientState.state == "chat":
				print("\rInfo: "+message["info"]+"\nYou: ", end ="")
			else: 
				print("\rInfo: "+message["info"]+"\nInput: ", end ="")
		elif "message" in message.keys():
			if self.clientState.state == "chat":
				if message["sender"] != self.clientState.userName:
					print("\r"+message["sender"] + ": " + message["message"]+"\nYou: ", end ="")
					#print(message["sender"] + ": " + message["message"])
		elif "history" in message.keys():
			print("Chat history:")
			for msg in message["history"]:
				if msg != "":
					if msg["sender"] == self.clientState.userName:
						print("\rYou: " + msg["message"])
					else:
						print("\r" + msg["sender"] + ": " + msg["message"])
			print("\rYou: ", end="")
			self.clientState.state = "chat"

	def sendPayload(self, payload):
		if not self.connection._closed:
			self.connection.send(payload.encode())
		else:
			print("\rError: Sending failed, no connection to server.")

if __name__ == "__main__":
	client = Client("localhost", 9998)
