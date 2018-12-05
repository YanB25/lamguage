from parser import Parser
from tokenizer import Tokenizer
from inputStream import InputStream

class Environment():
    def __init__(self, parent=None):
        self.vars = dict()
        assert(parent is None or type(parent) == Environment)
        self.parent = parent
    def extend(self):
        return Environment(self)
    def lookup(self, name):
        that = self
        while that is not None and name not in that.vars:
            that = that.parent
        return that
    def getname(self, name):
        '''
        find the most specific one
        '''
        if name in self.vars:
            return self.vars[name]
        scope = self.lookup(name)
        if scope is None:
            raise Exception('undefined error, variable {}'.format(name))
        return scope.getname(name)
    def define(self, name, val):
        '''
        only in current scopy
        '''
        self.vars[name] = val
        return val
    def setval(self, name ,value):
        '''
        set in the scope that var really define in
        '''
        scope = self.lookup(name)
        if scope is None and self.parent is not None:
            raise Exception('Do not set val when not in global scope.')
        if scope is not None:
            scope.vars[name] = value
        else:
            self.vars[name] = value
        return value

class Interpreter():
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env
    def run(self):
        self.evaluate(self.ast, self.env)
    def evaluate(self, exp, env):
        typ = exp['type']
        if typ == 'program':
            val = None
            for program in exp['progs']:
                val = self.evaluate(program, env)
            return val
        if typ == 'assign':
            name = exp['left']['value']
            if exp['left']['type'] != 'identity':
                raise Exception('left side of = should be identity. get {}'.format(name))
            return env.define(name, self.evaluate(exp['right'], env))
        if typ in ['number', 'string', 'bool']:
            return exp['value']
        if typ == 'identity':
            return env.getname(exp['value'])
        if typ == 'function':
            return self.make_function(exp, env)
        if typ == 'call':
            arg_lst = []
            for arg in exp['args']:
                arg_lst.append(self.evaluate(arg, env))
            func = env.getname(exp['function']['value'])
            func(*arg_lst)
            return func
        raise Exception('unknown type {}'.format(typ))
    def make_function(self, exp, env):
        def func():
            names = exp['args']
            scope = env.extend()
            for name in names:
                scope.define(name, env.getname(name))
            return self.evaluate(exp['body'], scope)
        return func




if __name__ == '__main__':
    f = open('input3', 'r')
    s = f.read().strip()
    f.close()

    parser = Parser(Tokenizer(InputStream(s)))
    env = Environment()
    env.define('print', lambda x : print(x))
    interpreter = Interpreter(parser.parse(), env)
    interpreter.run()