#!/usr/bin/env python
from unidecode import unidecode
import fileinput
import csv
import sys

if len(sys.argv) < 3:
	sys.exit(0)	

f_write = open(sys.argv[2], 'wb') if sys.argv[2] != '-' else sys.stdout
f_in = open(sys.argv[1], 'rb') if sys.argv[1] != '-' else sys.stdin

writer = csv.writer(f_write)
for i, line in enumerate(csv.reader(f_in)):
	line[1] = unidecode(unicode(line[1], 'utf-8')).strip().lower()
# 	line = [unidecode(unicode(cell, 'utf-8')).strip() for cell in line]
	writer.writerow(line)
	if (i+1) % 10000 == 0:
		print i+1, "lines done"
