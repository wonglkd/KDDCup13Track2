import csv
import sys
import exceptions
import numpy as np
import math

try:
	import apsw
	db_interface = 'apsw'
except ImportError:
	import sqlite3
	db_interface = 'sqlite'

def getDB(id='origdata'):
	DBs = {
		'origdata': "db/kddcup13.sqlite3",
		'pa': 'db/pa.sqlite3'
	}
	db_filename = DBs[id]
	if db_interface == 'apsw':
	 	conn = apsw.Connection(db_filename)
	else:
	 	conn = sqlite3.connect(db_filename)
# 	if id == 'pa':
# 		memcon = apsw.Connection(":memory")
# 		with memcon.backup("main", conn, "main") as backup:
# 			backup.step()
# 		return memcon
	return conn

def selectDB(conn, query, para = None):
	cur = conn.cursor()
	if db_interface == 'apsw':
		for row in cur.execute(query, para):
			yield row
	else:
		if para == None:
			para = []
		cur.execute(query, para)
		for row in cur.fetchall():
			yield row

def print_err(*args):
    sys.stderr.write(' '.join(map(str,args)) + '\n')

def skip_comments(iterable):
    for line in iterable:
        if not line.startswith('#') and line.strip():
            yield line

def verbose_iter(iter):
	for i, line in enumerate(iter):
		yield i, line
		if (i+1) % 10000 == 0:
			print_err(i+1, 'lines done')

def readcsv_iter(filename, discard_header=True, verbose=True):
	print_err("Reading file", filename)
	with open(filename, 'rb') as f:
		reader = csv.reader(f)
		if discard_header:
			header = reader.next()
		for i, line in enumerate(reader):
			yield i, line
			if (i+1) % 10000 == 0 and verbose:
				print_err(i+1, 'lines read')	

def num(s):
    try:
        return int(s)
    except exceptions.ValueError:
        try:
        	return float(s)
        except exceptions.ValueError:
        	if s == "":
        		print_err("Warning: empty values in file")
        		return 0.
        	else:
				raise Exception("Could not convert string to number:"+ s)
        	
def shared_terms_sum(aa, bb):
	terms_a = aa.nonzero()[1]
	terms_b = bb.nonzero()[1]
	terms_common = np.intersect1d(terms_a, terms_b, assume_unique=True)
	diffa = np.setdiff1d(terms_a, terms_common)
	diffb = np.setdiff1d(terms_b, terms_common)
	if terms_common.any():
		fsum = aa[[0] * len(terms_common), terms_common].sum()
	else:
		fsum = 0
	suma = aa[[0] * len(diffa), diffa].sum() if diffa.any() else 0
	sumb = bb[[0] * len(diffb), diffb].sum() if diffb.any() else 0
	return fsum - math.log10(1.0 + min(suma, sumb))

punc_nospacedash = ".;,'~:_@?\|\\/\"+)}{(&$*%=>^"
punc_nospace = punc_nospacedash + '-'
punc = punc_nospace + ' '

def strip_punc(str, strip_spaces = True, space_dashes=True):
	if space_dashes:
		return ' '.join(str.translate(None, punc_nospacedash).replace('-', ' ').split())
	elif strip_spaces:
		return str.translate(None, punc)
	else:
		return str.translate(None, punc_nospace)
