import re

#compiler message support

class code_position:

    def __init__(self, src = None, line = None, col = None, code = None, message = None):
        self.src = src
        self.line = line
        self.col = col
        self.code = code
        self.message = message

class compiler_message:

    (VERBOSE, WARNING, ERROR, UNKNOWN) = (0, 1, 2, 3)

    def __init__(self, compiler_string = None):

        self.type = self.UNKNOWN
        self.message = ''
        self.src_pos = None
        self.error_pos = None

        if compiler_string is not None:
            self.from_string(compiler_string)

    def from_string(self, compiler_string):

        lines = compiler_string.split('\n')

        i = 0

        #debug
        print "nb lines %d" % (len(lines))

        for l in lines:
            l = l.strip('\n')
            if i == 0:
                #error source
                r1 = re.compile('(?P<source>.+):(?P<line>[0-9]+):(?P<col>[0-9]+):')
                r2 = re.compile('(?P<source>.+): (?P<message>.+):')
                m = r1.match(l)
                m2 = r2.match(l)
                if m:
                    source = m.group("source")
                    line = int(m.group("line"))
                    col = int(m.group("col"))
                    self.src_pos = code_position(source, line, col)
                elif m2:
                    source = m.group("source")
                    message = m.group("message")

                    self.src_pos = code_position(source, 0, 0, None, message)
                else:
                    print 'no match!'
                    print l

            elif i == 1:
                #error type and error message
                r2 = re.compile('(?P<filepath>.+):(?P<line>[0-9]+):(?P<col>[0-9]+): (?P<type>error|warning): (?P<message>.+)')

                m = r2.match(l)

                if m:
                    filepath = m.group('filepath')
                    line = int(m.group('line'))
                    col = int(m.group('col'))
                    etype = m.group('type')
                    message = m.group('message')
                    self.message = ''

                    self.error_pos = code_position(filepath, line, col, None, message)

                    if etype == 'error':
                        self.type = self.ERROR
                    elif etype == 'warning':
                        self.type = self.WARNING
                else:
                    print 'no match!'
                    print l

            else:
                self.message = self.message + l + '\n'

            i = i + 1

    def print_data(self):
        #for debug purpose
        print self.type
        print self.src_pos.src
        print self.src_pos.line, self.src_pos.col
        print self.message

        print self.error_pos.src
        print self.error_pos.line, self.error_pos.col

        print self.message
