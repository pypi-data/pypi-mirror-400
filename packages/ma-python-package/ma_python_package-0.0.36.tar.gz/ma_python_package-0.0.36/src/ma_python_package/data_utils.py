# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 12:14:29 2024

@author: MejdiTRABELSI
"""

from dateutil.parser import parse
import datetime
import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import random


def is_date(string):
    """
    Return whether the string can be interpreted as a date.

    Parameters:
        string (str): string to check for date
    """

    try:
        if type(string) is not str:
            return False
        parse(string, fuzzy=False)
        return True

    except ValueError:
        return False


def filter_date_only(serie):
    """

    """
    filter_dates_only = serie[serie.apply(
        lambda x: isinstance(x, datetime.datetime) or is_date(x))]

    filter_dates_only = pd.Series(filter_dates_only.unique())

    if np.issubdtype(filter_dates_only.dtype, np.object_):
        try:
            filter_dates_only = pd.to_datetime(filter_dates_only)
        except:
            pass

    filter_dates_only = filter_dates_only.sort_values()

    return filter_dates_only


def get_date_columns(df):
    """
    Description
        Automatically determine the date column(s) in the DataFrame.

        The function analyzes the DataFrame columns and attempts to identify the column(s)
        containing date or datetime information. It returns either the name of the single
        date column as a string or a list of column names if multiple date columns are found.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be analyzed.

    Returns:
        Union[str, List[str]]: The name of the date column as a string if only one
        date column is found. If multiple date columns are detected, it returns a
        list of strings containing the names of all identified date columns.

    Raises:
        ValueError: If no date columns are found in the DataFrame.

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     'Date': ['2023-07-01', '2023-07-02', '2023-07-03'],
        ...     'Temperature': [30, 32, 31],
        ...     'Humidity': [60, 65, 70],
        ... }
        >>> df = pd.DataFrame(data)
        >>> get_date_columns(df)
        'Date'

        >>> data = {
        ...     'Start_Date': ['2023-07-01', '2023-07-02', '2023-07-03'],
        ...     'End_Date': ['2023-07-05', '2023-07-06', '2023-07-07'],
        ... }
        >>> df = pd.DataFrame(data)
        >>> get_date_columns(df)
        ['Start_Date', 'End_Date']
    """

    # Result list
    date_columns = []

    NUMBER_OF_ROWS = df.shape[0]

    NUMBER_ROW_TO_CHECK = min(1000, NUMBER_OF_ROWS)

    for column in df.columns:
        if np.issubdtype(df[column].dtype, np.datetime64):
            date_columns.append(column)
            continue
        elif np.issubdtype(df[column].dtype, np.object_):
            counter = 0
            index_range = np.random.choice(
                list(df.index), NUMBER_ROW_TO_CHECK, replace=False)
            for index in index_range:
                value = df[column][index]
                try:
                    pd.to_datetime(value)
                    counter += 1
                except:
                    continue

            if counter >= int(NUMBER_ROW_TO_CHECK * 0.50):
                date_columns.append(column)

    if len(date_columns) == 0:
        raise ValueError("No date columns found in the DataFrame.")
    else:
        return date_columns


def get_periodicity(df, *columns):
    """
    Description
        Determine the periodicity of the given DataFrame or specified columns.

        The function analyzes the DataFrame or specified columns and attempts to identify
        the data's periodicity, such as daily ('D'), weekly on Monday ('W-MON') or Saturday ('W-SAT'),
        or monthly ('M'). The function calculates the time interval between consecutive
        data points in the specified columns and returns the most likely periodicity based
        on the time differences.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be analyzed.
        *columns (str, optional): Names of the columns to consider when determining the periodicity.
                                If not provided, the entire DataFrame will be analyzed.

    Returns:
        dict: The periodicity identified in the DataFrame or specified columns.
            The returned value will be one of the following strings: 'D', 'W-MON',..., 'W-SAT', or 'M'.

    Raises:
        ValueError: If the specified column(s) do not exist in the DataFrame.

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     'Date': ['2023-07-01', '2023-07-02', '2023-07-03'],
        ...     'Temperature': [30, 32, 31],
        ... }
        >>> df = pd.DataFrame(data)
        >>> get_periodicity(df, 'Date')
        {'Date': 'D'}

        >>> data = {
        ...     'Date': ['2023-07-01', '2023-07-08', '2023-07-15'],
        ...     'Temperature': [30, 32, 31],
        ... }
        >>> df = pd.DataFrame(data)
        >>> get_periodicity(df, 'Date')
        {'Date': 'W-SAT'}
    """

    if columns:
        for col in columns:
            if col not in df.columns:
                raise ValueError(
                    "The specified column(s) do not exist in the DataFrame.")
    else:
        columns = get_date_columns(df)

    periodicity = {}  # Result variable

    for col in columns:
        col_serie = df[col]

        filter_dates_only = filter_date_only(col_serie)

        if filter_dates_only.size < 1000:
            range_slice = int(filter_dates_only.size / 3)
        else:
            range_slice = 333

        periodicity_paterns = []
        start = 0
        len_to_check = 3
        for index in range(range_slice):
            try:
                periodicity_paterns.append(pd.infer_freq(
                    filter_dates_only[start:start + len_to_check]))
            except:
                pass
            start += len_to_check

        if len(periodicity_paterns) > 0:
            periodicity[col] = max(
                set(periodicity_paterns), key=periodicity_paterns.count)
        else:
            periodicity[col] = 'D'

    return periodicity


def get_categorical_cols(df):
    return [col for col in df.columns if is_string_dtype(df[col])]


def get_numerical_columns(df):
    return [col for col in df.columns if is_numeric_dtype(df[col])]


def data_anonymization(df, replace_dict, numerical_cols=None, columns_to_remove=None):
    """
    Anonymize and transform a DataFrame for privacy preservation.

    This function performs data anonymization on a DataFrame by replacing values in specified categorical columns
    with predefined replacements, and applying linear transformations to numerical columns. Optionally, specified
    columns can be removed from the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame to be anonymized.
        replace_dict (dict): A dictionary where keys are substrings to search for in column names and values
            are the replacements for matching columns.
        numerical_cols (dict, optional): A dictionary where keys are numerical column names, and values are tuples
            (a, b) for linear transformation of the form: new_value = a * old_value + b. Default is None.
        columns_to_remove (list, optional): A list of column names to remove from the DataFrame. Default is None.

    Returns:
        pandas.DataFrame: The anonymized DataFrame.

    Notes:
        - For categorical columns, this function performs case-insensitive replacement using regular expressions.
        - If numerical_cols is not provided, random linear transformations are applied to numerical columns.
          You can specify a linear transformation for numerical columns using numerical_cols.
    """

    new_df = df.copy(True)
    if columns_to_remove is not None:
        new_df.drop(columns=columns_to_remove, inplace=True)

    if numerical_cols is None:
        numerical_cols = {}

    for key, val in replace_dict.items():
        for col in new_df.columns:
            if key.upper() in col.upper():
                new_df.rename(columns={col: col.upper().replace(
                    key.upper(), val)}, inplace=True)
                col = col.upper().replace(key.upper(), val)
            try:
                new_df[col] = new_df[col].str.replace(
                    key, val, case=False, regex=True)
            except:
                pass

    for col in [col for col in new_df.columns if is_numeric_dtype(new_df[col])]:
        if col in numerical_cols.keys():
            a = numerical_cols[col][0]
            b = numerical_cols[col][1]
            new_df[col] = a * new_df[col] + b
        else:
            minimum = new_df[col].min()
            maximum = new_df[col].max()
            mean = new_df[col].mean()
            delta = (maximum - minimum) / mean
            delta = int(delta)
            a = 1 + random.uniform(-0.2, 0.2)
            b = random.randrange(-delta, delta)
            new_df[col] = new_df[col].apply(
                lambda x: min(max(a * x + b, minimum), maximum))

    return new_df
