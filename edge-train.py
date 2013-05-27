#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from common import *
import argparse
import features as feat
import csv
import cPickle as pickle
import numpy as np
import scipy as sp

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('trainfile', nargs='?', default='data/train.csv')
	parser.add_argument('featfile', nargs='?', default='generated/train.feat')
	parser.add_argument('outfile', nargs='?', default='generated/model.pickle')
	args = parser.parse_args()

	randseed = 100
	n_trees = 130
	min_samples_split = 1 #3 #10
	n_jobs = -1 # -1 = no. of cores on machine

# 	n_trees = 500


	print_err("Loading features")
	ids, X = feat.load_features(args.featfile)

	print_err("Loading training dataset labels")
 	Y = []
 	feat_indices = feat.FeaturesGenerator.fields[2:]
 	reader = csv.reader(skip_comments(open(args.trainfile, 'rb')))
 	for i, (line, (id1, id2)) in enumerate(zip(reader, ids)):
 		line[:3] = map(int, line[:3])
 		Y.append(line[0])
 		if line[1] != id1 or line[2] != id2:
 			print_err("Mismatch!", line[1], line[2], id1, id2)
 			raise Exception("Mismatch of train.csv and train.feat")
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')

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
								 min_samples_leaf=1,
								 compute_importances=True,
								 random_state=randseed)
# 	clf = GradientBoostingClassifier(n_estimators=n_trees,
# 									 verbose=2,
# 									 learning_rate=0.1,
# 									 max_depth=3,
# 									 min_samples_split=min_samples_split,
# 									 min_samples_leaf=1,
# 									 subsample=0.7)
	
	print_err("Fitting data")
	clf.fit(X, Y)

#  	print_err("Train Score:", clf.train_score_)
	print_err("OOB Score (CV):", clf.oob_score_)

	print_err("Saving model")
	pickle.dump((clf, feat_indices, affil_median), open(args.outfile, 'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	main()