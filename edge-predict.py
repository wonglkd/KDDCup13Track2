#!/usr/bin/env python
from common import *
import argparse
import cPickle as pickle
import csv
import numpy as np
import features as feat

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('featurefile')
	parser.add_argument('modelfile', nargs='?', default='generated/model.pickle')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.featurefile.replace('.feat','') + '.prob'

	print_err("Loading saved classifier")	
	clf, feat_indices, feat_ind_remaining, affil_median = pickle.load(open(args.modelfile, 'rb'))

	ids, X = feat.load_features(args.featurefile)
 	X = X[:, feat_ind_remaining]
# 	affil_ind = feat_indices.index('affil_sharedidf')
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = affil_median
 	X[np.isnan(X)] = 0.

	print_err("Making predictions")
	predictions = clf.predict_proba(X)[:,1]
#	predictions = clf.predict(X)
	predictions = list(predictions)

	print_err("Writing predictions")
	writer = csv.writer(open(args.outfile, 'wb'))
	for i, ((id1, id2), prob) in enumerate(zip(ids, predictions)):
		writer.writerow([id1, id2, '{:g}'.format(prob)])
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')

if __name__=="__main__":
    main()