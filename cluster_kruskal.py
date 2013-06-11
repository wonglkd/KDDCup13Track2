#!/usr/bin/env python
# Given weighted graph, perform kruskal-based clustering
from common import *
from cluster_common import *
import argparse
import csv
import cPickle as pickle
from collections import defaultdict

class unionfind:
	mp = {}
	blacklisted_edges = set()
# 	blacklisted_e_nodes = set()
# 	blacklist_edges_adj = defaultdict(set)

	def get_id(self, a):
		if a not in self.mp:
			self.mp[a] = a
			return a
		if self.mp[a] == a:
			return a
		else:
			self.mp[a] = self.get_id(self.mp[a])
			return self.mp[a]
	
	def mergeset(self, a, b):
		self.mp[self.get_id(b)] = self.get_id(a)
	
	def mergeall(self, a):
		d = self.get_id(a[0])
		for b in a[1:]:
			self.mp[self.get_id(b)] = d

	def disallow(self, v1, v2):
		if v2 > v1:
			v1, v2 = v2, v1
		self.blacklisted_edges.add((v1, v2))
# 		self.blacklisted_e_nodes.add(v1)
# 		self.blacklisted_e_nodes.add(v2)
# 		self.blacklist_edges[v1].add(v2)
# 		self.blacklist_edges[v2].add(v1)

	def check_for_blacklist(self, v1, v2):
		v1, v2 = self.get_id(v1), self.get_id(v2)
		if v2 > v1:
			v1, v2 = v2, v1
		for e1, e2 in self.blacklisted_edges:
			c1, c2 = self.get_id(e1), self.get_id(e2)
			if c2 > c1:
				c1, c2 = c2, c1
			if c1 == v1 and c2 == v2:
				return True
		return False

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edgelist')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('-t', '--interconnectivity', default=0.82, type=float)
	parser.add_argument('-A', '--with-analysis', action='store_true')
	parser.add_argument('-a', '--authorprefeat', default='generated/Author_prefeat.pickle')
	parser.add_argument('-s', '--seedset', nargs='*', default=['data/goldstd_clusters.csv', 'data/seedset_clusters.csv'])
	parser.add_argument('-b', '--blacklist', nargs='*', default=['data/blacklist_edges.csv'])
	args = parser.parse_args()

	if args.outfile == None:
		args.outfile = args.edgelist.replace('.prob','') + '.clusters'

	threshold_interconnectivity = args.interconnectivity

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
	
	uf = unionfind()

	if args.seedset is not None:
		print_err("Loading seedset(s)")
		for filename in args.seedset:
			for cl in loadClusters(filename):
				if len(cl) < 2:
					continue
				uf.mergeall(cl)
	
	if args.blacklist is not None:
		for filename in args.blacklist:
			with open(filename, 'rb') as f:
				reader = csv.reader(skip_comments(f))
				for line in reader:
					if len(line) > 2:
						if line[0] == 1:
							continue
						line = line[1:]
					line[0:2] = map(int, line[0:2])
					uf.disallow(line[0], line[1])
	
	print_err("Clustering")
	for i, (w, v1, v2) in enumerate(edges):
		if uf.get_id(v1) != uf.get_id(v2) and not uf.check_for_blacklist(v1, v2):
			uf.mergeset(v1, v2)
		if (i+1) % 10000 == 0:
			print_err(i+1, "edges done")

	clusters = defaultdict(list)
	for v in uf.mp:
		clusters[uf.get_id(v)].append(v)
	clusters = [v for v in clusters.values() if len(v) > 1]

	clusters = sorted(clusters, key=len, reverse=True)

 	print_err("Writing clusters")
  	f_out = open(args.outfile, 'wb')

	if not args.with_analysis:
		for cl in clusters:
 			f_out.write(','.join(map(str, sorted(cl))) + '\n')

	if args.with_analysis:
		print_err("Loading pickled author pre-features")
		authors = pickle.load(open(args.authorprefeat, 'rb'))
		import networkx as nx
		G_sim = nx.read_weighted_edgelist(skip_comments(open(args.edgelist, 'rb')), nodetype=int, delimiter=',')
		outputClusters(clusters, f_out, G_sim, authors)

if __name__ == "__main__":
	main()