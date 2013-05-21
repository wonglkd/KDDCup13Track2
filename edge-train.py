#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier
from common import *
import argparse
from features import FeaturesGenerator
import csv
import cPickle as pickle
import numpy as np
import scipy as sp

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('trainfile', nargs='?', default='data/train.csv')
	parser.add_argument('outfile', nargs='?', default='generated/model.pickle')
	args = parser.parse_args()

	randseed = 2048
	n_trees = 50
	min_samples_split = 4 #2 #10
	n_jobs = -1 # -1 = no. of cores on machine

 	fg = FeaturesGenerator()

	print_err("Loading training dataset and getting features")
 	X, Y = [], []
 	feat_indices = fg.fields[2:]
 	reader = csv.reader(skip_comments(open(args.trainfile, 'rb')))
 	for i, line in enumerate(reader):
 		line[:3] = map(int, line[:3])
 		f = fg.getFeatures(line[1], line[2])
 		X.append([f[fi] for fi in feat_indices])
 		Y.append(line[0])
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')

	X = np.array(X)
	affil_ind = feat_indices.index('affil_sharedidf')
 	affil_median = sp.stats.nanmedian(X[:, affil_ind])
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = affil_median
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = 0.
	X[np.isnan(X)] = 0.

	clf = RandomForestClassifier(n_estimators=n_trees, 
								 verbose=2,
								 n_jobs=n_jobs,
								 oob_score=True,
								 min_samples_split=min_samples_split,
								 compute_importances=True,
								 random_state=randseed)
	print_err("Fitting data")
	clf.fit(X, Y)

	print_err("OOB Score (CV):", clf.oob_score_)
# 	print_err("Test Score:", clf.score(X, Y))

	print_err("Saving model")
	pickle.dump((clf, feat_indices, affil_median), open(args.outfile, 'wb'), pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
	main()