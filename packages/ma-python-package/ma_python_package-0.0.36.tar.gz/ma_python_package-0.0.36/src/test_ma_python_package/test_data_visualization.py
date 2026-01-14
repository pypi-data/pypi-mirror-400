# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 13:02:51 2024

@author: MejdiTRABELSI
"""
import unittest
import pandas as pd
import numpy as np
from plotly.graph_objs._figure import Figure
import sys
sys.path.append('../')
from ma_python_package.data_visualization import (plot_pie_chart)


class TestDonutChart(unittest.TestCase):
    def setUp(self):
        # Create sample DataFrame for testing
        data = {
            'Category': ['A', 'B', 'C', 'A', 'B', 'C'],
            'Value': [100, 200, 300, 400, 500, 600]
        }
        self.df = pd.DataFrame(data)

    def test_output_type(self):
        # Check if the function returns a Plotly Figure object
        figure = plot_pie_chart(self.df, 'Category', 'Value', return_fig=True)
        self.assertIsInstance(figure, Figure)

    def test_default_colors(self):
        # Check if default colors are used when colors parameter is not provided
        figure = plot_pie_chart(self.df, 'Category', 'Value', return_fig=True)
        colors = figure.data[0].marker.colors
        self.assertIsNotNone(colors)
        # Check if 10 default colors are used
        self.assertEqual(len(colors), 9)

    def test_custom_colors(self):
        # Check if custom colors are used when colors parameter is provided
        custom_colors = ('#FF9999', '#66B2FF', '#99FF99')
        figure = plot_pie_chart(
            self.df, 'Category', 'Value', colors=custom_colors,
            return_fig=True)
        colors = figure.data[0].marker.colors
        self.assertEqual(colors, custom_colors)

    def test_title(self):
        # Check if the title is set correctly
        title = "Test Title"
        figure = plot_pie_chart(self.df, 'Category', 'Value', title=title,
                                return_fig=True)
        self.assertEqual(figure.layout.title.text, title)

    def test_show_percent(self):
        # Check if percentages are displayed when show_percent parameter is True
        figure = plot_pie_chart(
            self.df, 'Category', 'Value', show_percent=True, return_fig=True)
        text_info = figure.data[0].textinfo
        self.assertIn('percent', text_info)

    def test_invalid_columns(self):
        # Check if the function raises ValueError for invalid column names
        with self.assertRaises(ValueError):
            plot_pie_chart(self.df, 'Invalid_Column', 'Value')

    def test_non_numeric_values(self):
        # Check if the function raises ValueError when the numerical column contains non-numeric values
        self.df.loc[0, 'Value'] = 'string'  # Insert non-numeric value
        with self.assertRaises(ValueError):
            plot_pie_chart(self.df, 'Category', 'Value')


if __name__ == '__main__':
    unittest.main()
