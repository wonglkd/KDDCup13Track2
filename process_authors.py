#!/usr/bin/env python
# Given authors, generate features for the individual authors
from common import *
import argparse
import csv
import math
import numpy as np
import cPickle as pickle
from nameparser import HumanName
import nameparser.constants
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, ENGLISH_STOP_WORDS
from unidecode import unidecode
from pprint import pprint

def loadAuthors(authorfile):
	reader = csv.reader(open(authorfile, 'rb'))
	reader.next()
	authors = []
	lastname_cnt = defaultdict(int)
	iFfL_cnt = defaultdict(int)
	affiliations = []
 	print_err("Parsing names and counts")
	punc = '.; '
	titles_c = nameparser.constants.TITLES - set(['wing'])
	for line in reader:
		line[1:] = [unidecode(unicode(cell, 'utf-8')) for cell in line[1:]]
		hn = HumanName(line[1], titles_c=titles_c)
		hn.title = hn.title.lower().strip(punc)
		hn.first = hn.first.lower().strip(punc)
		hn.middle = hn.middle.lower().strip(punc)
		hn.last = hn.last.lower().strip(punc)
		hn.suffix = hn.suffix.lower().strip(punc)
		hn.full_name = hn.full_name.strip().replace(';','').lower()
		full_parsed = hn.first + ' '
		if hn.middle:
			full_parsed += hn.middle + ' '
		full_parsed += hn.last + ' ' + hn.suffix
		full_parsed = full_parsed.strip()
		if hn.last:
			if hn.first:
				iFfL = hn.first[0] + ' ' + hn.last
			else:
				iFfL = 'L:' + hn.last
		elif hn.first:
			iFfL = 'F:' + hn.first # use full first name if no last name
		else:
			iFfL = 'ID:' + line[0]
		if hn.last and hn.first:
			fFfL = hn.first + ' ' + hn.last
		else:
			fFfL = iFfL

		if not hn.full_name:
			hn.full_name = 'ID:' + line[0]
		if not full_parsed:
			full_parsed = hn.full_name

		authors.append((int(line[0]), {
 			'name': hn.full_name,
 			'name_title': hn.title,
 			'name_first': hn.first,
 			'name_middle': hn.middle,
 			'name_last': hn.last,
 			'name_suffix': hn.suffix,
 			'fullparsedname': full_parsed,
			'iFfL': iFfL,
			'fFfL': fFfL,
			'affiliation': line[2]
		}))
 		lastname_cnt[hn.last] += 1
  		iFfL_cnt[iFfL] += 1
		affiliations.append(line[2])
		if len(affiliations) % 10000 == 0:
			print len(affiliations)

	print_err("Computing Counts of affiliations")
 	stopwordlist = ['a', 'an', 'and', 'at', 'by', 'department', 'of', 'supported', 'the', 'this']
 	stopwordlist = list(ENGLISH_STOP_WORDS | set(stopwordlist))
 	count_vec = CountVectorizer(min_df=1, binary=True, stop_words=stopwordlist)
 	affil_count = count_vec.fit_transform(affiliations)

	print_err("Computing TF-IDF of affiliations")
 	tt = TfidfTransformer(use_idf=True, smooth_idf=True, sublinear_tf=False)
 	affil_tfidf = tt.fit_transform(affil_count)
#    	print count_vec.inverse_transform(affil_tfidf)
#   	pprint(count_vec.get_feature_names())

	print_err("Calculating IDFs")
	iFfL_IDF = dict(zip(iFfL_cnt.keys(), np.log(float(len(authors)) / np.array(iFfL_cnt.values()))))
	lastname_IDF = dict(zip(lastname_cnt.keys(), np.log(float(len(authors)) / np.array(lastname_cnt.values()))))

	print_err("Packing it into a list")
	affil_count = affil_count.tocsr()
 	for i, a in enumerate(authors):
 		authors[i][1]['iFfL_idf'] = iFfL_IDF[a[1]['iFfL']]
 		authors[i][1]['lastname_idf'] = lastname_IDF[a[1]['name_last']]
 		if a[1]['affiliation'] == '':
 			authors[i][1]['affil_tdidf'], authors[i][1]['affil_count'] = None, None
 		else:
			authors[i][1]['affil_tdidf'] = affil_tfidf[i]
 			authors[i][1]['affil_count'] = affil_count[i]
		if (i+1) % 10000 == 0:
			print i+1
 	authors_dict = dict(authors)
 	return authors_dict

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('authorfile')
	parser.add_argument('outputfile')
	args = parser.parse_args()
	
	authors = loadAuthors(args.authorfile)
	print_err("Pickling...")
	pickle.dump(authors, open(args.outputfile, 'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	main()