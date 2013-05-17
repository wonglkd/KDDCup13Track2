#!/usr/bin/env python
# Given the blocks, generate edges
import argparse
from itertools import combinations

def getEdges(blockfile):
	edges = set()
	for line in open(blockfile):
		line = sorted([int(v) for v in line.split()])
		for e in combinations(line, 2):
			edges.add(e)
	return sorted(list(edges))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('blockfile')
	args = parser.parse_args()
	
	edges = getEdges(args.blockfile)
	for a, b in edges:
 		print "{0},{1}".format(a, b)

if __name__ == "__main__":
	main()