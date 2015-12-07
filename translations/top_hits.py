import pprint
import operator
from translation import Translation

class Main(Translation):
	def top_hits(self, results):
		sorted_results = sorted(results.items(), key=operator.itemgetter(1))	
		return sorted_results[-self.base_config['max_results']:]

	def main(self):
		results = []
		for algorithm in self.algorithms:
			algorithm.setup(self.symbols, self.data, **self.config)
			res = algorithm.main()
			if res:
				top = self.top_hits(res)
				results.append(top)

		return results
