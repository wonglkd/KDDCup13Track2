DATA_DIR := data
GEN_DIR := generated

AUTHOR_SET := Author
# AUTHOR_SET := Author_f20000
PREFEAT := $(GEN_DIR)/$(AUTHOR_SET)_prefeat.pickle
BIN_METHODS := iFfL samename fullparsedname offbylastone token ngrams fF3L iFoffbyoneL 2FoffbyoneL

BIN_FILES = $(foreach i,$(BIN_METHODS),$(GEN_DIR)/$i_bins.txt)
EDGE_FILES := $(GEN_DIR)/iFfL_edges.txt
FEAT_FILES := $(GEN_DIR)/iFfL.feat
#SIM_FILES := $(GEN_DIR)/iFfL.sim
CLUSTER_FILES := $(GEN_DIR)/combined.clusters
SUBMIT_FILES := $(GEN_DIR)/combined-submit.csv
# $(GEN_DIR)/iFfL-submit.csv 
SUBMIT_BIN_FILES := $(GEN_DIR)/samename-bins_submit.csv $(GEN_DIR)/fullparsedname-bins_submit.csv
TRAIN_PARA := --removefeat conferences journals names coauthor paperIDs affiliations
# Mac/Linux
EXEC_PREFIX := time ./
# Windows
#EXEC_PREFIX := "C:\Program Files (x86)\Python27\python.exe" 

feat: $(FEAT_FILES)

#sim-t: $(GEN_DIR)/iFfL.sim
edgefeat-t:
	./featEdges.py generated/edges_test.txt data/authors_with_papers.txt generated/test.edgefeat

all: $(SUBMIT_FILES)
.SECONDARY:

evaluate: evaluate.py $(GEN_DIR)/goldstd-submit.csv $(GEN_DIR)/best-submit.csv $(SUBMIT_FILES)
	./$^
submitgz: $(SUBMIT_FILES:=.gz)
bins: $(BIN_FILES)
cluster: $(CLUSTER_FILES)
bin-submit: $(SUBMIT_BIN_FILES)
prefeat-t: $(GEN_DIR)/Author_f20000_prefeat.pickle 
train: $(GEN_DIR)/model.pickle
authordata_u: authordata/pa_affiliation_u.csv authordata/pa_names_u.csv authordata/pa_coauthors_u.csv


%_u.csv: unidecodefile.py %.csv
	./$^ $@

%_idified.csv: idify.py %.csv
	./$^ $@

analyse: ./edge-analyseModel.py $(GEN_DIR)/model.pickle
	./$<
	
textdata/publication_tfidf.pickle: processTitles.py data/Conference.csv data/Journal.csv
	./$<

$(GEN_DIR)/train.feat: features.py $(DATA_DIR)/train.csv $(PREFEAT) featEdges.py
	$(EXEC_PREFIX)features.py $(DATA_DIR)/train.csv $(PREFEAT) $@

$(GEN_DIR)/%_bins.txt: blocking.py $(PREFEAT)
	$(EXEC_PREFIX)$^ $* > $@

$(GEN_DIR)/%_edges.txt: edges.py $(GEN_DIR)/%_bins.txt
	$(EXEC_PREFIX)$^ > $@
	
$(GEN_DIR)/combined_edges.txt: edges.py $(BIN_FILES)
	$(EXEC_PREFIX)$^ > $@

$(GEN_DIR)/%_prefeat.pickle: process_authors.py $(DATA_DIR)/%.csv
	$(EXEC_PREFIX)$^ $@

# textdata/publication_tfidf.pickle
$(GEN_DIR)/%.feat: features.py $(GEN_DIR)/%_edges.txt $(PREFEAT) featEdges.py
	$(EXEC_PREFIX)features.py $(GEN_DIR)/$*_edges.txt $(PREFEAT) $@

$(GEN_DIR)/%.sim: features2similarity.py $(GEN_DIR)/%.feat
	$(EXEC_PREFIX)$^ $@; sort $@ -grk 3 -t"," -o $@

$(GEN_DIR)/%.prob: edge-predict.py $(GEN_DIR)/%.feat $(GEN_DIR)/model.pickle
	$(EXEC_PREFIX)$^ $@; sort $@ -grk 3 -t"," -o $@
	
$(GEN_DIR)/model.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ $(TRAIN_PARA)

$(GEN_DIR)/model_%.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ --clf $* $(TRAIN_PARA)

cv: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ --cv $(TRAIN_PARA)

cv-gbm: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ --cv --clf gbm $(TRAIN_PARA)
	
$(GEN_DIR)/%-submit.csv: prep_submit.py $(GEN_DIR)/%.clusters
	$(EXEC_PREFIX)$^ $@

%.gz: %
	gzip -c $* > $@

$(GEN_DIR)/goldstd_edges.txt: edges.py $(DATA_DIR)/goldstd_clusters.csv
	$(EXEC_PREFIX)$^ > $@

$(GEN_DIR)/goldstd-submit.csv: prep_submit.py $(DATA_DIR)/goldstd_clusters.csv
	$(EXEC_PREFIX)$^ $@

$(GEN_DIR)/%-bins_submit.csv: prep_submit.py $(GEN_DIR)/%_bins.txt
	$(EXEC_PREFIX)$^ $@

# awk '{ if ($3 >= 0.6) print $0; }'

$(GEN_DIR)/%.clusters: cluster-hc.py $(GEN_DIR)/%.prob
	$(EXEC_PREFIX)$^ $@ > $(GEN_DIR)/$*.clusters-stats

$(GEN_DIR)/%.clusters-sim: cluster-cc.py $(GEN_DIR)/%.sim
	$(EXEC_PREFIX)$^ $@
