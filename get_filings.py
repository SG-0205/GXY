from ast import Constant
import os
import datetime
from pickle import LIST
from pprint import PrettyPrinter
from tkinter.filedialog import SaveFileDialog
from typing import List
from urllib.parse import urldefrag


import constants
import json
import requests
from sec_edgar_api.EdgarClient import EdgarClient
import get_xml_form

#Edgar Init
client = EdgarClient("GXY")

#Check last data update
def check_m_time(filepath: str):
    refresh_limit = datetime.timedelta(hours=constants.REFRESH_MIN_TIME_H)
    last_mod_t = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    if (datetime.datetime.now() - last_mod_t < refresh_limit):
        return (True)
    else:
        return (False)
    

#CIK filtering
def get_lines_from_names(cik_list: List[str], name_list: List[str]): 
    return_list = {name : [] for name in name_list}
    for name in name_list:
        for line in cik_list:
            if line.__contains__(name) == True:
                return_list[name].append(line)
    return (return_list)    

def get_cik_from_lines(cik_lines: List[str]):
    return_list = []
    for line in cik_lines:
        return_list.append(line.split(sep=':')[1])
    return (return_list)

#13F scraping
def get_13f_fillings(cik):
    endpoint = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = constants.API_HEADER
    doc = requests.get(url=endpoint, headers=headers)
    if (doc.status_code == 200):
        return (doc.json())
    else:
        print("API ERROR")
        return (0)

def get_json_list(ciks: List[str], save_name: str):
    save_file = open(f'{constants.JSON_SAVE_DIR}' + f'/{save_name}.json', "w")
    if save_file.writable() == True:
        for cik in ciks:
            dump = get_13f_fillings(cik)
            if (dump != 0):
                save_str = json.dumps(dump)
                save_file.write(save_str + '\n')
            else:
                return (None)
    save_file_r = open(f'{constants.JSON_SAVE_DIR}' + f'/{save_name}.json', "r")
    return (save_file_r.readlines())

def get_url_dict(ciks_db: str, to_retrieve: List[str], form_type: str, refresh_data: bool):
    if refresh_data == False:
        for cpy_name in to_retrieve:
            if os.path.exists(f'./json_data/{cpy_name}') == True:
                to_retrieve.remove(cpy_name)
    db_lines = open(ciks_db).readlines()
    retrieved_lines = get_lines_from_names(db_lines, to_retrieve)
    print(retrieved_lines)
    url_dict = {name : [] for name in to_retrieve}
    cik_dict = {name : [] for name in to_retrieve}
    for name in url_dict.keys():
        # print(name)
        cik_dict[name] = get_cik_from_lines(retrieved_lines[name])
        # print (url_dict)
        if (os.path.exists(f'{constants.JSON_SAVE_DIR}/{name}.json') == False) or (check_m_time(f'{constants.JSON_SAVE_DIR}/{name}.json') == False):
            json_list = get_json_list(cik_dict[name], name)
        else:
            json_list = open(f'{constants.JSON_SAVE_DIR}/{name}.json').readlines()
        if (json_list != None):
            for line in json_list:
                url_dict[name].append(get_xml_form.get_form_urls_from_data(json.loads(line), form_type))
        url_dict[name] = list(filter(None, url_dict[name]))
            
    return (url_dict)



test = get_url_dict(constants.CIK_FILE, constants.COMPANIES, "13F-HR", True)
get_xml_form.extract_xml_from_file(test['VANGUARD'][0][0])
# print(check_m_time(f'{constants.JSON_SAVE_DIR}/VANGUARD.json'))
# ciks = get_cik_from_lines(lines)
# get_json_list(ciks, "VANGUARD")
# json_list = open(f'{constants.JSON_SAVE_DIR}' + f'/VANGUARD.json', "r").readlines()
# doc_urls = []
# for line in json_list:
#     doc_urls.append(get_xml_form.get_form_urls_from_data(json.loads(line), "13F-HR"))

# doc_urls = list(filter(None, doc_urls))
# doc_urls.sort()



# print(doc_urls)    
# print(get_13f_fillings(ciks[0]))

