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
	titles = []
	ids = []
	print_err("Reading file", filename)
	with open(filename, 'rb') as f:
		reader = csv.reader(f)
		header = reader.next()
		for i, line in enumerate(reader):
			# Strip HTML tags
			yield re.sub('<[^<]+?>', ' ', line[1] + ' ' + line[5])
#			titles.append(re.sub('<[^<]+?>', ' ', line[1] + ' ' + line[5]))
#			ids.append(int(line[0]))
			if (i+1) % 10000 == 0:
				print_err(i+1, 'lines read')
#	return titles, ids

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('paperfile', nargs='?', default='data/Paper_u.csv')
	parser.add_argument('paperids', nargs='?', default='authordata/pa_paperids.csv')
	parser.add_argument('-o', '--output', default='textdata/papertitles_tfidf.pickle')
	args = parser.parse_args()

	print_err("Reading Titles")	
	#titles, ids = getTitleKeywords(args.paperfile)
	
	print_err("Computing TF-IDF")
	more_stop_words = ['discussion', 'paper', 'method', 'keyword', 'methods', 'case study', 'keywords', 'study', 'research', 'submission', 'evaluation', 'approach', 'framework', 'analysis']
	more_stop_words += ['conference', 'journal', 'international', 'national', 'on', 'workshop', 'symposium', 'int', 'conf']
	more_stop_words += ['keywords', 'based', 'using', 'analysis', 'words', 'key', 'word', 'design', 'test', 'title', 'titles', 'high', 'low', 'new', 'novel', 'effects', 'performance', 'applications', 'application']
	more_stop_words += ['und', 'gan', 'ein'] # and
	more_stop_words += ['baseado', 'na'] # based on
	more_stop_words += ['mm'] # 'based on'
	tfidfs, words_freq = pT.computeTFIDFs(getTitleKeywords(args.paperfile), more_stop_words, words_freq=True, min_df=2)

	pprint(words_freq)

	return
	
	print_err("Producing id-to-index map")
	id2ind = split_ids(len(args.titlefiles), boundaries, ids)
	
	print_err("Loading pubs by author")
	pubs_by_author, author_ids = loadPubsByAuthor(args.pafiles)

	print_err("Generating rows")
	TSVG = TextSimVecGenerator(pubs_by_author, tfidfs, id2ind)
	TextSimVecs = {}
	for i, aid in enumerate(author_ids):
 		tsv = TSVG.getTextSimPub(aid)
 		if tsv is not None:
	 		TextSimVecs[aid] = tsv
		if (i+1) % 1000 == 0:
			print_err(i+1, ' rows done')

 	pickle.dump(TextSimVecs, open(args.output, 'wb'), pickle.HIGHEST_PROTOCOL)

class TextSimVecGenerator:
	def __init__(self, pubs_by_author, pub_tfidf, pub_id2ind):
		self.pubs_by_author = pubs_by_author
		self.pub_tfidf = pub_tfidf
		self.pub_id2ind = pub_id2ind

	def getTextSimPub(self, aID):
		pub = self.pubs_by_author[aID]
		pubs = []
		for x in xrange(2):
			pubs.extend([self.pub_id2ind[x][v] for v in pub[x] if v in self.pub_id2ind[x]])
		if pubs:
			return sp.sparse.csr_matrix(self.pub_tfidf[pubs].sum(axis=0))
		else:
			return None

if __name__ == "__main__":
	main()