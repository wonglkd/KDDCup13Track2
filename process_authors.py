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
import jellyfish

def loadAuthors(authorfile, printaffilwordfreq=False):
	reader = csv.reader(open(authorfile, 'rb'))
	reader.next()
	authors = []
	lastname_cnt = defaultdict(int)
	iFfL_cnt = defaultdict(int)
	affiliations = []
 	print_err("Parsing names and counts")
	#[^~:_`@\?\\|\'/\"\.\-0-9a-z;,\n\r \+\-\)\}&%\$\*\{\>=\^]
	punc = ".;,-'~:_@?\|\\/\"+-)}{(&$*%=>^ "
	titles_c = nameparser.constants.TITLES - set(['wing'])
	id2affiliation = {}
	for i, line in enumerate(reader):
		line[1:] = [unidecode(unicode(cell, 'utf-8')) for cell in line[1:]]
		hn = HumanName(line[1], titles_c=titles_c)
		ai = {
 			'fullname_joined': hn.full_name,
 			'name_title': hn.title,
 			'name_first': hn.first,
 			'name_middle': hn.middle,
 			'name_last': hn.last,
 			'name_suffix': hn.suffix
		}
		ai = {k: v.lower().encode('ascii').translate(None, punc) for k, v in ai.iteritems()}
		ai['name'] = hn.full_name.lower().strip().encode('ascii').translate(None, ';')
		ai['fullname'] = hn.full_name.lower().encode('ascii').translate(None, punc.replace(' ',''))
		ai['fullname_parsed'] = ai['name_first'] + ai['name_middle'] + ai['name_last'] + ai['name_suffix']
		ai['affiliation'] = line[2].lower()
		ai['metaphone_fullname'] = jellyfish.metaphone(ai['fullname']).encode('ascii').translate(None, ' ')
		if ai['name_last']:
			if ai['name_first']:
				ai['iFfL'] = ai['name_first'][0] + ai['name_last']
			else:
				ai['iFfL'] = 'L:' + ai['name_last']
		elif ai['name_first']:
			ai['iFfL'] = 'F:' + ai['name_first'] # use full first name if no last name
		else:
			ai['iFfL'] = 'ID:' + line[0]
		if ai['name_last'] and ai['name_first']:
			ai['fFfL'] = ai['name_first'] + ai['name_last']
			ai['fFiL'] = ai['name_first'] + ai['name_last'][0]
		else:
			ai['fFfL'] = ai['iFfL']
			ai['fFiL'] = ai['iFfL']

		if not ai['fullname_joined']:
			ai['fullname_joined'] = 'ID:' + line[0]
		if not ai['fullname']:
			ai['fullname'] = 'ID:' + line[0]
		if not ai['fullname_parsed']:
			ai['fullname_parsed'] = ai['fullname']

		authors.append((int(line[0]), ai))
 		lastname_cnt[ai['name_last']] += 1
  		iFfL_cnt[ai['iFfL']] += 1
  		if line[2]:
			id2affiliation[int(line[0])] = len(affiliations)
			affiliations.append(line[2])
		if (i+1) % 10000 == 0:
			print_err(i+1, "rows processed")

	print_err("Computing Counts of affiliations")
 	stopwordlist = ['a', 'an', 'and', 'at', 'by', 'of', 'supported', 'the', 'this']
 	# stopwordlist += ['department', 'university''school', 'institute', 'college', 'institution']
 	stopwordlist = list(ENGLISH_STOP_WORDS | set(stopwordlist))
 	# min_df = 2 because we will be looking for common words
 	count_vec = CountVectorizer(min_df=2, binary=True, stop_words=stopwordlist)
 	affil_count = count_vec.fit_transform(affiliations)

	print_err("Computing TF-IDF of affiliations")
 	tt = TfidfTransformer(norm=None, use_idf=True, smooth_idf=True, sublinear_tf=False)
 	affil_tfidf = tt.fit_transform(affil_count)

	# print words sorted by frequency
	if printaffilwordfreq:
		kk = zip(affil_count.sum(axis=0).tolist()[0], count_vec.get_feature_names())
		kk = sorted(kk)
		for a, b in kk:
			print '{:} {:}'.format(a, b)
		return

	print_err("Calculating IDFs")
	iFfL_IDF = dict(zip(iFfL_cnt.keys(), np.log(float(len(authors)) / np.array(iFfL_cnt.values()))))
	lastname_IDF = dict(zip(lastname_cnt.keys(), np.log(float(len(authors)) / np.array(lastname_cnt.values()))))

	print_err("Packing it into a list")
	affil_count = affil_count.tocsr()
 	for i, a in enumerate(authors):
 		authors[i][1]['iFfL_idf'] = iFfL_IDF[a[1]['iFfL']]
 		authors[i][1]['lastname_idf'] = lastname_IDF[a[1]['name_last']]
 		if len(a[1]['affiliation']) == 0:
 			authors[i][1]['affil_tdidf'] = None
#  			authors[i][1]['affil_count'] = None
 		else:
			authors[i][1]['affil_tdidf'] = affil_tfidf[id2affiliation[a[0]]]
 # 			authors[i][1]['affil_count'] = affil_count[id2affiliation[a[0]]]
		if (i+1) % 10000 == 0:
			print_err(i+1)
 	authors_dict = dict(authors)
 	return authors_dict

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('authorfile')
	parser.add_argument('outputfile', nargs='?')
	parser.add_argument('--affilwordfreq', action='store_true')
	args = parser.parse_args()
	
	authors = loadAuthors(args.authorfile, args.affilwordfreq)
	if args.affilwordfreq:
		return
	print_err("Pickling...")
	pickle.dump(authors, open(args.outputfile, 'wb'), pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
	main()