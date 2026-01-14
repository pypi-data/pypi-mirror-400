# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 10:19:42 2024

@author: MejdiTRABELSI
"""

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from .data_utils import get_date_columns
from .data_utils import get_periodicity
from pandas.api.types import is_numeric_dtype


def check_missing_dates(df, date_column=None, start_date=None, end_date=None, freq=None, visual=False):
    """
    Analyzes a pandas DataFrame to identify any missing dates within specified date column.
    Generates a continuous date range based on the earliest and latest dates the column,
    identifies missing dates within this range, and optionally visualizes these findings.If 
    the visual is selected then the function returns a plotly figure.If not it will return a 
    dictionary containing the date column and its corresponding missing dates

    Parameters:
    - df (pandas.DataFrame): DataFrame containing date data.
    - date_column (str, optional): Column name containing date data. Automatically detected if None.
    - start_date (str, optional): The start date for the date range. Automatically detected if None.
    - end_date (str, optional): The end date for the date range. Automatically detected if None.
    - freq (str, optional): The frequency for the date range. Automatically detected if None.
    - visual (bool, optional): If True, visualizes missing dates using a bar chart. Defaults to False.

    Returns:
    - plotly.graph_objs._figure.Figure or dict: If visual is True, returns a Plotly figure.
      If visual is False, returns a dictionary with the date column as the key and a list of 
      missing dates ('YYYY-MM-DD') as the value.

    Example:
    >>> df = pd.DataFrame({'Date': ['2024-01-01', '2024-01-02', '2024-01-04', '2024-01-06']})
    >>> check_missing_dates(df, 'Date', visual=False)
    {'Date': ['2024-01-03', '2024-01-05']}
    """

    def visualize_missing_dates_for_column(df_col, all_dates, missing_dates):
        if visual:
            fig = go.Figure()
            present_dates = pd.Index(all_dates).difference(missing_dates)
            missing_count = len(missing_dates)
            total_count = len(all_dates)
            completion_percentage = round(
                (total_count - missing_count) / total_count * 100, 2)
            title = f"Date completion: {completion_percentage}%"
            if missing_dates.empty:
                fig.add_trace(go.Bar(x=all_dates, y=[
                              1] * len(all_dates), name='Present', marker_color='teal'))
            else:
                present_dates = pd.Index(all_dates).difference(missing_dates)
                fig.add_trace(go.Bar(x=present_dates, y=[
                              1] * len(present_dates), name='Present', marker_color='teal'))
                fig.add_trace(go.Bar(x=missing_dates, y=[
                              1] * len(missing_dates), name='Missing', marker_color='red'))

            fig.update_layout(title=title, barmode='overlay',
                              xaxis_title='Date', xaxis=dict(showgrid=False),
                              yaxis=dict(showticklabels=False, title='Presence'))
            return fig

    if date_column is None:
        date_column = get_date_columns(df)

    if not isinstance(date_column, str):
        raise Exception(
            "Please make sure your dataframe contains only one date column")
    else:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df[date_column] = df[date_column].dropna()

        if start_date is None:
            start_date = df[date_column].min()
        if end_date is None:
            end_date = df[date_column].max()
        if freq is None:
            periodicity = {}
            periodicity = get_periodicity(df, date_column)
            freq = periodicity[date_column]

        all_missing_dates = {}

        all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        present_dates = df[date_column].dt.floor('D').unique()
        missing_dates = pd.Index(all_dates).difference(present_dates)
        all_missing_dates[date_column] = missing_dates.strftime(
            '%Y-%m-%d').tolist()
        fig = visualize_missing_dates_for_column(
            df[date_column], all_dates, missing_dates)
        if visual is True:
            return fig
        if visual is False:
            return missing_dates


def calculate_completion(col, special_characters=None):
    """
    Calculate the completion rate for a given column in a DataFrame.
    Completion rate is the percentage of values that are neither missing
    nor considered special characters in the selected DataFrame.
    This function also supports the inclusion of special characters that
    the user wants to detect as a separate category.

    Parameters:
        col (pandas.Series): The column for which to calculate
        the completion rate.
        special_characters (list, optional): A list of special
        characters to be considered separately. Defaults to None.

    Returns:
        dict: A dictionary with keys 'complete', 'missing',
        'special', and 'total' representing the counts of each category.
    """
    total_rows = len(col)
    missing_count = col.isna().sum()
    special_count = 0
    if special_characters is not None:
        for special_character in special_characters:
            if special_character == "white space":
                special_count += col.astype(str).str.isspace().sum()
            elif (special_character == "negative values") & (is_numeric_dtype(col)):
                special_count += (col < 0).sum()
            elif (special_character == "zero values") & (is_numeric_dtype(col)):
                special_count += (col == 0).sum()
            else:
                col_as_str = col.astype(str)
                special_count += col_as_str.isin(
                    [str(char) for char in special_characters]).sum()

    complete_count = total_rows - missing_count - special_count

    return {
        'complete': complete_count,
        'missing': missing_count,
        'special': special_count,
        'total': total_rows
    }


def check_missing_values(df, missing_column=None, visual_donut=False, visual_bar=False, special_characters=None):
    """
    Check for missing values in a DataFrame and optionally visualize
    the completion rates. This function will use calculate_completion()
    to check columns completion rate, which is the percentage of existing data per column. This function allows the user to limit the search 
    to one or more specific columns if the argument missing_column is used, and it also allows the user to visualize the results by outputting
    a donut chart showing the overall completion rate of the dataframe, as well as horizontal bar charts representing the completion rate 
    of each column passed in the function.

    Parameters:
        df (pandas.DataFrame): The DataFrame to check for missing values.
        missing_column (str, optional): The name of a specific column to check for missing values. Defaults to None.
        visual_donut (bool, optional): Whether to visualize the overall completion rate with a donut chart. Defaults to False.
        visual_bar (bool, optional): Whether to visualize the completion rates of columns with bar charts. Defaults to False.
        special_characters (list, optional): A list of special characters to be considered separately. Defaults to None.

    Returns:
        pandas.DataFrame or plotly.graph_objs._figure.Figure: A DataFrame containing the completion rates for each column, or visualizations if specified.
    """

    completion_data = []

    if missing_column:
        if missing_column in df.columns:
            completion_info = calculate_completion(
                df[missing_column], special_characters)
            completion_data.append(
                (missing_column, completion_info['complete'], completion_info['missing'], completion_info['special'], completion_info['total']))
        else:
            print(f"Column {missing_column} does not exist in the DataFrame.")
    else:
        for column in df.columns:
            completion_info = calculate_completion(
                df[column], special_characters)
            completion_data.append(
                (column, completion_info['complete'], completion_info['missing'], completion_info['special'], completion_info['total']))

    completion_df = pd.DataFrame(completion_data, columns=[
                                 'Column', 'Complete', 'Missing', 'Special', 'Total'])

    # Calculate the rates
    completion_df['Completion Rate'] = (
        completion_df['Complete'] / completion_df['Total']) * 100
    completion_df['Missing Rate'] = (
        completion_df['Missing'] / completion_df['Total']) * 100
    completion_df['Special Rate'] = (
        completion_df['Special'] / completion_df['Total']) * 100
    visual_df = completion_df.copy()

    if visual_donut:
        overall_completion_rate = visual_df['Completion Rate'].mean()
        overall_missing_rate = visual_df['Missing Rate'].mean()
        overall_special_rate = visual_df['Special Rate'].mean()
        fig_donut = go.Figure(go.Pie(
            labels=['Complete', 'Missing', 'Special'],
            values=[overall_completion_rate,
                    overall_missing_rate, overall_special_rate],
            hole=.3,
            marker=dict(colors=['teal', 'crimson', 'orange'])
        ))
        fig_donut.update_layout(title="Overall Completion Rate of DataFrame")

    if visual_bar:
        fig_bar = go.Figure([
            go.Bar(name='Complete',
                   x=visual_df['Column'],
                   y=visual_df['Completion Rate'],
                   marker_color='teal'),
            go.Bar(name='Missing',
                   x=visual_df['Column'],
                   y=visual_df['Missing Rate'],
                   marker_color='crimson'),
            go.Bar(name='Special',
                   x=visual_df['Column'],
                   y=visual_df['Special Rate'],
                   marker_color='orange')
        ])
        fig_bar.update_layout(barmode='stack', title="Completion Rates by Column",
                              xaxis_title="Column", yaxis_title="Rate (%)")

    if visual_donut and visual_bar:
        return fig_donut, fig_bar
    elif visual_donut:
        return fig_donut
    elif visual_bar:
        return fig_bar
    else:
        return completion_df


def check_outliers(df, date_column, numerical_column, type_outlier="values", limit=None):
    """
    This is a function used by the outlier plotting functions, this function takes as input the datafarame, the date column and the numerical column
    to be checked for outliers. The function supports two types of calculations for detecting outliers: 'Variation' which is based on the z score of our
    variables and 'Values' which is based on the quartiles calculated using the .quantile() method.
    The function takes as input a dataframe, a date column and a numerical column as well as the type of calculation the user wishes to use to get the 
    outliers and finally the Limit argument which is optional and allows the user to set a maximum number of outliers for the function to detect.
    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        date_column (str): The name of the column containing date values.
        numerical_column (str): The name of the column containing numerical values.
        type_outlier (str): The type of outlier detection method ("variation" or "values").
        limit (int): The maximum number of outliers to detect.

    Returns:
        pandas.DataFrame: A DataFrame containing the original data and detected outliers.
    Example:
        # Detect outliers using 'Values' method with a limit of 50 outliers
        outliers_df = detect_outliers(dataframe, 'Date', 'Value', type_outlier='values', limit=50)
    """
    df1 = df[[date_column, numerical_column]].copy()

    if type_outlier == "variation":
        df1["shift"] = df1[numerical_column].shift(1)
        df1["diff"] = df1[numerical_column] - df1["shift"]
        mean_diff = df1['diff'].mean()
        std_diff = df1['diff'].std()
        threshold = 3
        df1['z_score'] = (df1['diff'] - mean_diff) / std_diff
        df1.loc[df1["z_score"] < -threshold, "var_class"] = "lower_outlier"
        df1.loc[df1["z_score"] > threshold, "var_class"] = "upper_outlier"
    else:
        q1 = df1[numerical_column].quantile(0.25)
        q3 = df1[numerical_column].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        lower = q1 - 1.5 * iqr
        df1.loc[df1[numerical_column] < lower, "var_class"] = "lower_outlier"
        df1.loc[df1[numerical_column] > upper, "var_class"] = "upper_outlier"

    if limit is not None:
        top_outliers = df1[df1['var_class'].notnull()].nlargest(
            limit, numerical_column)
        df1['var_class'] = np.where(df1.index.isin(
            top_outliers.index), df1['var_class'], None)

    return df1


def plot_with_outliers(df, date_column, numerical_column, type_outlier="values", limit=None):
    """
    Plot the data with outliers highlighted.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        date_column (str): The name of the column containing date values.
        numerical_column (str): The name of the column containing numerical values.
        type_outlier (str): The type of outlier detection method ("variation" or "values").
        limit (int): The maximum number of outliers to detect.
    Returns:
        plotly.graph_objs._figure
    """
    df_outliers = check_outliers(
        df, date_column, numerical_column, type_outlier=type_outlier, limit=limit)

    fig = go.Figure()
    fig.add_trace(go.Scatter(name='value', x=df_outliers[date_column].astype(
        str), y=df_outliers[numerical_column], mode='lines', line_color="#808080"))

    if type_outlier == "values":
        upper_outliers = df_outliers.loc[df_outliers["var_class"]
                                         == "upper_outlier", numerical_column]
        if not upper_outliers.empty:
            upper_threshold = upper_outliers.min()
            fig.add_trace(go.Scatter(name='upper threshold', x=df_outliers[date_column].astype(str), y=[
                          upper_threshold] * len(df_outliers), mode='lines', line_color="#EA9999", line=dict(dash='dash')))
        lower_outliers = df_outliers.loc[df_outliers["var_class"]
                                         == "lower_outlier", numerical_column]
        if not lower_outliers.empty:
            lower_threhold = lower_outliers.max()
            fig.add_trace(go.Scatter(name='lower threshold', x=df_outliers[date_column].astype(str), y=[
                          lower_threhold] * len(df_outliers), mode='lines', line_color="#6FA8DC", line=dict(dash='dash')))
    view = df_outliers.loc[df_outliers["var_class"] == "upper_outlier"]
    fig.add_trace(go.Scatter(name='upper_outlier', x=view[date_column].astype(
        str), y=view[numerical_column], mode='markers', marker=dict(color='red')))
    view = df_outliers.loc[df_outliers["var_class"] == "lower_outlier"]
    fig.add_trace(go.Scatter(name='lower_outlier', x=view[date_column].astype(
        str), y=view[numerical_column], mode='markers', marker=dict(color='blue')))

    fig.update_xaxes(tickangle=-45)
    fig.update_layout(font=dict(size=18), plot_bgcolor="white",
                      title=dict(text="Outlier detection"))
    return fig


def plot_outliers_only(df, date_column, numerical_column, type_outlier="values", limit=None):
    """
    Plot only the outliers.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        date_column (str): The name of the column containing date values.
        numerical_column (str): The name of the column containing numerical values.
        type_outlier (str): The type of outlier detection method ("variation" or "values").
        limit (int): The maximum number of outliers to detect.
    Returns:
        A plotly graph containing only the outlier values detected, the upper outliers will be highlighted in red and the lower
        ones will be highlighted in blue.
    Example:
        plot_outliers_only(df, "Date", "Value", type_outlier="values", limit=50)
    """
    df_outliers = check_outliers(
        df, date_column, numerical_column, type_outlier=type_outlier, limit=limit)

    fig = go.Figure()

    # Plot upper outliers
    upper_outliers = df_outliers.loc[df_outliers["var_class"]
                                     == "upper_outlier"]
    fig.add_trace(go.Scatter(name='upper_outlier', x=upper_outliers[date_column].astype(
        str), y=upper_outliers[numerical_column], mode='markers', marker=dict(size=3), line_color="#BF0000"))

    # Plot lower outliers
    lower_outliers = df_outliers.loc[df_outliers["var_class"]
                                     == "lower_outlier"]
    fig.add_trace(go.Scatter(name='lower_outlier', x=lower_outliers[date_column].astype(
        str), y=lower_outliers[numerical_column], mode='markers', marker=dict(size=3), line_color="#2900BF"))

    fig.update_xaxes(tickangle=-45)
    fig.update_layout(font=dict(size=18), plot_bgcolor="white",
                      title=dict(text="Outlier detection"))
    return fig
