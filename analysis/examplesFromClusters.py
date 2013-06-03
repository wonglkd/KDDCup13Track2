#!/usr/bin/env python
from itertools import combinations, product, chain

clusters = '''1077322
1004361
2290355
1030132
341152 
376374 
1798702
1211468
1229993
1177255
497471 
1145517
1492855
953365 
1702128
1557010'''

clusters = [cl.strip().split(',') for cl in clusters.split('\n')]
for cl in clusters:
	for a1, a2 in combinations(cl, 2):
		print ",".join(['1', a1, a2])

for a, b in combinations(clusters, 2):
	for a1, b1 in product(a, b):
		print ",".join(['0', a1, b1])
