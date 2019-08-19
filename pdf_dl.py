#Import packages
import pandas as pd
import numpy as np
import requests
import os

#Preprocessing steps to split the csv files
# #Read csv file
# location = r'C:\Users\Andy\OneDrive\UpLevel\Whitepaper_data_v3.csv.csv'
# data = pd.read_csv(location)

# #pdf only files
# data_pdf = data[data['link_type'] == 'pdf']
# len(data_pdf) #1433

# #filter to only names and the pdf links
# data_pdf_filtered = data_pdf.filter(['Cryptocurrency', 'Links'])

# #Convert to numpy array so we can split to relatively equal parts
# data_pdf_np = data_pdf_filtered
# split_df = np.array_split(data_pdf_np, 4)
# number = 0 #Aziz take 1, Carol take 2, Jackie take 3

# #df to dict
# df = split_df[number]
# name_dl_dic = df.set_index('Cryptocurrency').T.to_dict('records')[0]
# len(name_dl_dic)

#pdf downloader
# csv = 'Andy.csv'
# dirc = r'D:\\Users\\Andy\\Desktop'
def pdf_downloader(csv, dirc):
    """
    This function takes in the csv containing the names and pdf,
    and downloads the pdfs into a directory of choice. Any problems will be saved
    as a problems.csv in the same directory
    inputs: csv file (e.g. Andy.csv), directory (e.g. 'C://Users//Andy)
    """
    os.chdir(dirc)
    df = pd.read_csv(csv)
    df = df.filter(['Cryptocurrency', 'Links'])
    name_dl_dic = df.set_index('Cryptocurrency').T.to_dict('records')[0]
    problem_ls = []
    for name in name_dl_dic.keys():
        try:
            dl_link = name_dl_dic[name]
            r = requests.get(dl_link, timeout = 10)
            if 'pdf' not in r.headers.get('content-type'):
                print(name, 'file not pdf')
                problem_ls.append([name, dl_link, 'not_pdf'])
                continue   
            else:
                name = name.replace('?', '-')
                name = name.replace('/', '-')
                dest = os.getcwd() + '\\whitepaper\\' + name 
                os.makedirs(dest, exist_ok = True)
                filename = dest + '\\' + name + '_whitepaper.pdf'
                with open(filename,'wb') as file:
                    file.write(r.content)
        except Exception as e:
            problem_ls.append([name, dl_link, str(e)])
            print(name, e)
    failure_rate = len(problem_ls)/len(name_dl_dic) * 100
    success_rate = 100-failure_rate
    success_rate = str(success_rate) + '%'
    print('Sucess rate is', success_rate)
    problem_df = pd.DataFrame(problem_ls)
    problem_df.columns = ['name', 'link', 'error_descrption']
    problem_df.to_csv('problem.csv')

if __name__ == '__main__':
    print('Input CSV location in string format')
    csv = input()
    print('Input directory to create and write files')
    dirc = input()
    pdf_downloader(csv, dirc)