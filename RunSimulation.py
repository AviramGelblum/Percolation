import pickle
import concurrent.futures
from BoxesSimulation import SimulationResults, QuenchedGridTrailBiasSimulation, \
    QuenchedGridTrailBiasSimulationCanBeStuck
from BoxAnalysis import BoxAnalysis, DistributionResults
import misc


def sim_func(tilescale):
    number_of_iterations = 75
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    # results_pickle_file_name = 'Pickle Files/SimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    cube_densities = [100, 150, 200, 225, 250, 275, 300, 400]
    # number_of_mazes_per_density = 30
    # bias_values = ('constant', 0.75)
    bias_values = ('hooke', 0.8, 10, 0.3)
    # seed_lists = [[seed for seed in misc.yield_rand(number_of_mazes_per_density)] for i in range(
    #              len(cube_densities))]
    for cube_density in cube_densities:
        for seed in misc.seed_from_txt_files(cube_density):
            # print('scale = ' + str(tilescale))
            # print('seed = ' + str(seed))
            for iteration in range(1, number_of_iterations+1):
                print('scale = ' + str(tilescale) + ',seed = ' + seed + ',iter = '
                      + str(iteration))
                # print(iteration)
                # sim = TiledGridSimulation(pickle_file_name, video_number=video_number,
                #                           tile_scale=tilescale)
                # sim = QuenchedGridSimulation(pickle_file_name, video_number=video_number,
                #                              tile_scale=tilescale)
                sim = QuenchedGridTrailBiasSimulationCanBeStuck(pickle_file_name, bias_values,
                                                      seed=int(seed), num_stones=cube_density,
                                                      tile_scale=tilescale)
                load_path, load_trajectory_length, load_time, where_out = sim.run_simulation()
                try:
                    ResultsObject.append(SimulationResults(load_path, load_trajectory_length,
                                                           load_time, where_out, tilescale,
                                                           cube_density, seed=int(seed)))
                except NameError as e:
                    if e.args[0][16:29] == 'ResultsObject':
                        ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                          load_time, where_out, tilescale,
                                                          cube_density, seed=int(seed))
                    else:
                        raise
                except AttributeError:
                    ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                      load_time, where_out, tilescale,
                                                      cube_density, seed=int(seed))
    # results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
    #                            '_iterations_' + str(number_of_iterations) + '.pickle'
    # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_Scale_' + str(tilescale) \
    #                            + '_iterations_' + str(number_of_iterations) + '.pickle'
    results_pickle_file_name = 'Pickle ' \
                               'Files/QuenchedMidBiasSimulationResults_Simulated_Cubes_Scale_' \
                               + str(tilescale) + '_iterations_' + str(number_of_iterations) \
                               + '.pickle'
    with open(results_pickle_file_name, 'wb') as handle:
        pickle.dump([ResultsObject, tilescale, cube_densities, number_of_iterations,
                     bias_values], handle,
                    protocol=pickle.HIGHEST_PROTOCOL)
    # ResultsObject = None

def main_func(par):
    if par:
        scale_list = [2, 4, 6, 8, 10, 15]
        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
            executor.map(sim_func, scale_list)
    else:
        sim_func(1)  # for debug purposes

if __name__ == '__main__':
    main_func(False)
    #main_func(True)
