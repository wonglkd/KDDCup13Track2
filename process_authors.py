#!/usr/bin/env python
# Given authors, generate features for the individual authors
import argparse
import csv
import math
import numpy as np
import cPickle as pickle
from nameparser import HumanName
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from unidecode import unidecode
#from pprint import pprint

def loadAuthors(authorfile):
	reader = csv.reader(open(authorfile, 'rb'))
	reader.next()
	authors = []
	lastname_cnt = defaultdict(int)
	iFfL_cnt = defaultdict(int)
	affiliations = []
 	print "Parsing names and counts"
	for line in reader:
		line[1:] = [unicode(cell, 'utf-8') for cell in line[1:]]
		line[1], line[2] = unidecode(line[1]), unidecode(line[2])
		hn = HumanName(line[1])
		if hn.last:
			if hn.first:
				iFfL = hn.first[0] + ' ' + hn.last.strip('.')
				fFfL = hn.first + ' ' + hn.last.strip('.')
				fFfL = fFfL.strip().lower()
			else:
				iFfL = 'L:' + hn.last.strip('.')
				fFfL = iFfL
		elif hn.first:
			iFfL = 'F:' + hn.first # use full first name if no last name
			fFfL = iFfL
		else:
			iFfL = 'ID:' + line[0]
			fFfL = iFfL
		iFfL = iFfL.strip().lower()

		full_name = hn.full_name.strip().lower()
		if full_name == '':
			full_name = 'ID: ' + line[0]

		authors.append((int(line[0]), {
 			'name': full_name,
 			'name_title': hn.title.lower().strip('.'),
 			'name_first': hn.first.lower().strip('.'),
 			'name_middle': hn.middle.lower().strip('.'),
 			'name_last': hn.last.lower().strip('.'),
 			'name_suffix': hn.suffix.lower().strip('.'),
			'iFfL': iFfL,
			'fFfL': fFfL,
			'affiliation': line[2]
		}))
		affiliations.append(line[2])
		if len(affiliations) % 10000 == 0:
			print len(affiliations)
 		lastname_cnt[hn.last.strip('.').lower()] += 1
  		iFfL_cnt[iFfL] += 1
# 	stopwordlist = ['this', 'supported', 'the', 'by']
	print "Computing Counts of affiliations"
 	count_vec = CountVectorizer(min_df=1, binary=True)
 	affil_count = count_vec.fit_transform(affiliations)
	print "Computing TF-IDF of affiliations"
 	tt = TfidfTransformer(smooth_idf=True, sublinear_tf=False)
 	affil_tfidf = tt.fit_transform(affil_count)
#	print l
#    	print count_vec.inverse_transform(affil_tfidf)
#   	pprint(count_vec.get_feature_names())
	print "Calculating IDFs"
# 	iFfL_IDF = np.log(float(len(authors)) / np.array(iFfL_cnt.values()))
# 	iFfL_IDF = dict(zip(iFfL_cnt.keys(), iFfL_IDF / iFfL_IDF.max()))
# 	lastname_IDF = np.log(float(len(authors)) / np.array(lastname_cnt.values()))
# 	lastname_IDF = dict(zip(lastname_cnt.keys(), lastname_IDF / lastname_IDF.max()))

	iFfL_IDF = dict(zip(iFfL_cnt.keys(), np.log(float(len(authors)) / np.array(iFfL_cnt.values()))))
	lastname_IDF = dict(zip(lastname_cnt.keys(), np.log(float(len(authors)) / np.array(lastname_cnt.values()))))

	affil_count = affil_count.tocsr()
	print "Packing it into a list"
 	for i, a in enumerate(authors):
 		authors[i][1]['iFfL_idf'] = iFfL_IDF[a[1]['iFfL']]
 		authors[i][1]['lastname_idf'] = lastname_IDF[a[1]['name_last'].lower()]
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
	print "Pickling..."
	pickle.dump(authors, open(args.outputfile, 'wb'))

if __name__ == "__main__":
	main()