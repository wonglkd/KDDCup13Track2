import networkx as nx
from common import *

def enforce_min(iterable, min_weight):
    for line in iterable:
    	vl = line.split(',')
        if float(vl[2]) >= min_weight:
            yield line

def outputClusters(clusters, fout, G_sim, threshold_density=None):
	clusters_o = []
 	for clist in clusters:
 		cl = G_sim.subgraph(clist)
		cl_nodes = len(cl)
		cl_edges = cl.number_of_edges()
		cl_unweighted_density = nx.density(cl)
		cl_weighted_density = cl.size(weight='weight')

		if cl_nodes != 1:
			cl_weighted_density /= (.5 * cl_nodes * (cl_nodes - 1))
		if threshold_density is None or cl_weighted_density >= threshold_density:
			clusters_o.append((cl_nodes, cl_weighted_density, cl_edges, cl_unweighted_density, ','.join(map(str, sorted(clist)))))
		else:
			print_err(cl_nodes, cl_edges, cl_unweighted_density, cl_weighted_density)
	
	for cl_nodes, cl_weighted_density, cl_edges, cl_unweighted_density, clstr in sorted(clusters_o, reverse=True):
		print cl_nodes, cl_edges, cl_unweighted_density, cl_weighted_density
		fout.write('{:},{:g};{:}\n'.format(cl_nodes, cl_weighted_density, clstr))			
