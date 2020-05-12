class SimpleCommunicator:

    def __init__(self, state):
        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def send(self, receiver, message, ms):
        ms.putMessages(receiver, message)
        return "sent", []

    def receive(self, receiver, ms):
        message = ms.getMessages(receiver)
        if len(message) != 0:
            return "got message", message
        else:
            return "no messages yet", []
