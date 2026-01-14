# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 10:25:53 2024

@author: MejdiTRABELSI
"""

import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from ma_python_package.data_check import (check_missing_dates,
                                          check_missing_values,
                                          plot_outliers_only
                                          )


class TestCheckMissingDates(unittest.TestCase):

    def setUp(self):
        self.data = {
            'Date': ['2024-01-01', '2024-01-02', '2024-01-04', '2024-01-06'],
            'WeeklyDate': ['2024-01-07', '2024-01-14', '2024-01-21', '2024-01-28']
        }
        self.df = pd.DataFrame(self.data)

    @patch('Missing_Date_Checker.go.Figure.show')
    def test_visualization_called_with_missing_dates(self, mock_show):
        check_missing_dates(self.df, date_columns='Date', Visual=True)
        mock_show.assert_called_once()

    @patch('Missing_Date_Checker.go.Figure.show')
    def test_visualization_called_without_missing_dates(self, mock_show):
        continuous_date_df = pd.DataFrame(
            {'Date': pd.date_range(start='2024-01-01', periods=4, freq='D')})
        check_missing_dates(continuous_date_df,
                            date_columns='Date', Visual=True)
        mock_show.assert_called_once()

    def test_date_column_with_null_values(self):
        self.df.loc[2, 'Date'] = pd.NaT
        expected_result = {
            'Date': ['2024-01-03', '2024-01-05'], 'WeeklyDate': []}
        result = check_missing_dates(
            self.df, date_columns=['Date', 'WeeklyDate'])
        self.assertEqual(result, expected_result)

    def test_multiple_date_columns_non_continuous_range(self):
        expected_result = {
            'Date': ['2024-01-03', '2024-01-05'],
            'WeeklyDate': ['2024-01-21']
        }
        result = check_missing_dates(
            self.df, date_columns=['Date', 'WeeklyDate'])
        self.assertEqual(result, expected_result)

    def test_with_leap_year_dates(self):

        leap_year_df = pd.DataFrame({
            'Date': ['2020-02-28', '2020-03-01']
        })
        expected_result = {'Date': ['2020-02-29']}
        result = check_missing_dates(leap_year_df, 'Date')
        self.assertEqual(result, expected_result)


class TestCheckMissingValues(unittest.TestCase):

    def test_no_missing_values_no_special_chars(self):
        """Test the function with a DataFrame that has no missing values and no special characters defined."""
        df = pd.DataFrame({
            'Column1': [1, 2, 3],
            'Column2': ['a', 'b', 'c']
        })
        result = check_missing_values(df, visual=False)
        expected_data = {'Column': [
            'Column1', 'Column2'], 'Completion Rate': ['100%', '100%']}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result.sort_values(by='Column').reset_index(
            drop=True), expected_df.sort_values(by='Column').reset_index(drop=True))

    def test_with_missing_values_no_special_chars(self):
        """Test the function with a DataFrame that has missing values but no special characters defined."""
        df = pd.DataFrame({
            'Column1': [1, None, 3],
            'Column2': ['a', 'b', None]
        })
        result = check_missing_values(df, visual=False)
        expected_data = {'Column': ['Column1', 'Column2'],
                         'Completion Rate': ['66.67%', '66.67%']}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result.sort_values(by='Column').reset_index(
            drop=True), expected_df.sort_values(by='Column').reset_index(drop=True))

    def test_specific_column(self):
        """Test the function's ability to handle a specified column correctly."""
        df = pd.DataFrame({
            'Column1': [1, None, 3],
            'Column2': ['a', 'b', None]
        })
        result = check_missing_values(
            df, missing_column='Column1', visual=False)
        expected_data = {'Column': ['Column1'], 'Completion Rate': ['66.67%']}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result.sort_values(by='Column').reset_index(
            drop=True), expected_df.sort_values(by='Column').reset_index(drop=True))


class TestPlotOutliersOnly(unittest.TestCase):

    @patch('Outlier_checker.detect_outliers')
    def test_plot_outliers_only(self, mock_detect_outliers):
        # Mocking detect_outliers function
        mock_detect_outliers.return_value = pd.DataFrame({
            'Date': pd.date_range(start='2022-01-01', periods=10),
            'Value': np.random.normal(0, 1, 10),
            'var_class': ['upper_outlier', 'lower_outlier', None, None,
                          'upper_outlier', None, None, 'lower_outlier', None, None]
        })

        plot_outliers_only(pd.DataFrame(), 'Date', 'Value')


if __name__ == '__main__':
    unittest.main()
