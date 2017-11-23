import pickle
import numpy as np
from BoxesSimulation import SimulationResults  # for pickle import
import configuration

if __name__ == "__main__":
    #which = 'sim_example'
    which = 'sums_vs_scale'
    # which = 'boxplot'
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    # number_of_iterations = 50
    number_of_iterations = 75
    # cube_counts = [100, 200, 225, 250, 275, 300]
    cube_counts = [100, 150,  200, 225, 250, 275, 300, 400]
    box_densities = np.arange(0, 1, 0.1)
    maze_base = ''
    # maze_base = '_Simulated_Cubes'

    # simtype = 'Quenched'
    # simtype = ''
    # simtype = 'QuenchedMidBias'
    simtype2 = 'RegularUniform'
    simtype = simtype2 + 'SimulationResults'
    if which == 'sim_example':
        iterations = [60+number_of_iterations*x for x in range(len(box_densities))]
        for tilescale in scale_list:
            results_pickle_file_name = 'Pickle Files/' + simtype + maze_base + '_Scale_' \
                                       + str(tilescale) + '_iterations_' + str(number_of_iterations) \
                                       + '.pickle'
            with open(results_pickle_file_name, 'rb') as handle:
                ResultsObject = pickle.load(handle)[0]
            for iteration in iterations:
                print('scale = ' + str(tilescale) + ', iter=' + str(iteration))
                resobj = ResultsObject[iteration]
                save_location = 'BoxSimulation Results/' + simtype + maze_base + '_scale_' + str(
                    tilescale) + '_iteration_' + str(iteration+1)
                if maze_base:
                    resobj.draw_simulation_run(configuration.Configuration(
                        seed=resobj.seed[0], num_stones=resobj.number_of_cubes[0], border=False),
                                               save=True, save_location=save_location)
                else:
                    resobj.draw_simulation_run(configuration.Configuration(
                        seed=resobj.seed[0], num_stones=0, border=False),
                                               save=True, save_location=save_location)
                    # resobj.draw_simulation_run(configuration.Configuration(
                    #     file_name=resobj.video_number[0], border=False),
                    #                             save=True, save_location=save_location)

    elif which == 'sums_vs_scale':
        if simtype2[-7:] == 'Uniform':
            mean_total_lengths, mean_total_times, fractions_front = \
                ({box_den: [] for box_den in box_densities} for i in range(3))
            attribute_list = ['scale', 'box_density']
            for tilescale in scale_list:
                results_pickle_file_name = 'Pickle Files/' + simtype + maze_base + '_Scale_' + \
                                           str(tilescale) + '_iterations_' \
                                           + str(number_of_iterations) + '.pickle'
                with open(results_pickle_file_name, 'rb') as handle:
                    ResultsObject = pickle.load(handle)[0]
                for box_den in box_densities:
                    attribute_value_list = [tilescale, box_den]
                    relevant_runs = ResultsObject.get_relevant_runs(attribute_list,
                                                                    attribute_value_list)
                    fraction_front, mean_total_length, mean_total_time = \
                        ResultsObject.compute_mean_and_median_sums(relevant_runs)[:3]
                    mean_total_lengths[box_den].append(mean_total_length)
                    mean_total_times[box_den].append(mean_total_time)
                    fractions_front[box_den].append(fraction_front)

            for box_den in box_densities:
                box_den_str = str(box_den)
                box_den_str = box_den_str.replace('.', 'p')
                SimulationResults.plot_means_vs_scale(mean_total_lengths[box_den],
                                                      mean_total_times[box_den],
                                                      fractions_front[box_den],
                                                      scale_list, box_den_str, save=True,
                save_location='BoxSimulation Results/' + simtype + maze_base + '_stats_vs_scale')
        else:
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

