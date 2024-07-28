import json

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

def check_for_form_type(company_data: dict, form_type):
    filings = company_data.get('filings', {})
    recent = filings.get('recent', {})
    forms = recent.get('form', [])
    return (forms.__contains__(form_type))