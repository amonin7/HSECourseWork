import random
import subproblems.SimpleSubproblem as subprob


class SimpleSolver:

    # def __init__(self):
    #     pass

    def __init__(self, subProblems, records, isRecordUpdated, maxDepth, prc_put=0.0, prc_slv=1.0):
        self.subProblems = subProblems
        self.records = records
        self.isRecordUpdated = isRecordUpdated
        self.maxDepth = maxDepth
        self.testDict = {1: 0}
        self.prc_put = prc_put
        self.prc_slv = prc_slv

    def getSubproblems(self, amountOfSubProbs):
        if amountOfSubProbs == -1:
            subprobForReturn = self.subProblems
            self.subProblems = []
        else:
            subprobForReturn = self.subProblems[:amountOfSubProbs]
            for x in subprobForReturn:
                self.subProblems.remove(x)
        return subprobForReturn

    def getRecord(self):
        return self.records

    def compareRecord(self, otherRecord):
        return self.records > otherRecord

    def getInfo(self):
        return [len(self.subProblems), self.isRecordUpdated]

    def putSubproblems(self, newSubproblems):
        try:
            self.subProblems.extend(newSubproblems)
        except Exception:
            print(Exception)
            return -1
        else:
            time = len(newSubproblems) * self.prc_put
            return time

    def putRecord(self, newRecord):
        self.records = newRecord

    # функция выдающая с вероятностью р '1' и 1-р '0'
    # вероятность р = (текущая глубина дерева) / (макс глубину дерева)
    def generateContinueOrNot(self, subProblem):
        return random.choices([0, 1],
                              weights=[ float(subProblem.depth) / float(self.maxDepth),
                                        1 - float(subProblem.depth) / float(self.maxDepth)])[0]

    # непосредственное ветвление одной вершины
    def ramify(self):
        curSubProblem = self.subProblems.pop()
        if self.generateContinueOrNot(curSubProblem) == 1:
            self.subProblems.append(subprob.SimpleSubProblem(depth=curSubProblem.depth + 1, weight=0, cost=0))
            self.subProblems.append(subprob.SimpleSubProblem(depth=curSubProblem.depth + 1, weight=0, cost=0))
            if curSubProblem.depth + 1 in self.testDict.keys():
                self.testDict[curSubProblem.depth + 1] += 2
            else:
                self.testDict[curSubProblem.depth + 1] = 2

    # ветвление на эн итераций
    def solve(self, n):
        time = 0.0
        if n > 0:
            i = 0
            while i < n and len(self.subProblems) != 0:
                i += 1
                self.ramify()
            self.records = i
            time = i * self.prc_slv
            self.isRecordUpdated = True
        elif n == -1:
            self.isRecordUpdated = True
            while len(self.subProblems) != 0:
                self.records += 1
                self.ramify()
                time += self.prc_slv
        return "solved", self.getInfo(), time


# if __name__ == "__main__":
#     solver = SimpleSolver(subProblems=[subprob.SimpleSubProblem(0, 0, 0)],
#                           records=[],
#                           isRecordUpdated=False,
#                           maxDepth=20)
#
#     solver.solve(2048)
#
#     print(solver.testDict)

