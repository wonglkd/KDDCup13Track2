#!/usr/bin/env python
# Given weighted graph, perform kruskal-based clustering
from common import *
from cluster_common import *
import argparse
import csv
from collections import defaultdict

def get_id(mp, a):
	if a not in mp:
		mp[a] = a
		return a
	if mp[a] == a:
		return a
	else:
		mp[a] = get_id(mp, mp[a])
		return mp[a]

def mergeset(mp, a, b):
	mp[get_id(mp, b)] = get_id(mp, a)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edgelist')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('-t', '--interconnectivity', default=0.80)
	parser.add_argument('-A', '--with-analysis', action='store_true')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edgelist.replace('.prob','') + '.clusters'

	threshold_interconnectivity = float(args.interconnectivity)

	print_err("Loading graph")
	reader = csv.reader(enforce_min(skip_comments(open(args.edgelist, 'rb')), threshold_interconnectivity))
	edges = []
	for i, line in enumerate(reader):
		line[0:2] = map(int, line[0:2])
		line[2] = float(line[2])
		edges.append((line[2], line[0], line[1]))
		if (i+1) % 10000 == 0:
			print_err(i+1, "edges done")

	print_err("Sorting edges by weight")
	edges = sorted(edges, reverse=True)
	
	print_err("Clustering")
	mp = {}
	for i, (w, v1, v2) in enumerate(edges):
		if get_id(mp, v1) != get_id(mp, v2):
			mergeset(mp, v1, v2)
		if (i+1) % 10000 == 0:
			print_err(i+1, "edges done")

	clusters = defaultdict(list)
	for v in mp:
		clusters[get_id(mp, v)].append(v)
	clusters = clusters.values()

	clusters = sorted(clusters, key=len, reverse=True)

 	print_err("Writing clusters")
  	f_out = open(args.outfile, 'wb')

	if not args.with_analysis:
		for cl in clusters:
 			f_out.write(','.join(map(str, sorted(cl))) + '\n')

	if args.with_analysis:
		import networkx as nx
		G_sim = nx.read_weighted_edgelist(skip_comments(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')
		outputClusters(clusters, f_out, G_sim)

if __name__ == "__main__":
	main()