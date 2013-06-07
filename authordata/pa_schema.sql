.mode csv

CREATE TABLE pa_coauthors (AuthorId INT, Coauthor INT, cnt INT, PRIMARY KEY (AuthorId, Coauthor));
.import pa_coauthors_u_strippunc_idified_cnts.csv pa_coauthors

CREATE INDEX pa_coauthors_authorid_idx  ON pa_coauthors (AuthorId);

CREATE TABLE pa_coauthors_total (AuthorId INT PRIMARY KEY, cnt INT, total INT);
INSERT INTO pa_coauthors_total (AuthorId, cnt, total)
SELECT AuthorId, COUNT(*), SUM(cnt) FROM pa_coauthors GROUP BY AuthorId;

CREATE TABLE pa_coauthors_ids (AuthorId INT, Coauthor_id INT, cnt INT, PRIMARY KEY (AuthorId, Coauthor_id));
.import pa_coauthors_ids_cnts.csv pa_coauthors_ids

CREATE INDEX pa_coauthors_ids_authorid_idx  ON pa_coauthors_ids (AuthorId);

CREATE TABLE pa_coauthors_ids_total (AuthorId INT PRIMARY KEY, cnt INT, total INT);
INSERT INTO pa_coauthors_ids_total (AuthorId, cnt, total)
SELECT AuthorId, COUNT(*), SUM(cnt) FROM pa_coauthors_ids GROUP BY AuthorId;

ANALYZE;
VACUUM;
