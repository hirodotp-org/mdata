import re
import importlib
import ply.lex as lex
import ply.yacc as yacc
from specification import *
from errors import *

class Lexer(object):
	tokens = [
		'KEYWORD', 'STRING', 'NUMBER', 'COMMENT',
		'EQUALS',
		'LBRACKET', 'RBRACKET', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA',
	]

	reserved = {
		'specification': 'SPECIFICATION',
		'configure': 'CONFIGURE',
		'transaction': 'TRANSACTION',
		'algorithms': 'ALGORITHMS',
		'translations': 'TRANSLATIONS',
		'outputs': 'OUTPUTS',
		'input': 'INPUT'
	}

	tokens += list(reserved.values())

	t_EQUALS	= r'='
	t_COMMA		= r','
	t_LBRACKET	= r'\['
	t_RBRACKET	= r'\]'
	t_LPAREN	= r'\('
	t_RPAREN	= r'\)'
	t_LBRACE	= r'\{'
	t_RBRACE	= r'\}'
	
	t_SPECIFICATION	= r'[sS][pP][eE][cC][iI][fF][iI][cC][aA][tT][iI][oO][nN]'
	t_CONFIGURE	= r'[cC][oO][nN][fF][iI][gG][uU][rR][eE]'	
	t_TRANSACTION	= r'[tT][rR][aA][nN][sS][aA][cC][tT][iI][oO][nN]'
	t_ALGORITHMS	= r'[aA][lL][gG][oO][rR][iI][tT][hH][mM][sS]'
	t_TRANSLATIONS	= r'[tT][rR][aA][nN][sS][lL][aA][tT][iI][oO][nN][sS]'
	t_OUTPUTS	= r'[oO][uU][tT][pP][uU][tT][sS]'
	t_INPUT		= r'[iI][nN][pP][uU][tT]'

	t_ignore = ' \t'

	def t_COMMENT(self, t):
		r'[#][^\n]*'
		pass

	def t_KEYWORD(self, t):
		r'[a-zA-Z_]{1,}'
		t.type = self.reserved.get(t.value, 'KEYWORD')
		return t

	def t_STRING(self, t):
		r'"([^\\"]+|\\"|\\\\|\\n|\\t)*"'
		t.value = t.value.decode('string-escape')[1:-1]
		return t

	def t_NUMBER(self, t):
		r'\d+'
		try:
			t.value = int(t.value)
		except ValueError:
			raise IntegerOverflow("Integer value too large %d" % t.value)
			sys.exit(3)
		return t

	def t_newline(self, t):
		r'\n'
		t.lexer.lineno += 1

	def t_error(self, t):
		raise ParseError("Illegal character '%s'" % t.value[0])
		sys.exit(4)

	def __init__(self, **kwargs):
		self.lexer = lex.lex(module=self, **kwargs)
	

