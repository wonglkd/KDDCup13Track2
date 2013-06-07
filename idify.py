#!/usr/bin/env python
import csv
import argparse
import sys
from common import verbose_iter

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', nargs='?', default='-')
	parser.add_argument('outfile', nargs='?', default='-')
	parser.add_argument('-c', '--col', default=1, type=int)
	args = parser.parse_args()
	
	f_write = open(args.outfile, 'wb') if args.outfile != '-' else sys.stdout
	f_in = open(args.infile, 'rb') if args.infile != '-' else sys.stdin
	
	seen = {}
	
	writer = csv.writer(f_write)
	reader = csv.reader(f_in)
	writer.writerow(reader.next()) # skip header
	for i, line in verbose_iter(reader):
		if line[args.col] not in seen:
			seen[line[args.col]] = len(seen)
		line[args.col] = seen[line[args.col]]
		writer.writerow(line)

if __name__ == "__main__":
	main()