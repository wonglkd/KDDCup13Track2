DATA_DIR := data
GEN_DIR := generated

AUTHOR_SET := Author
# AUTHOR_SET := Author_f20000
PREFEAT := $(GEN_DIR)/$(AUTHOR_SET)_prefeat.pickle
BIN_METHODS := iFfL samename fullparsedname offbylastone token ngrams fF3L

BIN_FILES = $(foreach i,$(BIN_METHODS),$(GEN_DIR)/$i_bins.txt)
EDGE_FILES := $(GEN_DIR)/iFfL_edges.txt
FEAT_FILES := $(GEN_DIR)/iFfL.feat
#SIM_FILES := $(GEN_DIR)/iFfL.sim
CLUSTER_FILES := $(GEN_DIR)/iFfL.clusters
SUBMIT_FILES := $(GEN_DIR)/combined-submit.csv
# $(GEN_DIR)/iFfL-submit.csv 
SUBMIT_BIN_FILES := $(GEN_DIR)/samename-bins_submit.csv $(GEN_DIR)/fullparsedname-bins_submit.csv
feat: $(FEAT_FILES)
#cluster-t: $(GEN_DIR)/iFfL.clusters
#sim-t: $(GEN_DIR)/iFfL.sim
edgefeat-t:
	./featEdges.py generated/edges_test.txt data/authors_with_papers.txt generated/test.edgefeat

all: $(SUBMIT_FILES)
.SECONDARY:

evaluate: evaluate.py $(GEN_DIR)/goldstd-submit.csv $(SUBMIT_FILES)
	./$^
bins: $(BIN_FILES)
bin-submit: $(SUBMIT_BIN_FILES)
prefeat-t: $(GEN_DIR)/Author_f20000_prefeat.pickle 
train: $(GEN_DIR)/model.pickle
authordata_u: authordata/pa_affiliation_u.csv authordata/pa_names_u.csv authordata/pa_coauthors_u.csv

%_u.csv: unidecodefile.py %.csv
	./$^ $@

analyse: ./edge-analyseModel.py $(GEN_DIR)/model.pickle
	./$<

$(GEN_DIR)/train.feat: features.py $(DATA_DIR)/train.csv $(PREFEAT) featEdges.py
	time ./features.py $(DATA_DIR)/train.csv $(PREFEAT) $@

$(GEN_DIR)/%_bins.txt: blocking.py $(PREFEAT)
	time ./$^ $* > $@

$(GEN_DIR)/%_edges.txt: edges.py $(GEN_DIR)/%_bins.txt
	time ./$^ > $@
	
$(GEN_DIR)/combined_edges.txt: edges.py $(BIN_FILES)
	time ./$^ > $@

$(GEN_DIR)/%_prefeat.pickle: process_authors.py $(DATA_DIR)/%.csv
	time ./$^ $@

$(GEN_DIR)/%.feat: features.py $(GEN_DIR)/%_edges.txt $(PREFEAT) featEdges.py
	time ./features.py $(GEN_DIR)/$*_edges.txt $(PREFEAT) $@

$(GEN_DIR)/%.sim: features2similarity.py $(GEN_DIR)/%.feat
	time ./$^ $@; sort $@ -nrk 3 -t"," -o $@

$(GEN_DIR)/%.prob: edge-predict.py $(GEN_DIR)/%.feat $(GEN_DIR)/model.pickle
	time ./$^ $@; sort $@ -nrk 3 -t"," -o $@
	
$(GEN_DIR)/model.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	time ./$^ $@

$(GEN_DIR)/%-submit.csv: prep_submit.py $(GEN_DIR)/%.clusters
	time ./$^ $@

$(GEN_DIR)/goldstd_edges.txt: edges.py $(DATA_DIR)/goldstd_clusters.csv
	time ./$^ > $@

$(GEN_DIR)/goldstd-submit.csv: prep_submit.py $(DATA_DIR)/goldstd_clusters.csv
	time ./$^ $@

$(GEN_DIR)/%-bins_submit.csv: prep_submit.py $(GEN_DIR)/%_bins.txt
	time ./$^ $@

# awk '{ if ($3 >= 0.6) print $0; }'

$(GEN_DIR)/%.clusters: cluster-hc.py $(GEN_DIR)/%.prob
	time ./$^ $@ > $(GEN_DIR)/$*.clusters-stats

$(GEN_DIR)/%.clusters-sim: cluster-cc.py $(GEN_DIR)/%.sim
	time ./$^ $@
