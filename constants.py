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
TICKERS_FILE = "./FTD_LIST_UNIQUE"

REFRESH_MIN_TIME_H = 72
COMPANIES = ['VANGUARD', 'BLACKROCK', 'MAN GROUP']
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
        """Crée un objet ReportData associé à un formulaire pour l'enregistrement et le traitement des parts détenues par l'auteur du document.

        Args:
            report_date (datetime.date): date de remplissage du formulaire
            form_id (str): id unique du formulaire (recommandation: nom du fichier sans l'extension)
            form_content_path (str): chemin vers le fichier de contenu, l'en-tête est cherchée dans le même dossier 
            cik (str): CIK de l'auteur du rapport
            group_name (str, optional): groupe d'entreprise auquel appartient le rapport, "UNLINKED" par défaut

        Returns:
            Pydantic ValidationError | None : Ne renvoie rien si la validation par la classe ReportInfo est OK.  
        """
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
            return (ve)
        
        self.report_date = info.report_date
        self.form_id = info.form_id
        self.company_cik = info.cik
        self.group_name = info.group_name
        self.holdings = {}

    def add_holding(self, cusip: str, ticker: str, shares_nb: str, holding_value: str):
        """Ajoute une entrée au dictionnaire des parts détenues rapportées dans le formulaire.

        Args:
            cusip (str): CUSIP de l'action
            ticker (str): Ticker de l'action
            shares_nb (str): Nombre de parts tenues
            holding_value (str): Valeur totale des parts

        Returns:
            Pydantic ValidationError | None : Ne renvoie rien si la validation par la classe HoldingRef est OK. 
        """
        try:
            holding = HoldingRef(
                cusip=cusip,
                ticker=ticker,
                shares_nb=int(shares_nb),
                holding_value=int(holding_value)
            )
        except ValidationError as ve:
            print(ve)
            return (ve)

        self.holdings[f'{holding.cusip}:{holding.ticker}'] = (holding.shares_nb, holding.holding_value)
