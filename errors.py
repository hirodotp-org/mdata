class BaseException(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class ParseError(BaseException):
	pass

class SyntaxError(BaseException):
	pass

class IntegerOverflow(BaseException):
	pass

class InvalidFunction(BaseException):
	pass
