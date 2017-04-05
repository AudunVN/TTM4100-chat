from threading import Thread
import socket

class MessageReceiver(Thread):
    def __init__(self, client, connection):
        super(MessageReceiver, self).__init__()

        self.daemon = True
        self.client = client
        self.connection = connection

    def run(self):
        while True:
            msg = self.connection.recv(4096).decode()
            if msg == "":
                self.client.disconnect()
                return
            else:
                self.client.receiveMessage(msg)