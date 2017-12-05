import percolation
import path
import misc
import configuration
import run
import pickle


class ResultsFromYoavRun:

    def __init__(self, cheerio_path, result, cube_density, simulation_variables_dic):
        self.cheerio_path = path.MotionPath(cheerio_path)
        self.result = result
        self.cube_density = cube_density
        self.simulation_variables_dic = simulation_variables_dic

if __name__ == '__main__':
    number_of_mazes_per_density = 800
    cube_densities = [100, 150, 200, 225, 250, 275, 300, 400]
    #cube_densities = [400]
    seed_lists = [[seed for seed in misc.yield_rand(number_of_mazes_per_density)] for i in range(
                  len(cube_densities))]
    SimResults = []
    # sigma = 0.35
    max_steps = 5000
    # rolling = True
    persistence_distance = 3
    for cube_density, seed_list in zip(cube_densities, seed_lists):
        for seed in enumerate(seed_list):
                print('cube density =  ' + str(cube_density) + ', seed =  '
                      + str(seed[1]) + ', count = ' + str(seed[0]))
                current_cfg = configuration.Configuration(num_stones=cube_density, seed=seed[1],
                                                          border=False)
                # taking the bias sigma to equal 0.35, from mail named "Simulations" dated 6/12/16
                # simulation_variables_dic = {'seed': seed[1], 'sigma': sigma, 'rolling': rolling,
                #                             'persistence_dist': persistence_distance,
                #                             'max_steps': max_steps}
                simulation_variables_dic = {'seed': seed[1],
                                            'persistence_dist': persistence_distance,
                                            'max_steps': max_steps}
                current_runner = run.SimulationRunner3(current_cfg, **simulation_variables_dic)
                cheerios_this_run, result_this_run = run.Run(current_runner).run()
                SimResults.append(ResultsFromYoavRun(cheerios_this_run, result_this_run,
                                                     cube_density, simulation_variables_dic))

                # percolation.run_movie(current_cfg, current_runner, repeat=True)

    filename = 'YoavSimulationResults_for_box_analysis/aviram_PersistenceDistance_' \
               + str(persistence_distance).replace('.', 'p') + '.pickle'

    with open(filename, 'wb') as handle:
        pickle.dump(SimResults, handle, protocol=pickle.HIGHEST_PROTOCOL)
