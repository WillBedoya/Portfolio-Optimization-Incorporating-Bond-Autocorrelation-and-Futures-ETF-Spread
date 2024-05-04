# Portfolio Optimization Incorporating Bond Auto-Correlation and Futures ETF Spread
Python code that optimizes a portfolio with 4 different sources of returns: ES futures, ZN futures, a momentum strategy on short-term treasury futures (ZT), and a spread that trades a TLT ETF/ZB futures pair.

## ES and ZN Futures
A widely used portfolio that seeks to optimize a trade-off between returns and risk is the 60/40 stock/bond portfolio. Initially, I used ES and ZB futures, however historically (over past 50+ years) 10-year treasuries have had a slightly higher Sharpe ratio compared to long-term treasuries. For this reason, I selected ES and ZN futures as 2 of the 4 assets in the portfolio.

## Momentum Strategy on Short-Term Treasury Futures
It has been well-documented that assets for most of the past 100-200 years have exhibited some sort of trend following/momentum. I did my own testing on data I collected from different futures contracts, including 4 different treasury durations, corn, crude oil, gold, and EURUSD. The strategy applied was to buy the contract if the 12-month return is greater than or equal to 0%, otherwise short the contract. Interestingly, for the 4 treasury futures (ZT, ZF, ZN, and ZB), for each higher duration the Sharpe ratio of momentum returns was lower. ZT had the highest Sharpe ratio at 0.98; ZB had the lowest at 0.26. ZT also had a significantly higher Sharpe ratio than any of the other futures contracts this momentum strategy was tested on. The reason for this was not immediately clear. However, my suspicion is that this occurs due to the fact that the federal funds rate set by the Federal Reserve apppears to trend. When the Fed cuts (or hikes) interest rates, it is usually entering a cycle of cuts (hikes) and subsequent cuts (hikes) typically follow. So, the closer in duration a treasury is to the federal funds rate, the more it will be prone to trend/momentum similar to how the funds rate does. This makes sense in the context of my momentum strategy performing worse for each contract that was a step up in duration.

## ZB Futures/TLT ETF Spread
Inspired by this [paper](https://www.bis.org/publ/qtrpdf/r_qt2103d.pdf) about bond ETF arbitrage, I created a pairs trade between ZB futures and the TLT ETF. Both track long-term futures contracts. The monthly returns for each instrument were calculated, and the underperforming asset of the last month was purchased while the overperforming asset was shorted.

## Portfolio Optimization
A Python script was written that includes several functions and splits the data into 80-20 train-test for portfolio optmization. The first function 'create_random_weights(n_assets)' creates random weights for the 4 assets and ensures the weights sum up to 1. This function allows for assets to be shorted, as I previously planned on also incorporating a short on volatility and may do so as an improvement in the future. The next function 'evaluate_random_portfolio(returns)' returns the mean and standard deviation of the returns for a random portfolio. Lastly, the function 'create_random_portfolios(returns, n_portfolios, risk_free_rate, freq = "monthly")' creates a random number of portfolios (in this case, 10000 portfolios were created) and returns their weights, returns, volatilities, and Sharpe ratios. There is also an option to adjust this function for either monthly returns or daily returns, depending on the type of data being used. In my case, monthly data was used. 
After importing all of the asset/strategy prices and calculating their percent returns, they were all combined into a single Pandas dataframe and sorted such that all of their dates were aligned properly. Next, the returns were broken into in-sample and out-of-sample. The 100 portfolios with the highest Sharpe ratios were found, and the median weight of each asset in these top 100 portfolios was used in the out-of-sample testing to construct the portfolio. After applying 5x leverage and substracting away borrowing costs, the annualized return out of sample was 19.3%, and the Sharpe ratio was 0.80.

<p align="center">
  <strong>Asset/Strategy Prices Over Time</strong><br>
  <img src="https://github.com/WillBedoya/Portfolio-Optimization-Incorporating-Momentum-and-Futures-ETF-Spread/assets/80056170/042a30a8-178e-4ad4-8853-5af710e70934">
</p>

<p align="center">
  <strong>Efficient Frontier (Shorting Allowed)</strong><br>
  <img src="https://github.com/WillBedoya/Portfolio-Optimization-Incorporating-Momentum-and-Futures-ETF-Spread/assets/80056170/d131e2ba-9164-4fe4-a6ca-b2bb3d84d14b">
</p>

<p align="center">
  <strong>Mean-Variance Optimized Portfolio (In-Sample and Out-of-Sample)</strong><br>
  <img src="https://github.com/WillBedoya/Portfolio-Optimization-Incorporating-Momentum-and-Futures-ETF-Spread/assets/80056170/6995ede0-b69e-4e29-a5e3-1ba7666a2faa">
</p>


<p align="center">
  <strong>Mean-Variance Optimized Portfolio (Out-of-Sample Performance)</strong><br>
  <img src="https://github.com/WillBedoya/Portfolio-Optimization-Incorporating-Momentum-and-Futures-ETF-Spread/assets/80056170/d897d888-ff98-4f63-8d84-0f8dac1674e6">
</p>


## Future Improvements
Several futures improvements could be made. Firstly, as mentioned previously I had an interest in shorting volatility through VIX futures. Back-adjusted VIX futures have historically offered a return similar to that of the S&P 500 but at a higher Sharpe ratio (~0.8). However, there are clearly issues with how to manage risk in such a position when volatility spikes. Something I am currently working on is simulating VIX index options that could be bought as a hedge as protection against a VIX spike while shorting it. A second improvement could be made in more rigorously testing the statistical significance of using momentum on ZT futures. While the reasoning I laid out earlier may be plausible, things change over time and I'm not confident that such performance will continue. This portion of the portfolio may also be prone to overfitting, as the 12-month lookback period on returns is arbitrary and I also selected the asset on which the strategy produced the highest Sharpe ratio compared to all the other futures contracts that momentum was tested on.

### Edit
Since my last writing, I have tested the monthly autocorrelation of logarithmic returns of ZT futures since its inception and found that there is indeed statistically significant autocorrelation at the 95% confidence level (sometimes even 99%). This test was done assuming returns are normally distributed. Interestingly, there was a significant autocorrelation 8 months, 9 months, 10 months, 11 months, and 12 months out into the future. There was also a significant autocorrelation 1 month into the future, but nothing significant between 2 and 7 months. These results fall in line with my finding that the previous 12-month return is predictive of the next month return.

<p align="center">
  <strong>ZT Futures Monthly Autocorrelation</strong><br>
  <img src="https://github.com/WillBedoya/Portfolio-Optimization-Incorporating-Momentum-and-Futures-ETF-Spread/assets/80056170/8304bed2-f403-4efe-adcf-b7e0040e27ed">
</p>

### Disclaimer
All futures contracts were properly back-adjusted, the TLT ETF prices include dividends/splits, and results are net of bid/ask spreads and borrowing costs required for leverage. Exchange fees were not taken into account. For futures positions, cash is assumed to gain the risk-free rate (3-month treasury bill rate).
