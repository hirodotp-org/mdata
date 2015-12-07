class Input(object):
	name = "Base Input -- Override this with the name of your module"

	def __init__(self, **kwargs):
		self.base_config = kwargs
		self.data = {}

	def setup(self, symbols, **kwargs):
		''' setup based on global configuration '''
		self.symbols = symbols
		self.config = kwargs

	def main(self):
		'''
		Override this function with your code
		'''
		pass
