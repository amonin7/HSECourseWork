import Messages.SimpleMessage as ms

class SimpleBalancer:

    def __init__(self, maxDepth, bal_type="slave"):
        self.maxDepth = maxDepth
        self.bal_type = bal_type

    def balance(self):
        if self.bal_type == "slave":
            return ms.SimpleMessage('b', 's', 'ramify', [-1])
        if self.bal_type == "slave":
            return ms.SimpleMessage('b', 'b', 'balance', [])


    '''
        TODO:
        MASTER BALANCER AND SLAVE BALANCER IN ONE CLASS
    '''

