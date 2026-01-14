import json
from typing import Dict, List

import pandas as pd
from fuzzywuzzy import fuzz, process

from .airline import airline_names
from .banks import bank_names
from .cities import airline_city_names
from .country import standardise_country_names
from .crops import crop_names
from .district import standardise_district_names
from .states import state_std_names


def standardise_entire_data(
    dfObj, thresh=70, manual_changes: Dict[str, Dict[str, str]] = {}, identifier="None"
):
    """
    standardise all names from a given dataframe
    dfObj : DataFrame object on which names should be standardize
    manual_changes : Dict[str, Dict[str, str]] , default : null dict , changes in names done manually.
    """
    if "country" in dfObj.columns:
        manual_countries = manual_changes.get("country", {})
        dfObj = standardise_country_names(
            dfObj, "country", thresh, manual_countries, identifier
        )

    if "airline" in dfObj.columns:
        manual_airlines = manual_changes.get("airline", {})
        dfObj = airline_names(dfObj, "airline", thresh, manual_airlines, identifier)

    if "airline_city" in dfObj.columns:
        manual_airline_cities = manual_changes.get("airline_city", {})
        dfObj = airline_city_names(
            dfObj, "airline_city", thresh, manual_airline_cities, identifier
        )

    if "bank" in dfObj.columns:
        manual_banks = manual_changes.get("bank", {})
        dfObj = bank_names(dfObj, "bank", thresh, manual_banks, identifier)

    if "crop" in dfObj.columns:
        manual_crops = manual_changes.get("crop", {})
        dfObj = crop_names(dfObj, "crop", thresh, manual_crops, identifier)

    if "state" in dfObj.columns:
        manual_states = manual_changes.get("state", {})
        dfObj = state_std_names(dfObj, "state", thresh, manual_states, identifier)

    if "state" in dfObj.columns and "district" in dfObj.columns:
        manual_districts = manual_changes.get("district", {})
        dfObj = standardise_district_names(
            dfObj, "state", "district", thresh, manual_districts, identifier
        )
    return dfObj


def standardise_with_manual_values(
    dfObj: pd.DataFrame,
    std_names: List[str],
    improper_names: List[str],
    col_name: str,
    thresh=70,
    identifier="None",
):
    """
    standardise names from a given dataframe
    dfObj : DataFrame object on which names should be standardize
    std_names : List of standard names
    improper_names : List of improper names
    col_name : name of column which has entries as names
    identifier : identifier for the log file
    """
    std_names = list(set(std_names))
    improper_names = list(set(improper_names))

    # Dictionaries will have key value pair as improper and proper name
    logs = {}
    changes = {}
    corrupt = {}
    # will probably create filters for ratio
    for query in improper_names:
        match = process.extract(query.strip(), std_names, scorer=fuzz.token_set_ratio)
        if match[0][1] >= thresh and match[0][1] >= match[1][1] + 2:
            changes[query] = match[0][0]
        else:
            corrupt[query] = ""

    # Provide the corrupt_names.json at the same folder where script is
    if bool(corrupt):
        print(
            "There are improper names that function can't fix.\nPlease refer to logs.json."
        )

    logs.update({identifier: {"changes": changes, "corrupt": corrupt}})

    with open("standard_names.log", "a+") as log_file:
        log_file.write(json.dumps(logs) + "\n")

    # replacing values that needs to be changes only to specific column
    dfObj = dfObj.replace({col_name: changes})

    return dfObj
