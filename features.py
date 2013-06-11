#!/usr/bin/env python
# Given edges + authorinfo, generate features
from common import *
import argparse
import csv
import numpy as np
import itertools as itl
import cPickle as pickle
from pprint import pprint
from collections import defaultdict
import featEdges
import math
try:
	import jellyfish
except ImportError:
	print_err("Could not import jellyfish")

def load_features(featurefile):
	print_err("Loading features")
	reader = csv.reader(skip_comments(open(featurefile, 'rb')), dialect='excel-tab')
	header = reader.next()
	ids, X = [], []
	for i, line in enumerate(reader):
		line[1:] = map(num, line[1:])
		ids.append(tuple(map(int, line[0].split(","))))
		X.append(line[1:])
 		if (i+1) % 10000 == 0:
 			print_err(i+1, ' rows done')
 	X = np.array(X)
 	return ids, X

class FeaturesGenerator:
	fields = [
		'exact',
		'mid',
		'first',
		'last',
		'lastidf',
		'iFfLidf',
		'has_affil',
		'fullname_sharedidf',
		'affil_sharedidf',
		'suffix',
		'jaro_distance',
		'jaro_winkler',
		'jarow_first',
		'jarow_mid',
		'jarow_last',
		'jarow_firstmid',
		'jarow_midlast',
		'firstmidswap',
		'metaphone',
		'subsetprefix',
		'offbylastone'
	] + featEdges.PaperauthorFeaturesGenerator.fields

	def __init__(self, authorprefeat='generated/Author_prefeat.pickle'):
		print_err("Loading pickled author pre-features")
		self.authors = pickle.load(open(authorprefeat, 'rb'))
		self.PFG = featEdges.PaperauthorFeaturesGenerator(self.authors)

	def getCosineSimilarity(self, a, b):
		print(a)
		print(b)
		return np.dot(a, b) / (math.sqrt(np.dot(a, a)) * math.sqrt(np.dot(b, b)))

	def getFeatures(self, a, b):
		# feature vector
		f = {}
 		aa, ab = self.authors[a], self.authors[b]
 		name_para = (('mid', 'name_middle'), ('first', 'name_first'), ('last', 'name_last'))
 		for id_f, id_o in name_para:
	 		la, lb = len(aa[id_o]), len(ab[id_o])
			if la == 0 or lb == 0: #at least one lacks the name part
				f[id_f] = 3 if (la == lb) else 2
			elif aa[id_o] == ab[id_o]: #full name match
				f[id_f] = 5 if (la > 1) else 4
			elif la > 1 and lb > 1: #full names supplied and no match
				f[id_f] = 0
			elif aa[id_o][0] == ab[id_o][0]: #at least one is initial and initials match
				f[id_f] = 4
			else: #initials don't match
				f[id_f] = 1


		if aa['fullname_tfidf'] is not None and ab['fullname_tfidf'] is not None:
			f['fullname_sharedidf'] = shared_terms_sum(aa['fullname_tfidf'], ab['fullname_tfidf'])

		if aa['affil_tfidf'] is not None and ab['affil_tfidf'] is not None:
			f['has_affil'] = 2
		elif aa['affil_tfidf'] is not None or ab['affil_tfidf'] is not None:
			f['has_affil'] = 1
		else:
			f['has_affil'] = 0

		if f['has_affil'] != 2:
			f['affil_sharedidf'] = np.nan
		else:
			f['affil_sharedidf'] = shared_terms_sum(aa['affil_tfidf'], ab['affil_tfidf'])

		if aa['name_last'] == ab['name_last'] and (
			(aa['name_first'] == ab['name_middle'] and not aa['name_middle']) or
			(ab['name_first'] == aa['name_middle'] and not ab['name_middle'])
		):
			if len(aa['name_first']) > 1:
				f['firstmidswap'] = 2
			else:
				f['firstmidswap'] = 1
		else:
			f['firstmidswap'] = 0

		# 1 = off by two, 2 = off by one
		f['offbylastone'] = 0
		
		la, lb = len(aa['fullname']), len(ab['fullname'])
		if aa['fullname'].startswith(ab['fullname']):
			f['subsetprefix'] = lb
			if la - lb <= 2:
				f['offbylastone'] = 3 - (la - lb)
		elif ab['fullname'].startswith(aa['fullname']):
			f['subsetprefix'] = la
			if lb - la <= 2:
				f['offbylastone'] = 3 - (lb - la)
		else:
			f['subsetprefix'] = 0
		
		f['lastidf'] = 0 if (aa['name_last'] != ab['name_last'] or not aa['name_last']) else aa['lastname_idf']
		f['iFfLidf'] = 0 if (aa['iFfL'] != ab['iFfL'] or not aa['iFfL']) else aa['iFfL_idf']
		f['exact'] = int(aa['fullname_joined'] == ab['fullname_joined'] and len(aa['fullname_joined']) > 0)
		f['jaro_distance'] = 0 if (':' in aa['fullname'] or ':' in ab['fullname']) else jellyfish.jaro_distance(aa['fullname'], ab['fullname'])
		f['jaro_winkler'] = 0 if (':' in aa['fullname'] or ':' in ab['fullname']) else jellyfish.jaro_winkler(aa['fullname'], ab['fullname'])
		f['jarow_first'] = jellyfish.jaro_winkler(aa['name_first'], ab['name_first'])
		f['jarow_mid'] = jellyfish.jaro_winkler(aa['name_middle'], ab['name_middle'])
		f['jarow_last'] = jellyfish.jaro_winkler(aa['name_last'], ab['name_last'])
		f['jarow_firstmid'] = jellyfish.jaro_winkler(aa['name_first']+aa['name_middle'], ab['name_first']+ab['name_middle'])
		f['jarow_midlast'] = jellyfish.jaro_winkler(aa['name_middle']+aa['name_last'], ab['name_middle']+ab['name_last'])
		
		f['suffix'] = int(aa['name_suffix'] == ab['name_suffix'] and len(aa['name_suffix']) > 0)
		f['metaphone'] = int(aa['metaphone_fullname'] == ab['metaphone_fullname'] and len(aa['metaphone_fullname']) > 0)

		f.update(self.PFG.getEdgeFeatures(a, b))

		return f

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edges')
	parser.add_argument('authorprefeat', nargs='?', default='generated/Author_prefeat.pickle')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edges.replace('_edges.txt', '') + '.feat'

	featgen = FeaturesGenerator(args.authorprefeat)

	print_err("Generating features for author pairs")

	writer = csv.DictWriter(open(args.outfile, 'wb'), dialect='excel-tab', fieldnames=['authors']+featgen.fields)
	writer.writeheader()

	rows_skipped = 0

 	for i, row in enumerate(csv.reader(skip_comments(open(args.edges, 'rb')))):
 		if len(row) >= 3:
 			row = row[1:3]
 		a, b = int(row[0]), int(row[1])
 		if a not in featgen.authors or b not in featgen.authors:
 			rows_skipped += 1
 			print_err("Skipped:", a, b)
 			continue
		
		f = featgen.getFeatures(a, b)
		f = {k: '{:g}'.format(v) for k, v in f.iteritems()}
		f['authors'] = '{:},{:}'.format(a, b)
 		writer.writerow(f)
 		if (i+1) % 5000 == 0:
 			print_err(i+1, ' rows done')
 
	print_err("Rows skipped: {0}".format(rows_skipped))

if __name__ == "__main__":
	main()