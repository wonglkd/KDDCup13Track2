#!/usr/bin/env python
# Given weighted graph, perform hierarchical clustering
from common import *
import argparse
import csv
import numpy as np
import scipy as sp
from pprint import pprint
import networkx as nx
from itertools import combinations, product
import heapq as hq
# from collections import defaultdict

def getSimilarity(G_sim, cl1, cl2):
	edge_sum = sum([G_sim[v1][v2]['weight'] for v1, v2 in product(cl1, cl2) if G_sim.has_edge(v1, v2)])
	return edge_sum / float(len(cl1) * len(cl2))

def hcluster(G_sim, threshold_sim=0.5):
	connected_components = nx.connected_component_subgraphs(G_sim)
	all_clusters = []
	for cc in connected_components:
		clusters = [[v] for v in cc]
		removed = set()
		adjclusters = [set()] * len(cc)
		c_sim = nx.to_scipy_sparse_matrix(cc, weight='weight', format='coo')
		pq = list(zip(-c_sim.data, c_sim.row, c_sim.col))
		for _, r, c in pq:
			adjclusters[r].add(c)
			adjclusters[c].add(r)
 		hq.heapify(pq)
# 		c_sim = c_sim.tolil()
		
 		while pq:
 			similarity, c1, c2 = hq.heappop(pq)
 			similarity = -similarity
 			if c1 in removed or c2 in removed:
 				continue
 			if similarity < threshold_sim:
 				break
#  			print similarity, c1, c2
	 		clusters.append(clusters[c1] + clusters[c2])
 			removed.add(c1)
 			removed.add(c2)
 			adjclusters.append((adjclusters[c1].union(adjclusters[c2])) - set([c1, c2]))
 			for nc in adjclusters[-1]:
 				nsim = getSimilarity(G_sim, clusters[-1], clusters[nc])
 				if nsim >= threshold_sim:
 					hq.heappush(pq, (-nsim, len(clusters)-1, nc))
 		all_clusters.extend([cl for i, cl in enumerate(clusters) if i not in removed and len(cl) > 1])
 	return sorted(all_clusters, key=len, reverse=True)
 
def skip_zero(iterable):
    for line in iterable:
        if not line.endswith(',0'):
            yield line

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edgelist')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edgelist.replace('.prob','') + '.clusters'

	threshold_interconnectivity = 0.4
	threshold_density = 0.5

	print_err("Loading graph")
	G_sim = nx.read_weighted_edgelist(skip_zero(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')

	print_err("Clustering")
	clusters = hcluster(G_sim, threshold_interconnectivity)

 	print_err("Writing clusters")
 	writer = csv.writer(open(args.outfile, 'wb'))
 	for clist in clusters:
 		cl = G_sim.subgraph(clist)
		cl_nodes = len(cl)
		cl_edges = cl.number_of_edges()
		cl_unweighted_density = nx.density(cl)
		cl_weighted_density = cl.size(weight='weight')
		if cl_nodes != 1:
			cl_weighted_density /= (.5 * cl_nodes * (cl_nodes - 1))
		if cl_weighted_density >= threshold_density:
			print cl_nodes, cl_edges, cl_unweighted_density, cl_weighted_density
			writer.writerow(sorted(clist))
		else:
			print_err(cl_nodes, cl_edges, cl_unweighted_density, cl_weighted_density)

if __name__ == "__main__":
	main()