from collections import defaultdict


class MessageService:

    def __init__(self):
        self.message_queue = defaultdict(list)

    def putMessage(self, receiver, message):
        self.message_queue[receiver].append(message)

    def getMessage(self, receiver):
        messages = self.message_queue[receiver]
        self.message_queue[receiver] = []
        return messages
