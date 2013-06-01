#!/usr/bin/env python
from common import *
from pprint import pprint
import argparse
try:
	import networkx as nx
except ImportError:
	print_err("Could not import networkx")

def getCluster(line, query, conn, raworder=False, G_prob=None):
	if ';' in line:
		line = line.split(';')[1]
	cluster = line.strip().split(',')
	output = []
	for v in cluster:
		res = selectDB(conn, query + ' WHERE a.Id = '+v+' LIMIT 2')
		for line in res:
			output.append(line)
	if not raworder:
		output = sorted(output)
	print_err(len(output), 'rows')
	if G_prob is not None and len(cluster) > 1:
		sg = G_prob.subgraph(map(int, cluster))
		print('V: {:}, E: {:}'.format(len(sg), sg.number_of_edges()))
		unweighted_density = nx.density(sg)
		weighted_density = sg.size(weight='weight')
		if len(sg) > 1:
			weighted_density /= (.5 * len(sg) * (len(sg) - 1))
		print("Density: {:g}, WDen: {:g}, AvgEWeight: {:g}".format(unweighted_density, weighted_density, (sg.size(weight='weight') / float(sg.number_of_edges()))))
	for line in output:
		print line[0], line[1:]
	print('-----------')

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('qtype', nargs='?', default='author')
	parser.add_argument('-i', '--interactive', action='store_true')
	parser.add_argument('-s', '--raworder', action='store_true')
	parser.add_argument('-l', '--loadinput', default='analysis/analyse.clusters.tmp')
	parser.add_argument('-g', '--loadgraph')
	args = parser.parse_args()
	
	queries = {
		'author': '''SELECT * FROM author a''',
		'all': '''SELECT a.*, pa.name, pa.affiliation, p.title, p.year, p.journalId, p.conferenceId FROM
	(author a LEFT JOIN paperauthor pa ON AuthorID = a.Id)
	LEFT JOIN paper p ON p.Id = PaperId'''
	}

	if args.loadgraph is not None:
		print_err("Reading edges", args.loadgraph)
		G_prob = nx.read_weighted_edgelist(args.loadgraph, delimiter=',', nodetype=int)
	else:
		G_prob = None

	with getDB() as conn:
		if args.interactive:
			while True:
				line = raw_input("Cluster: ")
				if not line:
					break
				getCluster(line, queries[args.qtype], conn, args.raworder, G_prob)
		else:
			with open(args.loadinput) as f:
				for line in skip_comments(f):
					getCluster(line, queries[args.qtype], conn, args.raworder, G_prob)

if __name__ == "__main__":
	main()

# clusters = [cl.strip().split(',') for cl in clusters.split('\n')]
# for cl in clusters:
# 	for a1, a2 in combinations(cl, 2):
# 		print ",".join(['1', a1, a2])
# 
# for a, b in combinations(clusters, 2):
# 	for a1, b1 in product(a, b):
# 		print ",".join(['0', a1, b1])
# 
# 
# from process_authors import *
# 
# abc = loadAuthors('data/Author_s100.csv')
# pprint(abc[423])
# 
# WHERE a.Id IN (96610)
# LIMIT 50;
# SELECT * FROM paperauthor WHERE AuthorID IN (96610);
# SELECT * FROM author WHERE ID IN (96610);
