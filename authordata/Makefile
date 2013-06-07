ROOT_DIR := ..
include $(ROOT_DIR)/Makefile.inc

DB_FILE := $(ROOT_DIR)/db/kddcup13.sqlite3
SQLITE_OPTS := -csv -header
SQLITE_EXEC := $(SQLITE_BIN) $(SQLITE_OPTS) $(DB_FILE)

OBJECTS := names_u_strippunc names_dup_u_strippunc affiliation_u conferences journals paperids paperids_dup years coauthors_u_strippunc coauthors_dup_u_strippunc coauthors_ids coauthors_ids_dup paperids_inpaper_titlenoblank paperids_inpaper_titlenoblank_dup titles_idified
FILENAMES := $(foreach i,$(OBJECTS),pa_$(i).csv)

all: $(FILENAMES)

pa_names.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT AuthorId, LOWER(TRIM(REPLACE(name, ';', ''))), COUNT(*) FROM paperauthor JOIN awithpapers ON Id=AuthorId WHERE name <> '' GROUP BY AuthorId, LOWER(TRIM(REPLACE(name, ';', '')))" -cmd ".output $@"

pa_names_dup.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT dup.AuthorId, LOWER(TRIM(REPLACE(name, ';', ''))), COUNT(*) FROM pa_duppairs dup, awithpapers awp, paperauthor pa WHERE awp.Id=dup.AuthorId and dup.AuthorId = pa.AuthorId and dup.PaperId = pa.PaperId and name <> '' GROUP BY dup.AuthorId, LOWER(TRIM(REPLACE(name, ';', '')))" -cmd ".output $@"

pa_affiliation.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT AuthorId, LOWER(affiliation), COUNT(*) FROM paperauthor JOIN awithpapers ON Id=AuthorId WHERE affiliation <> '' GROUP BY AuthorId, LOWER(affiliation)" -cmd ".output $@"

pa_years.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p.year, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p.year >= 1600 AND p.year <= 2013 GROUP BY AuthorId, p.year" -cmd ".output $@"

pa_conferences.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p.ConferenceId, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p.ConferenceId > 0 GROUP BY AuthorId, p.ConferenceId" -cmd ".output $@"

pa_journals.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p.JournalId, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p.JournalId > 0 GROUP BY AuthorId, p.JournalId" -cmd ".output $@"

pa_paperids.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=AuthorId GROUP BY AuthorId, pa.PaperId" -cmd ".output $@"

pa_paperids_dup.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=pa.AuthorId JOIN pa_duppairs dup ON dup.paperId = pa.paperId and dup.AuthorId = pa.AuthorId GROUP BY pa.AuthorId, pa.PaperId" -cmd ".output $@"

pa_paperids_inpaper_titlenoblank.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=AuthorId JOIN paper p ON PaperId = p.Id WHERE title <> '' GROUP BY AuthorId, pa.PaperId" -cmd ".output $@"

pa_paperids_inpaper_titlenoblank_dup.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=pa.AuthorId JOIN paper p ON pa.PaperId = p.Id JOIN pa_duppairs dup ON dup.paperId = pa.paperId and dup.AuthorId = pa.AuthorId WHERE title <> '' GROUP BY pa.AuthorId, pa.PaperId" -cmd ".output $@"

pa_coauthors.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', ''))) as Coauthor, COUNT(*) as cnt FROM paperauthor pa1 JOIN paperauthor pa2 ON pa1.PaperId = pa2.PaperId JOIN awithpapers a ON a.Id = pa1.AuthorId WHERE LOWER(TRIM(REPLACE(pa2.name, ';', ''))) <> '' AND pa1.AuthorId <> pa2.AuthorId GROUP BY pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', '')))"  -cmd ".output $@"

pa_coauthors_dup.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT dup1.AuthorId, LOWER(TRIM(REPLACE(pa.name, ';', ''))) as Coauthor, COUNT(*) as cnt FROM pa_duppairs dup1 JOIN pa_duppairs dup2 ON dup1.PaperId = dup2.PaperId JOIN awithpapers a ON a.Id = dup1.AuthorId JOIN paperauthor pa ON dup2.paperId = pa.paperId and dup2.AuthorId = pa.AuthorId WHERE LOWER(TRIM(REPLACE(pa.name, ';', ''))) <> '' AND dup1.AuthorId <> dup2.AuthorId GROUP BY dup1.AuthorId, LOWER(TRIM(REPLACE(pa.name, ';', '')))"

pa_coauthors_ids.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa1.AuthorId, pa2.AuthorId as Coauthor, COUNT(*) as cnt FROM paperauthor pa1 JOIN paperauthor pa2 ON pa1.PaperId = pa2.PaperId JOIN awithpapers a ON a.Id = pa1.AuthorId WHERE pa1.AuthorId <> pa2.AuthorId GROUP BY pa1.AuthorId, pa2.AuthorId" -cmd ".output $@"

pa_coauthors_ids_dup.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa1.AuthorId, pa2.AuthorId as Coauthor, COUNT(*) as cnt FROM pa_duppairs pa1 JOIN pa_duppairs pa2 ON pa1.PaperId = pa2.PaperId JOIN awithpapers a ON a.Id = pa1.AuthorId WHERE pa1.AuthorId <> pa2.AuthorId GROUP BY pa1.AuthorId, pa2.AuthorId" -cmd ".output $@"

pa_titles.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p1.Title, COUNT(*) FROM paper_u p1 JOIN paperauthor pa ON p1.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p1.Title <> '' GROUP BY AuthorId, p1.Title ORDER BY p1.Title" -cmd ".output $@"

%_u.csv: $(ROOT_DIR)/unidecodefile.py %.csv
	$(EXEC_PREFIX)$^ $@

%_u_strippunc.csv: $(ROOT_DIR)/unidecodefile.py %.csv
	$(EXEC_PREFIX)$^ $@ -p

%_cnts.csv: %.csv
	$(SORT_BIN) $< -o $< ; \
		uniq -c $< | awk 'BEGIN {OFS=","} {print $$2, $$1}' > $@

../db/pa.sqlite3: pa_schema.sql pa_coauthors_u_strippunc_idified_cnts.csv pa_coauthors_ids_cnts.csv
	$(SQLITE_BIN) -csv $@ < $<