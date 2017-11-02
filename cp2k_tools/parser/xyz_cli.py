# vim: set fileencoding=utf8 :

from __future__ import print_function

import re
import contextlib
import mmap

import click

from .xyz import FRAME_MATCH_REGEX

@contextlib.contextmanager
def mmapped(fhandle):
    fmapped = mmap.mmap(fhandle.fileno(), 0, access=mmap.ACCESS_READ)

    try:
        yield fmapped
    finally:
        fmapped.close()


CP2K_COMMENT_MATCH = re.compile(r"""
^[ \t]* i    [ ] = [ \t]+ (?P<iteration> \d+),
 [ \t]* time [ ] = [ \t]+ (?P<time> [\+\-]?  ( \d*[\.]\d+  | \d+[\.]?\d* )  ([Ee][\+\-]?\d+)? ),
 [ \t]* E    [ ] = [ \t]+ (?P<energy> [\+\-]?  ( \d*[\.]\d+  | \d+[\.]?\d* )  ([Ee][\+\-]?\d+)? )
""", re.VERBOSE)

# this one acts directly on the mmapped byte-like contnet:
FRAME_MATCH = re.compile(FRAME_MATCH_REGEX.encode('utf8'), re.VERBOSE | re.MULTILINE)


@click.command()
@click.argument('source', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def xyz_restart_cleaner(source, output):
    iteration = -1
    frames_cache = []

    with mmapped(source) as content:

        for frame in FRAME_MATCH.finditer(content):
            comment_match = CP2K_COMMENT_MATCH.match(frame.group('comment').decode('utf8'))

            last_iteration = iteration
            iteration = int(comment_match.group('iteration'))

            if iteration <= last_iteration:
                ndrop = last_iteration - iteration + 1
                if ndrop > len(frames_cache):
                    click.echo(
                        "WARNING: found earlier restart point than previous one, can not drop already flushed frames",
                        err=True)
                nflush = max(0, len(frames_cache) - ndrop)  # we can't flush more than what's inside the cache
                click.echo(("found restart point @{iteration},"
                            " dropping {drop} frames, flushing {flush}"
                           ).format(flush=nflush, drop=ndrop, iteration=last_iteration))
                for cached_frame in frames_cache[:-ndrop]:
                    output.write(cached_frame)
                del frames_cache[:]  # .clear(), but compatible with python 2

            frames_cache.append(frame.group(0))  # the 0. group is always the complete match

        click.echo("flushing remaining {flush} frames".format(flush=len(frames_cache)))
        for frame in frames_cache:
            output.write(frame)
