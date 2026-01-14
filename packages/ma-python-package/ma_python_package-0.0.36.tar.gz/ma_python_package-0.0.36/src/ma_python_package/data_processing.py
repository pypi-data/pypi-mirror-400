import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import os
from tqdm import tqdm
import inspect
import warnings
from .data_utils import (get_date_columns,
                         is_date,
                         get_periodicity,
                         get_numerical_columns,
                         get_categorical_cols)
from pandas.api.types import is_string_dtype


def read_data(input_path, header=0, sheet_name=0):
    """
    Reads data from files or a folder and returns a merged DataFrame.

    Parameters:
    input_path (str): Path to a file or a folder containing files to read.
    header (int or list of int, optional): Row(s) to use as the column names.
        Defaults to None.
    sheet_name (str, int, list, or None, optional): Name or index of sheet(s)
    to read from an Excel file. Defaults to None.

    Returns:
    pandas.DataFrame: Merged DataFrame if input_path is a folder containing
    files or a DataFrame if input_path is a single file.

    Raises:
    ValueError: If input_path is not a valid file or folder path,
        or if files in the folder have different structures.
    Example:
    ```python
    # Read a single CSV file
    df = read_data('path_to_file/filename.csv', header=0)
    # Read all files in a folder
    df = read_data('path_to_folder/', header=0)
    ```

    """
    # Function to read a single file
    def read_single_file(file_path):
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.csv':
            return pd.read_csv(file_path, header=header)
        elif ext.lower() == '.xlsx' or ext.lower() == '.xls':
            return pd.read_excel(file_path,
                                 sheet_name=sheet_name,
                                 header=header)
        elif ext.lower() == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError("Unsupported file format: {}".format(ext))

    # Check if input_path is a folder
    if os.path.isdir(str(input_path)):
        # List all files in the directory
        files = os.listdir(input_path)
        # Initialize an empty list to hold dataframes
        dfs = []
        # Iterate over each file
        for file in files:
            file_path = os.path.join(input_path, file)
            # Read each file and append the dataframe to dfs list
            dfs.append(read_single_file(file_path))
        # Check if all dataframes have the same structure
        if not all(set(df.columns)==set((dfs[0].columns)) for df in dfs):
            raise ValueError("Files in folder have different structures.")
        # Concatenate all dataframes in the list into a single dataframe
        merged_df = pd.concat(dfs, ignore_index=True)
        return merged_df
    elif type(input_path) == list:
        dfs = []
        # Iterate over each file
        for file in input_path:
            # Read each file and append the dataframe to dfs list
            dfs.append(read_single_file(file_path))
        # Check if all dataframes have the same structure
        if not all(df.columns.equals(dfs[0].columns) for df in dfs):
            raise ValueError("Files in folder have different structures.")
        # Concatenate all dataframes in the list into a single dataframe
        merged_df = pd.concat(dfs, ignore_index=True)
        return merged_df
    else:
        # Read a single file
        return read_single_file(input_path)


