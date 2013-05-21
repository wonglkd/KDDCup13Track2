#!/usr/bin/env python
from common import *
import csv
import argparse
from unidecode import unidecode
from nameparser import HumanName
from collections import defaultdict
import cPickle as pickle

def bin_samename(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		bins[a['name']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_fFfL(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		bins[a['fFfL']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_iFfL(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
		bins[a['iFfL']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_fullparsedname(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		bins[a['fullparsedname']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_ngrams(authors, n=5):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if not a['name'].startswith('ID:'):
 			lname = a['name'].replace('.','')
	 		ngrams = zip(*[lname[i:] for i in range(n)])
			for p in ngrams:
				bins[p].add(id)
		if (i+1) % 10000 == 0:
			print_err(i+1)
 	return bins

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('authorprefeat', nargs='?', default='generated/Author_prefeat.pickle')
	parser.add_argument('type', nargs='?', default='iFfL')
	args = parser.parse_args()
 	print_err("Loading pickled author pre-features")
  	authors = pickle.load(open(args.authorprefeat, 'rb'))

	bins = globals()["bin_"+args.type](authors)
	bins = sorted([(len(bv), blabel, bv) for blabel, bv in bins.iteritems()], reverse=True)

	for _, binlabel, binv in bins:
		print binlabel + ';' + ','.join(map(str, binv))
		
if __name__ == "__main__":
	main()