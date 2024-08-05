import pandas as pd

def add_row_from_json(dataframe: pd.DataFrame, json_data: dict) -> pd.DataFrame:
    """
    Add a new row to the DataFrame from a JSON object.
    If the JSON object contains keys not in the DataFrame, add them as new columns.
    """
    # Get the current columns of the DataFrame
    current_columns = set(dataframe.columns)
    
    # Get the keys from the JSON data
    json_keys = set(json_data.keys())
    
    # Find missing keys
    missing_keys = json_keys - current_columns
    
    # Add missing columns to the DataFrame with NaN values
    for key in missing_keys:
        dataframe[key] = pd.NA
    
    # Create a new row with NaN values for missing keys
    new_row = {key: pd.NA for key in dataframe.columns}
    
    # Update the new row with values from the JSON data
    new_row.update(json_data)
    
    # Append the new row to the DataFrame using concat
    new_row_df = pd.DataFrame([new_row])
    updated_dataframe = pd.concat([dataframe, new_row_df], ignore_index=True)
    
    return updated_dataframe

def update_row_from_json(row: pd.Series, json_data: dict) -> pd.Series:
    """
    Update a specific row (as a Series) with values from a JSON object.
    If the JSON object contains keys not in the row, add them as new elements.
    """
    # Get the current index (columns) of the Series
    current_columns = set(row.index)
    
    # Get the keys from the JSON data
    json_keys = set(json_data.keys())
    
    # Find missing keys
    missing_keys = json_keys - current_columns
    
    # Add missing elements to the Series with NaN values
    for key in missing_keys:
        row[key] = pd.NA
    
    # Update the Series with values from the JSON data
    for key, value in json_data.items():
        row[key] = value
    
    return row

