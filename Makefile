DATA_DIR := data
GEN_DIR := generated

AUTHOR_SET := Author_f20000

BIN_METHODS := iFfL samename

feat-t: $(GEN_DIR)/iFfL.feat
sim-t: $(GEN_DIR)/iFfL.sim
bins: $(addprefix $(GEN_DIR)/,$(BIN_METHODS:=_bins.txt))

$(GEN_DIR)/%_bins.txt: blocking.py $(DATA_DIR)/$(AUTHOR_SET).csv
	time ./$< $* > $@

$(GEN_DIR)/%_edges.txt: edges.py $(GEN_DIR)/%_bins.txt
	time ./$^ > $@			

$(GEN_DIR)/%_prefeat.pickle: process_authors.py $(DATA_DIR)/%.csv
	time ./$^ $@

$(GEN_DIR)/%.feat: features.py $(GEN_DIR)/%_edges.txt $(GEN_DIR)/$(AUTHOR_SET)_prefeat.pickle
	time ./$^ $@

$(GEN_DIR)/%.sim: features2similarity.py $(GEN_DIR)/%.feat
	time ./$^ $@
