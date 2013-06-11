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
	fullnames = []
 	print_err("Parsing names and counts")
	#[^~:_`@\?\\|\'/\"\.\-0-9a-z;,\n\r \+\-\)\}&%\$\*\{\>=\^]
	titles_c = nameparser.constants.TITLES - set(['wing', 'lord', 'mg', 'mate', 'king', 'sharif', 'sheikh', 'rt', 'lama', 'gen', 'bg', 'baba', 'ab'])
	suffixes_c = nameparser.constants.SUFFIXES | set(['junior', 'senior', 'vii']) 
	prefixes_c = nameparser.constants.PREFIXES - set(['bin']) # more common as first name

	id2affiliation = {}
	id2fullname = {}
	for i, line in verbose_iter(reader):
		line[1:] = [unidecode(unicode(cell, 'utf-8')) for cell in line[1:]]

  		if line[2]:
			id2affiliation[int(line[0])] = len(affiliations)
			line[2] = strip_punc(line[2].lower())
			affiliations.append(line[2])

		fullnm = strip_punc(line[1].lower().encode('ascii'))
		if fullnm:
			id2fullname[int(line[0])] = len(fullnames)
			fullnames.append(fullnm)
		if printaffilwordfreq:
			continue
		
		hn = HumanName(line[1].replace('-', ' '), titles_c=titles_c, prefixes_c=prefixes_c, suffixes_c=suffixes_c)
		ai = {
 			'fullname_joined': hn.full_name,
 			'name_title': hn.title,
 			'name_first': hn.first,
 			'name_middle': hn.middle,
 			'name_last': hn.last,
 			'name_suffix': hn.suffix
		}
		ai = {k: strip_punc(v.lower().encode('ascii'), space_dashes=False) for k, v in ai.iteritems()}
		ai['name'] = hn.full_name.lower().strip().encode('ascii').translate(None, ';')
		ai['fullname'] = strip_punc(hn.full_name.lower().encode('ascii'))
		ai['fullname_parsed'] = ai['name_first'] + ai['name_middle'] + ai['name_last'] + ai['name_suffix']
		ai['affiliation'] = line[2]
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

	print_err("Computing TF-IDF of affiliations")

	# min_df = 2 because though we deduct non common words, they should be significant first
	affil_tfidf = computeTFIDFs(affiliations, 'all', min_df=2, words_freq=printaffilwordfreq)
	if printaffilwordfreq:
		print "-----"
	name_tfidf = computeTFIDFs(fullnames, None, min_df=2, ngram_range=(1,3), words_freq=printaffilwordfreq, token_pattern=u'(?u)\\b[a-zA-Z][a-zA-Z]+\\b')
	if printaffilwordfreq:
		return

	print_err("Calculating IDFs")
	iFfL_IDF = dict(zip(iFfL_cnt.keys(), np.log(float(len(authors)) / np.array(iFfL_cnt.values()))))
	lastname_IDF = dict(zip(lastname_cnt.keys(), np.log(float(len(authors)) / np.array(lastname_cnt.values()))))

	print_err("Packing it into a list")
 	for i, a in enumerate(authors):
 		authors[i][1]['iFfL_idf'] = iFfL_IDF[a[1]['iFfL']]
 		authors[i][1]['lastname_idf'] = lastname_IDF[a[1]['name_last']]
 		if len(a[1]['affiliation']) == 0:
 			authors[i][1]['affil_tfidf'] = None
 		else:
			authors[i][1]['affil_tfidf'] = affil_tfidf[id2affiliation[a[0]]]
		if a[0] in id2fullname:
 			authors[i][1]['fullname_tfidf'] = name_tfidf[id2fullname[a[0]]]
 		else:
			authors[i][1]['fullname_tfidf'] = None
			
		if (i+1) % 10000 == 0:
			print_err(i+1)
 	authors_dict = dict(authors)
 	return authors_dict

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('authorfile')
	parser.add_argument('outputfile', nargs='?')
	parser.add_argument('--affilwordfreq', action='store_true')
	parser.add_argument('--format', default='pickle')
	args = parser.parse_args()
	
	authors = loadAuthors(args.authorfile, args.affilwordfreq)
	if args.affilwordfreq:
		return
		
	if args.format == 'pickle':
		if not args.outputfile:
			args.outputfile = args.authorfile.replace(".csv","").replace("data","generated") + "_prefeat.pickle"
		print_err("Pickling...")
		pickle.dump(authors, open(args.outputfile, 'wb'), pickle.HIGHEST_PROTOCOL)
	elif args.format == 'csv':
		fields = ['id', 'name_title', 'name_first', 'name_middle', 'name_last', 'name_suffix', 'name', 'iFfL', 'metaphone_fullname', 'affiliation']
		with open(args.outputfile, 'wb') as f:
			writer = csv.DictWriter(f, fieldnames=fields)
			writer.writeheader()
			for ak, av in authors.iteritems():
				f = {key: av[key] for key in fields if key != 'id'}
				f['id'] = ak
				writer.writerow(f)
	else:
		raise Exception("Invalid format")


if __name__ == "__main__":
	main()