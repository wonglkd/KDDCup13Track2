#!/usr/bin/env python
# Given edges + authorinfo, generate features
import argparse
import csv
import numpy as np
import itertools as itl
import cPickle as pickle
from pprint import pprint

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edges')
	parser.add_argument('authorprefeat', nargs='?', default='authors_prefeat.pickle')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edges.replace('_edges.txt', '') + '.feat'
	
	print "Loading pickled author pre-features"
 	authors = pickle.load(open(args.authorprefeat, 'rb'))

	print "Generating features for author pairs"

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
		'suffix'
	]
	writer = csv.DictWriter(open(args.outfile, 'wb'), dialect='excel-tab', fieldnames=fields)
	writer.writeheader()

	rows_skipped = 0

 	for a, b in csv.reader(open(args.edges)):
 		a, b = int(a), int(b)
 		if a not in authors or b not in authors:
 			rows_skipped += 1
 			continue
		# feature vector
		f = {
			'id1': a,
			'id2': b
 		} 
 		aa, ab = authors[a], authors[b]
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
			f['affil_sharedidf'] = 0
		else:
			affil_terms_a = aa['affil_tdidf'].nonzero()[1]
			affil_terms_b = ab['affil_tdidf'].nonzero()[1]
			affil_ind = np.intersect1d(affil_terms_a, affil_terms_b, assume_unique=True)
			if affil_ind.any():
				f['affil_sharedidf'] = np.sum(aa['affil_tdidf'][[0] * len(affil_ind), affil_ind])
			else:
				f['affil_sharedidf'] = 0
		
		f['lastidf'] = 0 if (aa['name_last'] != ab['name_last'] or not aa['name_last']) else aa['lastname_idf']
		f['iFfLidf'] = 0 if (aa['iFfL'] != ab['iFfL'] or not aa['iFfL']) else aa['iFfL_idf']
		f['exact'] = int(aa['name'] == ab['name'] and len(aa['name']) > 0)
		f['suffix'] = int(aa['name_suffix'] == ab['name_suffix'] and len(aa['name_suffix']) > 0)
		
		writer.writerow(f)

	print "Rows skipped: {0}".format(rows_skipped)

if __name__ == "__main__":
	main()