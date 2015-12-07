tokens = (
	'KEYWORD', 'STRING', 'NUMBER',
	'EQUALS',
	'LBRACKET', 'RBRACKET', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA',
)

t_EQUALS	= r'='
t_COMMA		= r','
t_LBRACKET	= r'\['
t_RBRACKET	= r'\]'
t_LPAREN	= r'\('
t_RPAREN	= r'\)'
t_LBRACE	= r'\{'
t_RBRACE	= r'\}'
t_KEYWORD	= r'[a-zA-Z_][a-zA-Z0-9_]*'
t_STRING	= r'".*?"'

def t_NUMBER(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		print "Integer value too large %d" % t.value
		t.value = 0
	return t

t_ignore = " \t"

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)
