#!/usr/bin/env python
from unidecode import unidecode
import fileinput
import csv
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', nargs='?', default='-')
	parser.add_argument('outfile', nargs='?', default='-')
	parser.add_argument('-c', '--cols', nargs='*', default=[1])
	parser.add_argument('-a', '--all-cols', action='store_true')
	args = parser.parse_args()

	f_in = open(args.infile, 'rb') if args.infile != '-' else sys.stdin
	f_write = open(args.outfile, 'wb') if args.outfile != '-' else sys.stdout

	args.cols = map(int, args.cols)

	writer = csv.writer(f_write)
	for i, line in enumerate(csv.reader(f_in)):
		if args.all_cols:
			line = [unidecode(unicode(cell, 'utf-8')).strip().lower() for cell in line]
		else:
			for c in args.cols:
				line[c] = unidecode(unicode(line[c], 'utf-8')).strip().lower()
		writer.writerow(line)
		if (i+1) % 10000 == 0:
			print i+1, "lines done"

if __name__ == "__main__":
	main()