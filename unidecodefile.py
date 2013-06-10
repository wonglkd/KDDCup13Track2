#!/usr/bin/env python
from unidecode import unidecode
import fileinput
import csv
import argparse
import sys
from common import strip_punc

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', nargs='?', default='-')
	parser.add_argument('outfile', nargs='?', default='-')
	parser.add_argument('-c', '--cols', nargs='*', default=[1])
	parser.add_argument('-a', '--all-cols', action='store_true')
	parser.add_argument('-p', '--strip-punc', action='store_true')
	args = parser.parse_args()

	f_in = open(args.infile, 'rb') if args.infile != '-' else sys.stdin
	f_write = open(args.outfile, 'wb') if args.outfile != '-' else sys.stdout

	args.cols = map(int, args.cols)

	reader = csv.reader(f_in)
	if args.all_cols:
		args.cols = range(len(reader.next()))
		f_in.seek(0)
	
	writer = csv.writer(f_write)
	for i, line in enumerate(reader):
		for c in args.cols:
			line[c] = unidecode(unicode(line[c], 'utf-8')).strip().lower()
		if args.strip_punc:
			for c in args.cols:
				line[c] = strip_punc(line[c])
		writer.writerow(line)
		if (i+1) % 10000 == 0:
			print i+1, "lines done"

if __name__ == "__main__":
	main()