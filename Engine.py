import balancer.SimpleBalancer as sb
import subproblems.SimpleSubproblem as sp
import solver.SimpleSolver as slv
import communicator.SimpleCommunicator as com
import messages.MessageService as ms
import numpy as np
import route.RouteCollector as rc


class Engine:

    def __init__(self,
                 proc_amount,
                 max_depth,
                 price_receive=1e-2,
                 price_send=1e-2,
                 price_put=1e-2,
                 price_get=1e-3,
                 price_balance=1.0,
                 price_solve=10.0):
        self.processes_amount = proc_amount  # amount of simulated processes
        self.max_depth = max_depth  # max depth of solving tree
        self.price_rcv = price_receive  # price of receiving message
        self.price_snd = price_send  # price of sending message
        self.price_put = price_put  # price of putting message into solver
        self.price_get = price_get  # price of getting message from solver
        self.price_blc = price_balance  # price of balancing
        self.price_slv = price_solve  # price of solving

        self.mes_service = ms.MessageService()
        self.route_collector = rc.RouteCollector('Trace.csv', self.processes_amount)
        self.balancers = []
        self.solvers = []
        self.communicators = []
        self.timers = []
        self.downtime = []  # amount of time when process was without any tasks
        self.isDoneStatuses = []

    def initializeAll(self) -> None:
        master = sb.MasterBalancer("start", max_depth=self.max_depth,
                                   proc_am=self.processes_amount,
                                   prc_blnc=self.price_blc)
        self.balancers = [master]
        self.solvers = [slv.SimpleSolver(subProblems=[sp.SimpleSubProblem(0, 0, 0)],
                                         records=0,
                                         isRecordUpdated=False,
                                         maxDepth=self.max_depth,
                                         prc_put=self.price_put,
                                         prc_slv=self.price_slv)]
        self.communicators = [com.SimpleCommunicator("ready",
                                                     proc_id=0,
                                                     proc_am=self.processes_amount,
                                                     prc_rcv=self.price_rcv,
                                                     prc_snd=self.price_snd)]
        self.timers = [0.0] * self.processes_amount
        self.downtime = [0.0] * self.processes_amount
        self.isDoneStatuses = [False] * self.processes_amount

        for i in range(1, self.processes_amount):
            slave = sb.SlaveBalancer("start", max_depth=self.max_depth, proc_am=self.processes_amount,
                                     prc_blnc=self.price_blc)
            self.balancers.append(slave)

            solver = slv.SimpleSolver(subProblems=[], records=0, isRecordUpdated=False, maxDepth=self.max_depth,
                                      prc_put=self.price_put, prc_slv=self.price_slv)
            self.solvers.append(solver)

            communicator = com.SimpleCommunicator("ready", proc_id=i, proc_am=self.processes_amount,
                                                  prc_rcv=self.price_rcv,
                                                  prc_snd=self.price_snd)
            self.communicators.append(communicator)
            
    def run(self):
        self.initializeAll()
        # command = "start"
        outputs = []
        optimal_value = 0
        while True:
            try:
                proc_ind = self.isDoneStatuses.index(False)
                command = self.balancers[proc_ind].state

                while command != "stop":
                    if command == "start":
                        state = "starting"
                        command, outputs = self.start(proc_id=proc_ind, state=state)
                    elif command == "solve":
                        tasks_am = outputs[0]
                        state, outputs, command = self.solve(proc_id=proc_ind, tasks_amount=tasks_am)
                    elif command == "balance":
                        state = "solved"
                        command, outputs = self.balance(proc_id=proc_ind, state=state)
                    elif command == "send":
                        state = "sending"
                        command, outputs = self.send(proc_id=proc_ind, messages_to_send=outputs)

                    self.isDoneStatuses[proc_ind] = (command == "stop")

                if command == "stop" and self.solvers[proc_ind].compareRecord(optimal_value):
                    optimal_value = self.solvers[proc_ind].getRecord()

            except Exception as e:
                # print(e)
                break

        self.route_collector.save()
        return self.timers

    def start(self, proc_id, state):
        command, messages, time_for_rcv = self.communicators[proc_id].receive(proc_id, self.mes_service)
        if command == "put messages":
            for [probs, record, sending_time] in messages:

                if self.timers[proc_id] < sending_time:
                    self.route_collector.write(proc_id,
                                               str(round(self.timers[proc_id], 3)) + '-' + str(
                                                   round(sending_time, 3)),
                                               'Await for receive',
                                               '-')
                    self.route_collector.write(proc_id,
                                               str(round(sending_time, 3)) + '-' + str(
                                                   round(sending_time + time_for_rcv, 3)),
                                               'Receive',
                                               'Probs length=' + str(len(probs)) + ', record=' + str(record))
                    self.downtime[proc_id] += sending_time - self.timers[proc_id]
                    self.timers[proc_id] = sending_time + time_for_rcv
                else:
                    self.route_collector.write(proc_id,
                                               str(round(self.timers[proc_id], 3)) + '-' + str(
                                                   round(self.timers[proc_id] + time_for_rcv, 3)),
                                               'Receive',
                                               'Probs length=' + str(len(probs)) + ', record=' + str(record))
                    self.timers[proc_id] += time_for_rcv

                self.solvers[proc_id].putSubproblems(probs)
                if self.solvers[proc_id].compareRecord(record):
                    time = self.solvers[proc_id].putRecord(record)
                    if time == -1:
                        raise Exception("Putting problems went wrong")
                    else:
                        self.route_collector.write(proc_id,
                                                   str(round(self.timers[proc_id], 3)) + '-' + str(
                                                       round(self.timers[proc_id] + time, 3)),
                                                   'Put probs into queue',
                                                   'Probs length=' + str(len(probs)))
                        self.timers[proc_id] += time

        command, outputs = self.balance(proc_id, state)
        return command, outputs

    def solve(self, proc_id, tasks_amount):
        state, outputs, time = self.solvers[proc_id].solve(tasks_amount)
        if state == "solved":
            command = "balance"
            self.route_collector.write(proc_id,
                                       str(round(self.timers[proc_id], 3)) + '-' + str(
                                           round(self.timers[proc_id] + time, 3)),
                                       'Solve',
                                       'tasks_am=' + str(tasks_amount))
            self.timers[proc_id] += time
        else:
            raise Exception('Solving went wrong')
        return state, outputs, command

    def balance(self, proc_id, state):
        command, outputs, time = self.balancers[proc_id].balance(state=state)
        self.route_collector.write(proc_id,
                                   str(round(self.timers[proc_id], 3)) + '-' + str(
                                       round(self.timers[proc_id] + time, 3)),
                                   'Balance',
                                   'state=' + state)
        self.timers[proc_id] += time
        return command, outputs

    def send(self, proc_id, messages_to_send):
        is_sent = True
        """
        outputs[0] -- is the list of numbers of processes, where we will send subprobs

        outputs[1] -- is the list of amounts of subproblems, which we will send to other processes
        """
        if len(messages_to_send[0]) >= 1 and messages_to_send[0][0] == -1:
            if len(messages_to_send[1]) >= 1 and messages_to_send[1][0] == -1:
                probs = self.solvers[proc_id].getSubproblems(-1)
                probs_amnt = len(probs)
                part = 1 / (self.processes_amount - 1)
                for dest_proc in range(1, self.processes_amount):
                    message = [probs[int((dest_proc - 1) * probs_amnt * part): int(dest_proc * probs_amnt * part)],
                               self.solvers[proc_id].getRecord(), self.timers[proc_id]]
                    state, outputs, time = self.communicators[proc_id].send(dest_proc, message, self.mes_service)
                    is_sent = is_sent and (state == 'sent')
                    self.save_time(proc_id=proc_id, timestamp=time, message=message, dest_proc=dest_proc)
        elif len(messages_to_send[1]) == len(messages_to_send[0]):
            probs = self.solvers[proc_id].getSubproblems(np.sum(messages_to_send[1]))
            for com_id in messages_to_send[0]:
                list_to_put = []
                for dest_proc in range(messages_to_send[1][com_id]):
                    list_to_put.append(probs.pop())
                message = [list_to_put, self.solvers[proc_id].getRecord(), self.timers[proc_id]]
                state, outputs, time = self.communicators[proc_id].send(com_id, message, self.mes_service)
                is_sent = is_sent and (state == 'sent')
                self.save_time(proc_id=proc_id, timestamp=time, message=message, dest_proc=com_id)
            if len(probs) > 0:
                self.solvers[0].putSubproblems(probs)
        elif len(messages_to_send[1]) >= 1 and messages_to_send[1][0] == -1 and len(messages_to_send[0]) >= 1:
            probs = self.solvers[-1].getSubproblems(-1)
            probs_amnt = len(probs)
            part = 1 / len(messages_to_send[0])
            for dest_proc in messages_to_send[0]:
                message = [probs[int((dest_proc - 1) * probs_amnt * part): int(dest_proc * probs_amnt * part)],
                           self.solvers[proc_id].getRecord(), self.timers[proc_id]]
                state, outputs, time = self.communicators[proc_id].send(dest_proc, message, self.mes_service)
                is_sent = is_sent and (state == 'sent')
                self.save_time(proc_id=proc_id, timestamp=time, message=message, dest_proc=dest_proc)
        if not is_sent:
            raise Exception('Sending went wrong')
        else:
            state = "sent"

        command, outputs = self.balance(proc_id, state)
        return command, outputs
    
    def save_time(self, proc_id, timestamp, message, dest_proc):
        self.route_collector.write(proc_id,
                                   str(round(self.timers[proc_id], 3)) + '-' + str(
                                       round(self.timers[proc_id] + timestamp, 3)),
                                   'Send',
                                   'dest=' + str(dest_proc) + ',mess_len=' + str(len(message)))
        self.timers[proc_id] += timestamp


if __name__ == "__main__":
    proc_am = [10, 50, 100, 200, 500, 1000]
    eng = Engine(5, 30)
    eng.run()
