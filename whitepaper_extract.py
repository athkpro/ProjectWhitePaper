#Importing packages
import requests, bs4, re, json, os, copy
from collections import Counter

#Reusable Functions
def retrieve_links(url, href = re.compile('(?s).*'), string = re.compile('(?s).*')):
    """This function retrieves all links on a webpage and returns a list of them, with some filtering options
    ARGS: 
    url: url of the site you want to retrieve links
    href: Allow the users to filter by a regex pattern within the link. By default, it matches everything
    string: Allows user to filter by a regex pattern if a string is followed after the link. E.g. Text layered over a hyperlink By default, it matches everything.
    """
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    ls = []
    for link in soup.find_all('a', href = href, string = string):
        ls.append((link.get('href')))
    return ls

def retrieve_html(url):
    """retrieve all links within a text and prints it out to observe
    """
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    for link in soup.find_all('a'):
        print(link)

def store_dic(dic, name):
    """Saves dic as json file in current directory
    """
    with open(name, 'w') as file:
        json.dump(dic, file)

def store_soup(soup, name):
    """saves soup object as text file in current directory
    """
    with open(name, 'w') as file:
        file.write(soup.prettify())

#Workflow
#Obtain a list of individual links for each crypotcurrency from allcryptowhitepapers.com
url = 'https://www.allcryptowhitepapers.com/whitepaper-overview/'
temp_ls = retrieve_links(url)
#Our list has irrelevant links, find out where the relevant links are at 
print(temp_ls[:20]) #check where the first relevant crypto paper starts
print(temp_ls[-20:]) #check where does the last relevant paper is at

#Find index of the bookends for the relevant links and filter them
first = 'https://www.allcryptowhitepapers.com/crypto-dictionary/' 
last = 'https://www.allcryptowhitepapers.com/about-us/'
first_index = temp_ls.index(first)
last_index = temp_ls.index(last)
crypto_ls = temp_ls[first_index+1:last_index] #final crypto list
crypto_ls = list(set(crypto_ls))
assert len(crypto_ls) == 2826 #check if number of links tally up, accurate as of 7.8.2019

#Generate a list of all the names of cryptocurrencies listed on allcryptowhitepaper
crypto_names = []
res = requests.get(url)
soup = bs4.BeautifulSoup(res.text, 'lxml')
for name in soup.find_all("td", {"class":"column-1"}):
    crypto_names.append(name.text)
assert len(crypto_names) == len(crypto_ls)

#Combine both the name and link lists together into a single dictionary
link_name_dic = dict(zip(crypto_ls, crypto_names))
assert len(link_name_dic.values()) == 2817 #notice it is 2817 instead of 2828, i.e. there are 9 duplicates! Of note, bismuth is still duplicated in this dictionary!
store_dic(link_name_dic, 'link_name.json') #save this in case

#Find all links without the div class = entry-content tag to filter out redundant links, then search for the specific link with "whitepaer" in the .string
test_size = len(crypto_ls)
crypto_ls_test = crypto_ls[:test_size]
name_dl_dic = {}
problem_ls = []
for link in crypto_ls_test:
    req2 = requests.get(link)
    soup2 = bs4.BeautifulSoup(req2.text, 'lxml')
    name = link_name_dic[link]
    try:
        for div in soup2.find_all("div", {"class": "entry-content"}):
            for dl_link in div.find_all('a', string = re.compile("whitepaper", re.IGNORECASE)):
                name_dl_dic[name] = dl_link['href']
    except:
        name_dl_dic[name] = None
        problem_ls.append(link)
Success_rate = (test_size - len(problem_ls))/test_size * 100
print(Success_rate) #100%, no errors woohoo!

#Edit bitcoin key as it retrieved the comic link
name_dl_dic['Bitcoin'] = 'https://www.bitcoin.com/bitcoin.pdf'

#Count the number of cryptos that do not have a download link
counter = Counter(list(name_dl_dic.values()))
print(len(name_dl_dic)) #2112
print(counter['']) #66 links self referencing itself (i.e. point back to the allcryptowhitepaper site)
print(len(set(link_name_dic.values())- set(name_dl_dic.keys()))) #705 no links at all
#705 + 2112 = 2817 it tallies!

#Store the download dictionary into a json file 
store_dic(name_dl_dic, 'crypto_dl.json')

#Remove the cryptocurrencies with the '' values
remove_ls = [key for key,value in name_dl_dic.items() if value == '']
for name in remove_ls:
    del name_dl_dic[name]
assert len(name_dl_dic) == 2112-66 #2046

#Store the final download dictionary into a json file
store_dic(name_dl_dic, 'crypto_dl_filtered.json')

#make a directory to store the files
current_dir = os.getcwd()
os.mkdir(current_dir + '\whitepapers')
for name in name_dl_dic.keys():
    name = name.replace('?', '-')
    name = name.replace('/', '-')
    try:
        os.mkdir(current_dir + '\whitepapers\\' + name)
    except Exception as e:
        print(name,e)

#One error was thrown, SafeCoin vs Safecoin, another duplicate!
del name_dl_dic['Safecoin'] #final is 2045
store_dic(name_dl_dic, 'crypto_final.json')


#Test out downloading a single link [WORK IN PROGRESS]
name = crypto_names[5]
test_url = name_dl_dic[name]
dl_req = requests.get(test_url)
content_type = dl_req.headers.get('content-type')
if 'application/pdf' in content_type:
    ext = '.pdf'
elif 'text/html' in content_type:
    ext = '.html'
else:
    ext = ''
    print('Unknown format')



#OLD CODES/IDEAS
#Extract names from the links in crypto_ls [NOT an ideal solution]
# def extract_names(link):
#     try:
#         m = re.search('(?<=.com/).*(?=-whitepaper)', link, re.IGNORECASE)
#         return m.group(0)
#     except AttributeError: #3 papers don't end with -whitepaper
#         m = re.search('(?<=.com/).*',link, re.IGNORECASE)
#         return m.group(0)
#     else:
#         print(link)
# crypto_names = [extract_names(link) for link in crypto_ls]

#Check whether each individual page has a .pdf, code takes too long to run so don't run it LOL
# no_pdf_ls = []
# for link in crypto_ls:
#     try:
#         res = requests.get(link)
#         soup = bs4.BeautifulSoup(res.text)
#         if not soup.find_all('a', href = re.compile('.pdf')):
#             no_pdf_ls.append(link)
#     except Exception as e:
#         print(e)
