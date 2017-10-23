
class ElementParserSection:
    import re

    def __init__(self):
        self._p = {
                'DBCSR': dict(),
                'CP2K': dict(),
                'GLOBAL': dict(),
                'ENERGY': dict()
                }
        self._k = ''
        self._v = ''

    # returns true if parser can parse this line
    def match(self, line):
        m = re.match('^ (?P<key>[a-zA-Z0-9]+)\| (?P<value>.*)', line)
        if m:
            self._k = m.group('key')
            self._v = m.group('value')
            return True

        return False

    def parse(self, line):
        if self._k in self._p.keys():
            ms = re.match('^(?P<desc>.+?)(?:\s{2,})(?P<value>.+)', self._v)
            if ms:
                # add the found desc/parameter, but strip ':' beforehand
                self._p[self._k][ms.group('desc').rstrip(':')] = ms.group('value')
            else:
                raise InvalidValueForKey(self._k, self._v)

    # this element parser is stateless, always finish directly
    def finished(self):
        return True

    def data(self):
        return self._p


class ElementParserProgramInfo:
    import re

    def __init__(self):
        self._k = ''
        self._v = ''
        self._finished = True
        self._p = {}

    # returns true if parser can parse this line
    def match(self, line):
        # if we are here, we finished parsing before
        self._finished = True

        m = re.match('^ [\* ]{13,} PROGRAM (?P<key>(STARTED (AT|ON|BY|IN))|(RAN (ON|BY))|STOPPED IN|PROCESS ID|ENDED AT)\s+(?P<value>.*)$', line)

        if m:
            self._k = m.group('key')
            self._v = m.group('value')
            return True

        return False

    def parse(self, line):
        if self._finished:
            self._p[self._k] = self._v

            if self._k in ['STARTED IN', 'STOPPED IN']:
                # we have to check the next line first
                self._finished = False

        # possible second line of the value
        else:
            mp = re.match(' \s{42}(?P<value>.+)', line)
            if mp:
                # append the value to the existing one and return True to get another peek,
                # we might have yet another line after all!
                self._p[self._k] += mp.group('value').strip()
                return True

            # give other parsers a chance with this line, but we are done here
            self._finished = True
            return False

    def finished(self):
        return self._finished

    def data(self):
        return {'PROGRAM': self._p}


class ElementParserError:
    import re

    # returns true if parser can parse this line
    def match(self, line):
        m = re.match('^ \*{76}$', line)

        if m:
            return True

        return False

    def parse(self, line):
        if self._k in self._p.keys():
            ms = re.match('^(?P<desc>.+?)(?:\s{2,})(?P<value>.+)', self._value)
            if ms:
                # add the found desc/parameter, but strip ':' beforehand
                self._p[self._k][ms.group('desc').rstrip(':')] = ms.group('value')
            else:
                raise InvalidValueForKey(self._k, self._value)

    # this element parser is stateless, always finish directly
    def finished(self):
        return True

    def data(self):
        return {}


class ElementParserTable:
    import re

    def __init__(self):
        self._tn = ''

    # returns true if parser can parse this line
    def match(self, line):
        m = re.match('^ \*\*\* (?P<tablename>.+?) \*\*\*$', line)

        if m:
            self._tn = m.group('tablename')
            return True

        return False

    def parse(self, line):
        pass

    # this element parser is stateless, always finish directly
    def finished(self):
        return True

    def data(self):
        return {}

class CP2KOutputParser:
    def __init__(self):
        self._parsers = [
                ElementParserSection(),
                ElementParserError(),
                ElementParserProgramInfo(),
                ] 

    def parse(self, fh):
        p = None
        for line in fh:
            line = line.strip('\n')

            # if we still have an element parser set and it is not done yet, continue with that one
            if p is not None and not p.finished():
                # in case the parser needed a lookahead but was in fact done, it will return false
                if p.parse(line):
                    continue

            # otherwise restart with all possible parsers
            for p in self._parsers:
                if p.match(line):
                    p.parse(line)
                    break
