import sys
import exceptions

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

def num(s):
    try:
        return int(s)
    except exceptions.ValueError:
        try:
        	return float(s)
        except exceptions.ValueError:
        	raise Exception("Could not convert string to number:"+ s)