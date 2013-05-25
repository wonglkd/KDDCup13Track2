#!/usr/bin/env python
from common import *
from pprint import pprint
import argparse

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('qtype', nargs='?', default='author')
	args = parser.parse_args()

	queries = {
		'author': '''SELECT * FROM author a''',
		'all': '''SELECT a.*, pa.name, pa.affiliation, p.title, p.year, p.journalId, p.conferenceId FROM
	(author a LEFT JOIN paperauthor pa ON AuthorID = a.Id)
	LEFT JOIN paper p ON p.Id = PaperId'''
	}

	with open('analysis/analyse.clusters') as f:
		with getDB() as conn:
			for line in skip_comments(f):
				if ';' in line:
					line = line.split(';')[1]
				cluster = line.strip().split(',')
				for v in cluster:
					res = selectDB(conn, queries[args.qtype] + ' WHERE a.Id = '+v+' LIMIT 2')
					for line in res:
						print(line)
				print('-----------')

if __name__ == "__main__":
	main()

# clusters = [cl.strip().split(',') for cl in clusters.split('\n')]
# for cl in clusters:
# 	for a1, a2 in combinations(cl, 2):
# 		print ",".join(['1', a1, a2])
# 
# for a, b in combinations(clusters, 2):
# 	for a1, b1 in product(a, b):
# 		print ",".join(['0', a1, b1])
# 
# 
# from process_authors import *
# 
# abc = loadAuthors('data/Author_s100.csv')
# pprint(abc[423])
# 
# WHERE a.Id IN (96610)
# LIMIT 50;
# SELECT * FROM paperauthor WHERE AuthorID IN (96610);
# SELECT * FROM author WHERE ID IN (96610);
