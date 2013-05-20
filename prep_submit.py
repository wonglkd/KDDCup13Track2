#!/usr/bin/env python
# Given list of clusters, prepare submission format
from common import *
import argparse
import csv
from pprint import pprint
import sys

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('clusterfile')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('authorfile', nargs='?', default='data/Author.csv')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edgelist.replace('.sim','') + '-submit.csv'

	print_err("Reading clusters")
	clusterset = []
	clusterid = {}
	reader_clusterfile = csv.reader(open(args.clusterfile))
	for label, line in enumerate(reader_clusterfile):
		line = map(int, line)
		clusterset.append(' '.join(map(str, line)))
		for node in line:
			clusterid[node] = label

	print_err("Reading authorfile")
	reader_authors = csv.reader(open(args.authorfile, 'rb'))
	header = reader_authors.next()
	authorids = []
	for line in reader_authors:
		authorids.append(int(line[0]))
 	authorids = sorted(set(authorids))
 	
	print_err("Writing submission")
 	writer = csv.writer(open(args.outfile, 'wb'))
 	writer.writerow(['AuthorId','DuplicateAuthorIds'])
 	for id in authorids:
 		if id in clusterid:
 			label = clusterset[clusterid[id]]
 		else:
 			label = id
 		writer.writerow([id, label])

if __name__ == "__main__":
	main()