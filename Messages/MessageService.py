from collections import defaultdict


class MessageService:

    def __init__(self):
        self.message_queue = defaultdict(list)

    def putMessages(self, receiver, message):
        self.message_queue[receiver].append(message)

    def getMessages(self, receiver):
        messages = self.message_queue[receiver]
        self.message_queue[receiver] = []
        return messages
