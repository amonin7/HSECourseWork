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

    price_rcv = 0.01 #float(input("Enter price of receiving message: "))
    price_snd = 0.01 #float(input("Enter price of sending message: "))
    price_put = 0.001 #float(input("Enter price of putting message into solver: "))
    price_get = 0.001 #float(input("Enter price of getting message from solver: "))
    price_blc = 1.0 #float(input("Enter price of balancing: "))
    price_slv = 10.0 #float(input("Enter price of solving: "))


    # max_depth = int(input("Enter max depth: "))
    # max_depth = int(input("Enter max depth: "))
    # max_depth = int(input("Enter max depth: "))

    isDoneStates = [False]

    mes_service = ms.MessageService()

    master = sb.MasterBalancer("start", max_depth=max_depth, prc_blnc=price_blc)
    balancers = [master]
    solvers = [slv.SimpleSolver(subProblems=[sp.SimpleSubProblem(0, 0, 0)], records=0,
                                isRecordUpdated=False, maxDepth=max_depth, prc_put=price_put, prc_slv=price_slv)]
    communicators = [com.SimpleCommunicator("ready", proc_id=0, proc_am=processes_amount)]
    timers = [0.0]
    downtime = [0.0] # amount of time when process was without any tasks

    for i in range(1, processes_amount):
        slave = sb.SlaveBalancer("start", max_depth=max_depth, prc_blnc=price_blc)
        balancers.append(slave)

        solver = slv.SimpleSolver(subProblems=[], records=0, isRecordUpdated=False, maxDepth=max_depth, prc_put=price_put, prc_slv=price_slv)
        solvers.append(solver)

        communicator = com.SimpleCommunicator("ready", proc_id=i, proc_am=processes_amount, prc_rcv=price_rcv, prc_snd=price_snd)
        communicators.append(communicator)

        timers.append(0.0)
        downtime.append(0.0)

        isDoneStates.append(False)

    command = "start"
    outputs = []
    optimal_value = 0

    # TODO: add as return from balancer or solver current optimal_value (balancer send command to send optimal_value) -- fixed
    # TODO: add simulation of sending and receiving (communicator) -- fixed
    # TODO: add state as a parameter -- fixed
    # TODO: add default value to balance method as max_depth=... -- fixed
    # TODO: add model time -- fixed

    # TODO: 2 add maxdepth to init method and delete it from balance method -- fixed
    # TODO: 2 separate commands and states -- FIXED
    # TODO: 2 add current state in solver to balance method -- FIXED

    while True:
        try:
            proc_ind = isDoneStates.index(False)
            command = balancers[proc_ind].state

            while command != "stop":
                if command == "start":
                    state = "starting"
                    command, messages, time_for_rcv = communicators[proc_ind].receive(proc_ind, mes_service)
                    if command == "put messages":
                        for [probs, record, sending_time] in messages:

                            if timers[proc_ind] < sending_time:
                                downtime[proc_ind] += sending_time - timers[proc_ind]
                                timers[proc_ind] = sending_time + time_for_rcv
                            else:
                                timers[proc_ind] += time_for_rcv

                            solvers[proc_ind].putSubproblems(probs)
                            if solvers[proc_ind].compareRecord(record):
                                time = solvers[proc_ind].putRecord(record)
                                if time == -1:
                                    raise Exception("Putting problems went wrong")
                                else:
                                    timers[proc_ind] += time

                    command, outputs, time = balancers[proc_ind].balance(state=state)
                    timers[proc_ind] += time
                elif command == "solve":
                    state, outputs, time = solvers[proc_ind].solve(outputs[0])
                    if state == "solved":
                        command = "balance"
                        timers[proc_ind] += time
                    else:
                        raise Exception('Solving went wrong')
                elif command == "balance":
                    state = "solved"
                    command, outputs, time = balancers[proc_ind].balance(state=state)
                    timers[proc_ind] += time
                elif command == "send":
                    state = "sending"
                    isSent = True
                    if len(outputs[0]) >= 1 and outputs[0][0] == -1:
                        if len(outputs[1]) >= 1 and outputs[1][0] == -1:
                            probs = solvers[proc_ind].getSubproblems(-1)
                            probs_amnt = len(probs)
                            part = 1 / (processes_amount - 1)
                            for i in range(1, processes_amount):
                                message = [probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)],
                                           solvers[proc_ind].getRecord(), timers[proc_ind]]
                                state, outputs, time = communicators[proc_ind].send(i, message, mes_service)
                                timers[proc_ind] += time
                                isSent = isSent and (state == "sent")
                    elif len(outputs[1]) == len(outputs[0]):
                        probs = solvers[proc_ind].getSubproblems(np.sum(outputs[1]))
                        for com_id in outputs[0]:
                            list_to_put = []
                            for i in range(outputs[1][com_id]):
                                list_to_put.append(probs.pop())
                            message = [list_to_put, solvers[proc_ind].getRecord(), timers[proc_ind]]
                            state, outputs, time = communicators[proc_ind].send(com_id, message, mes_service)
                            timers[proc_ind] += time
                            isSent = isSent and (state == "sent")
                        if len(probs) > 0:
                            solvers[0].putSubproblems(probs)
                    elif len(outputs[1]) >= 1 and outputs[1][0] == -1 and len(outputs[0]) >= 1:
                        probs = solvers[-1].getSubproblems(-1)
                        probs_amnt = len(probs)
                        part = 1 / len(outputs[0])
                        for i in outputs[0]:
                            message = [probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)],
                                       solvers[proc_ind].getRecord(), timers[proc_ind]]
                            state, outputs, time = communicators[proc_ind].send(i, message, mes_service)
                            isSent = isSent and (state == "sent")
                            timers[proc_ind] += time

                    # if len(outputs[1]) == 1 and outputs[1][0] == -1:
                    #     if len(outputs[0]) == 1 and outputs[0] == -1:
                    #         receivers_am = processes_amount - 1
                    #     else:
                    #         receivers_am = len(outputs[0])
                    #     probs = solvers[proc_ind].getSubproblems(-1)
                    #     probs_amnt = len(probs)
                    #     part = 1 / (processes_amount - 1)
                    #     for i in range(1, processes_amount):
                    #         message = [probs[int((i - 1) * probs_amnt * part): int(i * probs_amnt * part)],
                    #                    solvers[proc_ind].getRecord()]
                    #         state, outputs = communicators[proc_ind].send(i, message, mes_service)
                    #         isSent = isSent and (state == "sent")

                    if not isSent:
                        raise Exception('Sending went wrong')
                    else:
                        state = "sent"

                    command, outputs, time = balancers[0].balance(state=state)
                    timers[proc_ind] += time

                isDoneStates[proc_ind] = (command == "stop")
                
            if command == "stop" and solvers[proc_ind].compareRecord(optimal_value):
                optimal_value = solvers[proc_ind].getRecord()
                
        except Exception as e:
            print(e)
            break

    print(solvers[0].testDict)
    print("Timers are ", timers)
    print("Downtimes are ", downtime)
    print("Record is", optimal_value)
