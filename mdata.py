import os
import sys
import argparse
from lexer import Parser

class Stock:
	def parse_args(self):
		parser = argparse.ArgumentParser()
		parser.add_argument("specification", help="Specification file to process", type=str)
		args = parser.parse_args()
		return args

	def main(self):
		args = self.parse_args()
		if not os.path.isfile(args.specification):
			print "specification does not exist"
			return 1
		if not os.access(args.specification, os.R_OK):
			print "cannot access specification"
			return 1

		p = Parser();
		fd = open(args.specification, "r")
		data = fd.read()
		fd.close()

		return p.run_parse(data)

if __name__ == "__main__":
	app = Stock()
	sys.exit(app.main())
