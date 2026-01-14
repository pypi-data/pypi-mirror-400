**ma_python_package**

Simplicity, Standardization, And Speed

---

Creating and utilizing a Python package offers a myriad of advantages in data handling processes. Firstly, it serves as a powerful tool to streamline repetitive coding tasks, enhancing efficiency and reducing the likelihood of errors. Moreover, Python packages facilitate the standardization of data processing methodologies, ensuring uniformity across different projects and modules. By centralizing dependencies required for data manipulation, packages simplify the management of project requirements, enhancing portability and reproducibility. Additionally, they enable rapid data visualization, aiding in the interpretation and communication of insights. Furthermore, Python packages allow for the implementation of robust execution and logging scripts, facilitating the monitoring and management of workflows, thereby promoting transparency and accountability in project development.

---

**Installation**

You can install `ma_python` package using pip with the following command:

```bash
pip install git+<url>
```

---

**Modules**

1. **data_processing**:
   Centralizes functions for handling data tasks, from reading and saving data to processing it in the MassTer format.
   - Example functions: `read_data`, `save_data`, `pivot_by_key`, `get_mapping_table`, `change_periodicity`, `split_dates`, `map_table`.

2. **data_summary**:
   Contains functions to summarize data information at different levels, such as data size, available date columns, periodicity, and numerical summaries.
   - Example functions: `get_date_column`, `get_periodicity`, `data_summary`, `categorical_summary`, `numerical_summary`.

3. **data_utils**:
   Houses utility functions to assist with various tasks, like anonymizing data.
   - Example functions: `anonymize_data`.

4. **data_check**:
   Provides functions for checking data integrity, including available dates, duplicated rows, outliers, and missing values. These are integrated into the Data Checker tool.
   - Example functions: `check_available_dates`, `check_duplication`, `check_missing_values`, `check_outliers`.

5. **data_visualization**:
   Offers essential graphical functions for plotting data with ease.
   - Example functions: `plot_time_series`, `plot_two_time_series`, `plot_piechart`, `plot_avm`, `plot_bar_chart`, `plot_histogram`.

6. **workflow_management**:
   Includes functions for creating and monitoring workflows and pipelines, such as executing scripts and logging workflows.
   - Example functions: `execute`, `execute_all`, `log_in`, `log_out`, `get_error`, `plan_task`.

7. **script_management**:
   Provides functions for checking script quality and conformity with coding conventions and best practices.
   - Example functions: `get_variable_function_names`, `check_code_quality`, `check_mstr_task`.

---

Feel free to explore the functionalities of each module and leverage the power of `ma_python` package for your data handling needs. If you have any questions or feedback, please don't hesitate to reach out.