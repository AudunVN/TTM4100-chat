class ClientState():
	def __init__(self):
		self.state = "disconnected"
		self.userName = ""
		#self.currentMessages = []
		#self.pendingMessages = []

	def movePendingToCurrent(self):
		currentMessages.append(pendingMessages)
		pendingMessages = []