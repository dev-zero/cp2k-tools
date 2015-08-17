
import re

class ElementParserSection:
    def __init__(self):
        self._p = {
                'DBCSR': {},
                'CP2K': {},
                'GLOBAL': {},
                'ENERGY': {}
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

class ElementParserProgramInfo:
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

     # this element parser is stateless, always finish directly
    def finished(self):
        return self._finished

class ElementParserError:
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

class ElementParserTable:
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
            else:
                if len(line.strip()) > 0:
                    print('no parser found for: "%s"' % line)

        #import pprint
        #pp = pprint.PrettyPrinter(indent=2)
        #pp.pprint(self._p)


