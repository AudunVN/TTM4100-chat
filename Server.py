import socketserver
import re
import json
import time
from ChatRoom import ChatRoom

defaultChatRoom = ChatRoom()

def encode_message(sender, message):
	return json.dumps({"timestamp": time.time(),
	                   "sender": sender,
					   "response": "message",
					   "content": message})
					   
def encode_info(info):
	return json.dumps({"timestamp": time.time(),
	                   "sender": "",
					   "response": "info",
					   "content": info})

def encode_error(error):
	return json.dumps({"timestamp": time.time(),
	                   "sender": "",
					   "response": "error",
					   "content": error})

def encode_history(history):
	return json.dumps({"timestamp": time.time(),
	                   "sender": "",
					   "response": "history",
					   "content": history})

def parse(payload):
	payload = json.loads(payload)

	if payload["request"] in validResponses:
		return validResponses[payload["request"]](payload)
	else:
		return None

def parse_login(payload):
	return {"login": payload["content"]}

def parse_logout(payload):
	return {"logout": None}

def parse_message(payload):
	return {"message": payload["content"]}

def parse_names(payload):
	return {"names": None}

def parse_help(string):
	return {"help": None}

validResponses = {
	"login": parse_login,
	"logout": parse_logout,
	"msg": parse_message,
	"names": parse_names,
	"help": parse_help
}

class ClientHandler(socketserver.BaseRequestHandler):
	def handle(self):
		self.connection = self.request
		self.chatRoom = defaultChatRoom

		while True:
			payload = parse(self.connection.recv(4096).decode())
			print("[" + str(time.time()) + "] " + "Received payload: " + str(payload))
			if "login" in payload.keys():
				if re.match("^[A-Za-z0-9_-]*$", payload["login"]):
					self.connection.send(encode_history(self.chatRoom.messageLog).encode())
					self.chatRoom.addMember(self.connection, payload["login"])
					print("[" + str(time.time()) + "] " + "Added user: " + str(payload["login"]))
					for member in self.chatRoom.members.keys():
						member.send(encode_info("User " + self.chatRoom.members[self.connection] + " joined the room "+ self.chatRoom.name +".").encode())
				else:
					self.connection.send(encode_error("Invalid username").encode())
			elif "help" in payload.keys():
				self.connection.send(encode_info("Supported server modes/commands: \n - help: This command  \n - names: Show chatroom participants  \n - login, logout").encode())
			elif "message" in payload.keys():
				message = encode_message(self.chatRoom.members[self.connection], payload["message"])
				self.chatRoom.addMessage(message)
				for member in self.chatRoom.members.keys():
					member.send(message.encode())
			elif "names" in payload.keys():
				self.connection.send(encode_info(", ".join(self.chatRoom.members.values())).encode())
			elif "logout" in payload.keys():
				for member in self.chatRoom.members.keys():
					member.send(encode_info("User " + self.chatRoom.members[self.connection] + " left the room " + self.chatRoom.name +".").encode())
				self.connection.close()
				self.chatRoom.removeMember(self.connection)
				return
					
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	allow_reuse_address = True

if __name__ == "__main__":
	host = "localhost"
	port = 9998
	print("[" + str(time.time()) + "] " + "Server started.")
	
	server = ThreadedTCPServer((host, port), ClientHandler)
	server.serve_forever()
