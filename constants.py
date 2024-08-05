from ast import pattern
from asyncio import format_helpers
import datetime
from numpy import positive
from typing_extensions import Annotated
from pydantic import BaseModel, FieldSerializationInfo, StringConstraints, Field, ValidationError, conint

JSON_SAVE_DIR = "./json_data"
XML_SAVE_DIR = "./xml_forms_13f"
XML_SAVE_DIR_G = "./xml_forms_13g"
XML_SAVE_DIR_D = "./xml_forms_13d"
XML_SAVE_DIR_4 = "./xml_forms_4"
XML_SAVE_DIR_5 = "./xml_forms_5"
CIK_FILE = "./CIK_LIST_FULL.txt"

REFRESH_MIN_TIME_H = 72
COMPANIES = ['VANGUARD', 'BLACKROCK']
API_HEADER = {'User-Agent' : 'GXY - Goldenberg WM - samgold0205@gmail.com'}

class ReportInfo(BaseModel):
    report_date : datetime.date
    form_id : Annotated[str, StringConstraints(pattern=r'^[0-9]{20}$')]
    form_header_path : Annotated[str, StringConstraints(pattern=r'[0-9]*(\-header.xml)$')]
    form_content_path : Annotated[str, StringConstraints(pattern=r'[0-9]*(\.xml)$')]
    group_name : Annotated[str, StringConstraints(to_upper=True)]
    cik : Annotated[int, Field(pattern=r'[0-9]{11}')]

class HoldingRef(BaseModel):
    cusip : Annotated[str, StringConstraints(pattern=r'^[A-Z0-9]{10}$')]
    ticker : Annotated[str, StringConstraints(to_upper=True)]
    shares_nb : Annotated[int, Field(gt=0)]
    holding_value : Annotated[int, Field(gt=0)]

class ReportData:
    def __init__(self, report_date: datetime.date, form_id: str, form_content_path: str, cik: str, group_name="UNLINKED"):
        try:
            info = ReportInfo(
                report_date=report_date,
                form_id=form_id,
                form_content_path=form_content_path,
                form_header_path=f'{form_content_path}-header.xml',
                group_name=group_name,
                cik=int(cik))
        except ValidationError as ve:
            print(ve)
        
        self.report_date = info.report_date
        self.form_id = info.form_id
        self.company_cik = info.cik
        self.group_name = info.group_name
        self.holdings = {}

    def add_holding(self, cusip: str, ticker: str, shares_nb: str, holding_value: str):
        try:
            holding = HoldingRef(
                cusip=cusip,
                ticker=ticker,
                shares_nb=int(shares_nb),
                holding_value=int(holding_value)
            )
        except ValidationError as ve:
            print(ve)

        self.holdings[f'{holding.cusip}:{holding.ticker}'] = (holding.shares_nb, holding.holding_value)
