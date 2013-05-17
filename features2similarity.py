#!/usr/bin/env python
# Given feature vectors, get similarities
import argparse
import csv
import numpy as np
from pprint import pprint

def extract_minmax(reader):
	# get min and max of features
	header = reader.next()
	firstline = reader.next()
	vmin = map(float, firstline[2:])
	vmax = list(vmin)
	for line in reader:
		line[2:] = map(float, line[2:])
		vmin = [min(oldv, newv) for oldv, newv in zip(vmin, line[2:])]
		vmax = [max(oldv, newv) for oldv, newv in zip(vmax, line[2:])]
	return vmin, vmax
	
def combine(reader, writer, vmin, vmax, weights):
	header = reader.next()
	for line in reader:
		line[2:] = [(float(v) - vlow)/(vhigh - vlow) for v, vlow, vhigh in zip(line[2:], vmin, vmax)]
		sim = sum([v * w for v, w in zip(line[2:], weights)])
		writer.writerow((line[0], line[1], sim))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('featfile')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.featfile.replace('.feat','') + '.sim'

	# our weights
	weights = [1.] * 8

	with open(args.featfile) as f_featfile:
		reader = csv.reader(f_featfile, dialect='excel-tab')
		vmin, vmax = extract_minmax(reader)
		f_featfile.seek(0)

		# remove features that don't have change
		for i, (a, b) in enumerate(zip(vmin, vmax)):
			if a == b:
				weights[i] = 0
				vmin[i], vmax[i] = 0., 1.

		# normalize
		weights = [v / sum(weights) for v in weights]

		writer = csv.writer(open(args.outfile, 'wb'), dialect='excel-tab')
		combine(reader, writer, vmin, vmax, weights)

if __name__ == "__main__":
	main()