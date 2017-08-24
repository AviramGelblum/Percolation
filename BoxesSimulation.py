import pickle
from BoxAnalysis import DistributionResults

loadloc = 'middle'
filename = 'Pickle Files/ExperimentalBoxDistribution' + loadloc + '.pickle'
with open(filename, 'rb') as handle:
    distribution_list = pickle.load(handle)




exit(0)
