import pickle
import concurrent.futures
from BoxesSimulation import SimulationResults, TiledGridSimulation, \
    QuenchedGridTrailBiasSimulation, \
    QuenchedGridTrailBiasSimulationLoopStuck, RegularUniformDensitySimulation, \
    QuenchedGridSimulation, QuenchedUniformDensitySimulation
from BoxAnalysis import BoxAnalysis, DistributionResults
import misc
import numpy as np
import parallel

def sim_func(tilescale):
    number_of_iterations = 50
    loadloc = 'middle'
    rolling = True
    sigma = 0.35
    persistence_distance = 0
    # pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    distribution_results_filename_root = 'Pickle Files/SimulationBoxDistribution_' + loadloc + \
                                         '_rolling_' + str(rolling) + '_sigma_' + str(
                                         sigma).replace('.', 'p') + '_PersistenceDistance_' \
                                         + str(persistence_distance).replace('.', 'p') + '_scale_'
    # results_pickle_file_name = 'Pickle Files/SimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_' + str(
    #     number_of_iterations)+'iterations'
    cube_densities = [100, 150, 200, 225, 250, 275, 300, 400]
    # number_of_mazes_per_density = 30
    # bias_values = ('constant', 0.75)
    # bias_values = ('hooke', 0.8, 10, 0.3)
    # seed_lists = [[seed for seed in misc.yield_rand(number_of_mazes_per_density)] for i in range(
    #              len(cube_densities))]
    for cube_density in cube_densities:
        for seed in misc.seed_from_txt_files(cube_density):
        # for video_number in misc.file_names_by_density(cube_density):
        #       print('scale = ' + str(tilescale))

            for iteration in range(1, number_of_iterations+1):
                #print('scale = ' + str(tilescale) + ',seed = ' + seed + ',iter = '
                #      + str(iteration))
                print('scale = ' + str(tilescale) + ', seed = ' + seed + ', iteration = ' +
                      str(iteration))
                pickle_file_name = distribution_results_filename_root + str(tilescale) + \
                                   '_stucking.pickle'
                # sim = TiledGridSimulation(pickle_file_name, video_number=video_number,
                #                           tile_scale=tilescale, is_stuckable=True)
                sim = TiledGridSimulation(pickle_file_name, seed=int(seed), num_stones=cube_density,
                                          tile_scale=tilescale, is_stuckable=True)
                # sim = QuenchedGridSimulation(pickle_file_name, video_number=video_number,
                #                               tile_scale=tilescale)
                # sim = QuenchedGridTrailBiasSimulationLoopStuck(pickle_file_name, bias_values,
                #                                     seed=int(seed), num_stones=cube_density,
                #                                    tile_scale=tilescale)
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
    # results_pickle_file_name = 'Pickle ' \
    #                            'Files/QuenchedMidBiasSimulationResults_Simulated_Cubes_Scale_' \
    #                            + str(tilescale) + '_iterations_' + str(number_of_iterations) \
    #                            + '.pickle'
    results_pickle_file_name = 'Pickle Files/YoavBasedTiledSimulationResults_Scale_' \
                                + str(tilescale) + '_rolling_' + str(rolling) + '_sigma_' \
                                + str(sigma).replace('.', 'p') + '_PersistenceDistance_' \
                                + str(persistence_distance).replace('.', 'p') + '_iterations_'\
                                + str(number_of_iterations) + '.pickle'
    with open(results_pickle_file_name, 'wb') as handle:
        pickle.dump([ResultsObject, tilescale, cube_densities, number_of_iterations], handle,
                    protocol=pickle.HIGHEST_PROTOCOL)
    # ResultsObject = None


def sim_func_uniform(tilescale):
    number_of_iterations = 75
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    box_densities = np.arange(0, 1, 0.1)
    seed = None
    for box_density in box_densities:
        for iteration in range(1, number_of_iterations+1):
            seed = misc.init_rand()
            print('scale = ' + str(tilescale) + ',density = ' + str(box_density) + ',iter = '
                  + str(iteration))
            sim = QuenchedUniformDensitySimulation(pickle_file_name, box_density, seed=seed,
                                                  tile_scale=tilescale)
            load_path, load_trajectory_length, load_time, where_out = sim.run_simulation()
            try:
                ResultsObject.append(SimulationResults(load_path, load_trajectory_length,
                                                       load_time, where_out, tilescale, 0,
                                                       seed=seed, box_density=box_density))
            except NameError as e:
                if e.args[0][16:29] == 'ResultsObject':
                    ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                      load_time, where_out, tilescale, 0, seed=seed,
                                                      box_density=box_density)

                else:
                    raise
            except AttributeError:
                ResultsObject = SimulationResults(load_path, load_trajectory_length,
                                                  load_time, where_out, tilescale, 0, seed=1,
                                                  box_density=box_density)

    # results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
    #                            '_iterations_' + str(number_of_iterations) + '.pickle'
    # results_pickle_file_name = 'Pickle Files/QuenchedSimulationResults_Scale_' + str(tilescale) \
    #                            + '_iterations_' + str(number_of_iterations) + '.pickle'
    results_pickle_file_name = 'Pickle ' \
                               'Files/QuenchedUniformSimulationResults_Scale_' \
                               + str(tilescale) + '_iterations_' + str(number_of_iterations) \
                               + '.pickle'
    with open(results_pickle_file_name, 'wb') as handle:
        pickle.dump([ResultsObject, tilescale, box_densities, number_of_iterations], handle,
                    protocol=pickle.HIGHEST_PROTOCOL)
    # ResultsObject = None


# def main_func(par):
#     if par:
#         scale_list = [1, 2, 4, 6, 8, 10, 15]
#         with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
#             executor.map(sim_func, scale_list)
#     else:
#         # sim_func(1)  # for debug purposes
#         sim_func(2)

if __name__ == '__main__':
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    parcomp = parallel.ParallelComputing(sim_func, scale_list, 3)
    parcomp.run()
    #parcomp.run_not_parallel()
