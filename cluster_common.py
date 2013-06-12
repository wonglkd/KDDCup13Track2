import networkx as nx
from common import *

def loadClusters(filename):
	with open(filename, 'rb') as f:
		print_err('Reading', filename)
		for line in csv.reader(skip_front(skip_comments(f))):
			yield map(int, line)

def enforce_min(iterable, min_weight):
    for line in iterable:
    	vl = line.split(',')
        if float(vl[2]) >= min_weight:
            yield line

def outputClusters(clusters, fout, G_sim=None, authors=None, threshold_density=None):
	clusters_o = []
	
 	for clist in clusters:
		line = []
		if G_sim is not None:
			cl = G_sim.subgraph(clist)
			cl_nodes = len(cl)
			cl_edges = cl.number_of_edges()
			cl_unweighted_density = nx.density(cl)
			cl_weighted_density = cl.size(weight='weight')
			if cl_nodes != 1:
				cl_weighted_density /= (.5 * cl_nodes * (cl_nodes - 1))
			line.append([cl_nodes, cl_weighted_density, cl_unweighted_density]) #cl_edges
		else:
			line.append([len(clist)])

		if authors is not None:
			fullnames = set([authors[v]['fullname'] for v in clist])
			lastnames = set([authors[v]['name_last'] for v in clist])
			firstnames = set([authors[v]['name_first'] for v in clist])
			if '' in firstnames:
				firstnames.remove('')
			middlenames = set([authors[v]['name_middle'] for v in clist])
			if '' in middlenames:
				middlenames.remove('')
			a_l = [len(lastnames), len(firstnames), len(middlenames)]
			fullnames = '|'.join(sorted(fullnames))
			lastnames = '|'.join(sorted(lastnames))
			firstnames = '|'.join(sorted(firstnames))
			middlenames = '|'.join(sorted(middlenames))
			a_l += [lastnames, firstnames, middlenames, fullnames]
			line.append(a_l)

		if G_sim is None or threshold_density is None or cl_weighted_density >= threshold_density:
			clusters_o.append(line + [','.join(map(str, sorted(clist)))])
		else:
			print_err(*(line[0]+line[1]))
	
	# size,weighted_density,unweighted_density,lastnames,fullnames;cluster
	for cline in sorted(clusters_o, reverse=True):
		fout.write(','.join(map('{:g}'.format, cline.pop(0))))
		if authors is not None:
			fout.write(',')
			fout.write(','.join(map(str, cline.pop(0))))
		fout.write(';')
		fout.write('{:}\n'.format(cline.pop(0)))
