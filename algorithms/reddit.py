import os
import sys
import time
import datetime
import pandas as pd
from math import log
from algorithm import Algorithm

epoch = datetime.datetime(1970, 1, 1)

class Hot:
	"""
	Ranks stocks based on if the daily close price is above or below
	the open stock price.
	"""
	def __init__(self, ups, downs, date):
		self.ups = ups
		self.downs = downs
		self.date = date
		self.score = self.ups - self.downs
		self.start_time = 1

	def set_start_time(self, timestamp):
		self.start_time = timestamp
		#timestamp

	def epoch_seconds(self):
		""" Return the number of seconds from the epoch to date."""
		td = self.date - epoch
		return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

	def execute(self):
		""" The hot formula.  Should match the equivalent function in postgres."""
		order = log(max(abs(self.score), 1), 10)
		sign = 1 if self.score > 0 else -1 if self.score < 0 else 0
		seconds = self.epoch_seconds() - self.start_time
		return round(sign * order + seconds / 45000, 7)

class Main(Algorithm):
	name = "Reddit HOT Ranking"

	def __init__(self, **kwargs):
		''' Set local variables '''
		self.good_time = time.mktime(time.strptime(kwargs['start_date'], "%Y-%m-%d"))
		year = kwargs['start_date'].split('-')[0]
		month = kwargs['start_date'].split('-')[1]
		day = kwargs['start_date'].split('-')[2]
		self.last_time = datetime.datetime(int(year), int(month), int(day))
		super(Main, self).__init__()

	def main(self):
		self.results = {}

		for symbol in self.symbols:
			ups = 0
			downs = 0
			last_time = None

			symbol_data = self.data[symbol]
			try:
				for i in range(len(symbol_data['Date'])):
					str_open = "Open"
					str_close = "Close"

					s_time = str(symbol_data['Date'][i])
					s_time = time.mktime(time.strptime(s_time, "%Y-%m-%d %H:%M:%S"))
					s_open = symbol_data[str_open][i]
					s_close = symbol_data[str_close][i]

					if s_time >= self.good_time:
						if s_close >= s_open:
							ups = ups + 1
						elif s_close < s_open:
							downs = downs + 1

				hot = Hot(ups, downs, self.last_time)
				#hot.set_start_time(1101798784)
				rank = hot.execute(), symbol
				self.results[symbol] = rank
			except:
				self.results[symbol] = -1

		return self.results

