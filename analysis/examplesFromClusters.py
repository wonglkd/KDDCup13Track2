#!/usr/bin/env python
from itertools import combinations, product, chain

clusters = '''721471
1294623
2219483
1444079
2072490'''

clusters = '''123,456
345,753'''

clusters = [cl.split(',') for cl in clusters.split('\n')]
for cl in clusters:
	for a1, a2 in combinations(cl, 2):
		print ",".join(['1', a1, a2])

for a, b in combinations(clusters, 2):
	for a1, b1 in product(a, b):
		print ",".join(['0', a1, b1])
