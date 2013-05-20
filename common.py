import sys

def print_err(*args):
    sys.stderr.write(' '.join(map(str,args)) + '\n')
