import balancer.SimpleBalancer as sb
import subproblems.SimpleSubproblem as sp
import solver.SimpleSolver as slv
import communicator.SimpleCommunicator as com
import Messages.MessageService as ms
import numpy as np


if __name__ == "__main__":
    max_depth = int(input("Enter max depth: "))
    # TODO: rename to amount of processes -- fixed
    processes_amount = int(input("Enter processes amount: "))

    isDoneStates = [False]

    mes_service = ms.MessageService()

    master = sb.MasterBalancer("initial")
    balancers = [master]
    solvers = [slv.SimpleSolver(subProblems=[sp.SimpleSubProblem(0, 0, 0)], records=0,
                                isRecordUpdated=False, maxDepth=max_depth)]
    communicators = [com.SimpleCommunicator("ready")]

    for i in range(1, processes_amount):
        slave = sb.SlaveBalancer("initial")
        balancers.append(slave)

        solver = slv.SimpleSolver(subProblems=[], records=0, isRecordUpdated=False, maxDepth=max_depth)
        solvers.append(solver)

        communicator = com.SimpleCommunicator("ready")
        communicators.append(communicator)

        isDoneStates.append(False)

    state = "initial"
    outputs = []
    optimal_value = 0

    # TODO: add as return from balancer or solver current optimal_value (balancer send command to send optimal_value) -- fixed
    # TODO: add simulation of sending and receiving (communicator) -- fixed
    # TODO: add state as a parameter -- fixed
    # TODO: add default value to balance method as max_depth=... -- fixed
    # TODO: add model time

    while True:
        try:
            proc_ind = isDoneStates.index(False)
            state = balancers[proc_ind].state

            while state != "done":
                if state == "initial":
                    com_state, messages = communicators[proc_ind].receive(proc_ind, mes_service)

                    if com_state == "got message":
                        for [probs, record] in messages:
                            solvers[proc_ind].putSubproblems(probs)
                            if solvers[proc_ind].compareRecord(record):
                                solvers[proc_ind].putRecord(record)

                    state, outputs = balancers[proc_ind].balance(max_depth, state)
                if state == "solve":
                    state, outputs = solvers[proc_ind].solve(outputs[0])
                if state == "solved":
                    state, outputs = balancers[proc_ind].balance(state)
                if state == "send":
                    isSent = True
                    if len(outputs[0]) >= 1 and outputs[0][0] == -1:
                        if len(outputs[1]) >= 1 and outputs[1][0] == -1:
                            probs = solvers[proc_ind].getSubproblems(-1)
                            probs_amnt = len(probs)
                            part = 1 / (processes_amount - 1)
                            for i in range(1, processes_amount):
                                message = [probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)],
                                           solvers[proc_ind].getRecord()]
                                state, outputs = communicators[proc_ind].send(i, message, mes_service)
                                isSent = isSent and (state == "sent")
                                # solvers[i].putSubproblems(probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)])
                    elif len(outputs[1]) == len(outputs[0]):
                        probs = solvers[proc_ind].getSubproblems(np.sum(outputs[1]))
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
                            message = [probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)],
                                       solvers[proc_ind].getRecord()]
                            state, outputs = communicators[proc_ind].send(i, message, mes_service)
                            isSent = isSent and (state == "sent")
                            # solvers[i].putSubproblems(probs[(i - 1) * probs_amnt * part: i * probs_amnt * part])

                    if not isSent:
                        state = "send"

                    state, outputs = balancers[0].balance(state)

                isDoneStates[proc_ind] = (state == "done")
                
            if state == "done" and solvers[proc_ind].compareRecord(optimal_value):
                optimal_value = solvers[proc_ind].getRecord()
                
        except Exception as e:
            print(e)
            break

    print(solvers[0].testDict)
    print("Record is", optimal_value)