#            else:
#                if len(line.strip()) > 0:
#                    print('no parser found for: "%s"' % line)

    # the query language is supposed to follow the one from the 'jq' tool,
    # but for now we support only '.' (for everything), '.foo.bar' and 
    def query(self, q):
        import re

        keys = q.split('.')

        # the string should start with a '.', so the first segment is always empty
        # TODO: throw exception here
        if keys[0]:
            return {}

        d = {}

        # merge the data of all parsers first
        for p in self._parsers:
            for k, v in p.data().items():
                d[k] = v

        # if the second key is empty, '.' was passed and we return everything
        if not keys[1] and len(keys) is 2:
            return d

        # the first key is always in one of the parsers
        try:
            for k in keys[1:]:
                m = re.match(r'(?P<k>[^\[\]]*)(\[(?P<i>[\d\[\]]+)\])?$', k)
                if m.group('k') is not None:
                    d = d[m.group('k')]
                if m.group('i') is not None:
                    for i in m.group('i').split(']['):
                        # for dictionaries sort it alphabetically first (which makes it automatically a list of pairs)
                        if type(d) is dict:
                            d = sorted(d.items())
                        d = d[int(i)]

        # ignore key or type errors (when walking the parser data objects)
        except (TypeError, KeyError, IndexError):
            return {}

        return d

class BlockParserReferences:
    name = 'references'

    import regex

    _ref_table = regex.compile(r'''
\ \-+\n                                     # {
\ \-\ +\-\n                                 #
\ \-\ +R\ E\ F\ E\ R\ E\ N\ C\ E\ S\ +\-\n  #   match the header
\ \-\ +\-\n                                 #
\ \-+\n                                     # }
\ \n                                        # the newline between the header and the first entry
(\ CP2K.+\n){2}                             # also consume the two header CP2K declaration lines
\n
(                                           # match one block/reference
  (?P<references>(?s).*?                    #   non-greedily match everything (including newlines)
  (?=\n\n))                                 #   .. except two newlines
  \n+                                       #   now consume all newlines
)+                                          # there can be multiple references of course
(?=\ \-+\n)                                 # stop at ' --' because that marks the next table
        ''', regex.X | regex.M | regex.VERSION1)

    _ref_block = regex.compile(r'''
\s*                                         # consume the whitespace at the beginning
(?P<authors>[\w\s,\-]+)                     # match the primary author
(;(?P<authors>[\w\s,\-]+))*                 # .. and all others if available
\.\s*                                       # .. until the . and consume any whitespaces
(?P<journal>[\w\s\-]+),\s
(?P<volume>[\d\s\(\)\-]+),\s
(?P<pages>\d+\-\d+)\s
\( (?P<year>\d{4}) \)
\.\s*
(?P<title>[^\.]+)
\.\s*
(?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)
        ''', regex.X)

    @classmethod
    def parse(cls, txt):
        """
        Parse the provided string for reference block and return
        a tuple (content, nonparsedstring).
        """
        entry = lambda r: {
            'authors': r.captures('authors'),
            'journal': r.group('journal'),
            'volume':  r.group('volume'),
            'pages':   r.group('pages'),
            'year':    r.group('year'),
            'title':   r.group('title'),
            'url':     r.group('url'),
            }
        return ([entry(cls._ref_block.search(ref.replace('\n', '')))
                for ref in cls._ref_table.search(txt).captures('references')],
            cls._ref_table.sub("", txt))


class CP2KOutputBlockParser:
    """
    Parser working on a complete CP2K output log string and parsing it block by block
    (in contrast to the line-by-line streaming parser operating on a file handle)
    """

    def __init__(self):
        self._bparsers = [
            BlockParserReferences
        ]

    def parse(self, txt):
        out = {}
        for p in self._bparsers:
            out[p.name], txt = p.parse(txt)

        return out
