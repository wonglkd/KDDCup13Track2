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

.output pa_paperids.csv
SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=AuthorId
GROUP BY AuthorId, pa.PaperId;

.output pa_paperids_inpaper_titlenoblank.csv
SELECT pa.AuthorId, pa.PaperId, COUNT(*) FROM paperauthor pa JOIN awithpapers awp ON awp.Id=AuthorId JOIN paper p ON PaperId = p.Id
WHERE title <> ""
GROUP BY AuthorId, pa.PaperId;


CREATE TABLE pa_duppairs (PaperId INTEGER, AuthorId INTEGER, Count INTEGER, PRIMARY KEY (PaperId, AuthorId));
CREATE INDEX pa_duppairs_paperidx ON pa_duppairs (PaperId);
CREATE INDEX pa_duppairs_authoridx ON pa_duppairs (AuthorId);

SELECT COUNT(cnt) FROM
(SELECT LOWER(a.name), COUNT(*) as cnt FROM Author a JOIN 
(SELECT DISTINCT Id as AId FROM pa_duppairs JOIN Author ON AuthorId = Id)
ON AId = Id GROUP BY LOWER(name) HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC);

SELECT * FROM paperauthor pa JOIN (
SELECT * FROM pa_duppairs WHERE AuthorID IN (SELECT Id FROM Author WHERE Name = 'Chung-Kang Peng') ORDER BY AuthorId
) aa
ON aa.PaperId = pa.PaperId ORDER BY pa.AuthorId;

CREATE TABLE authorprocessed (id INT PRIMARY KEY, name_title TEXT, name_first TEXT, name_middle TEXT, name_last TEXT, name_suffix TEXT, name TEXT, iFfL TEXT, metaphone_fullname TEXT, affiliation TEXT);
SELECT COUNT(*) FROM (SELECT name_last, COUNT(*) as cnt FROM authorprocessed GROUP BY name_last HAVING COUNT(*) >= 2 ORDER BY cnt ASC);

SELECT COUNT(*) FROM
(SELECT name_last, COUNT(*) as cnt
FROM authorprocessed JOIN namelist ON name_last = surname
GROUP BY name_last);

-- no. of names not in whitelist
SELECT COUNT(*) FROM
(SELECT name_last, COUNT(*) as cnta
FROM authorprocessed
WHERE NOT EXISTS (SELECT NULL FROM namelist WHERE name_last = surname)
GROUP BY name_last HAVING COUNT(*) > 1 ORDER BY cnta);

-- no. of names in blacklist and not in whitelist
SELECT COUNT(*) FROM (SELECT name_last, COUNT(*) as cnta
FROM authorprocessed
WHERE EXISTS (SELECT NULL FROM engdict WHERE word = name_last)
AND NOT EXISTS (SELECT NULL FROM namelist WHERE name_last = surname)
GROUP BY name_last ORDER BY cnta);

-- no. of names that are not in whitelist and not in blacklist, and occurring more than once
SELECT COUNT(*) FROM
(SELECT name_last, COUNT(*) as cnta
FROM authorprocessed
WHERE NOT EXISTS (SELECT NULL FROM engdict WHERE word = name_last)
AND NOT EXISTS (SELECT NULL FROM lastname WHERE name_last = lastname.name)
GROUP BY name_last HAVING COUNT(*) > 1);

-- no

CREATE TABLE engdict (word TEXT PRIMARY KEY);

CREATE TABLE namelist (surname TEXT PRIMARY KEY, cnt INTEGER);

CREATE TABLE lastname_2000 (surname TEXT PRIMARY KEY, cnt INTEGER);
CREATE TABLE lastname_1990 (surname TEXT PRIMARY KEY, per FLOAT);
CREATE TABLE engdict (word TEXT PRIMARY KEY);
CREATE TABLE lastname (name TEXT PRIMARY KEY);
INSERT INTO lastname
SELECT surname FROM (SELECT surname FROM lastname_1990 UNION SELECT surname FROM lastname_2000);

SELECT DISTINCT AuthorId FROM pa_duppairs WHERE AuthorID IN (SELECT Id FROM Author WHERE Name = 'Chung-Kang Peng') ORDER BY AuthorId

Authors
349745
979292
1077240
1457448
1789568


1077240
1457448
210761

CREATE TABLE paper_u (Id INTEGER PRIMARY KEY,Title TEXT,Year INTEGER,ConferenceId INTEGER,JournalId INTEGER,Keyword TEXT);
CREATE INDEX paper_u_text_idx ON paper_u (title);

-- .output pa_titles_all.csv
-- SELECT pa.AuthorId, p1.Title, COUNT(*) FROM paper_u p1 JOIN paperauthor pa ON p1.Id = pa.paperId
-- JOIN awithpapers awp ON awp.Id=AuthorId
-- WHERE EXISTS (SELECT * FROM paper_u p2 WHERE p2.Title = p1.Title AND (p2.Id < p1.Id OR p2.Id > p1.Id))
-- AND p1.Title <> ""
-- GROUP BY AuthorId, p1.Title
-- ORDER BY p1.Title;