def save_data(df, output_path, mode="overwrite", subset=None):
    """
    Save a pandas DataFrame to a specified output file path.

    Parameters:
    - df (pandas.DataFrame): The DataFrame to be saved.
    - output_path (str): The path to save the DataFrame. If a folder path is provided, the output file
                         will be derived from the script or function name and saved as an Excel file in
                         that folder. If a file path is provided, the extension will determine the format
                         (CSV, Excel, or Parquet).
    - mode (str, optional): The mode for saving data. Options are 'overwrite' (default), 'append-new',
                            and 'append-old'. 'overwrite' replaces existing file if exists. 'append-new'
                            appends new data keeping the latest duplicates. 'append-old' appends new data
                            keeping the first duplicates.
    - subset (list[str], optional): Columns used to identify duplicates when appending data. Only applicable
                                     when mode is 'append-new' or 'append-old'.

    Raises:
    - ValueError: If an invalid mode is provided, or if the output file extension is not supported,
                  or if the existing file and new data have different column structures.

    Note:
    - When mode is 'append-new' or 'append-old', the function checks for duplicates based on the specified
      subset of columns and appends data accordingly.

    Example:
    >>> import pandas as pd
    >>> data = {'A': [1, 2], 'B': [3, 4]}
    >>> df = pd.DataFrame(data)
    >>> save_data(df, 'output.xlsx', mode='append-new', subset=['A'])
    """
    # Resolve output file name
    if os.path.isdir(output_path):
        # If output_path is a folder, derive file name from function or script name
        try:
            frame = inspect.stack()[1]
            filename = frame.filename
            basename = os.path.basename(filename)
            output_filename = os.path.splitext(basename)[0]
        except:
            raise ValueError(
                "Fail to get the file name, add the file name in your path")
        output_path = os.path.join(output_path, output_filename + ".xlsx")
        output_ext = ".xlsx"
    else:
        output_filename, output_ext = os.path.splitext(output_path)
        if output_ext.lower() not in ['.csv', '.xlsx', '.parquet']:
            raise ValueError(
                "Invalid output file extension. Supported formats are CSV, Excel, and Parquet.")

    # Determine write mode
    if mode == "append-new" or mode == "append-old":
        if os.path.exists(output_path):
            existing_data = read_data(output_path)
            if set(df.columns) != set(existing_data.columns):
                warnings.warn(
                    "The existing file and the new data have different column structures.", Warning)

            # check periodicity
            new_freq = get_periodicity(df)
            old_freq = get_periodicity(existing_data)
            cat_cols = get_categorical_cols(existing_data)
            if new_freq != old_freq:
                warnings.warn("""
                              The two tables have note the same periodicity,
                              We changed the periodicity of the old table.
                              All the columns are considered additive,
                              otherwise you need to change periodicity of the old data manualy
                              """, Warning)
                existing_data = change_periodicity(
                    existing_data, "Date", new_freq["Date"], categorical_cols=cat_cols)
            if mode == "append-new":
                combined_data = pd.concat([existing_data, df], join="outer").drop_duplicates(
                    subset=subset, keep='last').fillna(0)
            else:  # mode == "append-old"
                combined_data = pd.concat([existing_data, df], join="outer").drop_duplicates(
                    subset=subset, keep='first').fillna(0)
            if ("Region" in combined_data.columns) and ("Date" in combined_data.columns):
                df = combined_data.sort_values(by=["Region", "Date"])
        else:
            save_data(df, output_path, mode="overwrite")
    elif mode != "overwrite":
        raise ValueError(
            "Invalid mode. Supported modes are 'overwrite', 'append-new', and 'append-old'.")
    # Write DataFrame to file
    if output_ext.lower() == '.csv':
        df.to_csv(output_path, index=False)
    elif output_ext.lower() == '.xlsx':
        df.to_excel(output_path, index=False)
    elif output_ext.lower() == '.parquet':
        df.to_parquet(output_path, index=False)


def pivot_by_key(df, index_column_names, key_column_names, values_column_names, agg='sum'):
    """
    Description
        Pivots a DataFrame based on the given keys and performs aggregation on the specified value columns.

    Parameters:
        df (pd.DataFrame): The DataFrame to pivot and perform aggregation on.
        index_column_names (list): List of column names to be used as index during pivoting.
        key_column_names (list): List of column names to be used as keys for pivoting.
        values_column_names (list): List of column names to be used as values for pivoting.
        agg_funcs (dict, optional): Dictionary mapping columns to aggregation functions. The default is {'column_name': 'sum'}.

    Returns:
        pd.DataFrame: The resulting pivoted DataFrame with aggregation.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Date': ['1/1/2020', '1/2/2020', '1/3/2020'],
        ...                    'col1': ['A', 'B', 'C'],
        ...                    'col2': ['X', 'Y', 'Z'],
        ...                    'price': [10, 11, 15],
        ...                    'nb': [2, 1, 3]})
        >>> result = pivot_by_key(df, index_column_names='Date', key_column_names=['col1', 'col2'],
        ...                       values_column_names=['price', 'nb'], agg_funcs={'price': 'mean', 'nb': 'sum'})
        >>> print(result)

             Date          A_X_nb   B_Y_nb   C_Z_nb   A_X_price   B_Y_price   C_Z_price    
        0    1/1/2020        2        0        0        10          0           0
        1    1/2/2020        0        1        0        0           11          0
        2    1/3/2020        0        0        3        0           0           15
    """

    df['key'] = df.apply(lambda x: '_'.join([str(x[st])
                         for st in key_column_names]), axis=1)
    pivot_table = pd.pivot_table(df, values=values_column_names,
                                 index=index_column_names,
                                 columns='key',
                                 aggfunc=agg,
                                 fill_value=0)

    new_df = pd.DataFrame()
    for cols in pivot_table.columns:
        new_df['_'.join(
            cols[::-1]).strip(" .;,:*-()[]/!?").replace(" ", "_")] = pivot_table[cols]

    new_df.reset_index(inplace=True)

    return new_df


