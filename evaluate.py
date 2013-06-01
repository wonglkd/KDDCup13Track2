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
		with open(filename) as f:
			reader = csv.reader(f)
			reader.next()
			for line in reader:
				line[0] = int(line[0])
				line[1] = map(int, line[1].split())
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
					is_first = bool(line[0] == min(line[1]))
					scores.append((f1, precision, recall, line[0], is_first))
		scores = sorted(scores, reverse=True)
		print 'File:', filename
		print_err('File:', filename)
		print 'F1,Precision,Recall;Node ID'
		for line in scores:
			if line[0] != 1 and line[4]:
				print ','.join(map('{:g}'.format, line[:3])) + ';{:}'.format(line[3])
#  		pprint(scores)
		scores = np.array(scores)
		print_err('F1', 'Precision', 'Recall')
		print_err(np.mean(scores[:,:3], axis=0))

if __name__ == "__main__":
	main()