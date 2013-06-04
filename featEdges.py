#!/usr/bin/env python
# Given edges, generate features for those with papers
from common import *
import argparse
import csv
import cPickle as pickle
from pprint import pprint
from itertools import imap
from collections import defaultdict
import scipy as sp
from scipy.stats import scoreatpercentile

class PaperauthorFeaturesGenerator:
	# [authorid][field][value]
	pa_by_authors = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
	pa_by_authors_totals = defaultdict(dict)
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
			(SELECT cnt FROM pa_coauthors_total
			WHERE AuthorId = ?) as cnt1
		,
			(SELECT cnt FROM pa_coauthors_total
			WHERE AuthorId = ?) as cnt2'''
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
			(SELECT total FROM pa_coauthors_total
			WHERE AuthorId = ?) as cnt1
		,
			(SELECT total FROM pa_coauthors_total
			WHERE AuthorId = ?) as cnt2'''
	coauthor_query_f_ = '''SELECT IFNULL(SUM(CoauthorF),0) FROM
		(SELECT co0.Coauthor, co0.AuthorId, co0.cnt, pact.total, co0.cnt*1.0 / pact.total As CoauthorF
		FROM
			(pa_coauthors co0 JOIN
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = ?
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = ?) co_ ON co_.Coauthor = co0.Coauthor)
			JOIN pa_coauthors_total pact ON pact.AuthorId = co0.AuthorId
			WHERE co0.AuthorId IN (?,?)
			GROUP BY co0.Coauthor, co0.AuthorId)'''

	pa_files_ = {
# 		'name': 'authordata/pa_names_u.csv',
		'fullname': 'authordata/pa_names_u_strippunc.csv',
 		'affiliation': 'authordata/pa_affiliation_u.csv',
		'conferences': 'authordata/pa_conferences.csv',
		'paperids': 'authordata/pa_paperids.csv',
		'paperids_inpaper_titlenoblank': 'authordata/pa_paperids_inpaper_titlenoblank.csv',
		'journals': 'authordata/pa_journals.csv',
		'years': 'authordata/pa_years.csv',
		'titles_idified': 'authordata/pa_titles_idified.csv'
# 		'titles_dup_idified': 'authordata/pa_titles_dup_idified.csv'
	}
	
	fields = [
		'has_papers',
		'pa_fullname',
		'pa_affil',
		'fullnames',
		'fullnamesF',
		'affiliations',
		'affiliationsF',
		'conferences',
		'conferencesF',
		'journals',
		'journalsF',
		'years',
		'coauthor',
		'coauthorW',
		'coauthorF',
		'paperIDs',
		'paperIDsF',
# 		'paperIDs_p_title',
# 		'paperIDs_p_titleF'
# 		'titles_dup',
		'titles_dupW',
		'yearscore',
		'pubTextSim'
	]
	
	fields_num_index = set([
		'conferences',
		'journals',
		'years',
		'paperids',
		'paperids_inpaper_titlenoblank',
		'titles_dup_idified'
	])
	
	def __init__(self, authorprefeat, authorfilterfile='data/authors_with_papers.txt', publicationtfidffile='textdata/publication_tfidf.pickle'):
		self.filter = set(imap(int, open(authorfilterfile, 'rb')))
		self.TextSimVecs = pickle.load(open(publicationtfidffile, 'rb'))
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
	
	def sim(self, common, len1, len2):
		if common == 0:
			return 0.
		# return common
		return common / float(min(len1, len2))
		# Jaccard
		# return common / float(len1 + len2 - common)
	
	def dictSim(self, a, b):
		if not a or not b:
			return 0, len(a), len(b)
		n = len(set(a.keys()) & set(b.keys()))
		return (n, len(a), len(b))
	
	def dictSimW(self, a, b):
		if not a or not b:
			return 0, sum(a.values()), sum(b.values())
		common = set(a.keys()) & set(b.keys())
		total_common = sum([min(a[v], b[v]) for v in common])
 		return (total_common, sum(a.values()), sum(b.values()))

	def dictSimF(self, a, b, ta=1, tb=1):
		if not a or not b:
			return 0.
		common = set(a.keys()) & set(b.keys())
		total_common = sum([min(a[v] / float(ta), b[v] / float(tb)) for v in common])
		return total_common

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
			curr_a[field] = {fieldval: cnt for cnt, fieldval in results}

		self.pa_by_authors[aID] = curr_a
		return
	
	def getCoauthorsSim(self, a1, a2):
		common, len1, len2 = selectDB(self.conn_pa, self.coauthor_query_, [a1, a2, a1, a2]).next()
		return self.sim(common, len1, len2)

	def getCoauthorsSimW(self, a1, a2):
		common, len1, len2 = selectDB(self.conn_pa, self.coauthor_query_w_, [a1, a2, a1, a2, a1, a2]).next()
		return self.sim(common, len1, len2)

	def getCoauthorsSimF(self, a1, a2):
		return selectDB(self.conn_pa, self.coauthor_query_f_,  [a1, a2, a1, a2]).next()[0]

	def getTotal(self, field, aid):
		if field not in self.pa_by_authors_totals[aid]:
			self.pa_by_authors_totals[aid][field] = sum(self.pa_by_authors[aid][field].values())
		return float(self.pa_by_authors_totals[aid][field])

	def getFieldPA(self, field, a1, a2):
		# missing value
		if a1 not in self.filter:
			return 0.
		a2val = self.author_info[a2][field]
		# missing value
		if not len(a2val) or a2val.startswith('ID:'):
			return 0.
		if a2val in self.pa_by_authors[a1][field]:
			return self.pa_by_authors[a1][field][a2val] / self.getTotal(field, a1)
		else:
			return 0.
	
	def getPABoth(self, field, a1, a2):
		return self.getFieldPA(field, a1, a2) + self.getFieldPA(field, a2, a1)

	def getSetSim(self, field, a1, a2):
		return self.sim(*self.dictSim(self.pa_by_authors[a1][field], self.pa_by_authors[a2][field]))

	def getSetSimW(self, field, a1, a2):
		return self.sim(*self.dictSimW(self.pa_by_authors[a1][field], self.pa_by_authors[a2][field], self.getTotal(field, a1), self.getTotal(field, a2)))

	def getSetSimF(self, field, a1, a2):
		return self.dictSimF(self.pa_by_authors[a1][field], self.pa_by_authors[a2][field], self.getTotal(field, a1), self.getTotal(field, a2))
	
	def pcutl(self, a, p=10):
		return scoreatpercentile(a, p) # interpolation = 'lower'?

	def pcuth(self, a, p=90):
		return scoreatpercentile(a, p) # interpolation = 'higher'?
	
	def getYearScore(self, a1, a2):
		k1 = self.pa_by_authors[a1]['years'].items()
		k2 = self.pa_by_authors[a2]['years'].items()
		if not k1 or not k2:
			return 0
		kk1, kk2 = [], []
		for k, v in k1:
			kk1.extend([k] * int(v))
		for k, v in k2:
			kk2.extend([k] * int(v))
		x1, x2 = self.pcutl(kk1), self.pcuth(kk1)
		y1, y2 = self.pcutl(kk2), self.pcuth(kk2)
		return min(x2, y2) - max(x1, y1) + 1

	def getTextSimPub(self, a1, a2):
		if a1 not in self.TextSimVecs or a2 not in self.TextSimVecs:
			return 0
		
		terms1 = self.TextSimVecs[a1]
		terms2 = self.TextSimVecs[a2]
		return shared_terms_sum(terms1, terms2)

	def getTitlesOverlap(self, a1, a2):
