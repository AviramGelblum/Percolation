import pickle
from BoxesSimulation import SimulationResults  # for pickle import
import configuration

if __name__ == "__main__":
    which = 'sim_example'
    # which = 'sums_vs_scale'
    # which = 'boxplot'
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    # number_of_iterations = 50
    number_of_iterations = 75
    # cube_counts = [100, 200, 225, 250, 275, 300]
    cube_counts = [100, 150,  200, 225, 250, 275, 300, 400]

    # maze_base = ''
    maze_base = '_Simulated_Cubes'

    # simtype = 'QuenchedSimulationResults'
    # simtype='SimulationResults'
    simtype = 'QuenchedMidBiasSimulationResults'
    if which == 'sim_example':
        tilescale = 1
        results_pickle_file_name = 'Pickle Files/' + simtype + maze_base + '_Scale_' \
                                   + str(tilescale) + '_iterations_' + str(number_of_iterations) \
                                   + '.pickle'
        with open(results_pickle_file_name, 'rb') as handle:
            ResultsObject = pickle.load(handle)[0]
        iteration = 0
        resobj = ResultsObject[iteration]
        save_location = 'BoxSimulation Results/' + simtype + maze_base + '_scale_' + str(
            tilescale) + '_iteration_' + str(iteration+1)
        if maze_base:
            resobj.draw_simulation_run(configuration.Configuration(
                seed=resobj.seed[0], num_stones=resobj.number_of_cubes[0], border=False),
                                       save=True, save_location=save_location)
        else:
            resobj.draw_simulation_run(configuration.Configuration(
                file_name=resobj.video_number[0], border=False),
                                        save=True, save_location=save_location)

    elif which == 'sums_vs_scale':
        mean_total_lengths, mean_total_times, fractions_front = ({cube: [] for cube in cube_counts}
                                                                 for i in range(3))
        attribute_list = ['scale', 'number_of_cubes']
        for tilescale in scale_list:
            results_pickle_file_name = 'Pickle Files/' + simtype + maze_base + '_Scale_' + \
                                       str(tilescale) + '_iterations_' + str(number_of_iterations)\
                                       + '.pickle'
            with open(results_pickle_file_name, 'rb') as handle:
                ResultsObject = pickle.load(handle)[0]
            for cube_count in cube_counts:
                attribute_value_list = [tilescale, cube_count]

                relevant_runs = ResultsObject.get_relevant_runs(attribute_list,
                                                                attribute_value_list)
                fraction_front, mean_total_length, mean_total_time = \
                    ResultsObject.compute_mean_and_median_sums(relevant_runs)[:3]
                mean_total_lengths[cube_count].append(mean_total_length)
                mean_total_times[cube_count].append(mean_total_time)
                fractions_front[cube_count].append(fraction_front)

        for cube_count in cube_counts:
            SimulationResults.plot_means_vs_scale(mean_total_lengths[cube_count], mean_total_times[
                                                  cube_count], fractions_front[cube_count],
                                                  scale_list, cube_count, save=True,
                save_location='BoxSimulation Results/' + simtype + maze_base + '_stats_vs_scale')

    elif which == 'boxplot':
        relevant_runs_dict = {cube: [] for cube in cube_counts}

        attribute_list = ['scale', 'number_of_cubes']
        for tilescale in scale_list:
            results_pickle_file_name = 'Pickle Files/' + simtype + maze_base + '_Scale_' + str(
                tilescale) + '_iterations_' + str(number_of_iterations) + '.pickle'
            with open(results_pickle_file_name, 'rb') as handle:
                ResultsObject = pickle.load(handle)[0]
            for cube_count in cube_counts:
                attribute_value_list = [tilescale, cube_count]
                relevant_runs = ResultsObject.get_relevant_runs(attribute_list,
                                                                attribute_value_list)
                relevant_runs_dict[cube_count].append(relevant_runs)

        for cube_count in cube_counts:
            SimulationResults.plot_boxplots_vs_scale(relevant_runs_dict[cube_count],
                    scale_list, cube_count, save=True, save_location=
                    'BoxSimulation Results/' + simtype + maze_base + '_boxplots_vs_scale')

    print('finished!')

