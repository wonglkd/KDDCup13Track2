#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn import cross_validation
from sklearn.metrics import mean_squared_error
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
	cv = cross_validation.StratifiedKFold(Y, n_folds=kfolds, indices=True)
	results_ll = []
	results_rms = []
	oob_scores = []
	for i, (traincv, testcv) in enumerate(cv):
		print_err("Fold {:} of {:}".format(i+1, kfolds))
		pred = clf.fit(X[traincv], Y[traincv]).predict(X[testcv])
#		probas = clf.fit(X[traincv], Y[traincv]).predict_proba(X[testcv])
#		pred = [x[1] for x in probas]
 		lscore_ll = llfun(Y[testcv], pred)
		lscore_rms = mean_squared_error(Y[testcv], pred)
		try:
			print_err("LL E: {:g}, RMS E: {:g}, OOB: {:g}".format(lscore_ll, lscore_rms, clf.oob_score_))
			oob_scores.append(clf.oob_score_)
		except ValueError:
			print_err("LL E: {:g}, RMS E: {:g}".format(lscore_ll, lscore_rms))
		results_ll.append(lscore_ll)
		results_rms.append(lscore_rms)
	score_ll = np.array(results_ll).mean()
	score_rms = np.array(results_rms).mean()
	if oob_scores:
		oob = np.array(oob_scores).mean()
		print_err("CV (LL): {:g}, CV (RMS): {:g}, Mean OOB: {:g}".format(score_ll, score_rms, oob))
	else:
		print_err("CV (LL): {:g}, CV (RMS): {:g}".format(score_ll, score_rms))
	return score_ll

# def learning_curve(clf, X, Y, npoints=20, xstart=100):
# 	chunksize = range(xstart, len(X), (len(X) - xstart) / npoints) + [len(X)]
# 	for cs in chunksize:
# 		cv = cross_validation.StratifiedShuffleSplit(Y, n_iter=1, train_size=cs)

def loadTrainingLabels(trainfilename, ids):
 	Y = []
 	reader = csv.reader(skip_comments(open(trainfilename, 'rb')))
 	for i, (line, (id1, id2)) in enumerate(zip(reader, ids)):
 		line[:3] = map(int, line[:3])
 		Y.append(line[0])
 		if line[1] != id1 or line[2] != id2:
 			print_err("Mismatch!", line[1], line[2], id1, id2)
 			raise Exception("Mismatch of train.csv and train.feat")
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')
 	return np.asarray(Y)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('trainfile', nargs='?', default='data/train.csv')
	parser.add_argument('featfile', nargs='?', default='generated/train.feat')
	parser.add_argument('outfile', nargs='?', default='generated/model.pickle')
	parser.add_argument('--clf', default='rf')
	parser.add_argument('--removefeat', nargs='+', default=[])
	parser.add_argument('--cv', action='store_true')
	parser.add_argument('--folds', default=5)
	args = parser.parse_args()

	if args.removefeat:
		feat_to_remove = args.removefeat
	else:
		feat_to_remove = [
# 			'conferences',
# 			'journals',
# 			'affiliations',
# 			'jaro_distance'
		]
	
	params = {}
	# Random Forest
	params['rf'] = {
 		'max_features': 'auto', # 6
 		'n_estimators': 400, #130
# 		'n_estimators': 1000, #130
		'min_samples_split': 1, #3 #10
		'min_samples_leaf': 2,
		'random_state': 100,
		'n_jobs': 8, # -1 = no. of cores on machine
		'oob_score': True,
		'verbose': 0,
		'compute_importances': True
	}

	# GBM
	params['gbm'] = {
		'n_estimators': 20000,
#		'n_estimators': 15000,
		'learning_rate': 1e-04,
		'max_depth': 7,
#		'max_depth': 16,
		'min_samples_split': 1,
		'min_samples_leaf': 2,
		'subsample': 0.5,
		'verbose': 0
	}
	
	print params[args.clf]

	ids, X = feat.load_features(args.featfile)
 	feat_indices = feat.FeaturesGenerator.fields
 	feat_ind_remaining = [i for i, faid in enumerate(feat_indices) if faid not in feat_to_remove]
 	feat_indices = [v for v in feat_indices if v not in feat_to_remove]
 	X = X[:, feat_ind_remaining]

	print feat_indices

	print_err("Loading training dataset labels")
	Y = loadTrainingLabels(args.trainfile, ids)

	# Filling in missing values
# 	affil_ind = feat_indices.index('affil_sharedidf')
#  	affil_median = sp.stats.nanmedian(X[:, affil_ind])
	affil_median = 0
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = affil_median
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = 0.
	X[np.isnan(X)] = 0.

	if args.clf == 'rf':
		clf = RandomForestClassifier(**params['rf'])
	elif args.clf == 'gbm':
	 	clf = GradientBoostingClassifier(**params['gbm'])

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
		pickle.dump((clf, feat_indices, feat_ind_remaining, affil_median), open(args.outfile, 'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	main()