import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import cvxopt as opt
from cvxopt import solvers
from scipy.stats import norm

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Number of portfolios to simulate
n_portfolios = 10000

# Returns randomly choosen portfolio weights that sum to one
def create_random_weights(n_assets):
    w = np.random.randn(n_assets)
    w /= w.sum()
    # Ensure that the sum of weights is non-zero
    if np.isclose(w.sum(), 0):
        raise ValueError("Sum of weights is zero. Adjust the weights.")
    return w

# Function that returns the mean and standard deviation of returns for a random portfolio
def evaluate_random_portfolio(returns):
    returns = pd.DataFrame(returns)   
    
    # Calculate from covariance, asset returns and weights
    cov = np.matrix(returns.cov())
    R = np.matrix(returns.mean())
    w = np.matrix(create_random_weights(returns.shape[1]))
    
    # Calculate expected portfolio return and risk
    mu = w * R.T
    sigma = np.sqrt(w * cov * w.T)
    
    return mu, sigma

# Function to calculate and store Sharpe ratios and weights
# Set to either monthly or daily
def create_random_portfolios(returns, n_portfolios, risk_free_rate, freq = "monthly"):
    n_assets = returns.shape[1]
    all_weights = np.zeros((n_portfolios, n_assets))
    all_returns = np.zeros(n_portfolios)
    all_risks = np.zeros(n_portfolios)
    all_sharpe_ratios = np.zeros(n_portfolios)
    try:
        if freq == "daily":
            for i in range(n_portfolios):
                weights = create_random_weights(n_assets)
                all_weights[i, :] = weights
                annual_return = np.sum(returns.mean() * weights) * 252
                annual_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
                sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
                
                all_returns[i] = annual_return
                all_risks[i] = annual_volatility
                all_sharpe_ratios[i] = sharpe_ratio
        
        if freq == "monthly":
            for i in range(n_portfolios):
                weights = create_random_weights(n_assets)
                all_weights[i, :] = weights
                annual_return = np.sum(returns.mean() * weights) * 12
                annual_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 12, weights)))
                sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
                
                all_returns[i] = annual_return
                all_risks[i] = annual_volatility
                all_sharpe_ratios[i] = sharpe_ratio
    except:
        print("Must specify if monthly or daily data is being used")
    
    return all_weights, all_returns, all_risks, all_sharpe_ratios

# Specify path to CSV files
directory = r"C:\Users\willk\OneDrive\Desktop\Quant Projects"
ES_file = os.path.join(directory, "CME_MINI_DL_ES1!, 1M.csv")
ZN_file = os.path.join(directory, "CBOT_DL_ZN1!, 1M.csv")
tf_file = os.path.join(directory, "Trend_Following.csv")
tlt_zb_arb_file = os.path.join(directory, "TLT_ZB_Arbitrage.csv")
risk_free_rates_file = os.path.join(directory, "3M_TBill.csv")

# Load CSV files
ES = pd.read_csv(ES_file, index_col=0, parse_dates=True)
ZN = pd.read_csv(ZN_file, index_col=0, parse_dates=True)
tf = pd.read_csv(tf_file, index_col=0, parse_dates=True)
tlt_zb_arb = pd.read_csv(tlt_zb_arb_file, index_col=0, parse_dates=True)
risk_free_rates = pd.read_csv(risk_free_rates_file, index_col=0, parse_dates=True)

# Calculate daily returns
returns_ES = ES['close'].pct_change().ffill().dropna()
returns_ZN = ZN['close'].pct_change().ffill().dropna()
returns_tf = tf['close'].pct_change().ffill().dropna()
returns_tlt_zb_arb = tlt_zb_arb['close'].pct_change().ffill().dropna()
returns_risk_free_rates = risk_free_rates['yield'].ffill().dropna()*(1/12)*(1/100)

# Combine the returns into a single DataFrame
# Also adding risk free rates to positions that hold futures to gain income from cash
# 'returns_tlt_zb_arb' only has 0.5 times risk free rate because only half of position is in futures; other half is in TLT ETF
returns = pd.concat([returns_ES + returns_risk_free_rates, returns_ZN + returns_risk_free_rates, returns_tf + returns_risk_free_rates, returns_tlt_zb_arb + 0.5*returns_risk_free_rates], axis=1)
returns.columns = ['ES', 'ZN', 'ZT Trend Following', 'TLT/ZB Pair']
returns.ffill(inplace=True)
returns.sort_index(inplace=True)

