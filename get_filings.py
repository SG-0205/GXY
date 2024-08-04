from ast import Constant
import os
import datetime
from pickle import LIST
from pprint import PrettyPrinter
from tkinter.filedialog import SaveFileDialog
from typing import List
from urllib.parse import urldefrag
from anytree import Node, RenderTree

import constants
import json
import requests
from sec_edgar_api.EdgarClient import EdgarClient
import get_xml_form

#Edgar Init
client = EdgarClient("GXY")

def tree_builder(elems: List, parent=None):
    if (parent == None):
        parent = Node('root')
    for item in elems:
        if isinstance(item, list):
            child = Node('list', parent=parent)
            tree_builder(item, parent=child)
        else:
            Node(item, parent=parent)
        
    return (parent)
            

def check_m_time(filepath: str):
    """Compare la dernière modification d'un fichier d'entreprise avec la durée REFRESH_MIN_H.

    Args:
        filepath (str): Chemin vers le fichier.

    Returns:
        bool: Renvoie True si le fichier a été modifié dans la période REFRESH_MIN_H.
    """
    refresh_limit = datetime.timedelta(hours=constants.REFRESH_MIN_TIME_H)
    last_mod_t = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    if (datetime.datetime.now() - last_mod_t < refresh_limit):
        return (True)
    else:
        return (False)
    

#CIK filtering
def get_lines_from_names(cik_list: List[str], name_list: List[str]):
    """Récupère les lignes du fichier contenant les identifiants d'entreprise (CIK) correspondantes au noms passés en paramètre.

    Args:
        cik_list (List[str]): Liste complète des entreprises enregistrées auprès de la SEC.
        name_list (List[str]): Liste des entreprises à extraire.

    Returns:
        Dict{str: List[str]}: Dictionnaire avec comme clefs les noms des entreprises recherchées et comme valeurs les lignes extraites.
    """
    return_list = {name : [] for name in name_list}

    for name in name_list:
        for line in cik_list:
            if line.__contains__(name) == True:
                return_list[name].append(line)

    return (return_list)    


def get_cik_from_lines(cik_lines: List[str]):
    """Isole l'identifiant CIK de chaque ligne d'entreprise contenues dans la liste.

    Args:
        cik_lines (List[str]): Lignes d'information d'entreprise.

    Returns:
        List[str]: Liste d'identifiants CIK.
    """
    return_list = []

    for line in cik_lines:
        return_list.append(line.split(sep=':')[1])

    return (return_list)


def get_13f_fillings(cik: str):
    """Tente de récupérer les détails d'une entreprise à partir de son CIK et les renvoie formaté en JSON.

    Args:
        cik (str): Identifiant CIK de l'entreprise.

    Returns:
        JSON : Informations détaillées de l'entreprise au format JSON.
    """
    endpoint = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = constants.API_HEADER
    doc = requests.get(url=endpoint, headers=headers)

    if (doc.status_code == 200):
        return (doc.json())
    else:
        print("API ERROR")

        return (0)


def get_json_list(ciks: List[str], save_name: str):
    """Enregistre les documents liés aux CIKs de l'entreprise passés en paramètre dans un fichier qui prend le nom de l'entreprise.

    Args:
        ciks (List[str]): Liste d'identifiants CIKs rattachés au nom de la société.
        save_name (str): Nom de la société/groupe

    Returns:
        List[str]: Détails des CIKs au format JSON (Contenu du fichier créé).
    """
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
    """Crée un dictionnaire avec en clefs les noms des entreprises à analyser et en valeurs les url vers les documents de type [form_type].

    Args:
        ciks_db (str): FilePath vers le fichier contenant la liste complète des entreprises (CIK_FILE).
        to_retrieve (List[str]): Liste des entreprises à analyser.
        form_type (str): Type de formulaire à récupérer.
        refresh_data (bool): True : Ignore les entreprises avec un fichier JSON déjà créé.

    Returns:
        dict{str: List[str]}: Dictionnaire avec en clefs le nom des entreprises/groupes analysés en en valeurs des listes d'URL menant aux documents recherchés.
    """
    if refresh_data == False:
        for cpy_name in to_retrieve:
            if os.path.exists(f'./json_data/{cpy_name}') == True:
                to_retrieve.remove(cpy_name)
    db_lines = open(ciks_db).readlines()
    retrieved_lines = get_lines_from_names(db_lines, to_retrieve)
    url_dict = {name : [] for name in to_retrieve}
    cik_dict = {name : [] for name in to_retrieve}

    for name in url_dict.keys():
        cik_dict[name] = get_cik_from_lines(retrieved_lines[name])
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
visual_tree = tree_builder(test["VANGUARD"])
for pre, fill, node in RenderTree(visual_tree):
    print("%s%s" % (pre, node.name))
visual_tree = tree_builder(test["BLACKROCK"])
for pre, fill, node in RenderTree(visual_tree):
    print("%s%s" % (pre, node.name))
get_xml_form.save_xml_docs(test)
# get_xml_form.xml_save_cleaner()
# get_xml_form.extract_cik_from_url(test["VANGUARD"][0][0])
# test_xml = get_xml_form.extract_xml_from_file(test['VANGUARD'][0][0])
# t_file = open("./xml_forms/testV.xml", "w")
# t_file.write(get_xml_form.extract_xml_from_file(test['VANGUARD'][0][0]))
# print(test_xml)
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

