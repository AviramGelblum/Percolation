import pickle
from BoxesSimulation import SimulationResults  # for pickle import
import configuration

if __name__ == "__main__":
    tilescale = 1
    number_of_iterations = 50
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
    print('finished!')

