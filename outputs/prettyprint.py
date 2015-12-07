import pprint
from output import Output

class Main(Output):
	def __init__(self, **kwargs):
		super(Main, self).__init__()
		self.indent = kwargs['indent']

	def main(self):
		pprint.pprint(self.data, indent=self.indent)