# 		titles1, titles2 = self.pa_by_authors[a1]['titles_dup_idified'], self.pa_by_authors[a2]['titles_dup_idified']
# 		if not titles1 or not titles2:
# 			return 0
# 		common_titles = set(title1.keys()) & set(title2.keys())
# 		if not common_titles:
# 			return 0
# 		paperids1, paperids2 = self.pa_by_authors[a1]['paperids'], self.pa_by_authors[a2]['paperids']
# 		common_paperids = set(paperids1.keys()) & set(paperids2.keys())
# 		common_titles -= common_paperids
# 
# 		common = set(a.keys()) & set(b.keys())
# 		total_common = sum([min(a[v], b[v]) for v in common])

		common_titles, _, _ = self.dictSimW(self.pa_by_authors[a1]['titles_idified'], self.pa_by_authors[a2]['titles_idified'])
		common_paperids, _, _ = self.dictSimW(self.pa_by_authors[a1]['paperids_inpaper_titlenoblank'], self.pa_by_authors[a2]['paperids_inpaper_titlenoblank'])
		return common_titles - common_paperids

	def getEdgeFeatures(self, author1, author2):
# 		self.getAuthor(author1)
# 		self.getAuthor(author2)
		f = defaultdict(float)
		f.update({
			'pa_fullname': self.getPABoth('fullname', author1, author2),
			'pa_affil': self.getPABoth('affiliation', author1, author2),
			'fullnames': 0,
			'fullnamesF': 0,
			'affiliations': 0,
			'affiliationsF': 0,
			'conferences': 0,
			'conferencesF': 0,
			'journals': 0,
			'journalsF': 0,
			'years': 0,
			'yearscore': 0,
			'coauthor': 0,
			'coauthorW': 0,
			'coauthorF': 0,
			'paperIDs': 0,
			'paperIDsF': 0,
# 			'paperIDs_p_title': 0,
# 			'paperIDs_p_titleF': 0,
# 			'titles_dup': 0,
			'titles_dupW': 0,
			'pubTextSim': 0
		})
		if author1 in self.filter and author2 in self.filter:
			f.update({
				'has_papers': 2,
				'fullnames': self.getSetSim('fullname', author1, author2),
				'fullnamesF': self.getSetSimF('fullname', author1, author2),
				'affiliations': self.getSetSim('affiliation', author1, author2),
				'affiliationsF': self.getSetSimF('affiliation', author1, author2),
				'conferences': self.getSetSim('conferences', author1, author2),
				'conferencesF': self.getSetSimF('conferences', author1, author2),
				'journals': self.getSetSim('journals', author1, author2),
				'journalsF': self.getSetSimF('journals', author1, author2),
				'years': self.getSetSim('years', author1, author2),
				'yearscore': self.getYearScore(author1, author2),
				'coauthor': self.getCoauthorsSim(author1, author2),
				'coauthorW': self.getCoauthorsSimW(author1, author2),
				'coauthorF': self.getCoauthorsSimF(author1, author2),
				'paperIDs': self.getSetSim('paperids', author1, author2),
				'paperIDsF': self.getSetSimF('paperids', author1, author2),
# 				'paperIDs_p_title': self.getSetSim('paperids_inpaper_titlenoblank', author1, author2),
# 				'paperIDs_p_titleF': self.getSetSimF('paperids_inpaper_titlenoblank', author1, author2),
				'titles_dupW': self.getTitlesOverlap(author1, author2),
# 				'titles_dup': self.getSetSim('titles_dup_idified', author1, author2),
# 				'titles_dupW': self.getSetSimW('titles_dup_idified', author1, author2),
				'pubTextSim': self.getTextSimPub(author1, author2)
			})
		elif author1 in self.filter or author2 in self.filter:
 			f['has_papers'] = 1
 		else:
 			f['has_papers'] = 0
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
#   	authors = pickle.load(open(args.authorprefeat, 'rb'))
 	authors = {}
	PFG = PaperauthorFeaturesGenerator(authors, args.authorfilter)

	rows_skipped = 0
	rows = 0

	writer = csv.DictWriter(open(args.outfile, 'wb'), dialect='excel-tab', fieldnames=['authors']+PFG.fields)
	writer.writeheader()

 	for i, (a, b) in enumerate(csv.reader(skip_comments(open(args.edges, 'rb')))):
 		a, b = int(a), int(b)
 		if a not in PFG.filter and b not in PFG.filter:
 			rows_skipped += 1
 		else:
#  			print a, b
 			f = PFG.getEdgeFeatures(a, b)
 			f = {k: '{:g}'.format(v) for k, v in f.iteritems()}
 			f['authors'] = '{:},{:}'.format(a, b)
	 		writer.writerow(f)
	  		rows += 1

 		if (i+1) % 100 == 0:
 			print_err(i+1, 'rows done;', rows, 'rows extracted')
 	
	print_err("Rows skipped: {0}".format(rows_skipped))

if __name__ == "__main__":
	main()