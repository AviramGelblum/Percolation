from BoxAnalysis import BoxAnalysis as BoxAnalysis
from Percolation_main_run import ResultsFromYoavRun
import configuration
import pickle
from global_vars import root as root

if __name__ == '__main__':
    #scale_list = [1, 2, 4, 6, 8, 10, 15]
    scale_list = [5]
    # maxfiles = 3
    # filenum = 0
    loadloc = 'middle'
    sigma = 0.35
    max_steps = 5000
    rolling = True
    persistence_distance = 6
    Yoav_results_filename = root + 'YoavSimulationResults_for_box_analysis/rolling_' + str(rolling)\
                            + '_sigma_' + str(sigma).replace('.', 'p') + '_PersistenceDistance_' \
                            + str(persistence_distance).replace('.', 'p') + '.pickle'
    with open(Yoav_results_filename, 'rb') as handle:
        YoavSimResults_t = pickle.load(handle)

    for scale_size in scale_list:
        single_scale_analysis_list = []
        YoavSimResults = (x for x in enumerate(YoavSimResults_t) if x[1].cheerio_path.points
                          and x[1].result and x[1].cheerio_path.points[-1].x > 0.99)
        for sim in YoavSimResults:
            print('scale = ' + str(scale_size) + ', sim number = ' + str(sim[0]))
            current_cfg = configuration.Configuration(num_stones=sim[1].cube_density,
                                                      seed=sim[1].simulation_variables_dic['seed'],
                                                      border=False)
            NewBox = BoxAnalysis(scale_size, current_cfg, loadloc, given_path=sim[1].cheerio_path.points)
            NewBox.boxes_stats()
            single_scale_analysis_list.extend(NewBox.AnalysisResult)
            # filenum += 1
            # if filenum == maxfiles:
            #     break
            # run_movie(current_cfg, current_runner, only_save=True)
        distribution_list = BoxAnalysis.compute_statistics(single_scale_analysis_list, scale_size)
        filename = root + 'Pickle Files/SimulationBoxDistribution_' + loadloc + '_rolling_'\
                   + str(rolling) + '_sigma_' + str(sigma).replace('.', 'p') + \
                   '_PersistenceDistance_' + str(persistence_distance).replace('.', 'p') \
                   + '_scale_' + str(scale_size) + '.pickle'
        with open(filename, 'wb') as handle:
            pickle.dump(distribution_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
