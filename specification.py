class Transaction:
	def __init__(self, id = None):
		self.id = id
		self.symbols = []
		self.algorithms = []
		self.translations = []
		self.outputs = []
		self.input = None

	def set_symbols(self, symbols):
		self.symbols = symbols

	def set_input(self, input):
		self.input = input

	def push_algorithm(self, algorithm):
		self.algorithms.append(algorithm)

	def push_translation(self, translation):
		self.translations.append(translation)

	def push_output(self, output):
		self.outputs.append(output)

	def get_symbols(self):
		return self.symbols

	def get_algorithms(self):
		return self.algorithms

	def get_translations(self):
		return self.translations

	def get_outputs(self):
		return self.outputs

	def get_input(self):
		return self.input

class Specification:
	def __init__(self, id = None):
		self.id = id
		self.config = {}
		self.transactions = []

	def set_config_var(self, key, val):
		self.config[key] = val

	def push_transaction(self, transaction):
		self.transactions.append(transaction)

	def main(self):
		for transaction in self.transactions:
			symbols = transaction.get_symbols()
			input = transaction.get_input()

			input.setup(symbols, **self.config)
			symbol_data = input.main()

			if symbol_data:
				data = []
				translations = transaction.get_translations()

				# register algorithms to translations if defined
				# otherwise execute algorithms directly
				if translations:
					for translation in translations:
						for algorithm in transaction.get_algorithms():
							translation.register(algorithm)

						translation.setup(symbols, symbol_data, **self.config)
						data = translation.main()
				else:
					for algorithm in transaction.get_algorithms():
						algorithm.setup(symbols, symbol_data, **self.config)
						data.append(algorithm.main())

				# process outputs
				if data:
					for output in transaction.get_outputs():
						output.setup(data)
						output.main()	
