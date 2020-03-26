import Messages.SimpleMessage as ms

class SimpleBalancer:

    def __init__(self, maxDepth, bal_type="slave", is_solved=True, balancers_amount=1):
        self.maxDepth = maxDepth
        self.bal_type = bal_type
        self.is_solved = is_solved
        self.balancers_amount = balancers_amount

    def balance(self, amountOfProblems):
        if self.bal_type == "slave":
            return ms.SimpleMessage('b', 's', 'ramify', [-1])
        elif self.bal_type == "master":
            if self.is_solved:
                answer = []
                for i in range(1, self.balancers_amount):
                    answer.append(ms.SimpleMessage('b', 'b', 'send', [i, amountOfProblems / self.balancers_amount]))
                return answer
            else:
                return [ms.SimpleMessage('b', 's', 'ramify', [100])]
