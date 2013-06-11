#!/usr/bin/env python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn import cross_validation
from sklearn.metrics import mean_squared_error, zero_one_loss
from sklearn.grid_search import GridSearchCV
from common import *
from pprint import pprint
import multiprocessing
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

def loadTrainingLabels(trainfilename, idset):
 	Y = []
 	ids = []
 	reader = csv.reader(skip_comments(open(trainfilename, 'rb')))
 	for i, line in enumerate(reader):
 		line[:3] = map(int, line[:3])
 		Y.append(line[0])
 		if (line[1], line[2]) not in idset:
 			print_err("Not found!", line[1], line[2])
 			raise Exception("Training instance not present in feature file")
 		ids.append((line[1], line[2]))
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')
 	return np.asarray(Y), ids

def grid(clf, params_grid, X, Y, folds, **kwargs):
	clf_grid = GridSearchCV(clf, params_grid, cv=folds, pre_dispatch='2*n_jobs', verbose=1, refit=True, **kwargs)
	clf_grid.fit(X, Y)
	return clf_grid

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('trainfile', nargs='?', default='data/train.csv')
	parser.add_argument('featfile', nargs='?', default='generated/train.feat')
	parser.add_argument('outfile', nargs='?', default='generated/model.pickle')
	parser.add_argument('--clf', default='rf')
	parser.add_argument('--removefeat', nargs='+', default=[])
	parser.add_argument('--cv', action='store_true')
	parser.add_argument('--folds', default=3)
	parser.add_argument('--gridsearch', action='store_true')
	parser.add_argument('--usegrid', action='store_true')
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
		
	n_jobs = min(multiprocessing.cpu_count(), 8)
	
	params = {
		# Random Forest
		'rf': {
			'max_features': 3,
			'n_estimators': 300,
			'min_samples_split': 1,
			'min_samples_leaf': 1,
		},
		# GBM
		'gbm': {
			'n_estimators': 20000,
			'learning_rate': 1e-03,
			'max_depth': 3,
		}
	}

	params_grid = {
		'rf': {
			'min_samples_split': [1, 2],
			'min_samples_leaf': [1, 2],
			'n_estimators': [130, 200, 250, 300, 500, 750, 1000, 1250], # [130, 400, 1000]
			'max_features': [3, 4, 5, 6, 7, 8, 9] # [4, 6, 9]
		},
		'gbm': {
	# 		'n_estimators': [500, 200],
	# 		'learning_rate': [1e-04],
	# 		'max_depth': [7]
			'n_estimators': [15000, 20000] + [17500],
			'learning_rate': [1e-04, 1e-03, 1e-02] + [5e-03],
			'max_depth': [7, 16] + [3, 5, 6, 8, 12, 14, 18]
		}
	}

	params_fixed = {
		'rf': {
			'random_state': 100,
			'n_jobs': n_jobs, # -1 = no. of cores on machine
			'oob_score': True,
			'verbose': 0,
			'compute_importances': True
		},
		'gbm': {
			'min_samples_split': 1,
			'min_samples_leaf': 2,
			'subsample': 0.5,
			'verbose': 0
		}
	}

	for k, v in params_fixed.iteritems():
		params[k].update(v)

	if args.usegrid or args.gridsearch:
		print params_grid[args.clf]
	else:
		print params[args.clf]
	
	X_ids, X = feat.load_features(args.featfile)
	idmap = {id: i for i, id in enumerate(X_ids)}
 	feat_indices = feat.FeaturesGenerator.fields
 	feat_ind_remaining = [i for i, faid in enumerate(feat_indices) if faid not in feat_to_remove]
 	feat_indices = [v for v in feat_indices if v not in feat_to_remove]
 	X = X[:, feat_ind_remaining]

	print feat_indices

	print_err("Loading training dataset labels")
	Y, Y_ids = loadTrainingLabels(args.trainfile, set(X_ids))
	training_indices = [idmap[id] for id in Y_ids]
	X = X[training_indices]

	# Filling in missing values
# 	affil_ind = feat_indices.index('affil_sharedidf')
#  	affil_median = sp.stats.nanmedian(X[:, affil_ind])
	affil_median = 0
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = affil_median
# 	X[np.isnan(X[:, affil_ind]), affil_ind] = 0.
	X[np.isnan(X)] = 4.

	if args.clf == 'rf':
		clf = RandomForestClassifier()
	elif args.clf == 'gbm':
		clf = GradientBoostingClassifier()
	clf.set_params(**params[args.clf])
	
	if args.usegrid or args.gridsearch:
		print_err("Running grid search for best parameters")
		kwargs = {
			'n_jobs': n_jobs
		}
		if args.clf == 'rf':
			clf.set_params(n_jobs=1)
		elif args.clf == 'gbm':
			kwargs['loss_func'] = zero_one_loss
		clf_grid = grid(clf, params_grid[args.clf], X, Y, folds=args.folds, **kwargs)

		pprint(clf_grid.grid_scores_)
		print(clf_grid.best_score_)
		print(clf_grid.best_params_)
		if args.usegrid:
			clf = clf_grid.best_estimator_
	elif args.cv:
		print_err("Running cross-validation")
		m_cv(clf, X, Y, args.folds)

	if not args.cv and (not args.gridsearch or args.usegrid):
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