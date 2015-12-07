class Algorithm(object):
	name = "Base Translation -- Override this with the name of your module"

	def __init__(self, **kwargs):
		self.base_config = kwargs
		self.results = {}

	def setup(self, symbols, data, **kwargs):
		''' setup based on global configuration '''
		self.symbols = symbols
		self.data = data
		self.config = kwargs
