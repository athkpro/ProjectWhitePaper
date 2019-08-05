#Importing packages
import requests, bs4, re, json

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
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    for link in soup.find_all('a'):
        print(link)


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
assert len(crypto_ls) == 2826 #check if number of links tally up, accurate as of 5.8.2019

#Generate a list of all the names of cryptocurrencies listed on allcryptowhitepaper
crypto_names = []
res = requests.get(url)
soup = bs4.BeautifulSoup(res.text, 'lxml')
for name in soup.find_all("td", {"class":"column-1"}):
    crypto_names.append(name.text)
assert len(crypto_names) == len(crypto_ls)

#Combine both the name and link lists together into a single dictionary
link_name_dic = dict(zip(crypto_ls, crypto_names))

#Find the link in each crypto whitepaper page that points to a place to dl the whitepaper
#The general idea is that the download link has the string ('cryptocurrency' + 'whitepaper), so we can try to search for that.
test_size = len(crypto_ls) 
crypto_ls_test = crypto_ls[:test_size]
name_dl_dic = {}
problem_ls = []
for link in crypto_ls_test:
    req2 = requests.get(link)
    soup2 = bs4.BeautifulSoup(req2.text, 'lxml')
    name = link_name_dic[link]
    pattern = name + '[\s]*whitepaper'
    try:
        name_dl_dic[name] = soup2.find('a', string = re.compile(pattern, re.IGNORECASE))['href']
    except:
        name_dl_dic[name] = None
        problem_ls.append(link)
Success_rate = (test_size - len(problem_ls))/test_size * 100
print(Success_rate) #70.42

#Store the dictionary into a json file
with open('crypto_dl.json', 'w') as file:
    json.dump(name_dl_dic, file)

#Test area to see the link with html tags of the crypto page
test = 'https://www.allcryptowhitepapers.com/unus-sed-leo-whitepaper/'
retrieve_html(test)

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
