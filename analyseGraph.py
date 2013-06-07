#!/usr/bin/env python
# Extract selected components for analysis
from common import *
import argparse
import csv
import numpy as np
import scipy as sp
from pprint import pprint
import networkx as nx
from cluster_common import *

def analyse(G_sim, threshold_sim):
	print_err("Finding connected components")
	connected_components = nx.connected_component_subgraphs(G_sim)
	cclist = []
	print_err('Clustering', len(connected_components), 'components')
	for component_i, cc in enumerate(connected_components):
 		print_err('Starting component', component_i+1, 'of', len(connected_components), '(V={:}, E={:})'.format(len(cc), cc.size()))
 		if component_i == 0:
 			continue
 		if len(cc) == 3:
 			return cclist
 		cclist.extend(list(cc.nodes()))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edgelist', nargs='?', default='analysis/combined_716eef6.prob')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('-t', '--interconnectivity', default=0.80)
	parser.add_argument('-d', '--density', default=0.80)
	parser.add_argument('-m', '--min-edge', default=0.20)
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edgelist.replace('.prob','') + '.analysis.tmp'

	threshold_min_weight = args.min_edge
	threshold_interconnectivity = args.interconnectivity
	threshold_density = args.density

	print_err("Loading graph")
	G_sim = nx.read_weighted_edgelist(enforce_min(skip_comments(open(args.edgelist, 'rb')), threshold_min_weight), nodetype=int, delimiter=',')
	print_err('Loaded (V={:}, E={:})'.format(len(G_sim), G_sim.size()))

	cc = analyse(G_sim, threshold_interconnectivity)	
	
	nx.write_weighted_edgelist(G_sim.subgraph(cc), args.outfile)

if __name__ == "__main__":
	main()