.output pa_titles_dup.csv
SELECT pa.AuthorId, p1.Title, COUNT(*) FROM paper_u p1 JOIN paperauthor pa ON p1.Id = pa.paperId
JOIN awithpapers awp ON awp.Id=AuthorId
WHERE EXISTS (SELECT * FROM paper_u p2 WHERE p2.Title = p1.Title AND (p2.Id < p1.Id OR p2.Id > p1.Id)) AND
p1.Title <> ""
GROUP BY AuthorId, p1.Title
ORDER BY p1.Title;

.output pa_titles.csv
SELECT pa.AuthorId, p1.Title, COUNT(*) FROM paper_u p1 JOIN paperauthor pa ON p1.Id = pa.paperId
JOIN awithpapers awp ON awp.Id=AuthorId
WHERE p1.Title <> ""
GROUP BY AuthorId, p1.Title
ORDER BY p1.Title;

-- optimisation -- WHERE paperTitle is not unique

.output pa_coauthors.csv
SELECT pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', ''))) as Coauthor, COUNT(*) as cnt
FROM paperauthor pa1 JOIN paperauthor pa2 ON pa1.PaperId = pa2.PaperId
JOIN awithpapers a ON a.Id = pa1.AuthorId
GROUP BY pa1.AuthorId, LOWER(TRIM(REPLACE(pa2.name, ';', '')));

----
CREATE TABLE pa_coauthors_ (AuthorId INT, Coauthor TEXT, cnt INT);
.import pa_coauthors_u_noheader.csv pa_coauthors_

CREATE TABLE pa_coauthors (AuthorId INT, Coauthor TEXT, cnt INT, PRIMARY KEY (AuthorId, Coauthor));

INSERT INTO pa_coauthors (AuthorId, Coauthor, cnt)
SELECT AuthorId, Coauthor, SUM(cnt) as cnt FROM pa_coauthors_ GROUP BY AuthorId, Coauthor;

CREATE INDEX pa_coauthors_authorid_idx  ON pa_coauthors (AuthorId);

DROP TABLE pa_coauthors_;

CREATE TABLE pa_coauthors_total (AuthorId INT PRIMARY KEY, cnt INT, total INT);
INSERT INTO pa_coauthors_total (AuthorId, cnt, total)
SELECT AuthorId, COUNT(*), SUM(cnt) FROM pa_coauthors GROUP BY AuthorId;

SELECT
			(SELECT COUNT(*) FROM
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = 1688847
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = 364837)) as common
		,
			(SELECT cnt FROM pa_coauthors_total
			WHERE AuthorId = 1688847) as cnt1
		,
			(SELECT cnt FROM pa_coauthors_total
			WHERE AuthorId = 364837) as cnt2
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
			(SELECT total FROM pa_coauthors_total
			WHERE AuthorId = 1688847) as cnt1
		,
			(SELECT total FROM pa_coauthors_total
			WHERE AuthorId = 364837) as cnt2
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
			(SELECT total FROM pa_coauthors_total
			WHERE AuthorId = 426) as cnt1
		,
			(SELECT total FROM pa_coauthors_total
			WHERE AuthorId = 1107709) as cnt2
;

-- coauthorF

SELECT IFNULL(SUM(CoauthorF),0) FROM
(SELECT co0.Coauthor, co0.AuthorId, co0.cnt, pact.total, co0.cnt*1.0 / pact.total As CoauthorF
FROM
			(pa_coauthors co0 JOIN
			(SELECT Coauthor FROM pa_coauthors co1
			WHERE co1.AuthorId = 1688847
			INTERSECT
			SELECT Coauthor FROM pa_coauthors co2
			WHERE co2.AuthorId = 364837) co_ ON co_.Coauthor = co0.Coauthor)
			JOIN pa_coauthors_total pact ON pact.AuthorId = co0.AuthorId
			WHERE co0.AuthorId IN (364837,1688847)
			GROUP BY co0.Coauthor, co0.AuthorId)
;

.mode csv
.header ON
.output paper_duplicatetitles.csv
SELECT * FROM paper p1
WHERE p1.Title <> "" AND EXISTS (SELECT * FROM paper p2 WHERE p2.Title = p1.Title AND (p2.Id < p1.Id OR p2.Id > p1.Id))
ORDER BY p1.title;


--SELECT * FROM paper p1 JOIN paper p2 ON (p1.Id < p2.Id and p1.Title = p2.Title) WHERE p1.Title <> "";

SELECT * FROM paper WHERE Title = "" LIMIT 10;
-----


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
