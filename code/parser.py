import pprint
from inputStream import InputStream
from tokenizer import Tokenizer
FALSE = {
    'type': 'bool',
    'value': 'false'
}
class Parser():
    def __init__(self, tokenizer):
        assert(type(tokenizer) == Tokenizer)
        self.tokenizer = tokenizer
    
    def parse(self):
        self.programs = []
        while not self.tokenizer.eof():
            self.programs.append(self.parse_expression())
            if not self.tokenizer.eof():
                self.skip_punc(';')
        return {
            'type': 'program',
            'progs': self.programs
        }
    def parse_program(self):
        prog = self.delimited('{', '}', ';', self.parse_expression)
        if len(prog) == 0:
            return FALSE
        if len(prog) == 1:
            return prog[0]
        return {
            'type': 'program',
            'progs': prog
        }
    def delimited(self, beg, end, delimit, parser):
        toks = []
        first = True 
        self.skip_punc(beg)
        while not self.tokenizer.eof():
            if (self.is_punc(end)):
                break
            if (first):
                first = False
            else:
                self.skip_punc(delimit)
            # TODO: 这行是很重要的不能扔。对于prog类型，{ statement; }
            if (self.is_punc(end)):
                break
            toks.append(parser())
        self.skip_punc(end)
        return toks
    
    def parse_expression(self):
        '''
        return a expression.
        expression = maybe_call . maybe_binary . parse_atom
        '''
        def wrapper():
            return self.maybe_binary(self.parse_atom(), 0)
        return self.maybe_call(wrapper)

    def maybe_call(self, expr):
        expr = expr()
        return self.parse_call(expr) if self.is_punc('(') else expr
    
    def parse_call(self, func):
        return {
            'type': 'call',
            'function': func,
            'args': self.delimited('(', ')', ',', self.parse_expression)
        }

    def maybe_binary(self, left, prec):
        '''
        maybe binary?
        if the next token is op, it is binary, so it works.
        otherwise, return left. nothing happened
        '''
        if (self.is_op()):
            tok = self.tokenizer.peek() # it must be an op
            rhs_prec = Parser.precedence(tok.value)
            if rhs_prec > prec:
                ch = self.tokenizer.next()
                return self.maybe_binary({
                    'type': 'assign' if tok.value == '=' else 'binary',
                    'operator': tok.value,
                    'left': left,
                    'right': self.maybe_binary(self.parse_atom(), rhs_prec) # here, it is GREEDY
                }, prec) # and here, recursive goes back and become same "precedence level"
        else:
            # the next token is not op. so just return.
            return left
    
    def parse_atom(self):
        '''
        what is an atom?
        number is, and func(a, b, c) is also atom!
        '''
        def wrapper():
            if (self.is_punc('(')):
                # an atom starts with '(', must be expression
                ch = self.tokenizer.next()
                assert(Tokenizer.is_punc(ch.value))
                exp = self.parse_expression() # GREEDY
                self.skip_punc(')')
                return exp
            if (self.is_punc('{')):
                return self.parse_program()
            if (self.is_kw('if')):
                return self.parse_if()
            if (self.is_kw('true') or self.is_kw('false')):
                return self.parse_bool()
            if (self.is_kw('function')):
                return self.parse_function()
            # TODO:
            tok = self.tokenizer.next()
            if (tok is None):
                self.tokenizer.error('unexpected EOF')
            if (tok.type == 'identity' or tok.type == 'number' or tok.type == 'string'):
                return tok
            self.tokenizer.error('{} (type is {}) not expected. only expect var, num and str.'.format(tok.value, tok.type))
        return self.maybe_call(wrapper)

    def parse_if(self):
        self.skip_kw('if')
        cond = self.parse_expression()
        if not self.is_punc('{'):
            self.skip_kw('then')
        then = self.parse_expression()
        ret = {
            'type': 'if',
            'cond': cond,
            'then': then,
        }
        if self.is_kw('else'):
            self.skip_kw('else')
            else_statement = self.parse_expression()
            ret['else'] = else_statement
        return ret
    def parse_bool(self):
        return {
            'type': 'bool',
            'value': self.tokenizer.next()
        }
    
    def parse_function(self):
        self.skip_kw('function')
        return {
            'type': 'function',
            'args': self.delimited('(', ')', ',', self.parse_val),
            'body': self.parse_expression()
        }
    def parse_val(self):
        tok = self.tokenizer.next()
        if (tok.type != 'identity'):
            self.tokenizer.error('expect identity, got {}({})'.format(tok.value, tok.type))
        return tok.value

    @staticmethod
    def precedence(op):
        return {
            '=': 1,
            '||': 2,
            '&&': 3,
            '<': 7, '>': 7, '<=': 7, '>=': 7, '==': 7, '!=': 7,
            '+': 10, '-': 10,
            '*': 20, '/': 20, '%': 20
        }[op]

    def skip_punc(self, ch):
        tok = self.tokenizer.peek()
        if tok.type != 'punc' or tok.value != ch:
            self.tokenizer.error('{} not valid. expect {}(punc)'.format(tok.value, ch))
        eat_tok = self.tokenizer.next()
        assert(eat_tok.type == 'punc')
        assert(eat_tok.value == ch)

    def skip_kw(self, kw):
        tok = self.tokenizer.peek()
        if tok.type != 'keyword' or tok.value != kw:
            self.tokenizer.error('{} not valid. expect {}(keyword)'.format(tok.value, kw))

        eat_tok = self.tokenizer.next()
        assert(eat_tok.type == 'keyword')
        assert(eat_tok.value == kw)

    def is_punc(self, ch = None):
        tok = self.tokenizer.peek()
        return tok is not None and tok.type == 'punc' and (ch is None or tok.value == ch)
    def is_op(self, op = None):
        tok = self.tokenizer.peek()
        return tok is not None and tok.type == 'op' and (op is None or tok.value == op)
    
    def is_kw(self, kw = None):
        tok = self.tokenizer.peek()
        return tok is not None and tok.type == 'keyword' and (kw is None or tok.value == kw)
        
import sys
if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    f = open(sys.argv[1], 'r')
    s = f.read()
    parser = Parser(Tokenizer(InputStream(s)))
    pp.pprint(parser.parse())