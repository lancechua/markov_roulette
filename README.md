# Markov Chains and Roulette

Under the **terrible** assumption that roulette spins are a Markov process, generates transition matrices based on the following betting strategies as states:
	odd/even, red/black, high/low, dozen, column, call, . 

For entertainment purposes only. Please don't take this seriously, in any capacity whatsoever...

[TBD?]
  * code optimizations

     - current benchmark = 96.4s for 100,000 samples
     - translate once and store in memory?
     - use multiprocessing during translation?

  * suggested bets

     - given transition matrices and most recent result, best strategy = bet on both dozen 2 and dozen 3...