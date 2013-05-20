DATA_DIR := data
GEN_DIR := generated

AUTHOR_SET := Author
# AUTHOR_SET := Author_f20000
PREFEAT := $(GEN_DIR)/$(AUTHOR_SET)_prefeat.pickle
BIN_METHODS := iFfL samename

all: $(GEN_DIR)/iFfL_bins.txt $(GEN_DIR)/iFfL_edges.txt $(GEN_DIR)/iFfL.feat $(GEN_DIR)/iFfL.sim $(GEN_DIR)/iFfL.clusters $(GEN_DIR)/iFfL-submit.csv $(PREFEAT)
feat-t: $(GEN_DIR)/iFfL.feat
cluster-t: $(GEN_DIR)/iFfL.clusters
sim-t: $(GEN_DIR)/iFfL.sim
bins: $(addprefix $(GEN_DIR)/,$(BIN_METHODS:=_bins.txt))

prefeat-t: $(GEN_DIR)/Author_f20000_prefeat.pickle 

$(GEN_DIR)/%_bins.txt: blocking.py $(PREFEAT)
	time ./$^ $* > $@

$(GEN_DIR)/%_edges.txt: edges.py $(GEN_DIR)/%_bins.txt
	time ./$^ > $@

$(GEN_DIR)/%_prefeat.pickle: process_authors.py $(DATA_DIR)/%.csv
	time ./$^ $@

$(GEN_DIR)/%.feat: features.py $(GEN_DIR)/%_edges.txt $(PREFEAT)
	time ./$^ $@

$(GEN_DIR)/%.sim: features2similarity.py $(GEN_DIR)/%.feat
	time ./$^ $@; sort $@ -nrk 3 -t"," -o $@

$(GEN_DIR)/%.prob: edge-predict.py $(GEN_DIR)/%.feat $(GEN_DIR)/model.pickle
	time ./$^ $@; sort $@ -nrk 3 -t"," -o $@
	
$(GEN_DIR)/model.pickle: edge-train.py
	time ./$^

$(GEN_DIR)/%-submit.csv: prep_submit.py $(GEN_DIR)/%.clusters
	time ./$^ $@

# awk '{ if ($3 >= 0.6) print $0; }'

$(GEN_DIR)/%.clusters: cluster-hc.py $(GEN_DIR)/%.prob
	time ./$^ $@ > $(GEN_DIR)/$*.clusters-stats

$(GEN_DIR)/%.clusters-sim: cluster-cc.py $(GEN_DIR)/%.sim
	time ./$^ $@
