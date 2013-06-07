# Platform specific stuff
ifeq ($(OS),Windows_NT)
	# Windows - note: extra space behind for prefix
	EXEC32_PREFIX := "C:\Program Files (x86)\Python27\python.exe" 
	EXEC64_PREFIX := "C:\Python27_64\python.exe" 
	SORT_BIN := "C:\MinGW\msys\1.0\bin\sort"
	SQLITE_BIN := "D:\Daniel\software\sqlite3"
else
	# Mac/Linux
	EXEC32_PREFIX := time ./
	EXEC64_PREFIX := time ./
	SORT_BIN := sort
	SQLITE_BIN := sqlite3
endif

EXEC_PREFIX := $(EXEC64_PREFIX)