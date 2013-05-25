#!/usr/bin/env python
# Given feature vectors, get similarities
from common import *
import argparse
import csv
import numpy as np
from pprint import pprint

def extract_minmax(reader):
	# get min and max of features
	print_err("Extracting min and max of features for scaling")
	header = reader.next()
	firstline = reader.next()
	vmin = map(float, firstline[2:])
	vmax = list(vmin)
	for i, line in enumerate(reader):
		line[2:] = map(float, line[2:])
		vmin = [min(oldv, newv) for oldv, newv in zip(vmin, line[2:])]
		vmax = [max(oldv, newv) for oldv, newv in zip(vmax, line[2:])]
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')
	return vmin, vmax
	
def combine(reader, writer, vmin, vmax, weights):
	print_err("Combining features using weights")
	header = reader.next()
	for i, line in enumerate(reader):
		line[2:] = [(float(v) - vlow)/(vhigh - vlow) for v, vlow, vhigh in zip(line[2:], vmin, vmax)]
		sim = sum([v * w for v, w in zip(line[2:], weights)])
		writer.writerow((line[0], line[1], sim))
 		if (i+1) % 10000 == 0:
 			print_err(i+1, 'rows done')

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('featfile')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.featfile.replace('.feat','') + '.sim'

	# our weights
	#exact	mid	first	last	lastidf	iFfLidf	affil_sharedidf	suffix
	weights = [4, 4, 4, 1, 3, 3, 24, 4]

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
		weights = map(float, weights)
		weights = [v / sum(weights) for v in weights]

		writer = csv.writer(open(args.outfile, 'wb'))
		combine(reader, writer, vmin, vmax, weights)

if __name__ == "__main__":
	main()