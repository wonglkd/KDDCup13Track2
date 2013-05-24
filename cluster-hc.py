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

def hcluster(G_sim, threshold_sim):
	connected_components = nx.connected_component_subgraphs(G_sim)
	all_clusters = []
	for cc in connected_components:
		clusters = [[v] for v in cc]
		removed = set()
		adjclusters = [set()] * len(cc)
		c_sim = nx.to_scipy_sparse_matrix(cc, weight='weight', format='coo')
		pq = [(sim, r, c) for (sim, r, c) in zip(-c_sim.data, c_sim.row, c_sim.col) if r < c]
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
#  			print_err(clusters[c1])
#  			print_err(clusters[c2])
# 			print_err(c1, c2, similarity)
# 			for i, cl in enumerate(clusters):
# 				if i not in removed:
# 					print_err(i, cl)
# 			print_err("--")
	 		clusters.append(clusters[c1] + clusters[c2])
 			removed.add(c1)
 			removed.add(c2)
 			toremove = set([c1, c2])
 			adjclusters.append((adjclusters[c1] | adjclusters[c2]) - toremove)
 			for nc in adjclusters[-1]:
 				if nc in removed:
 					continue
 				adjclusters[nc] -= toremove
 				adjclusters[nc].add(len(clusters)-1)
 				nsim = getSimilarity(G_sim, clusters[-1], clusters[nc])
 				if nsim >= threshold_sim:
 					hq.heappush(pq, (-nsim, len(clusters)-1, nc))
#  				else:
#  					print_err("Not merged:")
# 					print_err(len(clusters)-1, clusters[len(clusters)-1])
# 					print_err(nc, clusters[nc])
# 					print_err(len(clusters)-1, nc, nsim)
# 			print_err("----")
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
	parser.add_argument('--interconnectivity', default=0.7)
	parser.add_argument('--density', default=0.7)
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edgelist.replace('.prob','') + '.clusters'

	threshold_interconnectivity = args.interconnectivity
	threshold_density = args.density

	print_err("Loading graph")
	G_sim = nx.read_weighted_edgelist(skip_zero(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')

	print_err("Clustering")
	clusters = hcluster(G_sim, threshold_interconnectivity)

 	print_err("Writing clusters")
 	f_out = open(args.outfile, 'w')
 	
 	clusters_o = []
 	
 	for clist in clusters:
 		cl = G_sim.subgraph(clist)
		cl_nodes = len(cl)
		cl_edges = cl.number_of_edges()
		cl_unweighted_density = nx.density(cl)
		cl_weighted_density = cl.size(weight='weight')

		if cl_nodes != 1:
			cl_weighted_density /= (.5 * cl_nodes * (cl_nodes - 1))
		if cl_weighted_density >= threshold_density:
			clusters_o.append((cl_nodes, cl_weighted_density, cl_edges, cl_unweighted_density, ','.join(map(str, sorted(clist)))))
		else:
			print_err(cl_nodes, cl_edges, cl_unweighted_density, cl_weighted_density)
	
	for cl_nodes, cl_weighted_density, cl_edges, cl_unweighted_density, clstr in sorted(clusters_o, reverse=True):
		print cl_nodes, cl_edges, cl_unweighted_density, cl_weighted_density
		f_out.write('{:},{:g};{:}\n'.format(cl_nodes, cl_weighted_density, clstr))			

if __name__ == "__main__":
	main()