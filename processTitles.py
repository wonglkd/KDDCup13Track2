#!/usr/bin/env python
from common import *
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from unidecode import unidecode
import csv
import cPickle as pickle
import argparse
from pprint import pprint
from collections import defaultdict
import numpy as np
import scipy as sp

def getTitles(filenames):
	titles = []
	ids = []
	boundaries = [0]
	for filename in filenames:
		print_err("Reading file", filename)
		with open(filename, 'rb') as f:
			reader = csv.reader(f)
			header = reader.next()
			for line in reader:
				titles.append(unidecode(unicode(line[2], 'utf-8')))
				ids.append(int(line[0]))
		boundaries.append(len(titles))
	return titles, boundaries, ids

def computeTFIDFs(titles, series, boundaries, ids):
	stop_words = ENGLISH_STOP_WORDS | set(['conference', 'journal', 'international', 'national', 'on', 'workshop', 'symposium', 'int', 'conf', 'research'])
	vec = TfidfVectorizer(analyzer='word', lowercase=True, stop_words=stop_words, min_df=1, max_df=1.0, binary=True, norm=None, use_idf=True, smooth_idf=True)
	tfidfs = vec.fit_transform(titles)
	# split by boundaries
	ids = [ids[boundaries[i]:boundaries[i+1]] for i in range(series)]
	for i in range(series):
		ids[i] = {idx: boundaries[i] + j for j, idx in enumerate(ids[i])}

	# print words sorted by frequency
	# kk = zip(tfidf.sum(axis=0).tolist()[0], vec.get_feature_names())
	# pprint(sorted(kk))
	return tfidfs, ids

def loadPubsByAuthor(filenames):
	pubs_by_author = {}
	author_ids = set()
	for i, filename in enumerate(filenames):
		with open(filename, 'rb') as f:
			print_err("Loading file", filename)
			reader = csv.reader(f)
			reader.next()
			# id, pubid, cnt
			for line in reader:
				line[0:3] = map(int, line[0:3])
				if line[0] not in pubs_by_author:
					pubs_by_author[line[0]] = [{} for x in range(len(filenames))]
				pubs_by_author[line[0]][i][line[1]] = line[2]
				author_ids.add(line[0])
	return pubs_by_author, author_ids

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--titlefiles', nargs='*', default=['data/Conference.csv', 'data/Journal.csv'])
	parser.add_argument('--pafiles', nargs='*', default=['authordata/pa_conferences.csv', 'authordata/pa_journals.csv'])
	parser.add_argument('-o', '--output', nargs='?', default='textdata/publication_tfidf.pickle')
	args = parser.parse_args()

	print_err("Reading Titles")	
	titles, boundaries, ids = getTitles(args.titlefiles)
	
	print_err("Computing TF-IDF")
	tfidfs, id2ind = computeTFIDFs(titles, len(args.titlefiles), boundaries, ids)
	
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