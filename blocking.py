#!/usr/bin/env python
from common import *
import csv
import argparse
from unidecode import unidecode
from nameparser import HumanName
from collections import defaultdict

def bin_samename(reader):
	bins = defaultdict(set)
 	for i, line in enumerate(reader):
		fullname = unidecode(unicode(line[1], 'utf-8')).strip().lower()
		if fullname == '':
			fullname = 'ID: ' + line[0]
 		bins[fullname].add(line[0])
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_fFfL(reader):
	bins = defaultdict(set)
 	for i, line in enumerate(reader):
 		hn = HumanName(unidecode(unicode(line[1], 'utf-8')))
		if hn.last:
			if hn.first:
				fFfL = hn.first + ' ' + hn.last.strip('.')
			else:
				fFfL = 'L:' + hn.last.strip('.')
		elif hn.first:
			fFfL = 'F:' + hn.first # use full first name if no last name
		else:
			fFfL = 'ID:' + line[0]
		fFfL = fFfL.strip().lower()
 		bins[fFfL].add(line[0])
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_iFfL(reader):
	bins = defaultdict(set)
 	for i, line in enumerate(reader):
 		hn = HumanName(unidecode(unicode(line[1], 'utf-8')))
		if hn.last:
			if hn.first:
				iFfL = hn.first[0] + ' ' + hn.last.strip('.')
			else:
				iFfL = 'L:' + hn.last.strip('.')
		elif hn.first:
			iFfL = 'F:' + hn.first # use full first name if no last name
		else:
			iFfL = 'ID:' + line[0]
		iFfL = iFfL.strip().lower()
		bins[iFfL].add(line[0])
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def bin_ngrams(reader, n=5):
	bins = defaultdict(set)
 	for i, line in enumerate(reader):
 		lname = unidecode(unicode(line[1], 'utf-8')).strip().lower()
 		ngrams = zip(*[lname[i:] for i in range(n)])
 		for p in ngrams:
 			bins[p].add(line[0])
 		if (i+1) % 10000 == 0:
 			print_err(i+1)
 	return bins

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('authorfile', nargs='?', default='data/Author.csv')
	parser.add_argument('type', nargs='?', default='iFfL')
	args = parser.parse_args()
	reader = csv.reader(open(args.authorfile))
	reader.next()

	bins = globals()["bin_"+args.type](reader)
	bins = sorted([(len(bv), blabel, bv) for blabel, bv in bins.iteritems()], reverse=True)

	for _, binlabel, binv in bins:
		print binlabel + ',' + ' '.join(binv)
		
if __name__ == "__main__":
	main()