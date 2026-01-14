import json
from collections import defaultdict
from typing import Dict

import pandas as pd
from factly.standard_names.states import check_state_names
from factly.standard_names.utils import get_district_code_data
from fuzzywuzzy import fuzz, process


def standardise_district_names(
    dfObj,
    state_col,
    district_col,
    thresh=70,
    manual_changes: Dict[str, Dict[str, str]] = {},
    identifier="district_names",
    exceptions_state_names=[],
):
    """
    Standardizes district names in a DataFrame by matching them with standardized names.

    Args:
        dfObj (pd.DataFrame): Input DataFrame containing district names to be standardized
        state_col (str): Name of the column containing state names
        district_col (str): Name of the column containing district names
        thresh (int, optional): Threshold for fuzzy matching score (0-100). Defaults to 70.
        manual_changes (Dict[str, Dict[str, str]], optional): Dictionary of manual overrides for district names.
                                                             Format: {"State": {"old_district_name": "new_district_name"}}
        identifier (str, optional): Identifier for logging purposes. Defaults to "district_names".
        exceptions_state_names (list, optional): List of state names to be excluded from standardization. Defaults to [].

    Returns:
        pd.DataFrame: DataFrame with standardized district names and additional columns
    """

    # check if district column contains null values
    if dfObj[district_col].isnull().any():
        print("***District names not standardised***")
        print("District column contains null values")
    # Load standardized district code data
    std_data = get_district_code_data()

    # Verify state names before proceeding with district standardization
    if not check_state_names(dfObj, std_data, state_col, exceptions_state_names):
        return dfObj

    # Rename the district column to standard name for consistency
    dfObj.rename(columns={district_col: "district_as_per_source"}, inplace=True)

    # Initialize dictionaries to track changes and issues:
    # - logs: Stores all logging information
    # - changes: Tracks successful district name changes
    # - corrupt: Tracks district names that couldn't be standardized
    logs = defaultdict(dict)
    changes = defaultdict(dict)
    corrupt = defaultdict(dict)

    # Get unique state names from the input data
    unique_state_names = dfObj["state"].unique().tolist()

    # Process each state's districts separately
    for state_name in unique_state_names:
        # Get list of standardized district names for the current state
        std_districts = (
            std_data[std_data["state"] == state_name]["district_as_per_source"]
            .unique()
            .tolist()
        )

        # Get list of district names from input data that need standardization
        improper_districts = (
            dfObj[
                (dfObj["state"] == state_name)
                & (dfObj["district_as_per_source"].notna())
            ]["district_as_per_source"]
            .unique()
            .tolist()
        )
        # Process each district name in the current state
        for district in improper_districts:
            district = district.strip()

            # Check for manual overrides first
            if district in manual_changes.get(state_name, {}).keys():
                changes[state_name][district] = manual_changes[state_name][district]
                continue

            # Use fuzzy string matching to find the closest match from standardized names
            # fuzz.token_set_ratio is used for better handling of partial string matches
            match = process.extract(
                district, std_districts, scorer=fuzz.token_set_ratio
            )
            if len(match) == 1 and match[0][1] >= thresh:
                changes[state_name][district] = match[0][0]
            elif match[0][1] >= thresh and (match[0][1] > match[1][1] + 1):
                changes[state_name][district] = match[0][0]
            else:
                corrupt[state_name][district] = ""

    if bool(corrupt):
        print(
            "There are improper district names that function can't fix.\nPlease refer to standard_names.log."
        )

    # Update logs with changes and corrupt entries
    logs.update({identifier: {"changes": changes, "corrupt": corrupt}})

    # Write logs to file
    with open("standard_names.log", "a+") as log_file:
        log_file.write(json.dumps(logs) + "\n")

    # Apply the standardized district names to the DataFrame by adding district_as_per_lgd column
    for state_name, district_changes in changes.items():
        # Create/update district_as_per_lgd column with standardized names
        dfObj.loc[dfObj["state"] == state_name, "district_as_per_source"] = dfObj.loc[
            dfObj["state"] == state_name, "district_as_per_source"
        ].replace(district_changes)

    if "district_as_per_lgd" in dfObj.columns:
        dfObj.drop(columns="district_as_per_lgd", inplace=True)
    if "district_lgd_code" in dfObj.columns:
        dfObj.drop(columns="district_lgd_code", inplace=True)

    dfObj = dfObj.merge(
        std_data[
            [
                "state",
                "district_as_per_source",
                "district_as_per_lgd",
                "district_lgd_code",
            ]
        ],
        on=["state", "district_as_per_source"],
        how="left",
    )
    dfObj["district_lgd_code"] = dfObj["district_lgd_code"].astype("Int64")
    district_col_loc = dfObj.columns.get_loc("district_as_per_source")
    district_as_per_lgd = dfObj.pop("district_as_per_lgd")
    dfObj.insert(district_col_loc + 1, "district_as_per_lgd", district_as_per_lgd)
    district_lgd_code = dfObj.pop("district_lgd_code")
    dfObj.insert(district_col_loc + 2, "district_lgd_code", district_lgd_code)

    if dfObj["district_lgd_code"].isnull().any():
        # Group districts by state
        district_with_no_code = (
            dfObj.loc[dfObj["district_lgd_code"].isnull()]
            .groupby("state")["district_as_per_source"]
            .apply(lambda x: x.unique().tolist())
            .to_dict()
        )
        print("LGD codes not found for districts")
        logs = {
            identifier: {
                "district_with_no_code in district_as_per_source": district_with_no_code
            }
        }
        with open("standard_names.log", "a+") as f:
            f.write(json.dumps(logs) + "\n")

    # Handle notes/description updates
    # Check which column name is being used for notes
    if "note" in dfObj.columns:
        note_var = "note"
    elif "notes" in dfObj.columns:
        note_var = "notes"
    dfObj[note_var] = dfObj[note_var].astype("object")

    # Build MultiIndex notes lookup once
    notes_map = std_data.set_index(["state", "district_as_per_source"])["notes"]

    if notes_map.dropna().empty:
        return dfObj
    # Build a MultiIndex key for dfObj rows
    df_index = dfObj.set_index(["state", "district_as_per_source"]).index
    mapped_notes = pd.Series(df_index.map(notes_map), index=dfObj.index)

    null_mask = dfObj[note_var].isna()
    dfObj.loc[null_mask, note_var] = mapped_notes[null_mask]
    append_mask = ~null_mask & mapped_notes.notna()
    dfObj.loc[append_mask, note_var] = (
        dfObj.loc[append_mask, note_var].astype(str) + ", " + mapped_notes[append_mask]
    )

    return dfObj
