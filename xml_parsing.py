import constants

def get_ticker_from_cusip(cusip: str, tickers_file_fd=open(constants.TICKERS_FILE, "r")):
    """Tente de récupérer un ticker associé à un CUSIP en comparant avec un fichier contenant les Fail-To-Deliver des actions, formaté en suivant le format de la SEC sans l'horodatage.

    Args:
        cusip (str): CUSIP de l'action recherchée
        tickers_file_fd (TextIOWrapper, optional): Objet TextIOWrapper obtenu après l'ouverture avec open(/path/to/file, "r"). Par défaut : open(constants.TICKERS_FILE, "r").

    Returns:
        str | None: Renvoie le ticker si il a été trouvé, sinon None.
    """
    ticker_lines = tickers_file_fd.readlines()
    for line in ticker_lines:
        if (cusip in line):
            return (line.split('|')[1])
    return (None)


# def parse_13f_header