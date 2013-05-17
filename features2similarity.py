#!/usr/bin/env python
# Given feature vectors, get similarities
import argparse
import csv
# import numpy as np
# from pprint import pprint

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('featfile')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.featfile + '.sim'

if __name__ == "__main__":
	main()