def get_mapping_table(df, date_column_name, column_values, freq='D', start_date=None, end_date=None):
    """
    Description
        Create a mapping table based on the provided DataFrame, date column, and column values.

        The function generates a new DataFrame that contains all unique combinations of the date
        values (within the specified frequency) and the unique values of each column in the 
        'column_values' list.

    Parameters:
        df (pandas.DataFrame): The original DataFrame containing the data.
        date_column_name (str): The name of the column that holds the date values.
        column_values (list): A list of column names for which unique values will be used
                              to create combinations in the mapping table.
        freq (str, optional): The frequency string for date_range(). 
                              Defaults to daily 'D'.
        start_date (str or None, optional): The start date of the mapping table.
                                            If None, the minimum date in the DataFrame's date_column_name
                                            will be used.
                                            Default is None.
        end_date (str or None, optional): The end date of the mapping table.
                                          If None, the maximum date in the DataFrame's date_column_name
                                          will be used.
                                          Default is None.

    Returns:
        pandas.DataFrame: A new DataFrame representing the mapping table with date_column_name 
                          and unique values from each column in column_values.

    Note:
        - Make sure to provide a valid 'freq' frequency string, such as 'D' for daily, 'W-SAT', 'W-MON'..
        - The returned DataFrame will have a row for each unique combination of date and column 
          values from the original DataFrame.

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     'Date': ['2023-07-01', '2023-07-02'],
        ...     'Product': ['A', 'B'],
        ...     'Category': ['X', 'Y'],
        ...     'Price': [100, 150],
        ... }
        >>> df = pd.DataFrame(data)
        >>> result = get_mapping_table(df, date_column_name='Date', column_values=['Product', 'Category'], freq='D')
        >>> print(result)
            Product Category    Date
        0      A       X        2023-07-01
        1      A       X        2023-07-02 
        2      B       X        2023-07-01
        3      B       X        2023-07-02
        4      A       Y        2023-07-01
        5      A       Y        2023-07-02
        6      B       Y        2023-07-01
        7      B       Y        2023-07-02

    """

    new_df = pd.DataFrame()

    if start_date is None:
        start_date = min(df[date_column_name])
    if end_date is None:
        end_date = max(df[date_column_name])

    new_df[date_column_name] = pd.date_range(
        start=start_date, end=end_date, freq=freq, inclusive='both')

    for col in column_values:
        new_df = pd.DataFrame(df[col].unique()).join(new_df, how='cross')
        new_df.rename(columns={0: col}, inplace=True)

    return new_df


def map_table(mapping_table, df):
    """
    Description
        The map_table function is designed to map data from the original DataFrame to the provided mapping table. 
        It performs a left merge between the mapping_table and the original DataFrame (df) based on their common date column(s). 
        The function then fills in missing values in the merged DataFrame with 0.

    Parameters:
        df (pandas.DataFrame): The original DataFrame containing the data to be mapped.
        mapping_table (pandas.DataFrame): The mapping table containing unique combinations of 
                                          data and columns to which the original data will be 
                                          mapped.

    Returns:
        pandas.DataFrame: A new DataFrame resulting from the left merge of the mapping_table and 
                          the original DataFrame (df), with missing values filled in with 0.

    Note:
        - The merge is performed based on the common columns between the mapping_table and the 
          original DataFrame. Make sure that the mapping_table and the df have at least one 
          common column.
        - Any missing values in the merged DataFrame are filled with 0.
        - The returned DataFrame will have the same number of rows as the mapping_table and will 
          include the additional columns from the original DataFrame (df) that matched the 
          common columns in the mapping_table.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Date': ['2023-08-01', '2023-08-02', '2023-08-03', '2023-08-04', '2023-08-05'],
        ...     'Value': [10, 20, 30, 40, 50]
        ... })
        >>> mapping_table = pd.DataFrame({
        ...     'Date': ['2023-08-01', '2023-08-03'],
        ...     'Label': ['Label A', 'Label B']
        ... })
        >>> result_df = map_table(df, mapping_table)
        >>> print(result_df)

            Date        Value    Label
        0 2023-08-01     10     Label A
        1 2023-08-03     30     Label B
    """

    # Cast Object type to datetime (df)
    date_cols = get_date_columns(df)

    if type(date_cols) is str:
        date_cols = [date_cols]

    for col in date_cols:
        df = df.drop(df[df.apply(lambda x: not (
            is_date(x[col]) or isinstance(x[col], datetime)), axis=1)].index)
        if np.issubdtype(df[col].dtype, np.object_):
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                print("Can\'t cast object to datetime type")

    # Cast Object type to datetime (mapping_table)
    date_cols = get_date_columns(mapping_table)
    if type(date_cols) is str:
        date_cols = [date_cols]

    for col in date_cols:
        mapping_table = mapping_table.drop(mapping_table[mapping_table.apply(lambda x: not (
            is_date(x[col]) or isinstance(x[col], datetime)), axis=1)].index)
        if np.issubdtype(mapping_table[col].dtype, np.object_):
            try:
                mapping_table[col] = pd.to_datetime(mapping_table[col])
            except:
                print("Can\'t cast object to datetime type")

    map_table = mapping_table.merge(df, how='left').fillna(0)

    return map_table


