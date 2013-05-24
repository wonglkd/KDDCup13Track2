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

def load_features(featurefile):
	print_err("Loading features")
	reader = csv.reader(open(featurefile, 'rb'), dialect='excel-tab')
	header = reader.next()
	ids, X = [], []
	for i, line in enumerate(reader):
		line = map(num, line)
		ids.append((line[0], line[1]))
		X.append(line[2:])
 		if (i+1) % 10000 == 0:
 			print_err(i+1, ' rows done')
 	X = np.array(X)
 	return ids, X

class FeaturesGenerator:
	fields = [
		'id1',
		'id2',
		'exact',
		'mid',
		'first',
		'last',
		'lastidf',
		'iFfLidf',
		'affil_sharedidf',
# 		'affil_cosineidf',
		'suffix'
	] + featEdges.PaperauthorFeaturesGenerator.fields

	def __init__(self, authorprefeat='generated/Author_prefeat.pickle'):
		print_err("Loading pickled author pre-features")
		self.authors = pickle.load(open(authorprefeat, 'rb'))
		self.PFG = featEdges.PaperauthorFeaturesGenerator(self.authors)
# 		self.fields += self.PFG.fields

	def getCosineSimilarity(self, a, b):
		print(a)
		print(b)
		return np.dot(a, b) / (math.sqrt(np.dot(a, a)) * math.sqrt(np.dot(b, b)))

	def getFeatures(self, a, b):
		# feature vector
		f = {
			'id1': a,
			'id2': b
 		}
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

		if aa['affil_tdidf'] is None or ab['affil_tdidf'] is None:
			f['affil_sharedidf'] = np.nan
# 			f['affil_cosineidf'] = np.nan
		else:
# 			print aa['affil_tdidf']
# 			print ab['affil_tdidf']
			affil_terms_a = aa['affil_tdidf'].nonzero()[1]
			affil_terms_b = ab['affil_tdidf'].nonzero()[1]
# 			f['affil_cosineidf'] = self.getCosineSimilarity(aa['affil_tdidf'], ab['affil_tdidf'])
			affil_common = np.intersect1d(affil_terms_a, affil_terms_b, assume_unique=True)
			diffa = np.setdiff1d(affil_terms_a, affil_common)
			diffb = np.setdiff1d(affil_terms_b, affil_common)
			if affil_common.any():
				f['affil_sharedidf'] = np.sum(aa['affil_tdidf'][[0] * len(affil_common), affil_common])
			else:
				f['affil_sharedidf'] = 0
			suma = np.sum(aa['affil_tdidf'][[0] * len(diffa), diffa]) if diffa.any() else 0
			sumb = np.sum(ab['affil_tdidf'][[0] * len(diffb), diffb]) if diffb.any() else 0
# 			print suma, sumb
			f['affil_sharedidf'] -= math.log(1.0 + min(suma, sumb))
# 			print "affil", f['affil_sharedidf']
		
		f['lastidf'] = 0 if (aa['name_last'] != ab['name_last'] or not aa['name_last']) else aa['lastname_idf']
		f['iFfLidf'] = 0 if (aa['iFfL'] != ab['iFfL'] or not aa['iFfL']) else aa['iFfL_idf']
		f['exact'] = int(aa['name'] == ab['name'] and len(aa['name']) > 0)
		f['suffix'] = int(aa['name_suffix'] == ab['name_suffix'] and len(aa['name_suffix']) > 0)

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

	writer = csv.DictWriter(open(args.outfile, 'wb'), dialect='excel-tab', fieldnames=featgen.fields)
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
		
 		writer.writerow(featgen.getFeatures(a, b))
 		if (i+1) % 5000 == 0:
 			print_err(i+1, ' rows done')
 
	print_err("Rows skipped: {0}".format(rows_skipped))

if __name__ == "__main__":
	main()