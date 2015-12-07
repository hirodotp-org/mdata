from lexer import *
import ply.yacc as yacc
import ply.lex as lex


class Parser:
	def __init__(self):
		self.lexer = lex.lex()
		self.parser = yacc.yacc()

	def parse(self, s):
		self.parser.parse(s)

if __name__ == "__main__":
	p = Parser();
	fd = open("stock.spec", "r")
	s = fd.read()
	fd.close()

	p.parse(s)
	
	
