#!/usr/bin/env python
from common import *
import cPickle as pickle
import numpy as np
import pylab as pl
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('modelfile', nargs='?', default='generated/model.pickle')
	parser.add_argument('-o', '--output')
	args = parser.parse_args()

	if args.output is None:
		args.output = args.modelfile.replace('.pickle', '') + '.pdf'

	unloaded = pickle.load(open(args.modelfile, 'rb'))
	if len(unloaded) == 4:
		clf, feat_indices, feat_ind_remaining, affil_median = unloaded
	else:
		clf, feat_indices, affil_median = unloaded
		feat_ind_remaining = range(len(feat_indices))
		
	print_err("OOB Score (CV):", clf.oob_score_)

	importances = clf.feature_importances_
	try:
		std = np.std([tree.feature_importances_ for tree in clf.estimators_],
					 axis=0)
	except AttributeError:
		1
# 		print_err("No tree importances")
	indices = np.argsort(importances)[::-1]

	# Print the feature ranking
	print_err("Feature ranking:")
	for f, indf in enumerate(indices):
		print_err("{0}. feature {1}: {2} ({3})".format(f + 1, indf, feat_indices[indf], importances[indf]))

	# Plot the feature importances of the forest
	pl.figure()
	pl.title("Feature importances")
	pl.bar(range(len(indices)), importances[indices],
		   color="r", yerr=std[indices], align="center")
	pl.xticks(range(len(indices)), [feat_indices[v] for v in indices], rotation=45, horizontalalignment='right')
	pl.xlim([-1, len(indices)])
	fig = pl.gcf()
	fig.subplots_adjust(bottom=0.2)
	if args.output == '-':
		pl.show()
	else:
		pl.savefig(args.output)

if __name__ == "__main__":
	main()