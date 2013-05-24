#!/usr/bin/env python
# Given edges, generate features for those with papers
from common import *
import argparse
import csv
import cPickle as pickle
from pprint import pprint
from itertools import imap
from collections import defaultdict

class PaperauthorFeaturesGenerator:
	pa_by_authors = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
	author_info = {}
	pa_queries_author_ = {
		'name': 'SELECT COUNT(*) as cnt, name FROM paperauthor WHERE AuthorId = ? and name <> "" GROUP BY name',
		'affiliation': 'SELECT COUNT(*) as cnt, affiliation FROM paperauthor WHERE AuthorId = ? and affiliation <> "" GROUP BY affiliation'
	}
	author_query_ = 'SELECT * FROM author WHERE Id = ?'
	coauthor_query_ = '''SELECT
			(SELECT COUNT(*) FROM
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = ?
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = ?)) as common
		,
			(SELECT COUNT(Coauthor) FROM pa_coauthors co3
			WHERE co3.AuthorId = ?) as cnt1
		,
			(SELECT COUNT(Coauthor) FROM pa_coauthors co4
			WHERE co4.AuthorId = ?) as cnt2'''
	coauthor_query_w_ = '''SELECT
			(SELECT IFNULL(SUM(mc), 0) FROM (SELECT MIN(cnt) as mc FROM
			pa_coauthors co0 JOIN
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = ?
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = ?) co_ ON co_.Coauthor = co0.Coauthor WHERE AuthorId IN (?,?)
			GROUP BY co_.Coauthor
			)) as common
		,
			(SELECT SUM(cnt) FROM pa_coauthors co3
			WHERE co3.AuthorId = ?) as cnt1
		,
			(SELECT SUM(cnt) FROM pa_coauthors co4
			WHERE co4.AuthorId = ?) as cnt2'''

	pa_files_ = {
		'name': 'authordata/pa_names_u.csv',
 		'affiliation': 'authordata/pa_affiliation_u.csv',
		'conferences': 'authordata/pa_conferences.csv',
		'journals': 'authordata/pa_journals.csv',
 		'years': 'authordata/pa_years.csv'
	}
	
	fields = [
		'pa_name',
		'pa_affil',
		'conferences',
		'conferencesW',
		'journals',
		'journalsW',
		'years',
		'yearscore',
# 		'coauthor',
# 		'coauthorW'
	]
	
	fields_num_index = set([
		'conferences',
		'journals',
		'years'
	])
	
	def __init__(self, authorprefeat, authorfilterfile='data/authors_with_papers.txt'):
		self.filter = set(imap(int, open(authorfilterfile, 'rb')))
		self.conn = getDB()
 		self.conn_pa = getDB('pa')

		self.author_info = authorprefeat
 		for field, filename in self.pa_files_.iteritems():
 			with open(filename) as f:
 				print_err("Loading file", filename)
 				reader = csv.reader(f)
 				reader.next()
 				for line in reader:
	 				if field in self.fields_num_index:
	 					line[1] = int(line[1])
 					self.pa_by_authors[int(line[0])][field][line[1]] += int(line[2])
 		for author, paf in self.pa_by_authors.iteritems():
 			for field, pai in paf.iteritems():
 				total = sum(pai.values())
 				self.pa_by_authors[author][field] = {val: cnt / float(total) for val, cnt in pai.iteritems()}
	
	def sim(self, common, len1, len2):
		if common == 0:
			return 0.
		return common / float(min(len1, len2))
		# Jaccard
		# return common / float(len1 + len2)
	
	def dictSim(self, a, b):
		if not a or not b:
			return 0.
		n = len(set(a.keys()) & set(b.keys()))
		return self.sim(n, len(a), len(b))
	
	def dictSimW(self, a, b):
		if not a or not b:
			return 0.
		common = set(a.keys()) & set(b.keys())
		total_common = sum([min(a[v], b[v]) for v in common])
		return self.sim(total_common, sum(a.values()), sum(b.values()))

	def getAuthor(self, aID):
		if aID in self.author_info:
			return
		
		authorinfo = selectDB(self.conn, self.author_query_, [aID]).next()
		self.author_info[authorinfo[0]] = {
			'name': authorinfo[1].replace(';','').strip().lower(),
			'affiliation': authorinfo[2].lower()
		}
		
		if aID not in self.filter or aID in self.pa_by_authors:
			return

 		curr_a = {}

		for field, query in self.pa_queries_author_.iteritems():
			results = selectDB(self.conn, query, [aID])
			total = sum([a for a, _ in results])
			curr_a[field] = {fieldval: cnt / float(total) for cnt, fieldval in results}

		self.pa_by_authors[aID] = curr_a
		return
	
	def getCoauthorsSim(self, a1, a2):
		common, len1, len2 = selectDB(self.conn_pa, self.coauthor_query_, [a1, a2, a1, a2]).next()
		return self.sim(common, len1, len2)

	def getCoauthorsSimW(self, a1, a2):
		common, len1, len2 = selectDB(self.conn_pa, self.coauthor_query_w_, [a1, a2, a1, a2, a1, a2]).next()
		return self.sim(common, len1, len2)

	def getFieldPA(self, field, a1, a2):
		# missing value
		if a1 not in self.filter:
			return 0.
		a2val = self.author_info[a2][field]
		# missing value
		if not len(a2val) or a2val.startswith('ID:'):
			return 0.
		if a2val in self.pa_by_authors[a1][field]:
			return self.pa_by_authors[a1][field][a2val]
		else:
			return 0.
	
	def getPABoth(self, field, a1, a2):
		return self.getFieldPA(field, a1, a2) + self.getFieldPA(field, a2, a1)

	def getSetSim(self, field, a1, a2):
		return self.dictSim(self.pa_by_authors[a1][field], self.pa_by_authors[a2][field])

	def getSetSimW(self, field, a1, a2):
		return self.dictSimW(self.pa_by_authors[a1][field], self.pa_by_authors[a2][field])
	
	def getYearScore(self, a1, a2):
		k1 = self.pa_by_authors[a1]['years'].keys()
		k2 = self.pa_by_authors[a2]['years'].keys()
		if not k1 or not k2:
			return 0
		x1, x2 = min(k1), max(k1)
		y1, y2 = min(k2), max(k2)
		return min(x2, y2) - max(x1, y1) + 1

	def getEdgeFeatures(self, author1, author2):
