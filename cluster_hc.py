#!/usr/bin/env python
# Given weighted graph, perform hierarchical clustering
from common import *
import argparse
import csv
import numpy as np
import scipy as sp
import cPickle as pickle
from pprint import pprint
import networkx as nx
from itertools import combinations, product
import heapq as hq
from cluster_common import *
# from collections import defaultdict

def getSimilarity_Average(G_sim, cl1, cl2):
	edge_sum = sum([G_sim[v1][v2]['weight'] for v1, v2 in product(cl1, cl2) if G_sim.has_edge(v1, v2)])
	return edge_sum / float(len(cl1) * len(cl2))

def getSimilarity_AvgPresent(G_sim, cl1, cl2):
	edgeweights = [G_sim[v1][v2]['weight'] for v1, v2 in product(cl1, cl2) if G_sim.has_edge(v1, v2)]
	return sum(edgeweights) / float(len(edgeweights))

def getSimilarity_Min(G_sim, cl1, cl2):
	return min([G_sim[v1][v2]['weight'] for v1, v2 in product(cl1, cl2) if G_sim.has_edge(v1, v2)])

def hcluster(G_sim, threshold_sim, sim_func):
	sim_funcs = {
		'average': getSimilarity_Average,
		'avgpresent': getSimilarity_AvgPresent,
		'min': getSimilarity_Min
	}
	chosen_simfunc = sim_funcs[sim_func]
	print_err("Finding connected components")
	connected_components = nx.connected_component_subgraphs(G_sim)
	all_clusters = []
	print_err('Clustering', len(connected_components), 'components')
	for component_i, cc in enumerate(connected_components):
 		print_err('Starting component', component_i+1, 'of', len(connected_components), '(V={:}, E={:})'.format(len(cc), cc.size()))
 		if len(cc) == 2:
 			cl = list(cc.nodes())
 			if cc.size(weight='weight') >= threshold_sim:
 				all_clusters.append(cl)
 			continue
 		elif len(cc) < 2:
 			continue
		clusters = [[v] for v in cc]
		removed = set()
		adjclusters = [set() for i in xrange(len(cc))]
		c_sim = nx.to_scipy_sparse_matrix(cc, weight='weight', format='coo')
		pq = [(sim, r, c) for (sim, r, c) in zip(-c_sim.data, c_sim.row, c_sim.col) if r < c]
		for _, r, c in pq:
			adjclusters[r].add(c)
			adjclusters[c].add(r)
 		hq.heapify(pq)
		
 		while pq:
 			similarity, c1, c2 = hq.heappop(pq)
 			similarity = -similarity
 			if c1 in removed or c2 in removed:
 				continue
 			if similarity < threshold_sim:
 				break
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
 				nsim = chosen_simfunc(G_sim, clusters[-1], clusters[nc])
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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edgelist')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('-t', '--interconnectivity', default=0.83, type=float)
	parser.add_argument('-d', '--density', default=0.83, type=float)
	parser.add_argument('-m', '--min-edge', default=0.05, type=float)
	parser.add_argument('-l', '--linkage', default='average')
	parser.add_argument('-a', '--authorprefeat', default='generated/Author_prefeat.pickle')
	args = parser.parse_args()

	if args.outfile == None:
		args.outfile = args.edgelist.replace('.prob','') + '.clusters'

	threshold_min_weight = args.min_edge
	threshold_interconnectivity = args.interconnectivity
	threshold_density = args.density

	print_err("Loading graph")
	G_sim = nx.read_weighted_edgelist(enforce_min(skip_comments(open(args.edgelist, 'rb')), threshold_min_weight), nodetype=int, delimiter=',')
	print_err('Loaded (V={:}, E={:})'.format(len(G_sim), G_sim.size()))

	print_err("Clustering")
	clusters = hcluster(G_sim, threshold_interconnectivity, args.linkage)

 	print_err("Writing clusters")
 	
	G_nsim = nx.read_weighted_edgelist(skip_comments(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')

	print_err("Loading pickled author pre-features")
  	authors = pickle.load(open(args.authorprefeat, 'rb'))

 	outputClusters(clusters, open(args.outfile, 'wb'), G_nsim, authors, threshold_density)

if __name__ == "__main__":
	main()