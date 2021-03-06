include Makefile.inc

DATA_DIR := data
GEN_DIR := generated

AUTHOR_SET := Author
PREFEAT := $(GEN_DIR)/$(AUTHOR_SET)_prefeat.pickle
BIN_METHODS := iFfL samename fullparsedname offbylastone token ngrams fF3L iFoffbyoneL 2FoffbyoneL metaphone

BIN_FILES = $(foreach i,$(BIN_METHODS),$(GEN_DIR)/$i_bins.txt)
EDGE_FILES := $(GEN_DIR)/iFfL_edges.txt
FEAT_FILES := $(GEN_DIR)/iFfL.feat
#SIM_FILES := $(GEN_DIR)/iFfL.sim
CLUSTER_FILES := $(GEN_DIR)/combined_kruskal.clusters
SUBMIT_FILES := $(GEN_DIR)/combined_kruskal-submit.csv $(GEN_DIR)/combined_hc-submit.csv
# EVALUATE_SETS := 20130531-oldtrainingdata/combined 20130531-afternoon/combined 20130531-1325/combined 20130531-1025/combined 20130531-0800/combined 20130530/combined 20130601-restore/combined 20130601-restore2/combined
EVALUATE_SETS = 20130603-2400_best/combined_716eef6 best best-2nd-0.8
EVALUATE_SETS += 20130605-2400/combined_716eef6_kruskal 20130605-2400/combined_716eef6_hc 20130605-2400/combined_kruskal 20130605-2400/combined_hc 20130606-0200/combined_716eef6_kruskal 20130605-1300/combined_716eef6_kruskal 20130606-2253/combined_hc 20130606-2253/combined_hc_min 20130606-2253/combined_hc_avgpresent 20130606-2253/combined_kruskal
EVALUATE_SETS += 20130607-2330/combined_kruskal 20130607-2330/combined_hc 20130607-2330/combined_716eef6_hc 20130607-2330/combined_716eef6_kruskal
EVALUATE_SETS += 20130607-2337/combined_kruskal 20130607-2337/combined_hc 20130607-2337/combined_716eef6_hc 20130607-2337/combined_716eef6_kruskal
EVALUATE_SETS += 20130608/combined_kruskal 20130608/combined_hc 20130608/combined_716eef6_hc 20130608/combined_716eef6_kruskal
EVALUATE_SETS += 20130609-1900/combined_gbm_hc 20130609-1900/combined_gbm_kruskal
EVALUATE_SETS += combined_kruskal combined_hc
EVALUATE_FILES := $(foreach i,$(EVALUATE_SETS),$(GEN_DIR)/$i-submit.csv)
SUBMIT_BIN_FILES := $(GEN_DIR)/samename-bins_submit.csv $(GEN_DIR)/fullparsedname-bins_submit.csv
FEAT_PARA = --removefeat conferences journals fullnames coauthor paperIDs affiliations jaro_distance
FEAT_PARA += suffix last jaro_winkler coauthors_idsW coauthors_dupW fullnames_dup coauthors_ids_dupW
FEAT_PARA += paperIDs_dup coauthors_ids_dupF coauthors coauthorsW coauthors coauthors_ids coauthors_dup
FEAT_PARA += jarow_mid jarow_firstmid metaphone
FEAT_PARA += jarow_midlast
TRAIN_PARA = --usegrid $(FEAT_PARA)

.PHONY:
.SECONDARY:
all: $(SUBMIT_FILES)
feat: $(FEAT_FILES)

edgefeat-t:
	$(EXEC_PREFIX)featEdges.py generated/edges_test.txt data/authors_with_papers.txt generated/test.edgefeat

evaluate: evaluate.py generated/goldstd-submit.csv
	$(EXEC_PREFIX)$^ $(EVALUATE_FILES) --verbose
evals: evaluate.py generated/goldstd-submit.csv
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

%_u.txt: unidecodefile.py %.txt
	$(EXEC_PREFIX)$^ $@ --all-cols

%_noheader.csv: %.csv
	tail -n +2 $< > $@

%_idified.csv: idify.py %.csv
	$(EXEC_PREFIX)$^ $@

%_analyse: edge-analyseModel.py $(GEN_DIR)/%.pickle
	$(EXEC_PREFIX)$^ -o -

