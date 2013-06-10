import networkx as nx
from common import *

def enforce_min(iterable, min_weight):
    for line in iterable:
    	vl = line.split(',')
        if float(vl[2]) >= min_weight:
            yield line

def outputClusters(clusters, fout, G_sim=None, authors=None, threshold_density=None):
	clusters_o = []
	
 	for clist in clusters:
		line = []
		if authors is not None:
			fullnames = set([authors[v]['fullname'] for v in clist])
			fullnames = '|'.join(sorted(fullnames))
			lastnames = set([authors[v]['name_last'] for v in clist])
			lastnames = '|'.join(sorted(lastnames))
			line.append([lastnames, fullnames])

		cl_nodes = len(cl)
		if G_sim is not None:
			cl = G_sim.subgraph(clist)
			cl_edges = cl.number_of_edges()
			cl_unweighted_density = nx.density(cl)
			cl_weighted_density = cl.size(weight='weight')
			if cl_nodes != 1:
				cl_weighted_density /= (.5 * cl_nodes * (cl_nodes - 1))
			line.append([cl_nodes, cl_weighted_density, cl_unweighted_density]) #cl_edges
		else:
			line.append([cl_nodes])

		if G_sim is None or threshold_density is None or cl_weighted_density >= threshold_density:
			clusters_o.append([','.join(map(str, sorted(clist)))] + line)
		else:
			print_err(*(line[0]+line[1]))
	
	# size,weighted_density,unweighted_density,lastnames,fullnames;cluster
	for cline in sorted(clusters_o, reverse=True):
		fout.write(','.join(map('{:g}'.format, cline.pop())))
		if authors is not None:
			fout.write(','.join(cline.pop()))
		fout.write(';')
		fout.write('{:}\n'.format(cline.pop()))
