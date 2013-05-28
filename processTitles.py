#!/usr/bin/env python
from common import *
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from unidecode import unidecode
import csv
import cPickle as pickle
import argparse
from pprint import pprint
import numpy as np

def main():
	default_files = ['data/Conference.csv', 'data/Journal.csv']
	parser = argparse.ArgumentParser()
	parser.add_argument('--titlefiles', nargs='*', default=default_files)
	parser.add_argument('-o', '--output', nargs='?', default='textdata/publication_tfidf.pickle')
	args = parser.parse_args()
	
	titles = []
	ids = []
	boundaries = [0]
	for filename in args.titlefiles:
		print_err("Reading file", filename)
		with open(filename, 'rb') as f:
			reader = csv.reader(f)
			header = reader.next()
			for line in reader:
				titles.append(unidecode(unicode(line[2], 'utf-8')))
				ids.append(int(line[0]))
		boundaries.append(len(titles))

	print_err("Computing TF-IDF")
	stop_words = ENGLISH_STOP_WORDS | set(['conference', 'journal', 'international', 'national', 'on', 'workshop', 'symposium', 'int', 'conf', 'research'])
	vec = TfidfVectorizer(analyzer='word', lowercase=True, stop_words=stop_words, min_df=1, max_df=1.0, binary=True, norm=None, use_idf=True, smooth_idf=True)
	tfidf = vec.fit_transform(titles)
	tfidfs = [tfidf[boundaries[i]:boundaries[i+1]] for i in range(len(args.titlefiles))]
	ids = [ids[boundaries[i]:boundaries[i+1]] for i in range(len(args.titlefiles))]
	id2score = []
	for i in range(len(args.titlefiles)):
		ids[i] = {idx: j for j, idx in enumerate(ids[i])}
		
	# print words sorted by frequency
	# kk = zip(tfidf.sum(axis=0).tolist()[0], vec.get_feature_names())
	# pprint(sorted(kk))

	pickle.dump((tfidfs, ids), open(args.output, 'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	main()