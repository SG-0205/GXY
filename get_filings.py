import os
from pickle import LIST
from pprint import PrettyPrinter
from tkinter.filedialog import SaveFileDialog
from typing import List

from numpy import true_divide
import constants
import json
import requests
from sec_edgar_api.EdgarClient import EdgarClient
import get_xml_form

#Edgar Init
client = EdgarClient("GXY")
cik_list = open("./CIK_LIST_FULL.txt").readlines()
tmp_dump = open("./tmp.json", "w")

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
    headers = {"User-Agent": "GXY"}
    doc = requests.get(url=endpoint, headers=headers)
    if (doc.status_code == 200):
        return (doc.json())
    else:
        print("GET ERROR IN SEC API")
        return (0)

def get_json_list(ciks: List[str], save_name: str):
    save_file = open(f'{constants.JSON_SAVE_DIR}' + f'/{save_name}.json', "w")
    if save_file.writable() == True:
        for cik in ciks:
            dump = get_13f_fillings(cik)
            if (dump != 0):
                save_str = json.dumps(dump)
                save_file.write(save_str + '\n')
    return (save_file.readlines())

def get_url_dict(ciks_db: str, to_retrieve: List[str], form_type: str, refresh_data: bool):
    if refresh_data == False:
        for cpy_name in to_retrieve:
            if os.path.exists(f'./json_data/{cpy_name}') == True:
                to_retrieve.remove(cpy_name)
    db_lines = open(ciks_db).readlines()
    retrieved_lines = get_lines_from_names(db_lines, to_retrieve)
    url_dict = {name : [] for name in to_retrieve}
    for name in to_retrieve:
        company_ciks = get_cik_from_lines(company_lines)            #INDEX OUT OF RANGE
        for company_lines in retrieved_lines[name]:
            print(company_lines)
            json_list = get_json_list(company_lines, name)
            for line in json_list:
                url_dict[name].append(get_xml_form.get_form_urls_from_data(json.loads(line), form_type))

test = get_url_dict("./CIK_LIST_FULL.txt", ['VANGUARD', 'BLACKROCK'], "13F-HR", True)
print(test)
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

