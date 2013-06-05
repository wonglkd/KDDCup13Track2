# Platform specific stuff
ifeq ($(OS),Windows_NT)
	# Windows
	EXEC32_PREFIX := "C:\Program Files (x86)\Python27\python.exe" 
	EXEC64_PREFIX := "C:\Python27_64\python.exe" 
	SORT_BIN := "C:\MinGW\msys\1.0\bin\sort"
else
	# Mac/Linux
	EXEC32_PREFIX := time ./
	EXEC64_PREFIX := time ./
	SORT_BIN := sort
endif

EXEC_PREFIX := $(EXEC64_PREFIX)