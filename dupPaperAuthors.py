#!/usr/bin/env python
from common import *
import csv
# import cPickle as pickle
import argparse
from collections import defaultdict
from pprint import pprint

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('paperauthorfile', default='data/PaperAuthor.csv')
	args = parser.parse_args()
	
	seen = defaultdict(int)
	
	reader = csv.reader(open(args.paperauthorfile, 'rb'))
	header = reader.next()
	for i, line in enumerate(reader):
		line[0:2] = map(int, line[0:2])
		paids = (line[0], line[1])
		seen[paids] += 1
# 		if seen[paids] == 2:
# 			print ' '.join(paids)
		if (i+1) % 50000 == 0:
			print_err(i+1)

	for k, v in seen.iteritems():
		if v > 1:
			print '{:},{:},{:}'.format(k[0], k[1], v)

if __name__ == "__main__":
	main()