from classes import *

if __name__ == '__main__':
    # pool object with number of element
    inputs = [Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation(),
              Simulation(), Simulation(), Simulation(), Simulation(), Simulation(), Simulation()]
    with multiprocessing.Pool(processes=6) as pool:
        outputs = pool.map(run_updates, inputs)

    # Saving total results
    sim_number = [[i] * len(outputs[i].results) for i in range(0, len(inputs))]
    sim_number = [item for sublist in sim_number for item in sublist]

    total_results = pd.concat(sim.results for sim in outputs)
    total_results['simulation'] = sim_number

    # Saving total car details
    sim_number = [[i] * len(outputs[i].waiting_times) for i in range(0, len(inputs))]
    sim_number = [item for sublist in sim_number for item in sublist]

    total_waiting_times = pd.concat(sim.waiting_times for sim in outputs)
    total_waiting_times['simulation'] = sim_number

    # Saving as feather
    nowtime = "{:%Y_%m_%d}".format(datetime.datetime.now())
    ft.write_feather(total_results, f"data/multirun_results_{nowtime}.feather")
    ft.write_feather(total_waiting_times, f"data/multirun_waitingtimes_{nowtime}.feather")