class Parser(object):
	def __init__(self):
		self.lexer = Lexer()
		self.tokens = self.lexer.tokens
		self.parser = yacc.yacc(module=self)
		self.spec = None
		self.transaction = None
		self.modes = []
		self.algorithm = None
		self.algorithm_kwargs = {}
		self.translation = None
		self.translation_kwargs = {}
		self.output = None
		self.output_kwargs = {}
		self.input = None
		self.input_kwargs = {}
		self.can_execute = False
		self.last_function_lineno = 0

	def p_statements(self, p):
		'''
		statements : statement
			   | statements statement
		'''
		if len(p) > 2:
			p[1].append(p[2])
			p[0] = p[1]
		else:
			p[0] = [p[1]]

		
	def p_statement(self, p):
		'''
		statement : statement_assignment
			  | statement_assignment RBRACE
			  | statement_function
			  | RBRACE
		'''
		p[0] = p[1]

		if len(p) == 3:
			if re.match(self.lexer.t_ALGORITHMS, self.modes[-1]):
				to_import = "algorithms.%s" % self.algorithm
				try:
					mod = importlib.import_module(to_import)
				except Exception, e:
					raise InvalidFunction("Invalid function '%s' on line %s" % (self.algorithm, self.last_function_lineno))
					sys.exit(4)
				algorithm = mod.Main(**self.algorithm_kwargs)
				self.transaction.push_algorithm(algorithm)
			elif re.match(self.lexer.t_TRANSLATIONS, self.modes[-1]):
				to_import = "translations.%s" % self.translation
				try:
					mod = importlib.import_module(to_import)
				except Exception, e:
					raise InvalidFunction("Invalid function '%s' on line %s" % (self.translation, self.last_function_lineno))
					sys.exit(4)
				translation = mod.Main(**self.translation_kwargs)
				self.transaction.push_translation(translation)
			elif re.match(self.lexer.t_OUTPUTS, self.modes[-1]):
				to_import = "outputs.%s" % self.output
				try:
					mod = importlib.import_module(to_import)
				except Exception, e:
					raise InvalidFunction("Invalid function '%s' on line %s" % (self.output, self.last_function_lineno))
					sys.exit(4)

				output = mod.Main(**self.output_kwargs)
				self.transaction.push_output(output)
			elif re.match(self.lexer.t_INPUT, self.modes[-1]):
				to_import = "inputs.%s" % self.input
				try:
					mod = importlib.import_module(to_import)
				except Exception, e:
					raise InvalidFunction("Invalid function '%s' on line %s" % (self.input, self.last_function_lineno))
					sys.exit(4)
				
				input = mod.Main(**self.input_kwargs)
				self.transaction.set_input(input)

			# done with current function, pop it off the stack
			self.modes.pop()
			self.can_execute = True
		elif type(p[1]) == str and re.match(self.lexer.t_RBRACE, p[1]):
			if re.match(self.lexer.t_TRANSACTION, self.modes[-1]):
				self.spec.push_transaction(self.transaction)

			# done with current function, pop it off the stack
			self.modes.pop()
			self.can_execute = True

		if len(self.modes) == 1 and self.can_execute:
			self.spec.main()

	def p_statement_assignment(self, p):
		'''
		statement_assignment : KEYWORD EQUALS STRING
				     | KEYWORD EQUALS NUMBER
				     | KEYWORD EQUALS array
				     | KEYWORD EQUALS STRING RBRACE
				     | KEYWORD EQUALS NUMBER RBRACE
				     | KEYWORD EQUALS array RBRACE
		'''
		if type(p[3]) == list:
			p[3] = p[3][::-1]
		p[0] = p[3]

		if re.match(self.lexer.t_CONFIGURE, self.modes[-1]):
			self.spec.set_config_var(p[1], p[3])
		elif re.match(self.lexer.t_TRANSACTION, self.modes[-1]):
			if p[1] == 'symbols':
				self.transaction.set_symbols(p[3])
		elif re.match(self.lexer.t_ALGORITHMS, self.modes[-1]):
			self.algorithm_kwargs[p[1]] = p[3]
		elif re.match(self.lexer.t_TRANSLATIONS, self.modes[-1]):
			self.translation_kwargs[p[1]] = p[3]
		elif re.match(self.lexer.t_OUTPUTS, self.modes[-1]):
			self.output_kwargs[p[1]] = p[3]
		elif re.match(self.lexer.t_INPUT, self.modes[-1]):
			self.input_kwargs[p[1]] = p[3]

	def p_array(self, p):
		'''
		array : LBRACKET array_components RBRACKET
		'''
		p[0] = p[2]

	def p_array_components(self, p):
		'''
		array_components : NUMBER
				 | STRING
				 | NUMBER COMMA
				 | STRING COMMA
				 | array_components NUMBER COMMA
				 | array_components STRING COMMA
				 | NUMBER COMMA array_components
				 | STRING COMMA array_components
		'''
		if len(p) > 3:
			p[3].append(p[1])
			p[0] = p[3]
		else:
			p[0] = [p[1]]

	def p_statement_function(self, p):
		'''
		statement_function : KEYWORD LBRACE
				   | SPECIFICATION LBRACE
				   | CONFIGURE LBRACE
				   | TRANSACTION LBRACE
				   | ALGORITHMS LBRACE
				   | TRANSLATIONS LBRACE
				   | OUTPUTS LBRACE
				   | INPUT LBRACE
				   | LBRACE
		'''
		if len(p) > 2:
			if re.match(self.lexer.t_SPECIFICATION, p[1]):
				self.modes.append(p[1])
				self.spec = Specification()
				self.last_function_lineno = p.lineno(1)
				p[0] = self.spec
			elif re.match(self.lexer.t_TRANSACTION, p[1]):
				self.modes.append(p[1])
				self.transaction = Transaction()
				self.last_function_lineno = p.lineno(1)
				p[0] = self.transaction
			elif re.match(self.lexer.t_ALGORITHMS, p[1]):
				self.last_function_lineno = p.lineno(1)
				self.modes.append(p[1])
			elif re.match(self.lexer.t_TRANSLATIONS, p[1]):
				self.last_function_lineno = p.lineno(1)
				self.modes.append(p[1])
			elif re.match(self.lexer.t_OUTPUTS, p[1]):
				self.last_function_lineno = p.lineno(1)
				self.modes.append(p[1])
			elif re.match(self.lexer.t_INPUT, p[1]):
				self.last_function_lineno = p.lineno(1)
				self.modes.append(p[1])
			elif re.match(self.lexer.t_CONFIGURE, p[1]):
				self.last_function_lineno = p.lineno(1)
				self.modes.append(p[1])
			else:
				if re.match(self.lexer.t_ALGORITHMS, self.modes[-1]):
					self.last_function_lineno = p.lineno(1)
					self.algorithm = p[1]	
				elif re.match(self.lexer.t_TRANSLATIONS, self.modes[-1]):
					self.last_function_lineno = p.lineno(1)
					self.translation = p[1]
				elif re.match(self.lexer.t_OUTPUTS, self.modes[-1]):
					self.last_function_lineno = p.lineno(1)
					self.output = p[1]
				elif re.match(self.lexer.t_INPUT, self.modes[-1]):
					self.last_function_lineno = p.lineno(1)
					self.input = p[1]
				p[0] = p[1]
		elif len(p) <= 2:
			pass	

	def p_error(self, t):
		raise SyntaxError("Syntax error at '%s' on line %d" % (t.value, t.lineno))
		sys.exit(5)

	def run_parse(self, s):
		self.parser.parse(s, debug=0)
		return 0
	
