import pandas as pd
import utilities 
import config
'''
^GSPC = S&P500
FTSE = FTSE 100 GBP
FCHI = CAC 40 EUR
N225 = Nikkei 225 JPY (Japan)
'''



show_all_dataframe = True

if show_all_dataframe :
	pd.set_option('display.max_rows',None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', None)
	pd.set_option('display.max_colwidth', None)

	
if __name__=='__main__':

	index_names = ['^GSPC','^FCHI','^N225']
	ticker_names = index_names+['USDEUR=X','USDJPY=X','GBPUSD=X']
	
	
	
	# in dollar 
	balance = {'^GSPC' : 4000000, '^FCHI' :2000000 , '^N225' : 1000000}
	starting_balance = 0
	for index in balance:
		starting_balance +=  balance[index]
	
	close_data = utilities.RetrieveDataFromWeb(config.start_date,config.end_date,ticker_names)
	close_data = pd.read_excel('data.xlsx')

	index_names = close_data.columns
	balance = {'FTSE-500' : 3000000, 'CAC-40' :1000000 , 'Nikkei' : 2000000,'S&P 500' : 4000000}
	
	
	#utilities.HistoricalSimulation(close_data,balance)
	
	utilities.ModelBuilding(close_data,balance)
	
	