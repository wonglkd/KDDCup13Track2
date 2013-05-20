SELECT id, pa.name, pa.affiliation
	FROM author a JOIN paperauthor pa ON AuthorId = a.Id WHERE a.name = '' AND pa.name <> '' ORDER BY a.Id, pa.name, pa.affiliation;