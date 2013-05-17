#!/usr/bin/env python
import csv
import argparse
from unidecode import unidecode
from nameparser import HumanName
from collections import defaultdict

def bin_samename(reader):
	bins = defaultdict(set)
 	for line in reader:
 		bins[unidecode(unicode(line[1], 'utf-8')).strip().lower()].add(line[0])
 	return bins

def bin_fFfL(reader):
	bins = defaultdict(set)
 	for line in reader:
 		hn = HumanName(unidecode(unicode(line[1], 'utf-8')))
 		bins[(hn.first + ' ' + hn.last).strip().lower()].add(line[0])
 	return bins

def bin_iFfL(reader):
	bins = defaultdict(set)
 	for line in reader:
 		hn = HumanName(unidecode(unicode(line[1], 'utf-8')))
 		if hn == '':
 			bins[''].add(line[0])
 		elif len(hn.first) == 0:
 			bins[hn.last.lower()].add(line[0])
 		else:
 			bins[(hn.first[0] + ' ' + hn.last).strip().lower()].add(line[0])
 	return bins

def bin_ngrams(reader, n=5):
	bins = defaultdict(set)
 	for line in reader:
 		lname = unidecode(unicode(line[1], 'utf-8')).strip().lower()
 		ngrams = zip(*[lname[i:] for i in range(n)])
 		for p in ngrams:
 			bins[p].add(line[0])
 	return bins

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('authorfile', nargs='?', default='Author.csv')
	parser.add_argument('type', nargs='?', default='samename')
	args = parser.parse_args()
	reader = csv.reader(open(args.authorfile))
	reader.next()

	bins = globals()["bin_"+args.type](reader)
	bins = sorted([(len(b), b) for b in bins.values()], reverse=True)

	for _, binv in bins:
		print ' '.join(binv)
		
if __name__ == "__main__":
	main()