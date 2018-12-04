import sys
sys.path.insert(0, '/Users/yanbin/Documents/Projects/lambda/code/')
import unittest 
from inputStream import InputStream
from parser import Parser
from tokenizer import Tokenizer
class testParser(unittest.TestCase):
    def test_parser(self):
        fs = ['input', 'input2', 'input3']
        for filename in fs:
            f = open('datas/{}'.format(filename), 'r')
            s = f.read()
            f.close()
            p = Parser(Tokenizer(InputStream(s)))
            p.parse()

if __name__ == '__main__':
    unittest.main()