#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn import cross_validation
from common import *
import argparse
import features as feat
import csv
import cPickle as pickle
import numpy as np
import scipy as sp


def llfun(act, pred):
	epsilon = 1e-15
	pred = sp.maximum(epsilon, pred)
	pred = sp.minimum(1-epsilon, pred)
	ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
	ll = ll * -1.0/len(act)
	return ll

def m_cv(clf, X, Y, kfolds):
	cv = cross_validation.KFold(len(X), n_folds=kfolds, indices=True)
	results = []
	oob_scores = []
	for i, (traincv, testcv) in enumerate(cv):
		print_err("Fold {:} of {:}".format(i+1, kfolds))
		probas = clf.fit(X[traincv], Y[traincv]).predict_proba(X[testcv])
		lscore = llfun(Y[testcv], [x[1] for x in probas])
		print_err("Error: {:g}, OOB: {:g}".format(lscore, clf.oob_score_))
		results.append(lscore)
		oob_scores.append(clf.oob_score_)
	score = np.array(results).mean()
	oob = np.array(oob_scores).mean()
	print_err("CV Error: {:g}, Mean OOB: {:g}".format(score, oob))
	return score

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('trainfile', nargs='?', default='data/train.csv')
	parser.add_argument('featfile', nargs='?', default='generated/train.feat')
	parser.add_argument('outfile', nargs='?', default='generated/model.pickle')
	parser.add_argument('--cv', action='store_true')
	parser.add_argument('--folds', default=5)
	args = parser.parse_args()

	params = {}
	# Random Forest
	params['rf'] = {
		'random_state': 100,
 		'n_estimators': 1000, #130
 		'max_features': 'auto', # 6
		'min_samples_split': 1, #3 #10
		'n_jobs': -1, # -1 = no. of cores on machine
		'verbose': 0,
		'oob_score': True,
		'min_samples_leaf': 1,
		'compute_importances': True
	}

	# GBM
	params['gbm'] = {
		'n_estimators': 15000,
		'learning_rate': 0.01,
		'max_depth': 16,
		'min_samples_split': 2,
		'subsample': 0.5,
		'verbose': 1,
		'min_samples_leaf': 1
	}

	ids, X = feat.load_features(args.featfile)

	print_err("Loading training dataset labels")
 	Y = []
 	feat_indices = feat.FeaturesGenerator.fields
 	reader = csv.reader(skip_comments(open(args.trainfile, 'rb')))
 	for i, (line, (id1, id2)) in enumerate(zip(reader, ids)):
 		line[:3] = map(int, line[:3])
 		Y.append(line[0])
 		if line[1] != id1 or line[2] != id2:
 			print_err("Mismatch!", line[1], line[2], id1, id2)
 			raise Exception("Mismatch of train.csv and train.feat")
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')
 	Y = np.array(Y)

	affil_ind = feat_indices.index('affil_sharedidf')
 	affil_median = sp.stats.nanmedian(X[:, affil_ind])
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = affil_median
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = 0.
	X[np.isnan(X)] = 0.

	clf = RandomForestClassifier(**params['rf'])
# 	clf = GradientBoostingClassifier(**params['gbm'])

	if args.cv:
		print_err("Running cross-validation")
		m_cv(clf, X, Y, args.folds)
	else:
		print_err("Fitting data for training")
		clf.fit(X, Y)
		# for GBM
		if hasattr(clf, 'train_score_'):
	  		print_err("Train Score:", clf.train_score_[-1])
		print_err("OOB Score (CV-estimate):", clf.oob_score_)

		print_err("Saving trained model")
		pickle.dump((clf, feat_indices, affil_median), open(args.outfile, 'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	main()