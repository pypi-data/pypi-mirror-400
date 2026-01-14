# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 10:05:00 2024

@author: MejdiTRABELSI
"""


import pandas as pd
import numpy as np
import tqdm
import os
import datetime
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from .data_processing import read_data
from .data_utils import get_date_columns, get_periodicity, is_date


def data_summary(path):
    """
    Description:
        Generate a summary of each CSV, XLS, or XLSX file in the specified path.

    Parameters:
        path (str): The directory path containing CSV, XLS, or XLSX files.

    Returns:
        pandas.DataFrame: A data frame with the following columns:
            - 'file_name': The name of the file (including the extension).
            - 'nb_rows': The number of rows in the file.
            - 'nb_columns': The number of columns in the file.
            - 'prop_null%': The proportion of null values in the file.

    Note:
        - Supported file formats: CSV, XLS, and XLSX.
        - The function will skip files with unsupported formats.
        - The 'prop_null' column represents the proportion of missing (null) values
          in the data, calculated as the number of missing values divided by the total
          number of elements in the file.

    Example:
        >>> path = '/path/to/files/'
        >>> summary_df = data_summary(path)
        >>> print(summary_df)
            file_name  nb_rows  nb_columns  prop_null%
        0  data_file.csv      100           5   0.023400
        1  data_file.xlsx      80           6   0.041250
        2  data_sheet.xls      50           4   0.005000
    """

    if os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            break
    else:
        filenames = [os.path.basename(path).split('/')[-1]]

    new_df = {'file_name': [],
              'nb_rows': [],
              'nb_columns': [],
              'prop_null%': []
              }

    for file in tqdm.tqdm(filenames):
        try:
            df = read_data(path + '/' + file)
        except Exception as e:
            print(e, file)
            continue

        new_df['file_name'].append(file)
        new_df['nb_rows'].append(df.shape[0])
        new_df['nb_columns'].append(df.shape[1])
        new_df['prop_null%'].append(("{:.2f}".format(
            ((1 - (df.count().agg("sum") / (new_df['nb_rows'][-1] * new_df['nb_columns'][-1])))) * 100)))

    return pd.DataFrame(new_df)


def categorical_summary(path):
    """
    Description
        Generate a summary of categorical columns in CSV, XLS, or XLSX files located in the given path.

    Parameters:
        path (str): The path to the directory containing CSV, XLS, or XLSX files.

    Returns:
        pandas.DataFrame: A DataFrame with columns 'file_name', 'categorical_columns', 'nunique' and 'prop_null%'.
                          Each row represents a file in the path and provides information about the
                          number of unique values in each categorical column found in that file.

    Example:
        >>> path = '/path/to/files/'
        >>> summary_df = categorical_summary(path)
        >>> print(summary_df)

            file_name        categorical_column  nunique  prop_null%
        0  data_file.csv        Category           10      0.020000
        1  data_file.csv        Gender             2       0.000000
        2  data_file.xlsx       Location           20      0.002500
        3  data_sheet.xls       Department         8       0.000000
        4  data_sheet.xls       City               15      0.010000
    """

    if os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            break
    else:
        filenames = [os.path.basename(path).split('/')[-1]]

    new_df = {'file_name': [],
              'categorical_columns': [],
              'nunique': [],
              'prop_null%': []
              }

    for file in tqdm.tqdm(filenames):
        try:
            df = read_data(path + '/' + file)
        except Exception as e:
            print(e, file)
            continue

        columns = []
        date_cols = get_date_columns(df)
        for col in df.columns:
            serie = df[col].dropna()
            get_date_columns
            if is_string_dtype(serie) and col not in date_cols:
                columns.append(col)

        if len(columns) == 0:
            print('No categorical columns found in the DataFrame', file)
            continue

        for col in columns:
            new_df['file_name'].append(file)
            new_df['categorical_columns'].append(col)
            new_df['nunique'].append(len(df[col].unique()))
            new_df['prop_null%'].append(
                ("{:.2f}".format(((1 - (df[col].count() / (df.shape[0])))) * 100)))

    return pd.DataFrame(new_df)


def numerical_summary(path):
    """
    Description
        Generate a summary of numerical columns in CSV, XLS, or XLSX files located in the given path.

    Parameters:
        path (str): The path to the directory containing CSV, XLS, or XLSX files.

    Returns:
        pandas.DataFrame: A DataFrame with columns 'file_name', 'num_column', 'mean', 'std', 'min', '25%',
                          '50%', '75%' and 'max'.
                          Each row represents a file in the path and provides information about the
                          minimum and maximum values for each numerical column found in that file.

    Example:
        >>> path = '/path/to/files/'
        >>> summary_df = numerical_summary(path)
        >>> print(summary_df)

            file_name       num_column   mean    std   min   25%   50%   75%   max
        0  data_file.csv      Column1    10.50   5.00    5  7.25  10.5  13.75   16
        1  data_file.csv      Column2    25.00   7.00   15  20.0  25.0  30.00   35
        2  data_file.xlsx     Column1    18.75   2.50   16  17.5  18.5  19.75   22
        3  data_sheet.xls     Column3    42.00  10.00   30  35.0  42.0  49.00   55
    """

    if os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            break
    else:
        filenames = [os.path.basename(path).split('/')[-1]]

    new_df = {'file_name': [],
              'num_column': [],
              'mean': [],
              'std': [],
              'min': [],
              '25%': [],
              '50%': [],
              '75%': [],
              'max': [],
              }

    for file in tqdm.tqdm(filenames):
        try:
            df = read_data(path + '/' + file)
            describe = df.describe()
        except Exception as e:
            print(e, file)
            continue

        columns = []
        for col in df.columns:
            filter_values = df[col].dropna()
            if is_numeric_dtype(filter_values) and len(filter_values) > 0:
                columns.append(col)

        if len(columns) == 0:
            print('No numerical columns found in the DataFrame', file)
            continue

        for col in columns:
            new_df['file_name'].append(file)
            new_df['num_column'].append(col)
            new_df['mean'].append(describe[col]['mean'])
            new_df['std'].append(describe[col]['std'])
            new_df['min'].append(describe[col]['min'])
            new_df['25%'].append(describe[col]['25%'])
            new_df['50%'].append(describe[col]['50%'])
            new_df['75%'].append(describe[col]['75%'])
            new_df['max'].append(describe[col]['max'])

    return pd.DataFrame(new_df)


def describe_categories(df, subset=None):
    """
    Generate a summary DataFrame containing the counts of unique categories for each categorical column in the input DataFrame.

    Parameters:
        df (pandas.DataFrame): The input DataFrame to be analyzed.
        subset (list or None, optional): A list of column names specifying a subset of columns to consider.
            If None, all columns in the DataFrame will be considered. Default is None.

    Raises:
        KeyError: If a column in the `subset` parameter doesn't exist in the DataFrame columns.
        ValueError: If a column specified in the `subset` is not a categorical column.

    Returns:
        pandas.DataFrame: A DataFrame with columns 'categorical_columns', 'values', and 'count'.
            - 'categorical_columns': The names of the categorical columns in the DataFrame.
            - 'values': The unique categories present in each categorical column.
            - 'count': The count of occurrences for each unique category in the corresponding column.

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     'Category1': ['A', 'A', 'B', 'C', 'B'],
        ...     'Category2': ['X', 'Y', 'X', 'X', 'Z'],
        ...     'Numerical': [10, 20, 30, 40, 50]
        ... }
        >>> df = pd.DataFrame(data)
        >>> result = describe_categories(df)
        >>> print(result)
             categorical_columns values  count
        0           Category1      A      2
        1           Category1      B      2
        2           Category1      C      1
        3           Category2      X      3
        4           Category2      Y      1
        5           Category2      Z      1
    """

    try:
        date_cols = get_date_columns(df)
    except:
        date_cols = []

    categ_columns = []
    for col in df.columns:
        serie = df[col]
        if np.issubdtype(df[col].dtype, np.object_):
            serie = serie[serie.apply(lambda x: isinstance(x, str))]
            serie = serie.apply(lambda x: x.strip(" %$").replace(
                '.', '').replace(',', '')).dropna()
            if serie.astype(str).str.isnumeric().any() == False and col not in date_cols:
                categ_columns.append(col)

    if subset is not None:
        columns = df.columns
        for col in subset:
            if col not in columns:
                raise KeyError(
                    col + " doesn\'t exist in the DataFrame columns.")
            if col not in categ_columns:
                raise ValueError(col + " is not a categorical column")
    else:
        subset = categ_columns

    new_df = {'categorical_columns': [],
              'values': [],
              'count': []
              }

    for col in subset:
        serie = df[col].value_counts(sort=False, dropna=False)
        new_df['values'] = new_df['values'] + list(serie.index)
        new_df['count'] = new_df['count'] + list(serie.values)
        new_df['categorical_columns'] = new_df['categorical_columns'] + \
            [col for count in range(serie.size)]

    return pd.DataFrame(new_df)


def date_summary(path):
    """
    Description
        Generate a data frame summarizing the date-related information for each CSV, XLS, or XLSX file in the given path.

        Parameters:
        path (str): The directory path containing CSV, XLS, or XLSX files.

    Returns:
    pandas.DataFrame: A data frame with the following columns:
        - file_name (str): The name of the file.
        - date_columns (str): The column name that contain date-related data.
        - periodicity (str): The frequency of the date-related data (e.g., 'daily', 'monthly', 'yearly').
        - start_date : The earliest date found in the date-related columns.
        - end_date : The latest date found in the date-related columns.
        - prop_null % : The proportion of missing values (NaNs) in the date-related columns.
    Note:
       This function will only consider CSV, XLS, and XLSX files in the specified path.

    Example:
        >>> print(date_summary('.'))
          file_name date_columns periodicity  start_date    end_date  prop_null %
        0  data.csv        Date       daily  2023-07-01  2023-07-03          0.0
    """

    if os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            break
    else:
        filenames = [os.path.basename(path).split('/')[-1]]

    new_df = {'file_name': [],
              'date_columns': [],
              'periodicity': [],
              'start_date': [],
              'end_date': [],
              'prop_null%': []
              }

    for file in tqdm.tqdm(filenames):
        try:
            if os.path.isdir(path):
                df = read_data(path + '/' + file)
            else:
                df = read_data(path)
        except Exception as e:
            print(e, file)
            continue

        try:
            columns = get_date_columns(df)
        except Exception as e:
            print(e, file)
            continue

        if type(columns) is str:
            columns = [columns]

        # periodicity = get_periodicity(df)
        for col in columns:
            new_df['file_name'].append(file)
            new_df['date_columns'].append(col)
            new_df['periodicity'].append(get_periodicity(df, col)[col])
            col_serie = df[col]

            if np.issubdtype(df[col].dtype, np.object_):
                col_serie = col_serie[col_serie.apply(
                    lambda x: isinstance(x, datetime.datetime) or is_date(x))]
                # col_serie = col_serie.astype('datetime64[ns]')
                col_serie = pd.to_datetime(
                    pd.Series(col_serie), errors='coerce')

            new_df['prop_null%'].append("{:.2f}".format(
                (1 - (col_serie.count() / df.shape[0])) * 100))
            try:
                new_df['start_date'].append(min(col_serie)._date_repr)
                new_df['end_date'].append(max(col_serie)._date_repr)
            except:
                new_df['start_date'].append('None')
                new_df['end_date'].append('None')

    return pd.DataFrame(new_df)
