# Platform specific stuff
ifeq ($(OS),Windows_NT)
	# Windows
	EXEC_PREFIX := "C:\Program Files (x86)\Python27\python.exe" 
	SORT_BIN := "C:\MinGW\msys\1.0\bin\sort"
else
	# Mac/Linux
	EXEC_PREFIX := time ./
	SORT_BIN := sort
endif