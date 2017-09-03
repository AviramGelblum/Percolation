import pickle
from BoxesSimulation import SimulationResults  # for pickle import
import configuration

if __name__ == "__main__":
    which = 'sums_vs_scale'
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    number_of_iterations = 50
    cube_counts = [100, 200, 225, 250, 275, 300]

    if which == 'sim_example':
        tilescale = 1
        results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
                                   '_iterations_' + str(number_of_iterations)
        with open(results_pickle_file_name, 'rb') as handle:
            ResultsObject = pickle.load(handle)[0]
        iteration = 0
        resobj = ResultsObject[iteration]
        save_location = 'BoxSimulation Results/SimulationResults_scale_' + str(tilescale) + \
                        '_iteration_' + str(iteration+1)
        resobj.draw_results(configuration.Configuration(file_name=resobj.video_number[0],border=False),
                            save=True, save_location=save_location)
    elif which == 'sums_vs_scale':
        mean_total_lengths, mean_total_times, fractions_front = ({cube: [] for cube in cube_counts}
                                                                 for i in range(3))
        attribute_list = ['scale', 'number_of_cubes']
        for tilescale in scale_list:
            results_pickle_file_name = 'Pickle Files/SimulationResults_Scale_' + str(tilescale) + \
                                       '_iterations_' + str(number_of_iterations)
            with open(results_pickle_file_name, 'rb') as handle:
                ResultsObject = pickle.load(handle)[0]
            for cube_count in cube_counts:
                attribute_value_list = [tilescale, cube_count]
                mean_total_length, mean_total_time, fraction_front = \
                    ResultsObject.compute_mean_sums_by(attribute_list, attribute_value_list)
                mean_total_lengths[cube_count].append(mean_total_length)
                mean_total_times[cube_count].append(mean_total_time)
                fractions_front[cube_count].append(fraction_front)

        for cube_count in cube_counts:
            SimulationResults.plot_stats_vs_scale(mean_total_lengths[cube_count], mean_total_times[
                                                  cube_count], fractions_front[cube_count],
                                                  scale_list, cube_count, save=True,
                                                  save_location=
                                                  'BoxSimulation Results/stats_vs_scale')

    print('finished!')

