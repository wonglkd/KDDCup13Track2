#!/usr/bin/env python
# Given HPC+HRC, list HPC by HRC
from common import *
from collections import defaultdict
from cluster_common import *
import cPickle as pickle
import argparse
import csv
from itertools import chain
from pprint import pprint
import sys

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('hpc_file')
	parser.add_argument('hrc_file')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('-a', '--authorprefeat', default='generated/Author_prefeat.pickle')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.hpc_file.replace('.clusters','') + '.clusgrp'

	hrc_of_author = {}
		
	for hrc_i, cl in enumerate(loadClusters(args.hrc_file)):
		for aid in cl:
			hrc_of_author[aid] = hrc_i

	hrc_of_hpc = defaultdict(list)

	for cl in loadClusters(args.hpc_file):
		seen_hrcs = set()
		for aid in cl:
			if aid in hrc_of_author:
				seen_hrcs.add(hrc_of_author[aid])
		if len(seen_hrcs) > 0:
			for id in seen_hrcs:
				hrc_of_hpc[id].append(cl)
#		else:
#			print_err("Not in hierarchy:", str(len(seen_hrcs))+','+' '.join(map(str, seen_hrcs)))

	fout = open(args.outfile, 'wb')

	print_err("Loading pickled author pre-features")
	authors = pickle.load(open(args.authorprefeat, 'rb'))
#		import networkx as nx
#		G_sim = nx.read_weighted_edgelist(skip_comments(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')
	
	for hrc, hpcs in hrc_of_hpc.iteritems():
		if len(hpcs) == 1:
			continue
 		outputClusters(hpcs, fout, authors=authors)
		fout.write("--combined:--\n")
		outputClusters([list(chain.from_iterable(hpcs))], fout, authors=authors)
		fout.write("---------\n")

if __name__ == "__main__":
	main()