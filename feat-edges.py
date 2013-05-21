#!/usr/bin/env python
# Given edges, generate features for those with papers
from common import *
import argparse
import csv
import cPickle as pickle
from pprint import pprint
from itertools import imap
import numpy as np
# import itertools as itl

class PaperauthorFeaturesGenerator:
	pa_by_authors = {}
	author_info = {}
	pa_queries_author_ = {
		'name': 'SELECT COUNT(*) as cnt, name FROM paperauthor WHERE AuthorId = ? and name <> "" GROUP BY name',
		'affiliation': 'SELECT COUNT(*) as cnt, affiliation FROM paperauthor WHERE AuthorId = ? and affiliation <> "" GROUP BY affiliation'
	}
	author_query_ = 'SELECT * FROM author WHERE Id = ?'
	
	feat = [
		'pa_name',
		'pa_affil'
	]
	
	def __init__(self, authorfilterfile):
		self.filter = set(imap(int, open(authorfilterfile, 'rb')))
		self.conn = getDB()
	
	def getAuthor(self, aID):
		if aID in self.author_info:
			return
		
		authorinfo = selectDB(self.conn, self.author_query_, [aID])[0]
		self.author_info[authorinfo[0]] = {
			'name': authorinfo[1],
			'affiliation': authorinfo[2]
		}
		
		if aID not in self.filter:
			return

		curr_a = {}

		for field, query in self.pa_queries_author_.iteritems():
			results = selectDB(self.conn, query, [aID])
			total = sum([a for a, _ in results])
			curr_a[field] = {fieldval: cnt / float(total) for cnt, fieldval in results}

		self.pa_by_authors[aID] = curr_a
		return

	def getFieldPA(self, field, a1, a2):
		# missing value
		if a1 not in self.filter:
			return 0.
		a2val = self.author_info[a2][field]
		# missing value
		if not len(a2val):
			return 0.
		if a2val in self.pa_by_authors[a1][field]:
			return self.pa_by_authors[a1][field][a2val]
		else:
			return 0.
	
	def getPABoth(self, field, a1, a2):
		return self.getFieldPA(field, a1, a2) + self.getFieldPA(field, a2, a1)

	def getEdgeFeatures(self, author1, author2):
		self.getAuthor(author1)
		self.getAuthor(author2)
		f = {
			'pa_name': self.getPABoth('name', author1, author2),
			'pa_affil': self.getPABoth('affiliation', author1, author2)
		}
		return f

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edges')
	parser.add_argument('authorfilter', nargs='?', default='data/authors_with_papers.txt')
	parser.add_argument('outfile', nargs='?')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edges.replace('_edges.txt', '') + '.edgefeat'

	PFG = PaperauthorFeaturesGenerator(args.authorfilter)

	rows_skipped = 0
	rows = 0
# 	authors_used = set()
# 	rows_single = 0

	writer = csv.DictWriter(open(args.outfile, 'wb'), dialect='excel-tab', fieldnames=PFG.feat)
	writer.writeheader()

 	for i, (a, b) in enumerate(csv.reader(open(args.edges, 'rb'))):
 		a, b = int(a), int(b)
 		if a not in PFG.filter and b not in PFG.filter:
 			rows_skipped += 1
 		else:
	 		writer.writerow(PFG.getEdgeFeatures(a, b))
	  		rows += 1

#  		elif bool(a in PFG.filter) != bool(b in PFG.filter):
#  			rows_single += 1
#  			if a in PFG.filter:
# 				authors_used.add(a)
# 			else:
# 				authors_used.add(b)
#  			continue
#  		print str(a)+','+str(b)
 		if (i+1) % 10 == 0:
 			print_err(i+1, ' rows done')
 			print_err(rows, ' rows extracted')
 	
	print_err("Rows skipped: {0}".format(rows_skipped))
# 	print_err("Single use", rows_single)
# 	print_err("Both use", rows)
# 	print_err(len(authors_used))

if __name__ == "__main__":
	main()