$(GEN_DIR)/%.pdf: edge-analyseModel.py $(GEN_DIR)/%.pickle
	$(EXEC_PREFIX)$^ -o $@
	
textdata/publication_tfidf.pickle: processTitles.py data/Conference.csv data/Journal.csv
	$(EXEC_PREFIX)$<
	
textdata/papertitles_tfidf.pickle: processPaperTitles.py processTitles.py data/Paper_u.csv authordata/pa_paperids.csv
	$(EXEC_PREFIX)$< data/Paper_u.csv authordata/pa_paperids.csv -o $@
	
textdata/papertitles_dup_tfidf.pickle: processPaperTitles.py processTitles.py data/Paper_u.csv authordata/pa_paperids_dup.csv
	$(EXEC_PREFIX)$< data/Paper_u.csv authordata/pa_paperids_dup.csv -o $@
	
$(GEN_DIR)/%_bins.txt: blocking.py $(PREFEAT)
	$(EXEC_PREFIX)$^ $* > $@

$(GEN_DIR)/%_edges.txt: edges.py $(GEN_DIR)/%_bins.txt
	$(EXEC_PREFIX)$^ > $@
	
$(GEN_DIR)/edges.txt: edges.py $(BIN_FILES)
	$(EXEC_PREFIX)$^ > $@

$(GEN_DIR)/%_prefeat.pickle: process_authors.py $(DATA_DIR)/%.csv
	$(EXEC_PREFIX)$^ $@

$(GEN_DIR)/train.feat: features.py $(DATA_DIR)/train.csv $(PREFEAT) featEdges.py textdata/publication_tfidf.pickle textdata/papertitles_tfidf.pickle
	$(EXEC_PREFIX)features.py $(DATA_DIR)/train.csv $(PREFEAT) $@
	
$(GEN_DIR)/train_%.feat: features.py $(DATA_DIR)/train_%.csv $(PREFEAT) featEdges.py textdata/publication_tfidf.pickle textdata/papertitles_tfidf.pickle
	$(EXEC_PREFIX)features.py $(DATA_DIR)/train_$*.csv $(PREFEAT) $@

$(GEN_DIR)/%.feat: features.py $(GEN_DIR)/edges.txt $(PREFEAT) featEdges.py textdata/publication_tfidf.pickle textdata/papertitles_tfidf.pickle
	$(EXEC_PREFIX)features.py $(GEN_DIR)/edges.txt $(PREFEAT) $@

$(GEN_DIR)/%.sim: features2similarity.py $(GEN_DIR)/%.feat
	$(EXEC_PREFIX)$^ $@; $(SORT_BIN) $@ -grk 3 -t"," -o $@

$(GEN_DIR)/%.prob: edge-predict.py $(GEN_DIR)/%.feat $(GEN_DIR)/model.pickle
	$(EXEC_PREFIX)$^ $@; $(SORT_BIN) $@ -grk 3 -t"," -o $@
	
$(GEN_DIR)/model.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ $(TRAIN_PARA)

grid_%: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ --gridsearch --clf $* $(FEAT_PARA) > $(GEN_DIR)/$@.log

$(GEN_DIR)/model_%.pickle: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ $@ --clf $* $(TRAIN_PARA)

$(GEN_DIR)/%_model.pickle: edge-train.py $(DATA_DIR)/train_%.csv $(GEN_DIR)/train_%.feat
	$(EXEC_PREFIX)$^ $@ $(TRAIN_PARA)

cv: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ --cv $(FEAT_PARA)

cv-gbm: edge-train.py $(DATA_DIR)/train.csv $(GEN_DIR)/train.feat
	$(EXEC_PREFIX)$^ --cv --clf gbm $(FEAT_PARA)
	
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

$(GEN_DIR)/%_hc.clusters: cluster_hc.py $(GEN_DIR)/%.prob
	$(EXEC_PREFIX)$^ $@ > $(GEN_DIR)/$*.hc.clusters-stats

$(GEN_DIR)/%_kruskal.clusters: cluster_kruskal.py $(GEN_DIR)/%.prob
	$(EXEC_PREFIX)$^ $@ -A > $(GEN_DIR)/$*.kruskal.clusters-stats

$(GEN_DIR)/%.clusters-sim: cluster_cc.py $(GEN_DIR)/%.sim
	$(EXEC_PREFIX)$^ $@
