import pickle
import configuration
from BoxAnalysis import BoxAnalysis as BoxAnalysis
from BoxAnalysis import DistributionResults
from Percolation_main_run import ResultsFromYoavRun
import math
import numpy as np
import parallel


def add_stuck_probabilities():
    loadloc = 'middle'
    sigma = 0.35
    # max_steps = 5000
    rolling = True
    persistence_distance = 6
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    Yoav_results_filename = 'YoavSimulationResults_for_box_analysis/rolling_' + str(rolling) + \
                            '_sigma_' + str(sigma).replace('.', 'p') + '_PersistenceDistance_' \
                            + str(persistence_distance).replace('.', 'p') + '.pickle'
    distribution_results_filename_root = 'Pickle Files/SimulationBoxDistribution_' + loadloc + \
        '_rolling_' + str(rolling) + '_sigma_' + str(sigma).replace('.', 'p') + '_PersistenceDistance_'\
        + str(persistence_distance).replace('.', 'p') + '_scale_'
    with open(Yoav_results_filename, 'rb') as handle:
        YoavSimResults_t = pickle.load(handle)
    for scale_size in scale_list:
        YoavSimResults_timeout = (x for x in enumerate(YoavSimResults_t[3200:3220]) if
                                  x[1].cheerio_path.points and not x[1].result)
        free_densities = []
        stucking_densities = []
        for sim in YoavSimResults_timeout:
            print('scale = ' + str(scale_size) + ', sim number = ' + str(sim[0]))
            current_cfg = configuration.Configuration(num_stones=sim[1].cube_density,
                                                      seed=sim[1].simulation_variables_dic['seed'],
                                                      border=False)
            reversed_path = sim[1].cheerio_path.points.__reversed__()
            max_steps = len(sim[1].cheerio_path.points)
            last_before_stuck = next((point[0] for point in enumerate(reversed_path)
                                     if sim[1].cheerio_path.points[-1].x-point[1].x
                                     > current_cfg.cheerio_radius*2), max_steps)
            last_before_stuck = max_steps - last_before_stuck
            if last_before_stuck:
                rel_points = sim[1].cheerio_path.points[:last_before_stuck]
                NewBox = BoxAnalysis(scale_size, current_cfg, loadloc,
                                     given_path=rel_points)
                NewBox.boxes_stats()
                densities = [box_res[0] for box_res in NewBox.AnalysisResult]
                # densities = [math.floor(current_density * 10) / 10 for current_density in densities]
                free_densities.extend(densities)

            box = BoxAnalysis.create_box(sim[1].cheerio_path.points[-1], loadloc, scale_size *
                                         current_cfg.cheerio_radius)
            stucking_density = current_cfg.stones.box_density(current_cfg.cheerio_radius, box)
            stucking_densities.append(stucking_density)

        edges = np.arange(0, 1.1, 0.1)
        stuck_hist = np.histogram(np.array(stucking_densities), edges)
        not_stuck_hist = np.histogram(np.array(free_densities), edges)

        with open(distribution_results_filename_root + str(scale_size) + '.pickle', 'rb') as handle:
                distribution_list = pickle.load(handle)

        finished_free_hist = []
        for density_distributions in distribution_list:
            free = sum([len(direction_distribution) for direction_distribution in
                        density_distributions])
            finished_free_hist.append(free)

        all_not_stuck = not_stuck_hist[0] + finished_free_hist
        stucking_probabilities = stuck_hist[0]/(all_not_stuck+stuck_hist[0])

        # Since I was dumb enough to make distribution_list a list of tuples, they are immutable and
        # need to be reassigned to add the stucking probabilites instead of just appending
        count = 0
        for direction_distributions, stucking_probability in zip(distribution_list,
                                                                 stucking_probabilities):
            distribution_list[count] = direction_distributions + (stucking_probability,)
            count += 1

        with open(distribution_results_filename_root + str(scale_size) + '_stucking.pickle',
                  'wb') as handle:
            pickle.dump(distribution_list, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    # scale_list = [1, 2, 4, 6, 8, 10, 15]
    # parcomp = parallel.ParallelComputing(add_stuck_probabilities, scale_list, 2)
    # #parcomp.run()
    # parcomp.run_not_parallel(series=True)
    add_stuck_probabilities()




