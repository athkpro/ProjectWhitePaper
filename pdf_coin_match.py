#Retrieving coin information from coingecko, creating a coin_names ls
# See https://www.coingecko.com/en/api

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

coin_list = cg.get_coins_list()
coin_names = {}
for coin in coin_list:
    name = coin['name']
    coin_id = coin['id']
    coin_names[name] = coin_id

#Retrieve the names of the pdfs we farmed using pydrive. Note you need a client secret key for this.
# See https://pythonhosted.org/PyDrive/quickstart.html
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

#Find drive name
drive_id = '1D7lco7MJxvesBEqxc5-qAn_KF7FKUeDV' #id for our shared drive
file_list = drive.ListFile({'q': "'1D7lco7MJxvesBEqxc5-qAn_KF7FKUeDV' in parents and trashed=false"}).GetList()
for file1 in file_list:
  print('title: %s, id: %s' % (file1['title'], file1['id']))

# title: whitepaper_pdf4, id: 1XxUoFz1-xfJC5r6O66VLhF3liTCRpjH_
# title: whitepaper_pdf3, id: 1qpyDrXbjCnnPSkSEWAfVPdDy3Lk0AX94
# title: whitepaper_pdfs2, id: 1gBcBJk_IeO2KMmqSvuQ8uxyTCXt-IJKh
# title: Whitepaper_pdfs, id: 19NQzctQhRIhuvBkieY3NFvpnckLwOVpT

#Creating a list of coin names from our pdfs called pdf_ls
pdf_ls = []
id4 = "'1XxUoFz1-xfJC5r6O66VLhF3liTCRpjH_'"
id3 = "'1qpyDrXbjCnnPSkSEWAfVPdDy3Lk0AX94'"
id2 = "'1gBcBJk_IeO2KMmqSvuQ8uxyTCXt-IJKh'"
id1 = "'19NQzctQhRIhuvBkieY3NFvpnckLwOVpT'"
id_ls = [id1, id2, id3]
def append_id(id, ls):
  file_list = drive.ListFile({'q': f'{id} in parents and trashed=false'}).GetList()
  for file1 in file_list:
    ls.append(file1['title'])
for id in id_ls:
  append_id(id, pdf_ls)

#Handling carol's folder
import re
pdf4_ls = []
append_id(id4, pdf4_ls)
def retrieve_name(text):
  pattern = re.compile(r'(?<=\\)(.*?)(?=_)')
  m = re.search(pattern, text)
  name = m.group(0).split('\\')[-1]
  return name
pdf4_ls_edit = [retrieve_name(title) for title in pdf4_ls]
for name in pdf4_ls_edit:
  pdf_ls.append(name)

#Matching our pdf_ls with the coin_names from coin gecko
def standardise(name):
  """
  This function takes in a name tries to standardise the names as much as possible by removing spaces, werid characters to ensure proper matching.
  """
  if '(' in name:
    name = name.split('(')[0]
  if '[' in name:
    name = name.split('[')[0]
  name = name.replace('#', '')
  name = name.replace('-', '')
  name = name.replace('?', '-')
  name = name.replace('/', '-')
  name = name.replace('  ', '')
  name = name.replace(' ', '')
  name = name.lower()
  return name


#Create a standardised version of both list
pdf_ls_standardised = [standardise(x) for x in pdf_ls]
coin_names_standardised = [standardise(x) for x in coin_names.keys()]

#These dics helps us retrieve back the unstandardized version later
pdf_dic = dict(zip(pdf_ls_standardised, pdf_ls))
coin_dic = dict(zip(coin_names_standardised, coin_names))

#checking how many match between the two lists using sets in python
match_set = set(pdf_ls_standardised).intersection(set(coin_names_standardised))
print(len(match_set)) #759 match
matchless_set = set(pdf_ls_standardised) - set(coin_names_standardised)
print(matchless_set)

#create a dataframe which contains coin_name and coin_id
import pandas as pd
pdf_final = []
coin_final = []
match_ls = sorted(list(match_set))
for name in match_ls:
  pdf_final.append(pdf_dic[name])
  coin_final.append(coin_dic[name])
len(pdf_final)  == len(coin_final)
coin_id_ls = [coin_names[name] for name in coin_final]
data = pd.DataFrame()
data['pdf_name'] = pdf_final
data['coin_id'] = coin_id_ls
print(data)

#Use coin_gecko api to retrieve inital price and current price!
coin_prices_dic = {}
error = []
for name in coin_id_ls:
  try:
    price_dic = cg.get_coin_market_chart_by_id(name, vs_currency = 'usd', days = 'max')
    price_list = price_dic['prices']
    first_date = price_list[0][0]
    first_price = price_list[0][1]
    latest_date = price_list[-1][0]
    latest_price = price_list[-1][1]
    coin_prices_dic[name] = [first_date, first_price, latest_date, latest_price]
    print(name, 'successly retrieved')
  except Exception as e:
    print(name, e)
    error.append(name)
print(len(coin_prices_dic))

#combine coin prices with corresponding with our data frame
prices_df = pd.DataFrame.from_dict(coin_prices_dic, orient = 'index', columns = ['first_date', 'first_price', 'latest_date [5/9/19]', 'latest_price'])
# data = data.set_index('coin_id', inplace = True)
df = data.join(prices_df)
df = df.reset_index()

#sort out timestamp to a  datetime object
df['first_date'] = df['first_date'].apply(lambda x: pd.Timestamp.fromtimestamp(x/1000))
df['latest_date [5/9/19]'] = df['latest_date [5/9/19]'].apply(lambda x: pd.Timestamp.fromtimestamp(x/1000))

#Output csv as df.csv
df.to_csv('df.csv', index = False, date_format = r'%d/%m/%Y')