import pandas as pd
import EngineSimple
# from Engine import Engine
from EngineThird import Engine
from tqdm import tqdm


def count(trace_file: str, comm_file: str):
    df = pd.read_csv(trace_file, index_col=0)

    time = pd.read_csv(comm_file, index_col=0)
    time = time.fillna('')

    processes = len(df.columns) // 3

    max_time = 0
    Tseq = 0
    for j in range(processes):
        x = list(df['timestamp' + str(j)].fillna(-1))[1:]
        y = list(df['state' + str(j)].fillna(-1))[1:]
        res = []
        for i, el in enumerate(x):
            if el == -1:
                continue
            el = list(map(float, el.split('-')))
            if el[1] > max_time:
                max_time = el[1]
            if y[i] == 'Solve':
                Tseq += el[1] - el[0]
            el.append(y[i])
            res.append(el)

    acceleration = Tseq / max_time
    efficiency = acceleration / processes
    return acceleration, efficiency

res = []
for prc in [3, 5, 10, 15, 20]:
    max_acc = 0
    arg = 0
    for rg in tqdm(range(1, prc*prc)):
        am = 100
        suma = (0, 0)
        for i in range(am):
            try:
                # eng = EngineSimple.Engine(proc_amount=3, max_depth=6)
                eng = Engine(proc_amount=prc, max_depth=prc * 2, arg=arg)
                eng.run()
            except Exception as e:
                # print(e)
                # break
                continue
            cur = count('Trace.csv', 'Communication.csv')
            suma = tuple(map(sum, zip(suma, cur)))
        acc_average = suma[0] / am
        eff_average = suma[1] / am
        if acc_average > max_acc:
            max_acc = acc_average
            arg = rg
    res.append(arg)
print(res)
