from inputStream import InputStream
typeList = ['op', 'punc', 'identity', 'number', 'keyword', 'string', 'bool']

# class Token():
#     def __init__(self, type_, value_):
#         self.type = type_
#         self.value = value_
#     def __repr__(self):
#         return str({
#             'type': self.type,
#             'value': self.value
#         })

class Tokenizer():
    def __init__(self, ipstr):
        assert(type(ipstr) == InputStream)
        self.ipstr = ipstr
        self.__current = None
    
    def peek(self):
        if self.__current is not None:
            return self.__current
        self.__current = self.__next()
        return self.__current
    
    def next(self):
        if self.__current is not None:
            ret = self.__current
            self.__current = None 
            return ret
        return self.__next()
    
    def eof(self):
        return self.peek() is None
    
    def error(self, msg):
        return self.ipstr.error(msg)

    def __next(self):
        if self.ipstr.eof():
            return None
        while Tokenizer.is_white_char(self.ipstr.peek()):
            self.ipstr.next()

        ch = self.ipstr.peek()
        if (ch == '#'):
            self.__skip_comment()
            return self.next()
        if (ch == '"'):
            return self.__read_string()
        if (Tokenizer.is_digit(ch)):
            return self.__read_number()
        if (Tokenizer.is_identity_begin(ch)):
            return self.__read_identity()
        if (Tokenizer.is_punc(ch)):
            return {
                'type': 'punc',
                'value': self.ipstr.next()
            }
        if (Tokenizer.is_op(ch)):
            return self.__read_op()
        self.ipstr.error('Can not handle charactor: {}'.format(ch))
    def __read_op(self):
        return {
            'type': 'op',
            'value': self.__read_while(Tokenizer.is_op)
        }
    def __read_until(self, predicate):
        ret = ''
        while not self.ipstr.eof() and not predicate(self.ipstr.peek()):
            ret += self.ipstr.next()
        ret += self.ipstr.next()
        return ret

    def __read_while(self, predicate):
        ret = ''
        while not self.ipstr.eof() and predicate(self.ipstr.peek()):
            ret += self.ipstr.next()
        return ret
        
    def __read_identity(self):
        idf = self.__read_while(Tokenizer.is_identity)
        if idf in Tokenizer.keywords():
            return {
                'type': 'keyword',
                'value': idf
            }
        else:
            return {
                'type': 'identity',
                'value': idf
            }

    def __read_number(self):
        num = self.__read_while(Tokenizer.is_digit)
        return {
            'type': 'number',
            'value': num
        }
    
    def __skip_comment(self):
        self.__read_until(Tokenizer.is_newline)

    def __read_string(self):
        assert(self.ipstr.peek() == '"')
        self.ipstr.next()
        ret = self.__read_until(Tokenizer.is_double_quote)
        # return Token('string', ret[:-1])
        return {
            'type': 'string',
            'value': ret[:-1]
        }
        
    @staticmethod
    def is_newline(ch):
        Tokenizer.check_is_char(ch)
        return ch == '\n'
    @staticmethod
    def is_double_quote(ch):
        Tokenizer.check_is_char(ch)
        return ch == '"'
    @staticmethod
    def is_digit(ch):
        Tokenizer.check_is_char(ch)
        return ch in list('0123456789')

    @staticmethod
    def is_identity_begin(ch):
        Tokenizer.check_is_char(ch)
        return (ord(ch) >= ord('a')
            and ord(ch) <= ord('z')) or (ord(ch) >= ord('A')
            and ord(ch) <= ord('Z')) or ch == '_'
    @staticmethod
    def is_identity(ch):
        Tokenizer.check_is_char(ch)
        return Tokenizer.is_identity_begin(ch) or ch in list('0123456789')

    @staticmethod
    def is_punc(ch):
        Tokenizer.check_is_char(ch)
        return ch in list(r',()[]{};')
    
    @staticmethod
    def is_op(ch):
        Tokenizer.check_is_char(ch)
        return ch in list('+-*/=<>%&|!')

    @staticmethod
    def check_is_char(ch):
        assert(type(ch) == str)
        assert(len(ch) == 1)

    @staticmethod
    def is_white_char(ch):
        Tokenizer.check_is_char(ch)
        return ch in list(' \t\n')
    
    @staticmethod
    def keywords():
        return ['if', 'else', 'function', 'then', 'true', 'false']

if __name__ == '__main__':
    f = open('input', 'r')
    s = f.read()
    tokenizer = Tokenizer(InputStream(s))
    while not tokenizer.eof():
        print(tokenizer.next())
 