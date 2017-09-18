import pickle
import numpy as np
from BoxAnalysis import BoxAnalysis, DistributionResults
import matplotlib.pyplot as plt
import misc

if __name__ == "__main__":
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    with open(pickle_file_name, 'rb') as handle:
        distribution_list = pickle.load(handle)
    back_dict, front_dict, sides_dict = ({scale: [] for scale in scale_list}
                                                             for i in range(3))
    for scale in scale_list:
        relevant_distributions = [item for item in distribution_list if item[0].scale ==scale]
        for i in range(len(relevant_distributions)):
            back_dict[scale].append(relevant_distributions[i][0].exit_probability)
            front_dict[scale].append(relevant_distributions[i][1].exit_probability)
            sides_dict[scale].append(relevant_distributions[i][2].exit_probability)

    density_vals = np.arange(0, 1, 0.1)
    save_loc = 'Computed Exit Distributions/exit_probabilities_vs_density_for_constant_scale'
    for scale, back_vals, front_vals, sides_vals in misc.zipdic(back_dict, front_dict, sides_dict):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(density_vals, back_vals, lw=1.5, color='blue')
        ax.plot(density_vals, front_vals, lw=1.5, color='red')
        ax.plot(density_vals, sides_vals, lw=1.5, color='green')
        ax.legend(['Back', 'Front', 'Sides'])
        ax.set(ylim=(-0.05, 1.05), xlim=(-0.05, 0.95))
        ax.set_title('Probabilities of exit directions from tile, ' + 'scale =' + str(scale))
        ax.set_xlabel('Cube Density (percent filled)')
        ax.set_ylabel('Exit Probability')
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.showMaximized()
        fig.savefig(save_loc + '_' + str(scale), bbox_inches='tight', dpi='figure')