def daily_to_weekly(df, date_col, weekday, categorical_cols=None, output_starting=True, agg=None):
    """
     Convert a daily frequency DataFrame to a weekly frequency DataFrame by aggregating data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing daily data.
    date_col (str): The name of the column containing date/time values.
    weekday (str): The target weekday for the weekly aggregation (e.g., 'MON', 'TUE', ...).
    categorical_cols (List[str], optional): List of column names to be included in grouping. Defaults to None.
    output_starting (bool, optional): If True, output the weekly DataFrame with dates aligned to the starting weekday. If False, align to ending weekday. Defaults to True.
    agg (Dict[str, str], optional): Custom aggregation methods for specific numerical columns. Keys are column names and values are aggregation functions. Defaults to None.

    Returns:
    pd.DataFrame: The resulting DataFrame with weekly aggregated data based on specified parameters.
    """

    new_df = df.copy(True)
    num_cols = get_numerical_columns(df)
    if categorical_cols is None:
        categorical_cols = []
    new_df = new_df[num_cols + [date_col] + categorical_cols]

    new_df[date_col] = pd.to_datetime(new_df[date_col])

    aggregation = {col: 'sum' for col in num_cols}

    if agg is not None:
        if not isinstance(agg, dict):
            raise ValueError('agg must be a dictionary!')
        #elif not set(agg.keys()).issubset(set(aggregation.keys())):
        #    raise ValueError('Wrong keys for the agg variable')

        for key, val in agg.items():
            aggregation[key] = val

    days = {'MON': 0, 'TUE': 1, 'WED': 2,
            'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
    day = days[weekday.upper()]

    if output_starting:
        new_df[date_col] = new_df[date_col].apply(lambda x: x - pd.to_timedelta(str(x.weekday()) + ' D') + pd.to_timedelta(str(
            day) + ' D') if - x.weekday() + day <= 0 else x - pd.to_timedelta(str(x.weekday() + 7) + ' D') + pd.to_timedelta(str(day) + ' D'))
    else:
        new_df[date_col] = new_df[date_col].apply(lambda x: x - pd.to_timedelta(str(x.weekday() - 7) + ' D') + pd.to_timedelta(str(
            day) + ' D') if - x.weekday() + day < 0 else x - pd.to_timedelta(str(x.weekday()) + ' D') + pd.to_timedelta(str(day) + ' D'))

    if categorical_cols is None:
        categorical_cols = []

    return new_df.groupby(by=categorical_cols + [date_col]).agg(aggregation).reset_index()


def daily_to_monthly(df, date_col, categorical_cols=None, agg=None):
    """
    Convert a daily frequency DataFrame to a monthly frequency DataFrame by aggregating data.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing daily data.
    date_col (str): The name of the column containing date/time values.
    categorical_cols (List[str], optional): List of column names to be included in grouping. Defaults to None.
    agg (Dict[str, str], optional): Custom aggregation methods for specific numerical columns. Keys are column names and values are aggregation functions. Defaults to None.

    Returns:
    pd.DataFrame: The resulting DataFrame with monthly aggregated data based on specified parameters.
    """

    new_df = df.copy(True)
    num_cols = get_numerical_columns(df)
    if categorical_cols is None:
        categorical_cols = []
    new_df = new_df[num_cols + [date_col] + categorical_cols]

    new_df[date_col] = pd.to_datetime(new_df[date_col])

    aggregation = {col: 'sum' for col in num_cols}

    if agg is not None:
        if not isinstance(agg, dict):
            raise ValueError('agg must be a dictionary!')
        elif not set(agg.keys()).issubset(set(aggregation.keys())):
            raise ValueError('Wrong keys for the agg variable')

        for key, val in agg.items():
            aggregation[key] = val

    new_df[date_col] = new_df[date_col].dt.to_period('M').dt.to_timestamp()

    if categorical_cols is None:
        categorical_cols = []

    return new_df.groupby(by=categorical_cols + [date_col]).agg(aggregation).reset_index()


def weekly_to_daily(df, date_col, categorical_cols=None, input_starting=True, agg=None):
    """
    Expand a DataFrame with weekly data into a daily granularity DataFrame.

    This function takes a DataFrame containing weekly data and converts it into a DataFrame with daily granularity.
    It replicates numerical values for each day within the week and repeats categorical values accordingly.
    Optionally, you can perform aggregation on numerical columns within each resulting group.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing weekly data.
    - date_col (str): The name of the column representing the date in the DataFrame.
    - categorical_cols (list, optional): List of column names to be treated as categorical variables.
    - input_starting (bool, optional): If True, assume the input data represents the starting date of each week.
                                        If False, assume the input data represents the ending date of each week.
    - agg (dict, optional): Dictionary specifying aggregation methods for numerical columns.
                           Keys are column names, and values are aggregation functions (e.g., 'sum', 'mean').

    Returns:
    - pd.DataFrame: A DataFrame with daily granularity, where numerical values are spread across the week
                    and categorical values are repeated for each day.

    Note:
    - If aggregation is specified, the returned DataFrame will be grouped by date and categorical columns,
      and the specified aggregation functions will be applied to the numerical columns within each group.

    Example:
    >>> weekly_data = pd.DataFrame({'date': ['2023-08-01', '2023-08-08'],
    ...                             'value': [70, 105]})
    >>> result = weekly_to_daily(weekly_data, 'date', ['category'], input_starting=True, agg={'value': 'sum'})
    >>> print(result)
         date   category  value
    0 2023-08-01     cat1    10
    1 2023-08-02     cat1    10
    2 2023-08-03     cat1    10
    ...   ...          ...    ...
    """

    new_df = df.copy(True)
    num_cols = get_numerical_columns(df)
    if categorical_cols is None:
        categorical_cols = []
    new_df = new_df[[date_col] + categorical_cols + num_cols]

    new_df[date_col] = pd.to_datetime(new_df[date_col])

    if input_starting:
        new_df[date_col] = new_df.apply(lambda x: pd.date_range(
            x[date_col], x[date_col] + pd.Timedelta(days=6)), axis=1)
    else:
        new_df[date_col] = new_df.apply(lambda x: pd.date_range(
            x[date_col] - pd.Timedelta(days=6), x[date_col]), axis=1)
    new_df = new_df.explode(date_col, ignore_index=True)

    if agg is None:
        new_df[num_cols] = new_df[num_cols] / 7
    else:
        additive_cols = [col for col in num_cols if agg[col] != "mean"]
        new_df[additive_cols] = new_df[additive_cols] / 7
    return new_df


def monthly_to_daily(df, date_col, categorical_cols=None, agg=None):
    num_cols = get_numerical_columns(df)
    if categorical_cols is None:
        categorical_cols = []
    new_df = df[[date_col] + categorical_cols + num_cols]
    if new_df[date_col].dtype == '<M8[ns]':
        new_df.loc[:, date_col] = pd.to_datetime(
            new_df[date_col])  # Use .loc here

    if agg is not None:
        additive_cols = [col for col in agg if agg[col] in [sum, "sum"]]
    else:
        additive_cols = num_cols

    date_min = df[date_col].min()
    date_max = df[date_col].max()
    date_start = datetime(date_min.year, date_min.month, 1)
    date_end = datetime(date_max.year, date_max.month,
                        pd.Period(date_max, 'M').days_in_month)
    df_mapping = pd.DataFrame({date_col: pd.date_range(date_start, date_end)})
    df_mapping["month"] = df_mapping[date_col].dt.to_period("M")
    df_mapping["nb_days"] = df_mapping[date_col].apply(
        lambda x: pd.Period(x, 'M').days_in_month)

    new_df["month"] = new_df[date_col].dt.to_period("M")
    new_df.drop(date_col, inplace=True, axis=1)

    df_daily = pd.merge(new_df, df_mapping, on="month")
    for col in additive_cols:
        df_daily[col] = df_daily[col] / df_daily["nb_days"]
    df_daily = df_daily[[date_col] + categorical_cols + num_cols]
    return df_daily


def change_periodicity(df, date_col, output_freq, categorical_cols=None, input_starting=True, output_starting=True, agg=None):
    """
    Adjusts the periodicity of a time series DataFrame to the desired output frequency.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing time series data.
    date_col : str
        The name of the column in 'df' that contains the date or timestamp values.
    output_freq : str
        The desired output frequency for the time series data. 
        Valid values are 'D' (daily), 'W' (weekly), or 'M' (monthly).
    categorical_cols : list of str, optional
        A list of column names to be treated as categorical variables.
    input_starting : bool, optional
        Indicates whether the input data starts at the beginning or end of the period.
        Default is True, meaning the input data starts at the beginning of each period.
    output_starting : bool, optional
        Indicates whether the output data should start at the beginning or end of the period.
        Default is True, meaning the output data starts at the beginning of each period.
    agg : callable, optional
        A function to aggregate data when reducing frequency.
        For example, 'np.mean' or 'np.sum'. Default is None, meaning no aggregation.

    Returns:
    -------
    pandas.DataFrame
        A DataFrame with the adjusted periodicity according to the specified 'output_freq'.

    Raises:
    -------
    Exception
        If the 'periodicity' of the input DataFrame is neither 'D' (daily), 'W' (weekly), nor 'M' (monthly).

    Example:
    --------
    # Convert daily data to weekly data
    weekly_df = change_periodicity(daily_df, 'date_column', 'W')
    """

    periodicity = get_periodicity(df, date_col)[date_col]
    if periodicity == 'D':
        if output_freq.upper() in ['D', 'DAILY']:
            return df
        elif output_freq.upper()[0] == 'W':
            return daily_to_weekly(df, date_col, output_freq.upper()[2:], categorical_cols, output_starting, agg)
        elif output_freq.upper() in ['M', 'MONTHLY']:
            return daily_to_monthly(df, date_col, categorical_cols, agg)
    elif periodicity[0] == 'W':
        if output_freq.upper() in ['D', 'DAILY']:
            return weekly_to_daily(df, date_col, categorical_cols, input_starting, agg)
        elif output_freq.upper()[0] == 'W':
            new_df = weekly_to_daily(
                df, date_col, categorical_cols, input_starting, agg)
            return daily_to_weekly(new_df, date_col, output_freq[2:], categorical_cols, output_starting, agg)
        elif output_freq.upper() in ['M', 'MONTHLY']:
            new_df = weekly_to_daily(
                df, date_col, categorical_cols, input_starting, agg)
            return daily_to_monthly(new_df, date_col, categorical_cols, agg)
    elif periodicity.startswith('M'):
        if output_freq.upper() in ['D', 'DAILY']:
            return monthly_to_daily(df, date_col, categorical_cols, agg)
        elif output_freq.upper()[0] == 'W':
            new_df = monthly_to_daily(df, date_col, categorical_cols, agg)
            return daily_to_weekly(new_df, date_col, output_freq[2:], categorical_cols, output_starting, agg)
        elif output_freq.upper() in ['M', 'MONTHLY']:
            return df
    else:
        raise Exception('Periodicity is neither daily, weekly, nor monthly.')


def split_value_by_day(df, start_date_col, end_date_col, num_col, additive=True, categorical_col=None):
    """
    Split the values in the 'value_col' column based on the daily or average allocation
    between the 'start_date_col' and 'end_date_col' period.

    Parameters:
        df (DataFrame): The input DataFrame containing the data.
        start_date_col (str): The name of the column in the DataFrame where the campaign starts.
        end_date_col (str): The name of the column in the DataFrame where the campaign ends.
        value_col (str): The name of the column in the DataFrame that contains the cost or price
                         between the start date and end date of the campaign.
        additive (bool, optional): If True, the costs will be split equally for each day within the campaign period.
                                   If False, the average value for the whole campaign period will be assigned to each day.
        categorical_col (str or None, optional): If categorical_col is None (default), the function will group the values based on the date only.
                                        If categorical_col is a valid column name in the DataFrame, the function will group the values
                                        based on both the categorical_col and date.

    Returns:
        DataFrame: A new DataFrame with the following columns:
            - 'categorical_col': The categorical_col from the input DataFrame (if 'categorical_col' parameter is not None).
            - 'Date': The date within the campaign period.
            - 'Value': The allocated value for each day in the campaign period.

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     'start_date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-02']),
        ...     'end_date': pd.to_datetime(['2023-01-02', '2023-01-04', '2023-01-05']),
        ...     'val': [200, 800, 900],
        ...     'categorical_col': ['DC', 'DC', 'TX']
        ... }
        >>> df = pd.DataFrame(data)
        >>> result_df = split_value_by_day(df, 'start_date', 'end_date', 'val', additive=True, categorical_col='region')
        >>> print(result_df)

           categorical_col       Date       Value
         0     DC 2023-01-01  100.000000
         1     DC 2023-01-02  366.666667
         2     DC 2023-01-03  266.666667
         3     DC 2023-01-04  266.666667
         4     TX 2023-01-02  225.000000
         5     TX 2023-01-03  225.000000
         6     TX 2023-01-04  225.000000
         7     TX 2023-01-05  225.000000
    """

    # Create a new dataframe to store the split cost rows
    new_rows = []

    for _, row in df.iterrows():
        start_date = row[start_date_col]
        end_date = row[end_date_col] + timedelta(days=1)
        # Calculate the number of days
        num_days = (end_date - start_date).days

        # Calculate the split cost per day
        if additive:
            split_cost = row[num_col] / num_days
        else:
            split_cost = row[num_col]

        # Create new rows for each day with the split cost
        for day in pd.date_range(start_date, end_date, inclusive='left'):
            data = {
                # 'Region': row['Region'],
                'Date': day,
                num_col: split_cost,
            }
            if categorical_col is not None:
                data[categorical_col] = row[categorical_col]
            new_rows.append(data)

    # Create a new dataframe from the new rows
    if categorical_col is None:
        new_df = pd.DataFrame(new_rows).groupby(['Date'])
    else:
        new_df = pd.DataFrame(new_rows).groupby([categorical_col, 'Date'])

    if additive:
        return new_df.sum().reset_index()
    else:
        return new_df.mean().reset_index()


def calculate_categorical_counts_over_time(df, date_col, categorical_col, division_col=None):
    """
    Calculate the count of unique values in a categorical column over time.

    Parameters:
        df (DataFrame): The input DataFrame.
        date_col (str): The name of the column containing dates.
        categorical_col (str): The name of the categorical column for which counts are to be calculated.
        division_col (str, optional): The name of the column used for division (e.g., groups). Default is None.

    Returns:
        DataFrame: A DataFrame containing the count of unique values in the categorical column over time.

    Raises:
        ValueError: If date_col, categorical_col, or division_col are not found in the DataFrame,
                    or if invalid dates are encountered after conversion.
    """
    # Check if the date_col exists in the DataFrame
    if date_col not in df.columns:
        raise ValueError("Date column not found in DataFrame")

    # Check if the categorical_col exists in the DataFrame
    if categorical_col not in df.columns:
        raise ValueError("Categorical column not found in DataFrame")

    # Check if division_col is provided and exists in the DataFrame
    if division_col is not None and division_col not in df.columns:
        raise ValueError("Division column not found in DataFrame")

    # Convert date_col to datetime if it's not already
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    # Check if any invalid dates are found after conversion
    if df[date_col].isnull().any():
        raise ValueError("Invalid dates found in date column")

    # Assuming daily frequency, can be changed as needed
    freq = get_periodicity(df, date_col)[date_col]

    # Generate a new DataFrame with dates ranging from min to max date in df
    df_new = pd.DataFrame({date_col: pd.date_range(
        df[date_col].min(), df[date_col].max(), freq=freq)})

    if division_col is None:
        for date in df_new[date_col]:
            df_new.loc[df_new[date_col] == date, categorical_col
                       + '_nb'] = df[df[date_col] <= date][categorical_col].nunique()
    else:
        for value in df[division_col].unique():
            for date in df_new[date_col]:
                df_new.loc[df_new[date_col] == date, categorical_col + "_" + str(value) + '_nb'] = df[(df[date_col] <= date) & (
                    df[division_col] == value)][categorical_col].nunique()

    return df_new
