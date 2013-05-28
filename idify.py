#!/usr/bin/env python
import csv
import sys

if len(sys.argv) < 3:
	sys.exit(0)	

f_write = open(sys.argv[2], 'wb') if sys.argv[2] != '-' else sys.stdout
f_in = open(sys.argv[1], 'rb') if sys.argv[1] != '-' else sys.stdin

seen = {}

writer = csv.writer(f_write)
for i, line in enumerate(csv.reader(f_in)):
	if i != 0:
		if line[1] not in seen:
			seen[line[1]] = len(seen)
		line[1] = seen[line[1]]
	writer.writerow(line)
	if (i+1) % 10000 == 0:
		print i+1, "lines done"
