from os import write
from pickle import LIST
from typing import List
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
    return_list = []
    for name in name_list:
        name = name.capitalize()
    for name in name_list:
        for line in cik_list:
            if line.__contains__(name) == True:
                return_list.append(line)
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

def get_json_list(ciks: List[str], filepath: str):
    save_file = open(filepath, "w")
    if save_file.writable() == True:
        for cik in ciks:
            dump = get_13f_fillings(cik)
            if (dump != 0):
                save_str = json.dumps(dump)
                save_file.write(save_str + '\n')

lines = get_lines_from_names(cik_list=cik_list, name_list=['VANGUARD'])
ciks = get_cik_from_lines(lines)
# get_json_list(ciks, "./json_saveV.json")
json_list = open("./json_saveV.json", "r").readlines()
doc_urls = []
for line in json_list:
    doc_urls.append(get_xml_form.get_form_urls_from_data(json.loads(line), "13F-HR"))

print(doc_urls)    
# print(get_13f_fillings(ciks[0]))

