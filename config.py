import datetime


index_names = ['^GSPC','^FCHI','^N225']
ticker_names = index_names+['USDEUR=X','USDJPY=X','GBPUSD=X']

balance = {'^GSPC' : 4000000, '^FCHI' :2000000 , '^N225' : 1000000}


start_date = datetime.datetime(2019,12,9)
end_date = datetime.datetime.now()