#!/usr/bin/env python
# Given the blocks, generate edges
# import argparse
from common import *
import fileinput
from itertools import combinations

def getEdges(blockfile):
	edges = set()
	for line in skip_comments(blockfile):
		line = line.split(';')[1]
		line = sorted([int(v) for v in line.split(',')])
		for e in combinations(line, 2):
			edges.add(e)
	return sorted(list(edges))

def main():
# 	parser = argparse.ArgumentParser()
# 	parser.add_argument('blockfile')
# 	args = parser.parse_args()
	
	edges = getEdges(fileinput.input())
	for a, b in edges:
 		print "{0},{1}".format(a, b)

if __name__ == "__main__":
	main()