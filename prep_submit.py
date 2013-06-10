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
	parser.add_argument('-n', '--no-write', action='store_true')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.clusterfile.replace('.clusters','') + '-submit.csv'

	print_err("Reading clusters")
	clusterset = []
	clusterid = {}
	f_clusterfile = skip_front(skip_comments(open(args.clusterfile)))
	
	reader_clusterfile = csv.reader(f_clusterfile)
	for label, line in enumerate(reader_clusterfile):
		line = map(int, line)
		clusterset.append(' '.join(map(str, line)))
		for node in line:
			clusterid[node] = label

	if 'goldstd' in args.clusterfile:
		authorids = sorted(clusterid.keys())
	else:
		print_err("Reading authorfile")
		reader_authors = csv.reader(open(args.authorfile, 'rb'))
		header = reader_authors.next()
		authorids = []
		for line in reader_authors:
			authorids.append(int(line[0]))
		authorids = sorted(set(authorids))
 	
 	print_err("No of clusters:", len(clusterset))
 	print_err("No of authors in clusters:", len(clusterid))
 	
 	if args.no_write:
 		return
 	
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