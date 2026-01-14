# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 14:30:43 2024

@author: MejdiTRABELSI
"""

import unittest
import pandas as pd
import sys
sys.path.append('../')
from ma_python_package.data_processing import (read_data,
                                               save_data,
                                               pivot_by_key,
                                               get_mapping_table,
                                               map_table,
                                               change_periodicity,
                                               split_value_by_day,
                                               calculate_categorical_counts_over_time)
from tempfile import TemporaryDirectory
import os


class TestReadData(unittest.TestCase):

    def test_read_single_csv(self):
        # Test reading a single CSV file
        df = read_data('../test_data/snapchat.csv', header=0)
        self.assertIsInstance(df, pd.DataFrame)
        # Assuming there are 3 rows in the CSV file
        self.assertEqual(len(df), 3448)

    def test_read_multiple_files(self):
        # Test reading multiple files in a folder
        df = read_data('../test_data/multiple_files/', header=0)
        self.assertIsInstance(df, pd.DataFrame)
        # Assuming there are 6 rows in total in all files
        self.assertEqual(len(df), 6459)

    def test_different_structures(self):
        # Test if different structures in folder raise an error
        with self.assertRaises(ValueError):
            read_data('../test_data/different_structures/', header=0)

    def test_invalid_path(self):
        # Test if an invalid path raises an error
        with self.assertRaises(ValueError):
            read_data('invalid_path')


class TestSaveData(unittest.TestCase):
    def test_overwrite_mode(self):
        with TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_overwrite.xlsx")
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            save_data(df, temp_file)
            self.assertTrue(os.path.exists(temp_file))

    def test_append_new_mode(self):
        with TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_append_new.xlsx")
            df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            df2 = pd.DataFrame({'A': [4, 5, 6], 'B': [7, 8, 9]})
            save_data(df1, temp_file)
            save_data(df2, temp_file, mode='append-new')
            df_expected = pd.concat(
                [df1, df2], ignore_index=True).drop_duplicates()
            df_result = pd.read_excel(temp_file)
            self.assertTrue(df_expected.equals(df_result))

    def test_append_old_mode(self):
        with TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_append_old.xlsx")
            df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            df2 = pd.DataFrame({'A': [4, 5, 6], 'B': [7, 8, 9]})
            save_data(df1, temp_file)
            save_data(df2, temp_file, mode='append-old')
            df_expected = pd.concat(
                [df2, df1], ignore_index=True).drop_duplicates()
            df_result = pd.read_excel(temp_file)
            self.assertTrue(df_expected.equals(df_result))

    def test_invalid_mode(self):
        data = {'A': [1, 2], 'B': [3, 4]}
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError) as cm:
            save_data(df, 'output.xlsx', mode='invalid-mode')
        self.assertEqual(str(
            cm.exception), "Invalid mode. Supported modes are 'overwrite', 'append-new', and 'append-old'.")

    def test_invalid_extension(self):
        data = {'A': [1, 2], 'B': [3, 4]}
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError) as cm:
            save_data(df, 'output.invalid', mode='overwrite')
        self.assertEqual(str(
            cm.exception), "Invalid output file extension. Supported formats are CSV, Excel, and Parquet.")

    def test_column_structure_mismatch(self):
        data1 = {'A': [1, 2], 'B': [3, 4]}
        data2 = {'C': [5, 6], 'D': [7, 8]}
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        with self.assertRaises(ValueError) as cm:
            save_data(df1, 'output.xlsx', mode='append-new', subset=['A'])
            save_data(df2, 'output.xlsx', mode='append-new', subset=['C'])
        self.assertEqual(
            str(cm.exception), "Existing file and new data have different column structures.")


class TestPivotByKey(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'Date': ['1/1/2020', '1/2/2020', '1/3/2020'],
            'col1': ['A', 'B', 'C'],
            'col2': ['X', 'Y', 'Z'],
            'price': [10, 11, 15],
            'nb': [2, 1, 3]
        })

    def test_pivot_sum(self):
        expected_result = pd.DataFrame({
            'Date': ['1/1/2020', '1/2/2020', '1/3/2020'],
            'A_X_nb': [2, 0, 0],
            'B_Y_nb': [0, 1, 0],
            'C_Z_nb': [0, 0, 3],
            'A_X_price': [10, 0, 0],
            'B_Y_price': [0, 11, 0],
            'C_Z_price': [0, 0, 15]
        })
        result = pivot_by_key(self.df, index_column_names='Date', key_column_names=['col1', 'col2'],
                              values_column_names=['price', 'nb'])
        pd.testing.assert_frame_equal(result, expected_result)

    def test_pivot_mean(self):
        expected_result = pd.DataFrame({
            'Date': ['1/1/2020', '1/2/2020', '1/3/2020'],
            'A_X_nb': [2, 0, 0],
            'B_Y_nb': [0, 1, 0],
            'C_Z_nb': [0, 0, 3],
            'A_X_price': [10, 0, 0],
            'B_Y_price': [0, 11, 0],
            'C_Z_price': [0, 0, 15]
        })
        result = pivot_by_key(self.df, index_column_names='Date', key_column_names=['col1', 'col2'],
                              values_column_names=['price', 'nb'], agg='mean')
        pd.testing.assert_frame_equal(result, expected_result)


class TestGetMappingTable(unittest.TestCase):
    def setUp(self):
        self.data = {
            'Date': ['2023-07-01', '2023-07-02', '2023-07-03'],
            'Product': ['A', 'B', 'C'],
            'Category': ['X', 'Y', 'Z'],
            'Price': [100, 150, 200],
        }
        self.df = pd.DataFrame(self.data)

    def test_normal_conditions(self):
        result = get_mapping_table(self.df, date_column_name='Date', column_values=[
                                   'Product', 'Category'], freq='D')
        # 3 dates * 3 unique products * 3 unique categories
        self.assertEqual(len(result), 27)

    def test_with_start_and_end_date(self):
        result = get_mapping_table(self.df, date_column_name='Date', column_values=[
                                   'Product', 'Category'], freq='D', start_date='2023-07-01', end_date='2023-07-02')
        # 2 dates * 3 unique products * 3 unique categories
        self.assertEqual(len(result), 18)

    def test_with_single_column_value(self):
        result = get_mapping_table(
            self.df, date_column_name='Date', column_values=['Product'], freq='D')
        self.assertEqual(len(result), 9)  # 3 dates * 3 unique products

    def test_with_no_column_values(self):
        result = get_mapping_table(
            self.df, date_column_name='Date', column_values=[], freq='D')
        self.assertEqual(len(result), 3)  # 3 dates

    def test_with_nonexistent_column(self):
        with self.assertRaises(KeyError):
            get_mapping_table(self.df, date_column_name='Date',
                              column_values=['Nonexistent'], freq='D')

    def test_with_nonexistent_date_column(self):
        with self.assertRaises(KeyError):
            get_mapping_table(self.df, date_column_name='Nonexistent', column_values=[
                              'Product'], freq='D')


class TestMapTable(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'Date': pd.to_datetime(['2023-08-01', '2023-08-02', '2023-08-03', '2023-08-04', '2023-08-05']),
            'Value': [10, 20, 30, 40, 50]
        })
        self.mapping_table = pd.DataFrame({
            'Date': pd.to_datetime(['2023-08-01', '2023-08-03']),
            'Label': ['Label A', 'Label B']
        })

    def test_map_table(self):
        result_df = map_table(self.df, self.mapping_table)
        expected_df = pd.DataFrame({
            'Date': pd.to_datetime(['2023-08-01', '2023-08-03']),
            'Label': ['Label A', 'Label B'],
            'Value': [10, 30]
        })
        pd.testing.assert_frame_equal(result_df, expected_df)


class TestChangePeriodicity(unittest.TestCase):

    def setUp(self):
        # Create sample dataframes for testing
        self.daily_df = pd.DataFrame({
            'date_column': pd.date_range(start='2022-01-01', end='2022-01-10'),
            'value': range(1, 11)
        })

        self.weekly_df = pd.DataFrame({
            'date_column': pd.date_range(start='2022-01-01', periods=10, freq='W'),
            'value': range(1, 11)
        })

        self.monthly_df = pd.DataFrame({
            'date_column': pd.date_range(start='2022-01-01', periods=10, freq='M'),
            'value': range(1, 11)
        })

    def test_daily_to_weekly(self):
        weekly_df = change_periodicity(self.daily_df, 'date_column', 'W-SUN')
        # Ensure the output DataFrame has the expected number of rows
        self.assertEqual(len(weekly_df), 3)

    def test_daily_to_monthly(self):
        monthly_df = change_periodicity(self.daily_df, 'date_column', 'M')
        # Ensure the output DataFrame has the expected number of rows
        self.assertEqual(len(monthly_df), 1)

    def test_weekly_to_daily(self):
        daily_df = change_periodicity(self.weekly_df, 'date_column', 'D')
        # Ensure the output DataFrame has the expected number of rows
        self.assertEqual(len(daily_df), 70)

    def test_weekly_to_monthly(self):
        monthly_df = change_periodicity(self.weekly_df, 'date_column', 'M')
        # Ensure the output DataFrame has the expected number of rows
        self.assertEqual(len(monthly_df), 3)

    def test_monthly_to_daily(self):
        daily_df = change_periodicity(self.monthly_df, 'date_column', 'D')
        # Ensure the output DataFrame has the expected number of rows
        self.assertEqual(len(daily_df), 304)

    def test_monthly_to_weekly(self):
        weekly_df = change_periodicity(self.monthly_df, 'date_column', 'W-SUN')
        # Ensure the output DataFrame has the expected number of rows
        self.assertEqual(len(weekly_df), 45)


class TestSplitValueByDay(unittest.TestCase):

    def test_additive_true_with_categorical_col(self):
        data = {
            'start_date': pd.to_datetime(['2023-01-01', '2023-01-02']),
            'end_date': pd.to_datetime(['2023-01-02', '2023-01-04']),
            'val': [200, 900],
            'categorical_col': ['DC', 'TX']
        }
        df = pd.DataFrame(data)
        result_df = split_value_by_day(
            df, 'start_date', 'end_date', 'val',
            additive=True, categorical_col='categorical_col')
        expected_df = pd.DataFrame({
            'categorical_col': ['DC', 'DC', 'TX', 'TX', 'TX'],
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02',
                                    '2023-01-02', '2023-01-03', '2023-01-04']),
            'val': [100.0, 100.0, 300.0, 300.0, 300.0]
        })
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_additive_false_without_categorical_col(self):
        data = {
            'start_date': pd.to_datetime(['2023-01-01', '2023-01-02']),
            'end_date': pd.to_datetime(['2023-01-02', '2023-01-04']),
            'val': [200, 800],
        }
        df = pd.DataFrame(data)
        result_df = split_value_by_day(
            df, 'start_date', 'end_date', 'val', additive=False)
        expected_df = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04']),
            'val': [200.0, 500.0, 800.0, 800.0]
        })
        pd.testing.assert_frame_equal(result_df, expected_df)


class TestCalculateCategoricalCountsOverTime(unittest.TestCase):
    # Test case for when division_col is None
    def test_calculate_categorical_counts_no_division(self):
        # Create sample data
        data = {
            'date_col': ['2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03', '2023-01-04'],
            'categorical_col': ['A', 'B', 'A', 'B', 'C']
        }
        df = pd.DataFrame(data)

        # Call the function
        result_df = calculate_categorical_counts_over_time(
            df, 'date_col', 'categorical_col')

        # Define the expected output
        expected_output = pd.DataFrame({
            'date_col': pd.date_range(start='2023-01-01', end='2023-01-04'),
            'categorical_col_nb': [1, 2, 2, 3]
        })

        # Check if the actual output matches the expected output
        pd.testing.assert_frame_equal(
            result_df, expected_output, check_dtype=False)

    # Test case for when division_col is provided
    def test_calculate_categorical_counts_with_division(self):
        # Create sample data
        data = {
            'date_col': ['2023-01-01', '2023-01-02', '2023-01-02',
                         '2023-01-03', '2023-01-04', '2023-01-05',
                         '2023-01-05'],
            'categorical_col': ['A', 'B', 'A', 'B', 'A', 'C', 'C'],
            'division_col': ['X', 'X', 'Y', 'Y', 'X', 'Y', 'X']
        }
        df = pd.DataFrame(data)

        # Call the function
        result_df = calculate_categorical_counts_over_time(
            df, 'date_col', 'categorical_col', division_col='division_col')

        # Define the expected output
        expected_output = pd.DataFrame({
            'date_col': pd.date_range(start='2023-01-01', end='2023-01-05'),
            'categorical_col_X_nb': [1, 2, 2, 2, 3],
            'categorical_col_Y_nb': [0, 1, 2, 2, 3]
        })

        # Check if the actual output matches the expected output
        pd.testing.assert_frame_equal(
            result_df, expected_output, check_dtype=False)

    # Test case for when columns are not found in the DataFrame
    def test_columns_not_found(self):
        # Create sample data
        data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03', '2023-01-04'],
            'category': ['A', 'B', 'A', 'B', 'A']
        }
        df = pd.DataFrame(data)

        # Call the function and expect it to raise a ValueError
        with self.assertRaises(ValueError):
            calculate_categorical_counts_over_time(
                df, 'date_col', 'categorical_col', division_col='division_col')

    def setUp(self):
        # Create a sample DataFrame for testing
        self.df = pd.DataFrame({
            'date_col': ['2022-01-01', '2022-01-01', '2022-01-02', '2022-01-02', '2022-01-03'],
            'categorical_col': ['A', 'B', 'A', 'C', 'B'],
            'division_col': ['X', 'X', 'Y', 'Y', 'X']
        })

    def test_valid_output(self):
        # Test the function with valid inputs
        result = calculate_categorical_counts_over_time(
            self.df, 'date_col', 'categorical_col')
        self.assertEqual(len(result), 3)  # Expecting 3 rows for 3 unique dates
        # Check if the expected column is present
        self.assertTrue('categorical_col_nb' in result.columns)

    def test_invalid_date_column(self):
        # Test the function with an invalid date column
        with self.assertRaises(ValueError):
            calculate_categorical_counts_over_time(
                self.df, 'invalid_date_col', 'categorical_col')

    def test_invalid_categorical_column(self):
        # Test the function with an invalid categorical column
        with self.assertRaises(ValueError):
            calculate_categorical_counts_over_time(
                self.df, 'date_col', 'invalid_categorical_col')

    def test_invalid_division_column(self):
        # Test the function with an invalid division column
        with self.assertRaises(ValueError):
            calculate_categorical_counts_over_time(
                self.df, 'date_col', 'categorical_col', 'invalid_division_col')

    def test_invalid_dates(self):
        # Test the function with invalid dates in the date column
        self.df.at[0, 'date_col'] = 'invalid_date'
        with self.assertRaises(ValueError):
            calculate_categorical_counts_over_time(
                self.df, 'date_col', 'categorical_col')


if __name__ == '__main__':
    unittest.main()
