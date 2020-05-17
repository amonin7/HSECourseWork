import Messages.SimpleMessage as ms


class SimpleBalancer:

    def __init__(self, state, max_depth, prc_blnc=0):
        self._state = state
        self.max_depth = max_depth
        self.prc_blnc = prc_blnc

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def balance(self, state):
        print("Balancing")


class MasterBalancer(SimpleBalancer):

    def __init__(self, state, max_depth, prc_blnc):
        super().__init__(state, max_depth, prc_blnc)

    '''
    :returns status, where to send, how many to send
    where to send -- either list of proc numbers or -1 (means all others)
    how many to send -- either list of amounts of tasks to each process to send
    or -1 (means all tasks should be separated into equal groups and send to all processes)
    '''
    def balance(self, state):
        self.state = state
        if self.state == "starting":
            return "solve", [self.max_depth], self.prc_blnc
        if self.state == "solved":
            return "send", [[-1], [-1]], self.prc_blnc
        if self.state == "sent":
            return "stop", [], self.prc_blnc


class SlaveBalancer(SimpleBalancer):
    def __init__(self, state, max_depth, prc_blnc):
        super().__init__(state, max_depth, prc_blnc)

    def balance(self, state):
        self.state = state
        if self.state == "starting":
            return "solve", [-1], self.prc_blnc
        if self.state == "solved":
            return "stop", [], self.prc_blnc

