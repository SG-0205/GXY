import json
import requests
import constants
import re

def format_accession_nb(accessionNumber: str):
    return_str = str
    nb_split = accessionNumber.split('-')
    return_str = return_str.join('', nb_split)
    return (return_str)

def get_form_urls_from_data(company_data: dict, form_type: str):
    forms_url_list = []
    url_base = "https://www.sec.gov/Archives/edgar/data/"
    filings = company_data.get('filings', {})
    recent = filings.get('recent', {})
    accession_number = recent.get('accessionNumber', [])
    primary_document = recent.get('primaryDocument', [])
    forms = recent.get('form', [])
    print(forms)
    i = 0
    for form in forms:
        if form == form_type:
            print(form)
            print(i)
            url_accessionNb = format_accession_nb(accessionNumber=accession_number[i])
            # prim_doc_url = primary_document[i]
            forms_url_list.append(f"{url_base}{company_data.get('cik')}/{url_accessionNb}/{accession_number[i]}.txt")
        i += 1
        print(i)
        print(form)
    return (forms_url_list)

def check_for_form_type(company_data: dict, form_type: str):
    filings = company_data.get('filings', {})
    recent = filings.get('recent', {})
    forms = recent.get('form', [])
    return (forms.__contains__(form_type))

def extract_xml_from_file(file_url: str):
    xml_start = "<XML>"
    xml_end = "</XML>"
    xml_pattern = re.compile(re.escape(xml_start) + r'(.*?)' + re.escape(xml_end), re.DOTALL)
    txt_rqst = requests.get(file_url, headers=constants.API_HEADER)
    if (txt_rqst.status_code == 200):
        entire_file = txt_rqst.text
        xml_result = xml_pattern.findall(entire_file)
        if (xml_result):
            return (''.join([xml_start + xml_content + xml_end for xml_content in xml_result]))
        else:
            print(f"NO XML IN FILE POINTED BY {file_url}")
            return (None)
    else:
        print(f"GET ERROR @ EXTRACT_XML_FROM_FILES : {txt_rqst.status_code}")
    # print(entire_file)