import sys
import math
import os
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
    def __repr__(self):
        return str(self.vars)

class Interpreter():
    def __init__(self, ast, env):
        self.ast = ast
        self.env = env
    def load_module(self, mname, basepath='lib/'):
        '''
        load in a module with mname.
        the path of the module would be path.join(basepath, mname + '.lamguage')
        '''
        target_path = os.path.join(basepath, '{}.lamguage'.format(mname))
        f = open(target_path, 'r')
        s = f.read().strip()
        parser = Parser(Tokenizer(InputStream(s)))
        ast = parser.parse()
        self.evaluate(ast, self.env)

    def __extend(self, ast):
        '''
        extend and parse another ast.
        '''
        self.ast = ast
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
        if typ == 'binary':
            return self.apply_op(exp['operator'], self.evaluate(exp['left'], env), self.evaluate(exp['right'], env))
        if typ == 'if':
            cond = self.evaluate(exp['cond'], env)
            if (cond == 'True'):
                return self.evaluate(exp['then'], env)
            if (exp.get('else')):
                return self.evaluate(exp['else'], env)
            else:
                return False
        if typ == 'call':
            arg_lst = []
            for arg in exp['args']:
                arg_lst.append(self.evaluate(arg, env))
            func = self.evaluate(exp['function'], env)
            return func(*arg_lst) #TODO: very important!!
        raise Exception('unknown type {}'.format(typ))
    def make_function(self, exp, env):
        def func(*myargs):
            names = exp['args']
            if len(myargs) != len(names):
                raise Exception('function should be call with {} param. get {}.'.format(len(names), len(myargs)))
            scope = env.extend()
            for myarg, name in zip(myargs, names):
                scope.define(name, myarg)
            return self.evaluate(exp['body'], scope)
        return func

    def apply_op(self, op, lhs, rhs):
        def toBool(s):
            if s not in ['True', 'False']:
                raise Exception('compiler internal error. s is {} not in True, False'.format(s))
            return True if s == 'True' else False
        if (op == '+'):
            return str(int(lhs) + int(rhs))
        if (op == '-'):
            return str(int(lhs) - int(rhs))
        if (op == '*'):
            return str(int(lhs) * int(rhs))
        if (op == '/'):
            return str(math.floor(int(lhs) / int (rhs)))
        if (op == '%'):
            return str(int(lhs) % int(rhs))
        if (op == '&&'):
            return str(toBool(lhs) and toBool(rhs))
        if (op == '||'):
            return str(toBool(lhs) or toBool(rhs))
        if (op == '<'):
            return str(int(lhs) < int(rhs))
        if (op == '>'):
            return str(int(lhs) > int(rhs))
        if (op == '<='):
            return str(int(lhs) <= int(rhs))
        if (op == '>='):
            return str(int(lhs) >= int(rhs))
        if (op == '=='):
            return (str(lhs == rhs)) #TODO: do not try to cast to int !
        if (op == '!='):
            return (str(lhs != rhs))
        raise Exception('can not recognise op {}'.format(op))
        



if __name__ == '__main__':
    f = open(sys.argv[1], 'r')
    s = f.read().strip()
    parser = Parser(Tokenizer(InputStream(s)))
    env = Environment()
    env.define('__builtin_print', lambda x : print(x, end=''))
    env.define('__builtin_enter', lambda : print())
    interpreter = Interpreter(parser.parse(), env)

    interpreter.load_module('basic')
    interpreter.load_module('arithmetic')
    interpreter.load_module('list')
    interpreter.load_module('maybe')
    interpreter.load_module('print')

    interpreter.run()