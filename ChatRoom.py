class ChatRoom():
	def __init__(self):
		self.members = {}
		self.name = "Default Room"
		self.state = "open"
		self.messageLog = []
		
	def addMessage(self, message):
		self.messageLog.append(message)
		
	def addMember(self, connection, member):
		self.members[connection] = member
		
	def removeMember(self, member):
		del self.members[member]