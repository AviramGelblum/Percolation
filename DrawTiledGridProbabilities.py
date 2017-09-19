import pickle
import numpy as np
from BoxAnalysis import BoxAnalysis, DistributionResults
import matplotlib.pyplot as plt
import misc
import configuration


def create_dicts_template(scale_list, distribution_list, fieldarg, mean_cheerio_size):
    back_dict, front_dict, sides_dict = ({scale: [] for scale in scale_list}
                                         for i in range(3))
    for scale in scale_list:
        relevant_distributions = [item for item in distribution_list if item[0].scale == scale]
        for i in range(len(relevant_distributions)):
            if is_sequence(getattr(relevant_distributions[i][0], fieldarg)):
                try:
                    sc_resize = scale*mean_cheerio_size
                    back_dict[scale].append(np.mean(getattr(relevant_distributions[i][0],
                                                            fieldarg)) / sc_resize)
                    front_dict[scale].append(np.mean(getattr(relevant_distributions[i][1],
                                                             fieldarg)) / sc_resize)
                    sides_dict[scale].append(np.mean(getattr(relevant_distributions[i][2],
                                                             fieldarg)) / sc_resize)
                except TypeError:
                    back_dict[scale].append(None)
                    front_dict[scale].append(None)
                    sides_dict[scale].append(None)
            else:
                back_dict[scale].append(getattr(relevant_distributions[i][0], fieldarg))
                front_dict[scale].append(getattr(relevant_distributions[i][1], fieldarg))
                sides_dict[scale].append(getattr(relevant_distributions[i][2], fieldarg))

    return back_dict, front_dict, sides_dict


def draw_probabilities_etc_dicts(back_dict, front_dict, sides_dict, string_measure, title):
    density_vals = np.arange(0, 1, 0.1)
    save_loc = 'Computed Exit Distributions/' + string_measure + '_vs_density_for_constant_scale'
    for scale, back_vals, front_vals, sides_vals in misc.zipdic(back_dict, front_dict, sides_dict):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(density_vals, back_vals, lw=1.5, color='blue')
        ax.plot(density_vals, front_vals, lw=1.5, color='red')
        ax.plot(density_vals, sides_vals, lw=1.5, color='green')
        def_lst = [-0.05, -0.05]
        maxyval = max(max(is_not_none_in_list(back_vals, def_lst)), max(is_not_none_in_list(
                front_vals, def_lst)), max(is_not_none_in_list(sides_vals, def_lst))) + 0.05
        ax.legend(['Back', 'Front', 'Sides'])
        ax.set(ylim=(-0.05, maxyval), xlim=(-0.05, 0.95))
        ax.set_title(title + ', ' + 'scale =' + str(scale))
        ax.set_xlabel('Cube Density (percent filled)')
        ax.set_ylabel(string_measure)
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.showMaximized()
        fig.savefig(save_loc + '_' + str(scale), bbox_inches='tight', dpi='figure')
        plt.close(fig)


def is_not_none_in_list(lst, def_lst_if_empty):
    try:
        list_back = [val for val in lst if not np.isnan(val)]
    except TypeError:
        list_back = [val for val in lst if val is not None]

    if list_back:
        return list_back
    else:
        return def_lst_if_empty




def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


def calculate_mean_cheerio_size():
    return np.mean([configuration.Configuration(file_name=file).cheerio_radius
                    for file in misc.all_file_names()])


if __name__ == "__main__":
    scale_list = [1, 2, 4, 6, 8, 10, 15]
    loadloc = 'middle'
    pickle_file_name = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
    with open(pickle_file_name, 'rb') as handle:
        distribution_list = pickle.load(handle)
    fieldargs = ['exit_probability', 'length_distribution', 'time_distribution']
    string_measures = ['Exit probability', 'Normalized mean distance', 'Normalized mean time']
    title_string = ['Probabilities of exit directions from tile',
                    'Mean distance traveled normalized by scale',
                    'Mean time traveled normalized by scale']
    mean_cheerio_size = calculate_mean_cheerio_size()
    for field, mstring, title in zip(fieldargs, string_measures, title_string):
        back_dict, front_dict, sides_dict = create_dicts_template(scale_list, distribution_list,
                                                                  field, mean_cheerio_size)
        draw_probabilities_etc_dicts(back_dict, front_dict, sides_dict, mstring, title)
    print('finished')


