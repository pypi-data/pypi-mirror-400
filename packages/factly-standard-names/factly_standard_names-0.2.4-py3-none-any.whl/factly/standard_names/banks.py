import json

from fuzzywuzzy import fuzz, process

from .utils import get_std_names


def bank_names(dfObj, column_name, thresh=70, manual_changes={}, identifier="None"):
    """
    Standardizes bank names in a given DataFrame.

    Args:
        dfObj (pd.DataFrame): The DataFrame containing bank names.
        column_name (str): The name of the column containing bank names.
        thresh (int): Matching threshold for fuzzy matching.
        manual_changes (dict): Manual replacements for specific names.
        identifier (str): Identifier for logging purposes.

    Returns:
        pd.DataFrame: DataFrame with standardized bank names.
    """

    proper_names = get_std_names(filter="bank")  # Get standard bank names
    proper_names = [name.strip() for name in proper_names]

    # Ensure we only process unique, non-null values
    improper_names = dfObj[column_name].dropna().unique().tolist()

    logs = {}
    changes = {}
    corrupt = {}

    for query in improper_names:
        match = process.extractOne(
            query.strip(), proper_names, scorer=fuzz.token_set_ratio
        )

        if match and match[1] >= thresh:
            changes[query] = match[0]  # Replace with best match
        else:
            changes[query] = ""

    # Ensure manual changes take precedence
    changes.update(manual_changes)

    # Log corrupt entries if needed
    if corrupt:
        print(
            "There are improper names that function can't fix. Please refer to logs.json."
        )

    logs[identifier] = {"changes": changes, "corrupt": corrupt}

    with open("standard_names.log", "a+") as log_file:
        log_file.write(json.dumps(logs) + "\n")

    # Apply replacements
    dfObj[column_name] = dfObj[column_name].replace(changes)

    return dfObj
