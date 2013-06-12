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

def check_for_blacklisted(hrc_c, blacklisted_edges, fout):
	if any(v1 in hrc_c and v2 in hrc_c for v1, v2 in blacklisted_edges):
		fout.write("--blacklisted edges:--\n")
		be = ((v1, v2) for v1, v2 in blacklisted_edges if v1 in hrc_c and v2 in hrc_c)
		for v1, v2 in be:
			fout.write("{:},{:}\n".format(v1, v2))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('hpc_file')
	parser.add_argument('hrc_file')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('-a', '--authorprefeat', default='generated/Author_prefeat.pickle')
	parser.add_argument('-b', '--blacklist', nargs='*', default=['data/blacklist_edges.csv', 'data/train.csv', 'data/train_extra.tmp.csv'])
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.hrc_file.replace('.clusters','') + '.clusgrp'

	blacklisted_edges = []

	if args.blacklist:
		for filename in args.blacklist:
			with open(filename, 'rb') as f:
				reader = csv.reader(skip_comments(f))
				for line in reader:
					line[0:3] = map(int, line[0:3])
					if len(line) > 2:
						if line[0] != 0:
							continue
						line = line[1:]
					blacklisted_edges.append((line[0], line[1]))


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
				loners.append(aid)

		if len(seen_hrcs) > 0:
			for id in seen_hrcs:
				hrc_of_hpc[id].append(cl)
			if loners:
				fout.write("--in HPC but not in HRC:--\n")
				outputClusters([loners], fout, authors=authors)
		else:
			fout.write("Not in hierarchy:\n")
	 		outputClusters([cl], fout, authors=authors)

		undiscovered_hrcs -= seen_hrcs

	fout.write("------------\n")

#		import networkx as nx
#		G_sim = nx.read_weighted_edgelist(skip_comments(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')
	
	for hrc, hpcs in hrc_of_hpc.iteritems():
 		hrc_c = set(hrc_contents[hrc])
		comb = set(list(chain.from_iterable(hpcs)))
		if len(hpcs) == 1 and hrc_c == comb:
			continue
  		outputClusters(hpcs, fout, authors=authors)
  		if len(hpcs) > 1:
			fout.write("--combined:--\n")
			outputClusters([comb], fout, authors=authors)

		singletons = list(hrc_c - comb)
		singletons_r = list(comb - hrc_c)
		if singletons_r:
			fout.write("--in HPC but not in HRC:--\n")
			outputClusters([singletons_r], fout, authors=authors)
		if singletons:
			fout.write("--in HRC but not in HPC:--\n")
			outputClusters([singletons], fout, authors=authors)
			fout.write("--full HRC with singletons:--\n")
			outputClusters([hrc_c], fout, authors=authors)

		check_for_blacklisted(hrc_c, blacklisted_edges, fout)

		fout.write("---------\n")

	if undiscovered_hrcs:
		fout.write("--HRCs never seen:--\n")
		outputClusters((hrc_contents[cl] for cl in undiscovered_hrcs), fout, authors=authors)
		for cl in undiscovered_hrcs:
			check_for_blacklisted(hrc_contents[cl], blacklisted_edges, fout)

if __name__ == "__main__":
	main()