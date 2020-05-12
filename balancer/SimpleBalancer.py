import Messages.SimpleMessage as ms


class SimpleBalancer:

    def __init__(self, state):
        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def balance(self, max_depth, state):
        print("Balancing")


class MasterBalancer(SimpleBalancer):

    def __init__(self, state="wait tasks"):
        super().__init__(state)

    '''
    :returns status, where to send, how many to send
    where to send -- either list of proc numbers or -1 (means all others)
    how many to send -- either list of amounts of tasks to each process to send
    or -1 (means all tasks should be separated into equal groups and send to all processes)
    '''
    def balance(self, state, max_depth=100):
        self.state = state
        if self.state == "initial":
            return "solve", [max_depth]
        if self.state == "solved":
            return "send", [[-1], [-1]]
        if self.state == "sent":
            return "done", []


class SlaveBalancer(SimpleBalancer):
    def __init__(self, state="wait tasks"):
        super().__init__(state)

    def balance(self, state, max_depth=100):
        self.state = state
        if self.state == "initial":
            return "solve", [-1]
        if self.state == "solved":
            return "done", []

