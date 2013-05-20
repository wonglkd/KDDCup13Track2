#!/usr/bin/env python
from common import *
import cPickle as pickle
import numpy as np
import pylab as pl
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('modelfile', nargs='?', default='generated/model.pickle')
	args = parser.parse_args()
	
	clf, feat_indices = pickle.load(open(args.modelfile, 'rb'))
	
	print_err("OOB Score (CV):", clf.oob_score_)

	importances = clf.feature_importances_
	std = np.std([tree.feature_importances_ for tree in clf.estimators_],
				 axis=0)
	indices = np.argsort(importances)[::-1]

	# Print the feature ranking
	print_err("Feature ranking:")
	for f, indf in enumerate(indices):
		print_err("{0}. feature {1}: {2} ({3})".format(f + 1, indf, feat_indices[indf], importances[indf]))

if __name__ == "__main__":
	main()