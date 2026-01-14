# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 12:16:02 2024

@author: MejdiTRABELSI
"""
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from .data_utils import get_date_columns
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from plotly.subplots import make_subplots


def plot_pie_chart(df, categorical_col, num_col, return_fig=False, colors=None, title=None, show_percent=False):
    """
    Plot a donut chart based on the provided DataFrame.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        categorical_col (str): The name of the column in the DataFrame that represents the categorical variable.
        num_col (str): The name of the column in the DataFrame that contains the numerical values.
        return_fig (bool, optional): If True (default is False), the function returns the Plotly Figure instead of showing it.
        colors (list, optional): List of colors for the donut chart slices. If None, default Plotly G10 colors will be used.
        title (str, optional): Title for the donut chart.
        show_percent (bool, optional): If True, display percentages alongside numerical values in the donut chart.

    Returns:
        plotly.graph_objs._figure.Figure (optional): A Plotly Figure representing the donut chart. 
                                                    (Returned only if 'return_fig' is True.)

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     'Category': ['A', 'B', 'C', 'A', 'B', 'C'],
        ...     'Value': [100, 200, 300, 400, 500, 600]
        ... }
        >>> df = pd.DataFrame(data)
        >>> plot_donut_chart(df, 'Category', 'Value')
        # This will display a donut chart based on the 'Category' and 'Value' columns in the DataFrame.

        >>> donut_chart_figure = plot_donut_chart(df, 'Category', 'Value', return_fig=True)
        # This will return the Donut chart as a Plotly Figure without displaying it.
    """

    # Error handling
    if categorical_col not in df.columns or num_col not in df.columns:
        raise ValueError("Specified columns not found in the DataFrame.")
    if not pd.api.types.is_numeric_dtype(df[num_col]):
        raise ValueError(
            "The specified numerical column must contain numeric values.")

    new_df = df[[categorical_col, num_col]].groupby(
        categorical_col).sum().reset_index()
    labels = new_df[categorical_col]
    values = new_df[num_col]

    # Default color palette: Plotly G10 colors
    default_colors = px.colors.qualitative.Set1

    # Use provided colors or default G10 colors
    donut_colors = colors if colors else default_colors

    # Customize donut chart appearance
    title_text = title if title else "Distribution of " + \
        num_col + " by " + categorical_col

    # Create the donut chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, hoverinfo='label+percent' if show_percent else 'label',
                                 textinfo='value' if not show_percent else 'percent',
                                 textfont=dict(size=12), marker=dict(colors=donut_colors))])

    fig.update_layout(title_text=title_text)

    if return_fig:
        return fig
    else:
        fig.show()


def plot_time_series(df, date_col=None, categorical_col=None, num_cols=None, agg=None):
    """
    Plot time series data from a DataFrame.

    Parameters:
        df (pandas.DataFrame): The input DataFrame containing time series data.
        date_col (str, optional): The name of the column in the DataFrame representing dates or timestamps.
                                  If not provided, the function will try to automatically detect a suitable date column.
        categorical_col (str, optional): The name of the column in the DataFrame representing categories or groups.
                                         If provided, the function will generate separate plots for each category.
        num_cols (list of str, optional): A list of column names in the DataFrame containing numerical data to be plotted.
                                          If not provided, all numeric columns will be used.
        agg (dict, optional): A dictionary specifying aggregation functions to apply to numerical columns.
                             The keys are the numerical column names, and values are aggregation functions
                             (e.g., {'Sales': 'sum', 'Profit': 'mean'}). Default is None, which performs sum.

    Raises:
        ValueError: If the provided `date_col` is not found in the DataFrame, or if there is more than one potential
                    date column when `date_col` is not specified, or if any of the columns in `num_cols` are not
                    numeric columns in the DataFrame.

    Returns:
        None: The function displays the generated plots using the Plotly library.

    Example:
        # Basic usage - plot all numeric columns by default date column
        plot_time_series(df)

        # Plot specific numeric columns with a specified date column
        plot_time_series(df, date_col='date_column', num_cols=['column_A', 'column_B'])

        # Plot time series for specific categories using a categorical column
        plot_time_series(df, date_col='date_column', categorical_col='category_column', num_cols=['column_C'])
    """

    # Check date_col
    if date_col is None:
        date_col = get_date_columns(df)
        if type(date_col) is not str:
            raise ValueError("There is more than one date column.", date_col)
    else:
        cols = get_date_columns(df)
        if type(cols) is str:
            cols = [cols]
        if date_col not in cols:
            raise ValueError(date_col, " is not a date column")
        if np.issubdtype(df[date_col].dtype, np.object_):
            df[date_col] = pd.to_datetime(df[date_col])
        df.sort_values(by=date_col, inplace=True)

    # Check categorical_col
    all_cat_cols = [col for col in df.columns if is_string_dtype(df[col])]
    if categorical_col is not None:
        if type(categorical_col) is not str:
            raise ValueError('categorical_col must be a string !')
        elif categorical_col not in all_cat_cols:
            raise ValueError('Wrong categorical_col')

    # Check num_cols
    all_num_cols = []
    for col in df.columns:
        if is_numeric_dtype(df[col]):
            all_num_cols.append(col)

    if num_cols is None:
        num_cols = all_num_cols
    elif type(num_cols) is not list:
        raise ValueError('num_cols must be a list')
    elif set(num_cols).issubset(set(all_num_cols)) == False:
        raise ValueError(num_cols, " aren\'t all numerical columns")

    aggregation = {}
    for num in num_cols:
        aggregation[num] = 'sum'

    if agg is not None:
        if type(agg) is not dict:
            raise ValueError('agg must be a dict !')
        elif set(agg.keys()).issubset(set(aggregation.keys())) == False:
            raise ValueError('Wrong keys for the agg variable')

        for num in num_cols:
            if num in agg.keys():
                aggregation[num] = agg[num]

    if categorical_col is None:
        new_df = df.groupby(date_col).agg(aggregation).reset_index()
        for num in num_cols:
            fig = go.Figure(data=go.Scatter(
                x=list(new_df[date_col]), y=list(new_df[num]), mode='lines'))
            fig.update_layout(title_text=num + " overtime")
            fig.show()
    else:
        new_df = df.groupby([categorical_col, date_col]).agg(
            aggregation).reset_index(date_col)
        for num in num_cols:
            fig = go.Figure()
            for cat in new_df.index.unique():
                fig.add_trace(go.Scatter(x=pd.Series(
                    new_df.loc[cat][date_col]), y=pd.Series(new_df.loc[cat][num]), name=cat))
                fig.update_layout(title_text=num + " overtime")
            fig.show()


def plot_two_time_series(df, date_col, num_col_1, num_col_2, two_axis=False, agg=None):
    """
    Plots two time series on a single plot, allowing comparison of two numerical columns over time.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data to be plotted.
    date_col (str): The column name in the DataFrame representing the date or time values.
    num_col_1 (str): The column name in the DataFrame representing the first numerical series to be plotted.
    num_col_2 (str): The column name in the DataFrame representing the second numerical series to be plotted.
    two_axis (bool, optional): If True, the two series will be plotted with separate y-axes. If False (default),
                               both series will share the same y-axis.
    agg (dict, optional): A dictionary specifying aggregation functions to apply to numerical columns.
                             The keys are the numerical column names, and values are aggregation functions
                             (e.g., {'Sales': 'sum', 'Profit': 'mean'}). Default is None, which performs sum.

    Returns:
    None

    Example:
    plot_two_time_series(df=my_data, date_col='Date', num_col_1='Sales', num_col_2='Profit', two_axis=True)
    """

    # Check date column
    cols = get_date_columns(df)
    if type(cols) is str:
        cols = [cols]
    if date_col not in cols:
        raise ValueError(date_col + " is not a date column")
    if np.issubdtype(df[date_col].dtype, np.object_):
        df[date_col] = pd.to_datetime(df[date_col])
    df.sort_values(by=date_col, inplace=True)

    aggregation = {}
    aggregation[num_col_1] = 'sum'
    aggregation[num_col_2] = 'sum'

    if agg is not None:
        if type(agg) is not dict:
            raise ValueError('agg must be a dict !')
        elif set(agg.keys()).issubset(set(aggregation.keys())) == False:
            raise ValueError('Wrong keys for the agg variable')

        if num_col_1 in agg.keys():
            aggregation[num_col_1] = agg[num_col_1]
        if num_col_2 in agg.keys():
            aggregation[num_col_2] = agg[num_col_2]

    new_df = df.groupby(date_col).agg(aggregation).reset_index()

    if two_axis is False:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=new_df[date_col], y=new_df[num_col_1],
                                 mode='lines',
                                 name=num_col_1))
        fig.add_trace(go.Scatter(x=new_df[date_col], y=new_df[num_col_2],
                                 mode='lines',
                                 name=num_col_2))
    else:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=new_df[date_col],
                       y=new_df[num_col_1], name=num_col_1),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=new_df[date_col],
                       y=new_df[num_col_2], name=num_col_2),
            secondary_y=True,
        )

        # Add figure title
        fig.update_layout(
            title_text=num_col_1 + " vs. " + num_col_2
        )

        # Set x-axis title
        fig.update_xaxes(title_text=date_col)

        # Set y-axes titles
        fig.update_yaxes(title_text=num_col_1, secondary_y=False)
        fig.update_yaxes(title_text=num_col_2, secondary_y=True)
    fig.show()


def plot_categorical_count_bar(df, cat_col):
    """
    Create a bar plot showing the count of different categories in a categorical column.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    cat_col (str): The name of the categorical column to be visualized.

    Returns:
    None
    """

    cat_counts = df[cat_col].value_counts()

    fig = go.Figure([go.Bar(x=cat_counts.index, y=cat_counts.values)])
    fig.update_layout(title=f"Count of Different Categories in '{cat_col}'",
                      xaxis_title=cat_col,
                      yaxis_title="Count")
    fig.show()


def plot_correlation_heatmap(df, num_cols=None):
    """
    Create a heatmap showing the correlation between different numerical features in a dataset.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    num_cols (list of str, optional): A list of column names in the DataFrame containing numerical data to be plotted.
                                          If not provided, all numeric columns will be used.
    Returns:
    None
    """

    all_num_cols = [col for col in df.columns if is_numeric_dtype(df[col])]

    if num_cols is None:
        num_cols = all_num_cols
    elif type(num_cols) is not list:
        raise ValueError("num_cols must be a list")
    elif set(num_cols).issubset(set(all_num_cols)) == False:
        raise ValueError(str(num_cols) + " aren\'t all numerical columns")

    # Calculate the correlation matrix
    correlation_matrix = df[num_cols].corr()

    # Create the heatmap using plotly.graph_objects
    fig = go.Figure(data=go.Heatmap(z=correlation_matrix.values,
                                    x=correlation_matrix.columns,
                                    y=correlation_matrix.index,
                                    colorscale="Viridis"))

    # Set plot title and axis labels
    fig.update_layout(title="Correlation Heatmap",
                      xaxis_title="Features",
                      yaxis_title="Features")

    # Show the plot
    fig.show()


def plot_boxplots(df, num_cols, categorical_col=None):
    """
    Create subplots with box plots for different numerical variables grouped by a categorical variable.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    num_cols (str or list of str): The name(s) of the numerical column(s) to be plotted.
    categorical_col (str, optional): The name of the categorical column for grouping box plots. 
                                     If provided, separate box plots are created for each category.
                                     Default is None.

    Returns:
    None
    """

    if type(num_cols) is str:
        num_cols = [num_cols]

    # Create box plots for each numerical variable
    all_num_cols = [col for col in df.columns if is_numeric_dtype(df[col])]
    all_cat_cols = [col for col in df.columns if is_string_dtype(df[col])]

    # Check num_cols
    if set(num_cols).issubset(set(all_num_cols)) == False:
        raise ValueError(str(num_cols) + " aren\'t all numerical columns")

    # Check categorical_col
    if categorical_col is not None:
        if categorical_col not in all_cat_cols:
            raise ValueError(categorical_col + " is not a categorical column")

    if categorical_col is None:
        for num_col in num_cols:
            fig = go.Figure()
            fig.add_trace(go.Box(y=df[num_col]))
            fig.update_layout(xaxis_title=num_col)
            fig.show()
    else:
        unique_data = df[categorical_col].dropna().unique()
        for num_col in num_cols:
            count = 1
            fig = go.Figure()
            for u_d in unique_data:
                fig.add_trace(
                    go.Box(y=df[df[categorical_col] == u_d][num_col], name=u_d))
                count += 1
            fig.update_layout(title="Box Plots by "
                              + categorical_col + " (" + num_col + ")")
            fig.show()


def plot_AVM(dates, y_true, y_pred, dates_test=None, y_true_test=None, y_pred_test=None):
    """
    Plot Actual vs. Predicted values along with Mean Absolute Percentage Error (MAPE) bars.

    Parameters:
    ----------
    dates : list-like
        List of dates or date-like objects corresponding to the data points.
    y_true : list-like
        List of actual target values.
    y_pred : list-like
        List of predicted target values.
    dates_test : list-like, optional
        List of dates or date-like objects corresponding to the test data points.
    y_true_test : list-like, optional
        List of actual target values for the test data points.
    y_pred_test : list-like, optional
        List of predicted target values for the test data points.

    Returns:
    -------
    None

    The function generates a plot that displays the actual and predicted values along with
    bars representing the Mean Absolute Percentage Error (MAPE) between actual and predicted values.

    If test data is provided, additional traces and bars are plotted for the test data.
    """

    df = pd.DataFrame({'date': dates,
                       'y_true': y_true,
                       'y_pred': y_pred})

    df['mape'] = abs(df['y_true'] - df['y_pred']) / df['y_true']
    df['mape'] = df['mape'].apply(lambda x: min(1, x))

    if np.issubdtype(df['date'].dtype, np.object_):
        df['date'] = pd.to_datetime(df['date'])

    df.sort_values(by='date', inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df['date'], y=df['y_true'], name="y_true"))

    fig.add_trace(go.Scatter(x=df['date'], y=df['y_pred'], name='y_pred',
                             line=dict(dash='dash')))

    fig.add_trace(go.Bar(x=df['date'], y=df['mape'],
                  name="mape", opacity=0.3), secondary_y=True)

    if dates_test is not None and y_true_test is not None and y_pred_test is not None:
        df_test = pd.DataFrame({'dates_test': dates_test,
                                'y_true_test': y_true_test,
                                'y_pred_test': y_pred_test})

        df_test['mape_test'] = abs(
            df_test['y_true_test'] - df_test['y_pred_test']) / df_test['y_true_test']
        df_test['mape_test'] = df_test['mape_test'].apply(lambda x: min(1, x))

        if np.issubdtype(df_test['dates_test'].dtype, np.object_):
            df_test['dates_test'] = pd.to_datetime(df_test['dates_test'])

        df_test.sort_values(by='dates_test', inplace=True)

        fig.add_trace(go.Scatter(
            x=df_test['dates_test'], y=df_test['y_true_test'], name="y_true_train"))

        fig.add_trace(go.Scatter(x=df_test['dates_test'], y=df_test['y_pred_test'], name='y_pred_train',
                                 line=dict(dash='dash')))

        fig.add_trace(go.Bar(x=df_test['dates_test'], y=df_test['mape_test'],
                      name="mape_train", opacity=0.3), secondary_y=True)

    fig.update_layout(title="Actual vs. Predicted")
    fig.update_yaxes(title_text="Mape", secondary_y=True)

    fig.show()


def plot_stacked_vs_lines(df, date_col, stacked_cols, lines_cols, two_axis=False, agg=None):
    """
    Create a plot with filled area plots and line plots to compare data trends over time.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the data to be plotted.
    date_col : str
        The column name in `df` representing the date or time period.
    stacked_cols : list-like
        List of column names to be represented as filled area plots in the plot.
    lines_cols : str or list-like
        Column name or list of column names to be represented as line plots in the plot.
    two_axis : bool, optional
        If True, use a secondary y-axis for line plots (default is False).
    agg : dict, optional
        A dictionary specifying custom aggregation functions for columns.
        Keys should match the column names, and values should be aggregation functions.
        Example: {'column_name': 'mean', 'other_column': 'sum'}

    Returns:
    -------
    None

    The function generates a plot that displays the trends of specified columns over time,
    with filled area plots for some columns and line plots for others. It is useful for
    visualizing and comparing multiple data series with different scales and formats.

    If `two_axis` is set to True, the line plots are displayed on a secondary y-axis.

    If `agg` is provided, custom aggregation functions can be applied to the specified columns
    during data preprocessing before plotting.
    """

    if np.issubdtype(df[date_col].dtype, np.object_):
        df[date_col] = pd.to_datetime(df[date_col])

    df.sort_values(by=date_col, inplace=True)

    if two_axis:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig = go.Figure()

    if type(lines_cols) is str:
        lines_cols = [lines_cols]

    aggregation = {}
    for num in stacked_cols:
        aggregation[num] = 'sum'
    for num in lines_cols:
        aggregation[num] = 'sum'

    if agg is not None:
        if type(agg) is not dict:
            raise ValueError('agg must be a dict !')
        elif set(agg.keys()).issubset(set(aggregation.keys())) == False:
            raise ValueError('Wrong keys for the agg variable')

        for num in stacked_cols:
            if num in agg.keys():
                aggregation[num] = agg[num]
        for num in lines_cols:
            if num in agg.keys():
                aggregation[num] = agg[num]

    new_df = df.groupby(date_col).agg(aggregation).reset_index()
    for col in stacked_cols:
        fig.add_trace(go.Scatter(
            name=col, x=new_df[date_col], y=new_df[col], mode='lines', stackgroup='one'))

    for col in lines_cols:
        if two_axis:
            fig.add_trace(go.Scatter(
                x=new_df[date_col], y=new_df[col], name=col), secondary_y=True)
        else:
            fig.add_trace(go.Scatter(
                x=new_df[date_col], y=new_df[col], name=col))

    fig.show()
