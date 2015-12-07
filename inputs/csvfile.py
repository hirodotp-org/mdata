import os
import pandas as pd
from input import Input

class Main(Input):
	name = "CSV File Input"

	def build_file_list(self):
		files = {}
		for s in self.symbols:
			normalized_file = "%s.%s" % (s, self.extension)
			if os.path.isfile(os.path.join(self.symbol_dir, normalized_file)):
				files[s] = os.path.join(self.symbol_dir, normalized_file)

		return files

	def main(self):
		self.extension = self.base_config['file_extension']
		self.symbol_dir = self.base_config['symbol_dir']

		files = self.build_file_list()

		for symbol in files.keys():
			df = pd.read_csv(files[symbol])
			df = df.reset_index()
			print df.tail
			self.data[symbol] = df

		return self.data


