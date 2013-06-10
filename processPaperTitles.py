#!/usr/bin/env python
from common import *
import processTitles as pT
import csv
import cPickle as pickle
import argparse
from pprint import pprint
from collections import defaultdict
import numpy as np
import scipy as sp
import re

def getTitleKeywords(filename):
	for i, line in readcsv_iter(filename):
		if (line[1] + line[5]).strip():
			# Strip HTML tags
			yield re.sub('<[^<]+?>', ' ', line[1] + ' ' + line[5])

def getIdsFromPapers(filename):
	idmap = {}
	i = 0
	for _, line in readcsv_iter(filename):
		if (line[1] + line[5]).strip():
			idmap[int(line[0])] = i
			i += 1
	return idmap
	
def loadPaperIDsByAuthor(filename):
	paperids_by_author = defaultdict(list)
	author_ids = set()
	for i, line in readcsv_iter(filename):
		# id, paperid, cnt
		line[0:3] = map(int, line[0:3])
		paperids_by_author[line[0]].append(line[1])
		author_ids.add(line[0])
	return paperids_by_author, author_ids

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('paperfile', nargs='?', default='data/Paper_u.csv')
	parser.add_argument('paperids', nargs='?', default='authordata/pa_paperids.csv')
	parser.add_argument('-o', '--output', default='textdata/papertitles_tfidf.pickle')
	parser.add_argument('--printaffilwordfreq', action='store_true')
	args = parser.parse_args()

	print_err("Computing TF-IDF")
	tfidfs = computeTFIDFs(getTitleKeywords(args.paperfile), 'all', min_df=2, words_freq=args.printaffilwordfreq)
	if args.printaffilwordfreq:
		return
	
	print_err("Reading id-to-index map")
	id2ind = getIdsFromPapers(args.paperfile)

	print_err("Loading paperids by author")
	paperids_by_author, author_ids = loadPaperIDsByAuthor(args.paperids)
	
	print_err("Generating rows")
	PTSVG = PaperTextSimVecGenerator(paperids_by_author, tfidfs, id2ind)
	TextSimVecs = {}
	for i, aid in enumerate(author_ids):
 		tsv = PTSVG.getTextSimPub(aid)
 		if tsv is not None:
	 		TextSimVecs[aid] = tsv
		if (i+1) % 2500 == 0:
			print_err(i+1, 'rows done')

 	pickle.dump(TextSimVecs, open(args.output, 'wb'), protocol=-1)

class PaperTextSimVecGenerator(pT.TextSimVecGenerator):
	def getTextSimPub(self, aID):
		pub = self.pubs_by_author[aID]
		pubs = [self.pub_id2ind[v] for v in pub if v in self.pub_id2ind]
		if pubs:
			return sp.sparse.csr_matrix(self.pub_tfidf[pubs].sum(axis=0))
		else:
			return None

if __name__ == "__main__":
	main()