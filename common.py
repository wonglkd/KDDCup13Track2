import sqlite3
import apsw
import sys
import exceptions

def getDB(id='origdata'):
	DBs = {
		'origdata': "kddcup13.sqlite3",
		'pa': 'pa.sqlite3'
	}
	db_filename = DBs[id]
# 	conn = sqlite3.connect(db_filename)
	conn = apsw.Connection(db_filename)
	if id == 'pa':
		memcon = apsw.Connection(":memory")
		with memcon.backup("main", conn, "main") as backup:
			backup.step()
		return memcon
	return conn

def selectDB(conn, query, para = None):
	cur = conn.cursor()
	for row in cur.execute(query, para):
		yield row
# 	return cur.fetchall()

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
        try:
        	return float(s)
        except exceptions.ValueError:
        	raise Exception("Could not convert string to number:"+ s)