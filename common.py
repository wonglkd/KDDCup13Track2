import sys
import exceptions

def print_err(*args):
    sys.stderr.write(' '.join(map(str,args)) + '\n')

def skip_comments(iterable):
    for line in iterable:
        if not line.startswith('#'):
            yield line

def num(s):
    try:
        return int(s)
    except exceptions.ValueError:
        return float(s)