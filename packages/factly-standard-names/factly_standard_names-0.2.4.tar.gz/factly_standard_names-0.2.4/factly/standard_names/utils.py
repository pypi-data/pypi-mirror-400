import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from factly.standard_names import settings

std_names_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.STANDARD_NAMES_SHEET_NAME}"
std_abbr_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.ABBREVIATIONS_SHEET_NAME}"
std_country_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.COUNTRY_SHEET_NAME}"
district_code_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.DISTRICT_CODE_SHEET_NAME}"


@retry(
    stop=stop_after_attempt(3),  # max 3 attempts
    wait=wait_exponential(multiplier=1, min=2, max=10),  # exponential backoff
    reraise=True,
)
def get_std_names(filter: str):
    """
    Get the standard names from the google sheet.
    :param filter: str
    :return: list of standard names
    """
    data = pd.read_csv(std_names_url)
    return data[filter].dropna().tolist()


@retry(
    stop=stop_after_attempt(3),  # max 3 attempts
    wait=wait_exponential(multiplier=1, min=2, max=10),  # exponential backoff
    reraise=True,
)
def get_std_abbreviations(filter: list):
    """
    Get the standard abbreviations from the google sheet.
    :param filter: list of column names
    :return: DataFrame
    """
    data = pd.read_csv(std_abbr_url)
    return data[filter].dropna()


@retry(
    stop=stop_after_attempt(3),  # max 3 attempts
    wait=wait_exponential(multiplier=1, min=2, max=10),  # exponential backoff
    reraise=True,
)
def get_country_data():
    """
    Get the country data from the google sheet.
    :return: DataFrame
    """
    data = pd.read_csv(std_country_url)[["country_name", "standard_country_name"]]
    return data.dropna(how="all")


def get_district_code_data():
    """
    Get the district code data from the google sheet.
    :return: DataFrame
    """
    data = pd.read_csv(district_code_url)
    return data.dropna(how="all")
