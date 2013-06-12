import csv
import sys
import exceptions
import numpy as np
import math
import re
from collections import Iterable

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


def skip_front(iterable):
	for line in iterable:
		if ';' in line:
			yield line.split(';')[1]
		else:
			yield line

def skip_comments(iterable):
    for line in iterable:
        if not line.startswith('#') and line.strip():
            yield line

def verbose_iter(iter, n=10000):
	for i, line in enumerate(iter):
		yield i, line
		if (i+1) % n == 0:
			print_err(i+1, 'lines done')

def readEdges_iter(filename, verbose=True, weighted=True, n=10000):
	print_err("Reading file", filename)
	ind = 3 if weighted else 2
	with open(filename, 'rb') as f:
		reader = csv.reader(f)
		for i, line in enumerate(reader):
			line[0:2] = map(int, line[0:2])
			if weighted:
				line[2] = float(line[2])
			yield i, line[0:ind]
			if (i+1) % n == 0 and verbose:
				print_err(i+1, 'edges read')

def readcsv_iter(filename, discard_header=True, verbose=True, n=10000):
	print_err("Reading file", filename)
	with open(filename, 'rb') as f:
		reader = csv.reader(f)
		if discard_header:
			header = reader.next()
		for i, line in enumerate(reader):
			yield i, line
			if (i+1) % n == 0 and verbose:
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

def computeTFIDFs(texts, additional_stop_words=[], words_freq=False, **kwargs):
	from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
	from collections import Counter
	if additional_stop_words == 'all':
		additional_stop_words = loadstopwords(['multilang_u', 'affiliations', 'titles'])

	if additional_stop_words is None:
		stop_words = []
	else:
		stop_words = ENGLISH_STOP_WORDS | set(additional_stop_words)

	defaults = {
		'token_pattern': u'(?u)\\b[0-9]*[a-zA-Z]+[a-zA-Z0-9]+\\b',
		'min_df': 2,
		'max_df': 1.0,
		'lowercase': True,
		'analyzer': 'word',
		'norm': None,
		'use_idf': True,
		'smooth_idf': True,
		'binary': True,
		'sublinear_tf': False,
		'ngram_range': (1,3),
		'stop_words': frozenset(stop_words)
	}
	defaults.update(kwargs)
	
	vec = TfidfVectorizer(**defaults)
	tfidfs = vec.fit_transform(texts)

	# print words sorted by frequency
	if words_freq:
		print_err("Preparing Word Frequency")
		wfreq = Counter(tfidfs.nonzero()[1])
		kk = [(wfreq[i], word.encode('ascii')) for i, word in enumerate(vec.get_feature_names())]
		# kk = zip(tfidfs.sum(axis=0).tolist()[0], vec.get_feature_names())
		kk = sorted(kk)
		for line in kk:
			print '{:} {:}'.format(*line)
	return tfidfs

def is_iterable(itl):
	return isinstance(itl, Iterable)

def loadfilelines(filenames):
	# allow for input of a single or multiple filenames
	if not is_iterable(filenames):
		filenames = [filenames]
	sw = []
	for filename in filenames:
		with open(filename, 'rb') as f:
			sw += [line.strip() for line in skip_comments(f)]
	return sw

def loadstopwords(setids):
	return loadfilelines(['textdata/stopwordlist_{:}.txt'.format(id) for id in setids])
		
def shared_terms_sum(aa, bb, deduct_diff=True):
	terms_a = aa.nonzero()[1]
	terms_b = bb.nonzero()[1]
	terms_common = np.intersect1d(terms_a, terms_b, assume_unique=True)
	if terms_common.any():
		fsum = aa[[0] * len(terms_common), terms_common].sum()
	else:
		fsum = 0
	if not deduct_diff:
		return fsum
	diffa = np.setdiff1d(terms_a, terms_common)
	diffb = np.setdiff1d(terms_b, terms_common)
	suma = aa[[0] * len(diffa), diffa].sum() if diffa.any() else 0
	sumb = bb[[0] * len(diffb), diffb].sum() if diffb.any() else 0
	return fsum - math.log10(1.0 + min(suma, sumb))

punc_nospacedash = ".;,'~:_@?\|\\/\"+)}{(&$*%=>^"
punc_nospace = punc_nospacedash + '-'
punc = punc_nospace + ' '

def strip_punc(str, strip_spaces = True, space_dashes=True):
	if space_dashes:
		return ' '.join(re.sub('[{:}]'.format(punc_nospace), ' ', str).split())
	elif strip_spaces:
		return str.translate(None, punc)
	else:
		return str.translate(None, punc_nospace)
