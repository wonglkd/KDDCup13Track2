ROOT_DIR := ..
DB_FILE := $(ROOT_DIR)/db/kddcup13.sqlite3
SQLITE_PATH := sqlite3
SQLITE_CMDS := -csv -header
SQLITE_EXEC := $(SQLITE_PATH) $(SQLITE_CMDS) $(DB_FILE)

OBJECTS := names_u affiliation_u years conferences journals paperids coauthors_u paperids_inpaper_titlenoblank
FILENAMES := $(foreach i,$(OBJECTS),pa_$(i).csv)

all: $(FILENAMES)

pa_names.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT AuthorId, LOWER(TRIM(REPLACE(name, ';', ''))), COUNT(*) FROM paperauthor JOIN awithpapers ON Id=AuthorId WHERE name <> '' GROUP BY AuthorId, LOWER(TRIM(REPLACE(name, ';', '')))" > $@

pa_affiliation.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT AuthorId, LOWER(affiliation), COUNT(*) FROM paperauthor JOIN awithpapers ON Id=AuthorId WHERE affiliation <> '' GROUP BY AuthorId, LOWER(affiliation)" > $@

pa_years.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p.year, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p.year >= 1600 AND p.year <= 2013 GROUP BY AuthorId, p.year" > $@

pa_conferences.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p.ConferenceId, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p.ConferenceId > 0 GROUP BY AuthorId, p.ConferenceId" > $@

pa_journals.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p.JournalId, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p.JournalId > 0 GROUP BY AuthorId, p.JournalId" > $@

pa_paperids.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=AuthorId GROUP BY AuthorId, pa.PaperId" > $@

pa_paperids_inpaper_titlenoblank.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=AuthorId JOIN paper p ON PaperId = p.Id WHERE title <> '' GROUP BY AuthorId, pa.PaperId" > $@

pa_coauthors.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', ''))) as Coauthor, COUNT(*) as cnt FROM paperauthor pa1 JOIN paperauthor pa2 ON pa1.PaperId = pa2.PaperId JOIN awithpapers a ON a.Id = pa1.AuthorId GROUP BY pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', '')))" > $@

pa_titles.csv: $(DB_FILE)
	$(SQLITE_EXEC) "SELECT pa.AuthorId, p1.Title, COUNT(*) FROM paper_u p1 JOIN paperauthor pa ON p1.Id = pa.paperId JOIN awithpapers awp ON awp.Id=AuthorId WHERE p1.Title <> '' GROUP BY AuthorId, p1.Title ORDER BY p1.Title" > $@

%_u.csv: $(ROOT_DIR)/unidecodefile.py %.csv
	$^ $@
