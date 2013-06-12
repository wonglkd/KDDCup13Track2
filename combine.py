#!/usr/bin/env python
# Given lists of edges, combine them using a measure
import argparse
from common import *
from collections import defaultdict
from scipy import stats 
import numpy as np

def combine_harmonic(lst):
	if len(lst) == 1:
		return lst[0]
	return stats.hmean(np.array(lst))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edges', nargs='+')
	parser.add_argument('-f', '--filters', nargs='*', type=float)
	parser.add_argument('-t', '--type', default='harmonic')
	args = parser.parse_args()

	comb = defaultdict(list)

	if not args.filters:
		args.filters = [0.0001] * len(args.edges)
	
	for filter_thres, filename in zip(args.filters, args.edges):
		for i, (v1, v2, prob) in readEdges_iter(filename, n=50000):
			if prob < filter_thres:
				continue
			if v1 > v2:
				v2, v1 = v1, v2
			comb[(v1, v2)].append(prob)

	for k, v in comb.iteritems():
		nv = globals()["combine_"+args.type](v)
		print "{:},{:},{:g}".format(k[0], k[1], nv) + ',' + ','.join(map('{:g}'.format, v))

if __name__ == "__main__":
	main()