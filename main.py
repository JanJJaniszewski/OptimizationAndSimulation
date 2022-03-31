from classes import *

if __name__ == '__main__':
    # pool object with number of element
    inputs = [Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation()]
    with multiprocessing.Pool(processes=6) as pool:
        outputs = pool.map(run_updates, inputs)

    pd.concat(outputs[0].results)
