#Importing packages
import requests, bs4, re

#Reusable Functions
def retrieve_links(url):
    """This function retrieves all links on a webpage and returns a list of them"""
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    ls = []
    for link in soup.find_all('a'):
        ls.append((link.get('href')))
    return ls

#Obtain a list of individual links for each crypotcurrency from allcryptowhitepapers.com
url = 'https://www.allcryptowhitepapers.com/whitepaper-overview/'
temp_ls = retrieve_links(url)
print(temp_ls[:40])
#Our list has irrelevant links, find out where the relevant links are at 
print(temp_ls[:20]) #check where the first relevant crypto paper starts
print(temp_ls[-20:]) #check where does the last relevant paper is at

#Find index of the bookends for the relevant links and filter them
first = 'https://www.allcryptowhitepapers.com/crypto-dictionary/' 
last = 'https://www.binance.com/?ref=19802351'
first_index = temp_ls.index(first)
last_index = temp_ls.index(last)
crypto_ls = temp_ls[first_index+1:last_index] #final crypto list
assert len(crypto_ls) == 2826 #check if number of links tally up

#Extract names from the links in crypto_ls
def extract_names(link):
    try:
        m = re.search('(?<=.com/).*(?=-whitepaper)', link, re.IGNORECASE)
        return m.group(0)
    except AttributeError: #3 papers don't end with -whitepaper
        m = re.search('(?<=.com/).*',link, re.IGNORECASE)
        return m.group(0)
    else:
        print(link)
crypto_names = [extract_names(link) for link in crypto_ls]

#Check whether each individual page has a .pdf, code takes too long to run so don't run it LOL
no_pdf_ls = []
for link in crypto_ls:
    try:
        res = requests.get(link)
        soup = bs4.BeautifulSoup(res.text)
        if not soup.find_all('a', href = re.compile('.pdf')):
            no_pdf_ls.append(link)
    except Exception as e:
        print(e)
        


