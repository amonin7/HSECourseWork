import balancer.SimpleBalancer as sb
import subproblems.SimpleSubproblem as sp
import solver.SimpleSolver as slv
import numpy as np


if __name__ == "__main__":
    max_depth = int(input("Enter max depth: "))
    balancers_amount = int(input("Enter balancers amount: "))

    isDoneStates = [False]

    master = sb.MasterBalancer("initial")
    balancers = [master]
    solvers = [slv.SimpleSolver(subProblems=[sp.SimpleSubProblem(0, 0, 0)], records=[],
                                isRecordUpdated=False, maxDepth=max_depth)]

    for i in range(balancers_amount):
        slave = sb.SlaveBalancer("initial")
        balancers.append(slave)

        solver = slv.SimpleSolver(subProblems=[], records=[], isRecordUpdated=False, maxDepth=max_depth)
        solvers.append(solver)

        isDoneStates.append(False)

    state = "initial"
    outputs = []

    while True:
        try:
            proc_ind = isDoneStates.index(False)
            state = balancers[proc_ind].state

            while state != "done":
                if state == "initial":
                    state, outputs = balancers[proc_ind].balance(max_depth)
                if state == "solve":
                    state, outputs = solvers[proc_ind].solve(outputs[0])
                if state == "solved":
                    balancers[proc_ind].state = "solved"
                    state, outputs = balancers[proc_ind].balance(max_depth)
                if state == "send":
                    if len(outputs[0]) >= 1 and outputs[0][0] == -1:
                        if len(outputs[1]) >= 1 and outputs[1][0] == -1:
                            probs = solvers[0].getSubproblems(-1)
                            probs_amnt = len(probs)
                            part = 1 / (balancers_amount - 1)
                            for i in range(1, balancers_amount):
                                solvers[i].putSubproblems(probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)])
                    elif len(outputs[1]) == len(outputs[0]):
                        probs = solvers[0].getSubproblems(np.sum(outputs[1]))
                        for bal_ind in outputs[0]:
                            list_to_put = []
                            for i in range(outputs[1][bal_ind]):
                                list_to_put.append(probs.pop())
                            solvers[bal_ind].putSubproblems(list_to_put)
                        if len(probs) > 0:
                            solvers[0].putSubproblems(probs)
                    elif len(outputs[1]) >= 1 and outputs[1][0] == -1 and len(outputs[0]) >= 1:
                        probs = solvers[-1].getSubproblems(-1)
                        probs_amnt = len(probs)
                        part = 1 / len(outputs[0])
                        for i in outputs[0]:
                            solvers[i].putSubproblems(probs[(i - 1) * probs_amnt * part: i * probs_amnt * part])
                    balancers[0].state = "sent"
                    state, outputs = balancers[0].balance(max_depth)

                isDoneStates[proc_ind] = (state == "done")
        except Exception as e:
            # print(e)
            break

    print(solvers[0].testDict)

