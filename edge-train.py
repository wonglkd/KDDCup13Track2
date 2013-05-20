#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier
from common import *
import argparse
from features import FeaturesGenerator
import csv
import cPickle as pickle

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('trainfile', nargs='?', default='data/train.csv')
	parser.add_argument('outfile', nargs='?', default='generated/model.pickle')
	args = parser.parse_args()

	randseed = 2048
	n_trees = 50
	min_samples_split = 3 #2 #10
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
 			print_err(i+1, ' rows done')

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
	print_err("Test Score:", clf.score(X, Y))

	print_err("Saving model")
	pickle.dump((clf, feat_indices), open(args.outfile, 'wb'))


if __name__ == "__main__":
	main()