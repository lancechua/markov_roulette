import pandas as pd
import numpy as np
import collections


class markov_roulette(object):
	'''	
	Please don't take this seriously in any capacity...
	For entertainment purposes only

	[TBD?]
			* code optimizations
					- current benchmark = 96.4s for 100,000 samples
					- translate once and store in memory?
					- use multiprocessing during translation?
			* suggested bets, i.e. given transition matrices and most recent result, best strategy = bet on both dozen 2 and dozen 3...
	'''

	def __init__(self, wheel='FR'):
		'''wheel = wheel type: French "FR" (for now...)'''

		self.wheel = wheel.upper()
		if self.wheel not in ['FR']:
			raise Exception('Invalid wheel. Wheels: "FR" (other wheels TBD)')

		self.labels_df = pd.DataFrame({'odd': ['even', 'odd', 'zero'],
									   'red': ['black', 'red', 'zero'],
									   'high': ['low', 'high', 'zero']})

		# only mutually exclusive completely exhaustive bets included
		if self.wheel == 'FR':
			self.vals = np.arange(37)

			df = pd.DataFrame(index=self.vals,
							  columns=['odd', 'red', 'high', 'dozen', 'column', 'call'])

			df['odd'] = [-1] + [a % 2 for a in df.index[1:]]
			odd_label = list(self.labels_df['odd'])
			df['odd'] = [odd_label[df.loc[a, 'odd']] for a in df.index]

			reds = [1, 3, 5, 7, 9, 12, 14, 16, 18,
					19, 21, 23, 25, 27, 30, 32, 34, 36]
			df['red'] = [-1] + [int(a in reds) for a in df.index[1:]]
			red_label = list(self.labels_df['red'])
			df['red'] = [red_label[df.loc[a, 'red']] for a in df.index]

			df['high'] = [-1] + [int(a > 18) for a in df.index[1:]]
			high_label = list(self.labels_df['high'])
			df['high'] = [high_label[df.loc[a, 'high']] for a in df.index]

			df['dozen'] = ['zero'] + ['doz_' +
									  str(int((a - 1) / 12) + 1) for a in df.index[1:]]
			df['column'] = ['zero'] + ['col_' +
									   str((a - 1) % 3 + 1) for a in df.index[1:]]

			voisins = [22, 18, 29, 7, 28, 12, 35,
					   3, 26, 0, 32, 15, 19, 4, 21, 2, 25]
			zero = [12, 35, 3, 26, 0, 32, 15]
			tiers = [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
			orphelins = [17, 34, 6, 1, 20, 14, 31, 9]

			call = {}
			call = {a: 'voisins' for a in voisins}
			call.update({a: 'zero' for a in zero})
			call.update({a: 'tiers' for a in tiers})
			call.update({a: 'orphelins' for a in orphelins})

			df['call'] = [call[a] for a in df.index]

			self.df = df

	def genP(self, hist, src_bet, dest_bet):
		'''
		Generate transition matrix based on historical data

		hist, list = historical data
		src_bet = source "bet type" i.e. odd,red, high,...raw
		dest_bet = dest "bet type"

		allowed bet types: 'odd', 'red', 'high', 'dozen', 'column', 'call'
		'''
		# validate inputs
		if not isinstance(hist, list):
			raise Exception('Input must be a list.')

		if self.wheel == 'FR':
			if not all([a in self.vals for a in hist]):
				raise Exception(
					'Values must be an int from 0-36 for wheel="FR".')

		src_bet = src_bet.lower()
		dest_bet = dest_bet.lower()

		if not (src_bet in self.df.columns | ['raw']) and (dest_bet in self.df.columns | ['raw']):
			raise Exception('allowed values for bet types: %s.' %
							(sorted(list(self.df.columns | ['raw']))))

		# functions
		def translate(source, bet):
			if bet == 'raw':
				return source

			if isinstance(source, collections.Iterable):
				return [self.df.loc[a, bet] for a in source]
			else:
				return self.df.loc[a, bet]

		def gen_matrix(pairs):
			'''pairs must be a list of tuples (orig_bet, dest_bet)'''
			out_df = pd.DataFrame(pairs, columns=['orig', 'dest'])
			out_df.loc[:, 'pct'] = 1
			out_df = out_df.groupby(['orig', 'dest'], as_index=False)[
				'pct'].sum()
			out_df['pct'] = out_df['pct'] / len(pairs)

			return out_df.pivot(index='orig', columns='dest')['pct'].fillna(0)

		def label(source, bet):
			if isinstance(source, collections.Iterable):
				return [self.labels_df.loc[a, bet] for a in source]
			else:
				return self.labels_df.loc[a, bet]

		self.src_trans = translate(hist[:-1], src_bet)
		self.dest_trans = translate(hist[1:], dest_bet)

		hist_results = list(zip(self.src_trans, self.dest_trans))

		return gen_matrix(hist_results)

if __name__ == '__main__':
	sample_data = [np.random.randint(37) for a in range(100)]
	x = markov_roulette('FR')
	print(sample_data, '\n')
	print(x.genP(sample_data, 'red', 'odd'), '\n')
	print(x.genP(sample_data, 'call', 'dozen'), '\n')
	print(x.genP(sample_data, 'column', 'high'), '\n')
	# print(x.genP(sample_data, 'raw', 'call'), '\n')
	print(x.genP(sample_data, 'dozen', 'dozen'), '\n')