# Split data into in-sample and out-of-sample
train_size = int(len(returns) * 0.8)
train_returns = returns.iloc[:train_size]
test_returns = returns.iloc[train_size:]

# Plot the returns for each series
colors = ['blue', 'green', 'red', 'purple']

for i, column in enumerate(returns.columns):
    plt.plot(returns[column].cumsum(), color=colors[i], label=column)

plt.legend(loc='best')
plt.title('Cumulative Returns of Each Series')
plt.ylabel('Cumulative Returns')
plt.xlabel('Time')
plt.show()

# Use training data to generate portfolios
risk_free_rate_train = np.mean(returns_risk_free_rates.iloc[:train_size]) * 12
all_weights, all_returns, all_risks, all_sharpe_ratios = create_random_portfolios(train_returns, n_portfolios, risk_free_rate_train)

# Find the top 100 portfolios by Sharpe ratio
top_indices = np.argsort(all_sharpe_ratios)[-100:]
top_weights = all_weights[top_indices]
top_sharpe_ratios = all_sharpe_ratios[top_indices]
top_returns = all_returns[top_indices]

# Calculate the median weights from the top 100 portfolios
median_weights = np.median(top_weights, axis=0)

# Print out the weightings for the top 100 portfolios
for i, idx in enumerate(top_indices):
    print(f"Portfolio {i+1} Weights - ES: {top_weights[i][0]:.2f}, ZN: {top_weights[i][1]:.2f}, TF: {top_weights[i][2]:.2f}, TLT/ZB Arb: {top_weights[i][3]:.2f}, Sharpe Ratio: {top_sharpe_ratios[i]:.2f}, Annualized Return: {top_returns[i]:.3f}")

# Identify the portfolio with the highest Sharpe ratio
max_sharpe_idx = np.argmax(all_sharpe_ratios)
max_sharpe_weights = all_weights[max_sharpe_idx]
max_sharpe_return = all_returns[max_sharpe_idx]
max_sharpe_volatility = all_risks[max_sharpe_idx]

# Print out the best portfolio
print(f"\nBest Portfolio Weights - ES: {max_sharpe_weights[0]:.2f}, ZN: {max_sharpe_weights[1]:.2f}, TF: {max_sharpe_weights[2]:.2f}, TLT/ZB Arb: {max_sharpe_weights[3]:.2f}")
print(f"Best Portfolio Sharpe Ratio: {all_sharpe_ratios[max_sharpe_idx]:.2f}")

# Plot the Efficient Frontier with all portfolios
plt.scatter(all_risks, all_returns, c=all_sharpe_ratios, cmap='viridis')
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Expected Volatility')
plt.ylabel('Expected Return')
plt.title('Efficient Frontier and Available Portfolios')

# Set x and y axis limits
plt.xlim([0, 0.5])
plt.ylim([-0.5, 0.5])

plt.show()

# Calculate and plot the overall profit using the best portfolio weights
cumulative_profit = (1 + (returns * max_sharpe_weights).sum(axis=1)).cumprod()
plt.figure(figsize=(10, 5))
plt.plot(cumulative_profit, label='Cumulative Profit of Best Portfolio')
plt.xlabel('Date')
plt.ylabel('Cumulative Profit')
plt.title('Cumulative Profit Using the Best Portfolio Weights')
plt.legend()
plt.show()

# Calculate annual return, volatility, and Sharpe ratio using test data
risk_free_rate_test = np.mean(returns_risk_free_rates.iloc[train_size:]) * 12
test_annual_return = np.sum(test_returns.mean() * median_weights) * 12  # Adjust factor based on your data frequency
test_annual_volatility = np.sqrt(np.dot(median_weights.T, np.dot(test_returns.cov(), median_weights))) * np.sqrt(12)
test_sharpe_ratio = (test_annual_return - risk_free_rate_test) / test_annual_volatility

# Print out test data
print("Test Annual Return:", test_annual_return)
print("Test Annual Volatility:", test_annual_volatility)
print("Test Sharpe Ratio:", test_sharpe_ratio)

# Plot returns using median weights
cumulative_returns_test = (1 + (test_returns * median_weights).sum(axis=1)).cumprod()
plt.figure(figsize=(10, 5))
plt.plot(cumulative_returns_test.index, cumulative_returns_test, label='Cumulative Returns using Median Weights')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.title('Performance on Test Data')
plt.legend()
plt.show()

print(cumulative_returns_test)