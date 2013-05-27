SELECT id, pa.name, pa.affiliation
	FROM author a JOIN paperauthor pa ON AuthorId = a.Id WHERE a.name = '' AND pa.name <> '' ORDER BY a.Id, pa.name, pa.affiliation;

.mode csv
.output pa_names.csv
SELECT AuthorId, LOWER(TRIM(REPLACE(name, ';', ''))), COUNT(*) FROM paperauthor JOIN awithpapers ON Id=AuthorId
WHERE name <> ''
GROUP BY AuthorId, LOWER(TRIM(REPLACE(name, ';', '')));

.output pa_affiliation.csv
SELECT AuthorId, LOWER(affiliation), COUNT(*) FROM paperauthor JOIN awithpapers ON Id=AuthorId
WHERE affiliation <> ''
GROUP BY AuthorId, LOWER(affiliation);

.output pa_years.csv
SELECT pa.AuthorId, p.year, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId
JOIN awithpapers awp ON awp.Id=AuthorId
WHERE p.year >= 1600 AND p.year <= 2013
GROUP BY AuthorId, p.year;

.output pa_conferences.csv
SELECT pa.AuthorId, p.ConferenceId, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId
JOIN awithpapers awp ON awp.Id=AuthorId
WHERE p.ConferenceId > 0
GROUP BY AuthorId, p.ConferenceId;

.output pa_journals.csv
SELECT pa.AuthorId, p.JournalId, COUNT(*) FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId
JOIN awithpapers awp ON awp.Id=AuthorId
WHERE p.JournalId > 0
GROUP BY AuthorId, p.JournalId;

.output pa_coauthors.csv
SELECT pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', ''))) as Coauthor, COUNT(*) as cnt
FROM paperauthor pa1 JOIN paperauthor pa2 ON pa1.PaperId = pa2.PaperId
JOIN awithpapers a ON a.Id = pa1.AuthorId
GROUP BY pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', '')));

CREATE TABLE pa_coauthors (AuthorId INT, Coauthor TEXT, cnt INT, PRIMARY KEY (AuthorId, Coauthor));

INSERT INTO pa_coauthors (AuthorId, Coauthor, cnt)
SELECT AuthorId, Coauthor, SUM(cnt) as cnt FROM pa_coauthors_ GROUP BY AuthorId, Coauthor;

CREATE INDEX pa_coauthors_authorid_idx  ON pa_coauthors (AuthorId);

DROP TABLE pa_coauthors_;

-- CREATE INDEX pa_coauthors_idx  ON Coauthor (AuthorId, Coauthor);
CREATE TABLE pa_coauthors_ (AuthorId INT, Coauthor TEXT, cnt INT);
.import pa_coauthors.csv pa_coauthors_

SELECT
			(SELECT COUNT(*) FROM
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = 1688847
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = 364837)) as common
		,
			(SELECT COUNT(Coauthor) FROM pa_coauthors co3
			WHERE co3.AuthorId = 1688847) as cnt1
		,
			(SELECT COUNT(Coauthor) FROM pa_coauthors co3
			WHERE co3.AuthorId = 364837) as cnt2
;

SELECT
			(SELECT IFNULL(SUM(mc),0) FROM (SELECT MIN(cnt) as mc FROM
			pa_coauthors co0 JOIN
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = 1688847
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = 364837) co_ ON co_.Coauthor = co0.Coauthor WHERE AuthorId IN (364837,1688847)
			GROUP BY co_.Coauthor
			)) as common
		,
			(SELECT SUM(cnt) FROM pa_coauthors co3
			WHERE co3.AuthorId = 1688847) as cnt1
		,
			(SELECT SUM(cnt) FROM pa_coauthors co3
			WHERE co3.AuthorId = 364837) as cnt2
;


SELECT
			(SELECT IFNULL(SUM(mc),0) FROM (SELECT MIN(cnt) as mc FROM
			pa_coauthors co0 JOIN
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = 426
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = 1107709) co_ ON co_.Coauthor = co0.Coauthor WHERE AuthorId IN (426,1107709)
			GROUP BY co_.Coauthor
			)) as common
		,
			(SELECT SUM(cnt) FROM pa_coauthors co3
			WHERE co3.AuthorId = 426) as cnt1
		,
			(SELECT SUM(cnt) FROM pa_coauthors co3
			WHERE co3.AuthorId = 1107709) as cnt2
;
 1107709


SELECT COUNT(Coauthor) FROM pa_coauthors co3
WHERE co3.AuthorId IN (1688847, 364837)
GROUP BY authorid

-- count number of papers that we actually need to parse
.output stdout
SELECT COUNT(DISTINCT p.Id) FROM
paper p
JOIN paperauthor ON p.Id = PaperId
JOIN awithpapers awp ON AuthorId = awp.Id;


SELECT pa.name, pa.affiliation, a.*, p.title, p.year FROM
(author a LEFT JOIN paperauthor pa ON AuthorID = a.ID)
LEFT JOIN paper p ON p.Id = PaperId
WHERE a.Id IN (96610)
LIMIT 50;
SELECT * FROM paperauthor WHERE AuthorID IN (96610);
SELECT * FROM author WHERE ID IN (96610);


-- SELECT COUNT(*) FROM paper p
-- WHERE EXISTS (SELECT * FROM paperauthor JOIN awithpapers awp ON awp.Id = AuthorId WHERE paperId = p.Id);


-- SELECT COUNT(*) FROM paper p
-- WHERE EXISTS (SELECT * FROM paperauthor WHERE paperId = p.Id AND AuthorId IN (2293204));

---
SELECT p.* FROM paper p JOIN paperauthor pa ON p.Id = pa.paperId
WHERE pa.AuthorId IN (2293204);

--- specific cases
SELECT pa1.AuthorId, pa2.name as Coauthor, COUNT(*) FROM paperauthor pa1 JOIN paperauthor pa2 ON pa1.PaperId = pa2.PaperId
WHERE pa1.AuthorId IN (2293114)
GROUP BY pa2.name;

SELECT AuthorId, COUNT(*), name FROM paperauthor
WHERE AuthorId IN (2293114,2293128,2293145,2293164,2293182,2293185,2293204,2293245,2293252,2293267,2293343)
GROUP BY AuthorId, name;



-- EXPLAIN QUERY PLAN
-- SELECT AuthorId, COUNT(*), name FROM paperauthor JOIN awithpapers ON Id=AuthorId
-- GROUP BY AuthorId, name;
-- LIMIT 1;
-- WHERE Id IN (282832,1837250)