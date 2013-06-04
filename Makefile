DATA_DIR := data
GEN_DIR := generated

AUTHOR_SET := Author
# AUTHOR_SET := Author_f20000
PREFEAT := $(GEN_DIR)/$(AUTHOR_SET)_prefeat.pickle
BIN_METHODS := iFfL samename fullparsedname offbylastone token ngrams fF3L iFoffbyoneL 2FoffbyoneL metaphone

BIN_FILES = $(foreach i,$(BIN_METHODS),$(GEN_DIR)/$i_bins.txt)
EDGE_FILES := $(GEN_DIR)/iFfL_edges.txt
FEAT_FILES := $(GEN_DIR)/iFfL.feat
#SIM_FILES := $(GEN_DIR)/iFfL.sim
CLUSTER_FILES := $(GEN_DIR)/combined.clusters
SUBMIT_FILES := $(GEN_DIR)/combined-submit.csv
EVALUATE_SETS := 20130531-oldtrainingdata 20130531-afternoon 20130531-1325 20130531-1025 20130531-0800 20130530 20130601-restore 20130601-restore2
EVALUATE_FILES := $(GEN_DIR)/best-submit.csv $(GEN_DIR)/20130530/combined_716eef6-submit.csv $(foreach i,$(EVALUATE_SETS),$(GEN_DIR)/$i/combined-submit.csv)
SUBMIT_BIN_FILES := $(GEN_DIR)/samename-bins_submit.csv $(GEN_DIR)/fullparsedname-bins_submit.csv
TRAIN_PARA := --removefeat conferences journals fullnames coauthor paperIDs affiliations jaro_distance suffix last jaro_winkler

# Platform specific stuff
ifeq ($(OS),Windows_NT)
	# Windows
	EXEC_PREFIX := "C:\Program Files (x86)\Python27\python.exe" 
	SORT_BIN := "C:\MinGW\msys\1.0\bin\sort"
else
	# Mac/Linux
	EXEC_PREFIX := time ./
	SORT_BIN := sort
endif

#sim-t: $(GEN_DIR)/iFfL.sim

.PHONY:
.SECONDARY:
all: $(SUBMIT_FILES)
feat: $(FEAT_FILES)

edgefeat-t:
	$(EXEC_PREFIX)featEdges.py generated/edges_test.txt data/authors_with_papers.txt generated/test.edgefeat

evaluate: evaluate.py
	$(EXEC_PREFIX)$^ $(EVALUATE_FILES)
submitgz: $(SUBMIT_FILES:=.gz)
bins: $(BIN_FILES)
cluster: $(CLUSTER_FILES)
bin-submit: $(SUBMIT_BIN_FILES)
prefeat-t: $(GEN_DIR)/Author_f20000_prefeat.pickle 
train: $(GEN_DIR)/model.pickle
authordata_u: authordata/pa_affiliation_u.csv authordata/pa_names_u.csv authordata/pa_coauthors_u.csv

textdata/Author_processed.csv: process_authors.py data/Author.csv
	$(EXEC_PREFIX)$^ $@ --format csv

generated/affil_wordcounts.txt: process_authors.py data/Author.csv
	$(EXEC_PREFIX)$^ --affilwordfreq > $@

%_u.csv: unidecodefile.py %.csv
	$(EXEC_PREFIX)$^ $@ --all-cols

%_idified.csv: idify.py %.csv
	$(EXEC_PREFIX)$^ $@

analyse: edge-analyseModel.py $(GEN_DIR)/model.pickle
	$(EXEC_PREFIX)$<
	
textdata/publication_tfidf.pickle: processTitles.py data/Conference.csv data/Journal.csv
	$(EXEC_PREFIX)$<

$(GEN_DIR)/%_bins.txt: blocking.py $(PREFEAT)
	$(EXEC_PREFIX)$^ $* > $@

$(GEN_DIR)/%_edges.txt: edges.py $(GEN_DIR)/%_bins.txt
	$(EXEC_PREFIX)$^ > $@
	
$(GEN_DIR)/combined_edges.txt: edges.py $(BIN_FILES)
	$(EXEC_PREFIX)$^ > $@

$(GEN_DIR)/%_prefeat.pickle: process_authors.py $(DATA_DIR)/%.csv
	$(EXEC_PREFIX)$^ $@

$(GEN_DIR)/train.feat: features.py $(DATA_DIR)/train.csv $(PREFEAT) featEdges.py textdata/publication_tfidf.pickle
	$(EXEC_PREFIX)features.py $(DATA_DIR)/train.csv $(PREFEAT) $@
	
$(GEN_DIR)/train_%.feat: features.py $(DATA_DIR)/train_%.csv $(PREFEAT) featEdges.py textdata/publication_tfidf.pickle
	$(EXEC_PREFIX)features.py $(DATA_DIR)/train_$*.csv $(PREFEAT) $@

$(GEN_DIR)/%.feat: features.py $(GEN_DIR)/%_edges.txt $(PREFEAT) featEdges.py textdata/publication_tfidf.pickle
	$(EXEC_PREFIX)features.py $(GEN_DIR)/$*_edges.txt $(PREFEAT) $@

$(GEN_DIR)/%.sim: features2similarity.py $(GEN_DIR)/%.feat
	$(EXEC_PREFIX)$^ $@; $(SORT_BIN) $@ -grk 3 -t"," -o $@

$(GEN_DIR)/%.prob: edge-predict.py $(GEN_DIR)/%.feat $(GEN_DIR)/model.pickle
	$(EXEC_PREFIX)$^ $@; $(SORT_BIN) $@ -grk 3 -t"," -o $@
	
$(GEN_DIR)/model.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ $(TRAIN_PARA)

$(GEN_DIR)/model_%.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ --clf $* $(TRAIN_PARA)

$(GEN_DIR)/%_model.pickle: edge-train.py $(DATA_DIR)/train_%.csv $(GEN_DIR)/train_%.feat
	$(EXEC_PREFIX)$^ $@ $(TRAIN_PARA)

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

$(GEN_DIR)/%.clusters: cluster_hc.py $(GEN_DIR)/%.prob
	$(EXEC_PREFIX)$^ $@ > $(GEN_DIR)/$*.clusters-stats

$(GEN_DIR)/%.clusters-sim: cluster_cc.py $(GEN_DIR)/%.sim
	$(EXEC_PREFIX)$^ $@