# 		self.getAuthor(author1)
# 		self.getAuthor(author2)
		f = defaultdict(float)
		f.update({
			'pa_name': self.getPABoth('name', author1, author2),
			'pa_affil': self.getPABoth('affiliation', author1, author2),
			'conferences': 0,
			'conferencesW': 0,
			'journals': 0,
			'journalsW': 0,
			'years': 0,
			'yearscore': 0,
# 			'coauthor': 0,
# 			'coauthorW': 0
		})
		if author1 in self.filter and author2 in self.filter:
			f.update({
				'conferences': self.getSetSim('conferences', author1, author2),
				'conferencesW': self.getSetSimW('conferences', author1, author2),
				'journals': self.getSetSim('journals', author1, author2),
				'journalsW': self.getSetSimW('journals', author1, author2),
				'years': self.getSetSim('years', author1, author2),
				'yearscore': self.getYearScore(author1, author2),
# 				'coauthor': self.getCoauthorsSim(author1, author2),
# 				'coauthorW': self.getCoauthorsSimW(author1, author2)
			})
		return f

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('edges')
	parser.add_argument('authorfilter', nargs='?', default='data/authors_with_papers.txt')
	parser.add_argument('outfile', nargs='?')
	parser.add_argument('authorprefeat', nargs='?', default='generated/Author_prefeat.pickle')
	args = parser.parse_args()
	if args.outfile == None:
		args.outfile = args.edges.replace('_edges.txt', '') + '.edgefeat'

 	print_err("Loading pickled author pre-features")
   	authors = pickle.load(open(args.authorprefeat, 'rb'))
#   	authors = {}
	PFG = PaperauthorFeaturesGenerator(authors, args.authorfilter)

	rows_skipped = 0
	rows = 0

	writer = csv.DictWriter(open(args.outfile, 'wb'), dialect='excel-tab', fieldnames=['a1','a2']+PFG.fields)
	writer.writeheader()

 	for i, (a, b) in enumerate(csv.reader(open(args.edges, 'rb'))):
 		a, b = int(a), int(b)
 		if a not in PFG.filter and b not in PFG.filter:
 			rows_skipped += 1
 		else:
 			f = PFG.getEdgeFeatures(a, b)
 			f = {k: '{:g}'.format(v) for k, v in f.iteritems()}
 			f['a1'], f['a2'] = a, b
	 		writer.writerow(f)
	  		rows += 1

 		if (i+1) % 100 == 0:
 			print_err(i+1, ' rows done;', rows, ' rows extracted')
 	
	print_err("Rows skipped: {0}".format(rows_skipped))

if __name__ == "__main__":
	main()