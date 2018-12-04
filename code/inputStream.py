class InputStream():
    def __init__(self, stream):
        assert(type(stream) == str)
        self.stream = stream
        self.pos = 0
        self.line = 1
        self.col = 0
        self.__current_line = ''
    def append(self, datas):
        assert(type(datas) == str)
        self.stream += datas
    def next(self):
        ch = self.stream[self.pos]
        self.pos += 1
        if (ch == '\n'):
            self.line += 1
            self.col = 0
            self.__current_line = ''
        else:
            self.col += 1
            self.__current_line += ch
        return ch
    def peek(self):
        return self.stream[self.pos]
    def eof(self):
        return self.pos >= len(self.stream)
    def error(self, msg):
        raise Exception('ERROR: {}\nat line {}, col {}\n{}'.format(msg, self.line, self.col, self.__current_line))

if __name__ == '__main__':
    ipstr = InputStream('abcdefg')
    while True:
        if ipstr.eof():
            break
        print(ipstr.peek())
        print(ipstr.next())
    print('ok')
    ipstr.error('heiyo')

