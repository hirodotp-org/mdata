import sys
import pandas as pd
from Quandl import Quandl
from input import Input

class Main(Input):
	name = "Quandl Datasets"

	def generate_quandl_code(self, symbol):
		try:
			code = self.base_config['code_format']
		except:
			code = '{DATABASE}/{EXCHANGE}_{TICKER}'

		code = code.replace('{DATABASE}', self.base_config['database'])
		code = code.replace('{EXCHANGE}', self.base_config['exchange'])
		code = code.replace('{TICKER}', symbol)
		return code
		
	def main(self):
		results = {}
		for symbol in self.symbols:
			code = self.generate_quandl_code(symbol)
			results[symbol] = Quandl.get(code, authtoken=self.base_config['api_key'], returns='pandas')
			results[symbol] = results[symbol].reset_index()
		return results
