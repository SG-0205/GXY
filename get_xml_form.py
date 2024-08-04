import json
from urllib.parse import urldefrag
import requests
import xml
import constants
import re
import os

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
    forms = recent.get('form', [])
    print(forms)
    i = 0
    for form in forms:
        if form == form_type:
            url_accessionNb = format_accession_nb(accessionNumber=accession_number[i])
            forms_url_list.append(f"{url_base}{company_data.get('cik')}/{url_accessionNb}/{accession_number[i]}.txt")
        i += 1

    return (forms_url_list)

def check_for_form_type(company_data: dict, form_type: str):
    filings = company_data.get('filings', {})
    recent = filings.get('recent', {})
    forms = recent.get('form', [])
    return (forms.__contains__(form_type))

def get_cpy_name_from_cik(cik: str, cik_list_path=constants.CIK_FILE):
    cik_lines = open(cik_list_path, "r").readlines()
    for line in cik_lines:
        if (line.__contains__(cik)):
            return (line.removesuffix('\n'))
            

def extract_cik_from_url(form_url: str):
    splitted_url = form_url.split('/')
    return (splitted_url[6])

def extract_form_nb_from_url(form_url: str):
    splitted_url = form_url.split('/')
    return (splitted_url[7])

def extract_xml_from_file(file_url: str, get_header=False) -> str:
    """Récupère un formulaire .txt pointé par une URL et en extrait la partie XML pour un traitement ultérieur.

    Args:
        file_url (str): URL vers le formulaire .txt.
        get_header (str): Si True, renvoie l'en-tête du document.

    Returns:
        str: String XML du document / None si aucune balise XML n'est trouvée.
    """
    xml_start = "<XML>"
    xml_end = "</XML>"
    xml_pattern = re.compile(re.escape(xml_start) + r'(.*?)' + re.escape(xml_end), re.DOTALL)
    txt_rqst = requests.get(file_url, headers=constants.API_HEADER)

    if (txt_rqst.status_code == 200):
        entire_file = txt_rqst.text
        xml_result = xml_pattern.findall(entire_file)
        if (xml_result):
            if (get_header == False):
                return (str(xml_result[1]))
            else:
                return (str(xml_result[0]))
        else:
            return ("ERROR")
    else:
        print(f"GET ERROR @ EXTRACT_XML_FROM_FILES : {txt_rqst.status_code}")
    return ("")


def save_xml_docs(url_dict: dict):
    for cpny in url_dict.keys():
        for sub_cpny in url_dict[cpny]:
            i = 0
            for form in sub_cpny:
                i += 1
                xml_doc = extract_xml_from_file(form, False)
                xml_header = extract_xml_from_file(form, True)
                if not (xml_doc.__contains__("ERROR")):
                    sub_cik = get_cpy_name_from_cik(extract_cik_from_url(form))
                    if not os.path.exists(f"{constants.XML_SAVE_DIR}/{cpny}/{sub_cik}"):
                        os.makedirs(f"{constants.XML_SAVE_DIR}/{cpny}/{sub_cik}")
                    xml_save = open(f"{constants.XML_SAVE_DIR}/{cpny}/{sub_cik}/{extract_form_nb_from_url(form)}.xml", "w")
                    xml_save.write(xml_doc)
                    print(f"[{sub_cik}] XML CONTENT OK ({i}/{sub_cpny.__len__()})")
                else:
                    print(f"[{sub_cik}] NO XML CONTENT ({i}/{sub_cpny.__len__()})")
                if not (xml_header.__contains__("ERROR")):
                    sub_cik = get_cpy_name_from_cik(extract_cik_from_url(form))
                    if not os.path.exists(f"{constants.XML_SAVE_DIR}/{cpny}/{sub_cik}"):
                        os.makedirs(f"{constants.XML_SAVE_DIR}/{cpny}/{sub_cik}")
                    xml_save = open(f"{constants.XML_SAVE_DIR}/{cpny}/{sub_cik}/{extract_form_nb_from_url(form)}-header.xml", "w")
                    xml_save.write(xml_header)
                    print(f"[{sub_cik}] XML HEADER OK ({i}/{sub_cpny.__len__()})")
                else:
                    print(f"[{sub_cik}] NO XML HEADER ({i}/{sub_cpny.__len__()})")
