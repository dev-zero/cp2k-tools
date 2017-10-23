# originally from http://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
import contextlib
import sys

@contextlib.contextmanager
def smart_open(filename=None, flag='w'):
    if filename and filename != '-':
        fh = open(filename, flag)
    else:
        if flag is 'w':
            fh = sys.stdout
        elif flag is 'r':
            fh = sys.stdin

    try:
        yield fh
    finally:
        if (fh is not sys.stdout) and (fh is not sys.stdin):
            fh.close()
