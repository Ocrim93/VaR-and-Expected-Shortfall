import numpy as np
import datetime 
import pandas_datareader as web
import pandas as pd
import csv
import matplotlib.pyplot as plt
import openpyxl
from tabulate import tabulate 
import utilities 
import math



def RetrieveDataFromWeb(start_date,end_date,ticker_names):

	df = web.DataReader(ticker_names,data_source="yahoo",start=start_date, end=end_date)
	
	close_data = df.loc[:,('Adj Close')].copy()
	
	# clear the data 
	close_data = close_data.dropna()
	
	close_data.loc[:,'^FCHI'] = close_data['^FCHI']/close_data['USDEUR=X']
	close_data.loc[:,'^N225'] = close_data['^N225']/close_data['USDJPY=X']
	
	close_data= close_data.drop(['USDEUR=X','USDJPY=X','GBPUSD=X'],axis=1)
	close_data = close_data.dropna()
	return close_data


def HistoricalSimulation(close_data,balance):
	starting_balance = 0
	for index in balance:
		starting_balance +=  balance[index]
	
	index_names = close_data.columns
	# compute the profit for the future scenarios 
	for ticker in index_names:
		close_data[ticker + '_profit'] =  close_data[ticker].copy().shift(-1)/close_data[ticker]
	
	close_data = close_data.dropna()
	close_data.to_csv('close_data.csv')
	close_data.reset_index()
	
	
	scenario = pd.DataFrame()
	for ticker in index_names:
		scenario[ticker] = np.array(close_data[ticker])[-1]*close_data[ticker + '_profit'] 
	
	portfolio_sum = 0
	for ticker in index_names:
		portfolio_sum += scenario[ticker]*balance[ticker]/np.array(close_data[ticker])[-1]
	scenario['Portfolio_Value'] = portfolio_sum
	
	scenario['Loss'] = scenario['Portfolio_Value'] - starting_balance
	scenario.reset_index(inplace=True,drop=True)	
	

	mean = scenario['Loss'].mean()
	vol = scenario['Loss'].std(ddof=1) # it uses n-1 degrees of freedom
	skewness = scenario['Loss'].skew()
	kurtosis = scenario['Loss'].kurtosis()
	print(skewness,'\t',kurtosis)

	'''
	skeness is the third momentum generator and measures the asymmetry of the normal distribution
	standard normal distribution has 0 skewness
	positive skewness -> longer or fatter right tail as lognormal distribution
	negative skewness -> longer or fatter left tail as lognormal distribution

	kurtosis measures the tailedness of normal distribution 
	standard normal distribution has 3 as kurtosis value
	kurtosis > 3 fatter tails 
	Kurtosis < 3 skinner tails 
	'''
	
	print(mean,vol)
	
	scenario['NormLoss'] = (scenario['Loss'] - mean)/vol
	
	scenario = scenario.sort_values(by=['Loss'])
	#scenario.reset_index(inplace=True,drop=True)
	# weighted observation
	lambda_weight = 0.995
	scenario['Weight'] = np.array(weight_formula(lambda_weight,i,len(scenario['Loss']))   for i in scenario.index)

	#Cumulative weight
	scenario['Cumulative_Weight'] = scenario['Weight'].cumsum()

	print(scenario[0:10])
	
	VaR99 = scenario['Loss'].quantile(0.01) 
	VaR95 = scenario['Loss'].quantile(0.05)

	#which position is the Var99
	a = ''
	a_idx = ''
	for idx,row in scenario.iterrows():
		if a == '':
			a = row['Loss']
			a_idx = idx
			continue
		if VaR99 > a and  VaR99 < row['Loss']:
			if abs(VaR99 - a) < abs(VaR99 - row['Loss']):
				VaR99_el,VaR99_el_idx = a,a_idx
			else:
				VaR99_el,VaR99_el_idx = row['Loss'],a_idx	
			break
		else:
			a = row['Loss']
			a_idx = idx
	ES = scenario.loc[scenario.index[0]:VaR99_el_idx]['Loss'].mean()
	

	threshold = 0.01
	for row in scenario.itertuples():
		if row.Cumulative_Weight > threshold:
			Var_weighted  = row.Loss
			break
	
	ES_weighted = scenario['Loss'][scenario.index[0]]*scenario['Weight'][scenario.index[0]]+ scenario['Loss'][scenario.index[1]]*scenario['Weight'][scenario.index[1]] +(threshold-scenario['Weight'][scenario.index[0]] - scenario['Weight'][scenario.index[1]])*scenario['Loss'][scenario.index[2]]  
	ES_weighted *=  100
	
	X=np.random.normal(mean,vol,len(scenario['Loss']))  # what excel uses
	VaR99M = np.percentile(X,1)
	
	print (tabulate([['99%',VaR99],['99%.M',VaR99M],['95%',VaR95],['ES',ES],['VaR_weighted',Var_weighted],['ES_weighted',ES_weighted]], headers = ['Confidence Level','Value at Risk']))
	scenario.to_csv('scenario.csv')
	
	count, bins, ignored = plt.hist(scenario['Loss'],100) # number of bins setted to 100
	
	#plt.show()
	#plt.pause(10) # 3 seconds
	#plt.close('all')
	

def ModelBuilding(close_data,balance):
	
	pd.set_option('display.float_format', '{:.10f}'.format)
	
	ticker_names = close_data.columns 

	rate_of_return = pd.DataFrame()

	for ticker in ticker_names:
		rate_of_return[ticker] = (close_data[ticker].copy().shift(-1) - close_data[ticker])/close_data[ticker]
	rate_of_return.dropna(inplace=True)

	correlation_matrix = rate_of_return.corr()

	cov_matrix = pd.DataFrame.cov(rate_of_return)   #ddof n-1, also the covariance coeff is with n-1 ddof

	balance_vector = pd.DataFrame({ 'S&P 500':[4000],'FTSE-500':[3000],'CAC-40':[1000],'Nikkei':[2000]})
	balance_vector=balance_vector.reset_index(drop =True)
	

	variance_portfolio = (balance_vector.dot(cov_matrix)).dot(balance_vector.T).iloc[0]
	vol = math.sqrt(variance_portfolio)

	z = np.percentile(np.random.normal(0,1,1000000),1)

	VaR99 = z*vol
	ES = vol*pow(math.e,-z*z/2)/(math.sqrt(2*math.pi)*(1-0.99))
	print(cov_matrix)
	print(correlation_matrix)
	print(variance_portfolio[0])
	print(VaR99,ES)

	
def weight_formula(lambda_weight,i,n):
	return	math.pow(lambda_weight,n - i)*(1- lambda_weight )/(1-math.pow(lambda_weight,n))

	