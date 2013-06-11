#!/usr/bin/env python
# Given two submission formats (one gold std, evaluate it)
from common import *
import argparse
import csv
import numpy as np
from pprint import pprint
from pandas import DataFrame

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('goldstd', default='generated/goldstd-submit.csv')
	parser.add_argument('submitfile', nargs='+')
	parser.add_argument('-v', '--verbose', action='store_true')
	args = parser.parse_args()

	submitted_scores = {
		'20130606-0200/combined_716eef6_kruskal': 0.96272,
		'20130605-1300/combined_716eef6_kruskal': 0.96276,
		'20130603-2400_best/combined_716eef6': 0.96452,
		'20130606-2253/combined_kruskal': 0.96227,
		'20130606-2253/combined_hc_min': 0.96006,
		'20130607/combined_kruskal': 0.96227,
		'20130607-2330/combined_716eef6_kruskal': 0.96057,
		'20130609-0220/combined_kruskal': 0.95850,
		'20130609-0251/combined_kruskal': 0.95990,
		'20130609-1900/combined_gbm_hc': 0.95959,
		'20130609-1900/combined_gbm_kruskal': 0.96007,
		'best': 0.96291,
		'best-2nd-0.8': 0.96286
	}

	goldstd = {}

	with open(args.goldstd) as f:
		reader = csv.reader(f)
		reader.next()
		for line in reader:
			line[0] = int(line[0])
			line[1] = map(int, line[1].split())
			goldstd[line[0]] = set(line[1])

	results = {}

	for filename in args.submitfile:
		scores = []
		no_of_clusters = 0
		no_of_authors_in_clusters = 0
		try:
			with open(filename) as f:
				reader = csv.reader(f)
				reader.next()
				for line in reader:
					line[0] = int(line[0])
					line[1] = map(int, line[1].split())
					is_first = bool(line[0] == min(line[1]))
					if len(line[1]) > 1:
						no_of_authors_in_clusters += 1
						if is_first:
							no_of_clusters += 1
					if line[0] in goldstd:
						tp = len(goldstd[line[0]] & set(line[1]))
						fp = len(line[1]) - tp
						fn = len(goldstd[line[0]]) - tp
						recall = tp / float(tp + fn)
						precision = tp / float(tp + fp)
						if tp == 0:
							f1 = 0.
						else:
							f1 = 2. * recall * precision / (recall + precision)
						scores.append((f1, precision, recall, tp, fp, fn, line[0], is_first))
		except IOError:
			continue
		scores = sorted(scores, reverse=True)
# 		print_err("No of clusters:", no_of_clusters)
# 		print_err("No of authors in clusters:", no_of_authors_in_clusters)
		print_err('File:', filename)
		if args.verbose:
			print 'File:', filename
			print 'F1,Precision,Recall;Node ID'
			for line in scores:
				if line[0] != 1 and line[7]:
					print ','.join(map('{:g}'.format, line[:6])) + ';{:}'.format(line[6])
		scores = np.array(scores)
# 		print_err('F1', 'Precision', 'Recall', 'TP', 'FP', 'FN')
# 		print_err(np.mean(scores[:,:6], axis=0))
# 		print_err('TP', 'FP', 'FN')
# 		print_err(np.sum(scores[:,3:6], axis=0))
		submitid = filename.replace("-submit.csv", '').replace('generated/','')
		results[submitid] = [submitted_scores.get(submitid, np.nan), no_of_clusters, no_of_authors_in_clusters] + np.mean(scores[:,:6], axis=0).tolist() + np.sum(scores[:,3:6], axis=0).tolist()
	cols = ['result', 'clusters', 'authors', 'F1', 'P', 'R', 'TP_avg', 'FP_avg', 'FN_avg', 'TP_cnt', 'FP_cnt', 'FN_cnt']
	print(DataFrame(results, index=cols).T.to_string())
	

if __name__ == "__main__":
	main()