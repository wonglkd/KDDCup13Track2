#!/usr/bin/env python
# Given two submission formats (one gold std, evaluate it)
from common import *
import argparse
import csv
import numpy as np
from pprint import pprint

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('goldstd', default='generated/goldstd-submit.csv')
	parser.add_argument('submitfile', nargs='+')
	args = parser.parse_args()

	goldstd = {}

	with open(args.goldstd) as f:
		reader = csv.reader(f)
		reader.next()
		for line in reader:
			line[0] = int(line[0])
			line[1] = map(int, line[1].split())
			goldstd[line[0]] = set(line[1])

	for filename in args.submitfile:
		scores = []
		no_of_clusters = 0
		no_of_authors_in_clusters = 0
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
		scores = sorted(scores, reverse=True)
		print_err("No of clusters:", no_of_clusters)
		print_err("No of authors in clusters:", no_of_authors_in_clusters)
		print 'File:', filename
		print_err('File:', filename)
		print 'F1,Precision,Recall;Node ID'
		for line in scores:
			if line[0] != 1 and line[7]:
				print ','.join(map('{:g}'.format, line[:6])) + ';{:}'.format(line[6])
		scores = np.array(scores)
		print_err('F1', 'Precision', 'Recall', 'TP', 'FP', 'FN')
		print_err(np.mean(scores[:,:6], axis=0))
		print_err('TP', 'FP', 'FN')
		print_err(np.sum(scores[:,3:6], axis=0))

if __name__ == "__main__":
	main()