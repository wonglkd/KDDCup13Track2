import sqlite3
import sys
import exceptions

def getDB():
	db_filename = "kddcup13.sqlite3"
	conn = sqlite3.connect(db_filename)
	return conn

def selectDB(conn, query, para = None):
	cur = conn.cursor()
	cur.execute(query, para)
	return cur.fetchall()

def print_err(*args):
    sys.stderr.write(' '.join(map(str,args)) + '\n')

def skip_comments(iterable):
    for line in iterable:
        if not line.startswith('#'):
            yield line

def num(s):
    try:
        return int(s)
    except exceptions.ValueError:
        return float(s)