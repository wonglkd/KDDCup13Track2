#!/usr/bin/env python
from common import *
import csv
import argparse
from unidecode import unidecode
from nameparser import constants as npc
from collections import defaultdict
import cPickle as pickle
import re

stopwords_custom = set(['document', 'preparation', 'system', 'consortium', 'committee', 'international', 'artificial', 'network', 'distributed', 'based', 'research', 'language', 'technology', 'project', 'design', 'computer', 'control', 'object', 'internet', 'propulsion', 'corp', 'workshop', 'xml', 'world', 'work', 'thesis', 'test', 'tool', 'structure', 'statistical', 'laboratory', 'ltd', 'objects', 'process', 'scheduling', 'september', 'special', 'student', 'programs', 'capacitated', 'balancing', 'assembly', 'aspect', 'model', 'inc', 'psychological', 'psychology', 'mohammed', 'computing', 'software', 'programming', 'new', 'applications', 'jet', 'propulsion', 'classification', 'recommendation'])
stopwords = stopwords_custom | npc.TITLES | npc.PREFIXES | npc.SUFFIXES | npc.CONJUNCTIONS

def bin_exactsamename(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		bins[a['fullname']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins
 
def bin_samename(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		bins[a['fullname_joined']].add(id)
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

def bin_fF3L(authors, max_bin_size=20):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if ':' not in a['fFiL'] and len(a['name_last']) >= 3 and len(a['fFiL']) > 2:
			bins[a['fFiL'] + a['name_last'][1:3]].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)

	bk = bins.keys()
	for b in bk:
		if len(bins[b]) > max_bin_size:
			del bins[b]

 	return bins

def bin_fFiL(authors, max_bin_size=20):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if len(a['fFiL']) > 2:
			bins[a['fFiL']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)

	bk = bins.keys()
	for b in bk:
		if len(bins[b]) > max_bin_size:
			del bins[b]

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
 		bins[a['fullname_parsed']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_iFoffbyoneL(authors, max_bin_size=30):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if ':' not in a['fullname'] and a['name_first'] and a['name_last']:
 			bins[a['name_first'][0] + a['name_last']].add(id)
 			if len(a['name_last']) > 1:
	 			bins[a['name_first'][0] + a['name_last'][:-1]].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)

	bk = bins.keys()
	for b in bk:
		if len(bins[b]) > max_bin_size:
			del bins[b]

 	return bins

def bin_2FoffbyoneL(authors, max_bin_size=30):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if ':' not in a['fullname'] and len(a['name_first']) >= 2 and a['name_last']:
 			bins[a['name_first'][0:2] + a['name_last']].add(id)
 			if len(a['name_last']) > 1:
	 			bins[a['name_first'][0:2] + a['name_last'][:-1]].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)

	bk = bins.keys()
	for b in bk:
		if len(bins[b]) > max_bin_size:
			del bins[b]

 	return bins

def bin_metaphone(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if a['metaphone_fullname']:
	 		bins[a['metaphone_fullname']].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)

# 	bk = bins.keys()
# 	for b in bk:
# 		if len(bins[b]) > max_bin_size:
# 			del bins[b]

 	return bins

def bin_offbylastone(authors):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if ':' not in a['fullname_joined']:
			bins[a['fullname_joined']].add(id)
			if len(a['fullname_joined']) > 1:
				bins[a['fullname_joined'][:-1]].add(id)
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_token(authors, nw=2, max_bin_size=100):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if ':' not in a['name']:
 			tokens = re.sub("[^\w]", " ",  a['name']).split()
 			tokens = [v for v in tokens if len(v) > 2 and v not in stopwords]
	 		ngrams = zip(*[tokens[j:] for j in range(nw)])
			for p in ngrams:
				pg = ' '.join(p)
				if len(pg) > len(p)*2-1:
					bins[pg].add(id)
		if (i+1) % 10000 == 0:
			print_err(i+1)

	bk = bins.keys()
	for b in bk:
		if len(bins[b]) > max_bin_size:
			del bins[b]

 	return bins

def bin_ngrams(authors, n=15, max_bin_size=30):
	bins = defaultdict(set)
 	for i, (id, a) in enumerate(authors.iteritems()):
 		if ':' not in a['fullname']:
 			lname = a['fullname']
	 		ngrams = zip(*[lname[j:] for j in range(n)])
			for p in ngrams:
				if not any(((s in p) for s in stopwords_custom)):
					bins[''.join(p)].add(id)
		if (i+1) % 10000 == 0:
			print_err(i+1)

	bk = bins.keys()
	for b in bk:
		if len(bins[b]) > max_bin_size:
			del bins[b]

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
		print binlabel + ';' + ','.join(map(str, sorted(binv)))
		
if __name__ == "__main__":
	main()