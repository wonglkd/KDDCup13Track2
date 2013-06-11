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
	hrc_contents = list(loadClusters(args.hrc_file))
		
	for hrc_i, cl in enumerate(hrc_contents):
		for aid in cl:
			hrc_of_author[aid] = hrc_i

	hrc_of_hpc = defaultdict(list)

	fout = open(args.outfile, 'wb')

	print_err("Loading pickled author pre-features")
 	authors = pickle.load(open(args.authorprefeat, 'rb'))

	undiscovered_hrcs = set(range(len(hrc_contents)))

	for cl in loadClusters(args.hpc_file):
		seen_hrcs = set()
		loners = []
		for aid in cl:
			if aid in hrc_of_author:
				seen_hrcs.add(hrc_of_author[aid])
			else:
				loners.add(aid)

		if loners:
			fout.write("--in HPC but not in HRC:--\n")
	 		outputClusters([comb], fout, authors=authors)

		if len(seen_hrcs) > 0:
			for id in seen_hrcs:
				hrc_of_hpc[id].append(cl)
		else:
			fout.write("Not in hierarchy:\n")
	 		outputClusters([cl], fout, authors=authors)
		undiscovered_hrcs -= seen_hrcs

	fout.write("------------\n")

#		import networkx as nx
#		G_sim = nx.read_weighted_edgelist(skip_comments(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')
	
	for hrc, hpcs in hrc_of_hpc.iteritems():
		if len(hpcs) == 1:
			continue
  		outputClusters(hpcs, fout, authors=authors)
		fout.write("--combined:--\n")
		comb = list(chain.from_iterable(hpcs))
 		outputClusters([comb], fout, authors=authors)

		singletons = list(set(hrc_contents[hrc]) - set(comb))
		if singletons:
			fout.write("--in HRC but not in HPC:--\n")
			outputClusters([singletons], fout, authors=authors)
		
		fout.write("---------\n")

	if undiscovered_hrcs:
		fout.write("--HRCs never seen:--\n")
		outputClusters([hrc_contents[cl] for cl in undiscovered_hrcs], fout, authors=authors)

if __name__ == "__main__":
	main()