import datetime


JSON_SAVE_DIR = "./json_data"
XML_SAVE_DIR = "./xml_forms_13f"
XML_SAVE_DIR_G = "./xml_forms_13g"
XML_SAVE_DIR_D = "./xml_forms_13d"
XML_SAVE_DIR_4 = "./xml_forms_4"
XML_SAVE_DIR_5 = "./xml_forms_5"
REFRESH_MIN_TIME_H = 24
COMPANIES = ['VANGUARD', 'BLACKROCK']
CIK_FILE = "./CIK_LIST_FULL.txt"
API_HEADER = {'User-Agent' : 'GXY - Goldenberg WM - samgold0205@gmail.com'}

class ReportData:
	def __init__(self, report_date: datetime.date, form_id: str):
		self.report_date = report_date
		self.form_id = form_id
		self.company_cik = None
		self.group_name = None
		self.holdings = {str, int}