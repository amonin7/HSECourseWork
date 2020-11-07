class SimpleCommunicator:

    def __init__(self, state, proc_id, proc_am, prc_snd=0, prc_rcv=0):
        self._state = state
        self.proc_id = proc_id
        self.proc_am = proc_am
        self.prc_snd = prc_snd
        self.prc_rcv = prc_rcv

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def send(self, receiver, message, ms):
        time = self.prc_snd
        ms.putMessage(receiver, message)
        return "sent", [], time

    def receive(self, receiver, ms):
        message = ms.getMessage(receiver)
        time = len(message) * self.prc_rcv
        if len(message) != 0:
            return "put messages", message, time
        else:
            return "continue", [], time
