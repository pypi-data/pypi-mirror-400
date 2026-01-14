import os
import datetime
import csv
import inspect 
import importlib.util
def get_next_id(log_file_path):
    """
    Generate the next unique ID for log entries.

    This function reads the existing log file, extracts the IDs, and generates the next ID in sequence. If the log file does not exist, it returns the initial ID "00000001".

    Parameters:
        log_file_path (str): The file path of the log CSV file.

    Returns:
        str: The next unique ID, formatted as an 8-digit string.

    Example:
        >>> get_next_id('path/to/log.csv')
        '00000002'
    """
    if not os.path.exists(log_file_path):
        return "00000001"  
    
    with open(log_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        existing_ids = [int(row['ID']) for row in reader]

    if existing_ids: 
        next_id = max(existing_ids) + 1
        return f"{next_id:08}" 
    else:
        return "00000001"

def log_in(custom_log_path, input_path, output_path):
    """
    Initialize logging process and create necessary files.

    This function sets up the logging environment by creating the log folder and log CSV file if they do not exist. It then logs the start of a new process and returns the new log entry ID and the log file path.

    Parameters:
        custom_log_path (str): The custom path where the log folder should be created.
        input_path (str or dict): The path of the input file or a dictionary.
        output_path (str): The path of the output file.

    Returns:
        tuple: A tuple containing the new log entry ID and the log file path.

    Example:
        >>> log_in('/path/to/custom_log', '/path/to/input', '/path/to/output')
        ('00000001', '/path/to/custom_log/log/log.csv')
    """
    start_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_folder_path = os.path.join(custom_log_path, 'log')
    
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)
        print("Log folder not found. Creating 'log' folder.")
    else:
        print("Found 'log' folder.")
    
    log_file_path = os.path.join(log_folder_path, 'log.csv')
    
    next_id = get_next_id(log_file_path) 
    
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Start Date", "End Date", "Input Path", "Output Path", "Status", "Error Message"])
        print("Log CSV file not found. Creating 'log.csv'.")
    else:
        print("Found 'log.csv' file.")
        
    
    # Convert input_path to string if it's a dictionary
    if isinstance(input_path, dict):
        input_path = str(input_path)
    
    with open(log_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([next_id, start_date, "", input_path, output_path, "", ""])
    
    return next_id, log_file_path
def get_function(script_path):
    """
    Import a Python script as a module and retrieve a function from it.

    This function dynamically imports a Python script based on its file path and retrieves a function whose name matches the script's filename.

    Parameters:
        script_path (str): The file path of the Python script.

    Returns:
        function: The function object retrieved from the module.

    Raises:
        ValueError: If no function matching the script name is found in the module.

    Example:
        >>> get_function('/path/to/script.py')
        <function script at 0x...>
    """
    module_name = os.path.splitext(os.path.basename(script_path))[0]

    # Load the module from the specified file path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None:
        raise ImportError(f"Cannot load the module from path '{script_path}'")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Retrieve the function from the module
    func = getattr(module, module_name, None)
    
    if func is None or not callable(func):
        raise ValueError(f"No function named '{module_name}' found in module '{module_name}'")
    
    return func

def get_signature(func):
    """
    Retrieve the signature of a given function.

    This function returns the signature of a provided function, detailing its parameters.

    Parameters:
        func (function): The function whose signature is to be retrieved.

    Returns:
        inspect.Signature: The signature of the function.

    Example:
        >>> get_signature(my_function)
        <Signature (param1, param2, param3)>
    """
    return inspect.signature(func)

def compare_signature(signature, parameters):
    """
    Compare function signature with provided parameters.

    This function checks if the provided parameters match the required parameters of the function's signature, considering default values for parameters.

    Parameters:
        signature (inspect.Signature): The signature of the function.
        parameters (dict): The parameters to compare with the function's signature.

    Raises:
        ValueError: If required parameters are missing.

    Example:
        >>> compare_signature(get_signature(my_function), {'param1': 1, 'param2': 2})
    """
    required_params = [param for param, param_info in signature.parameters.items() if param_info.default == inspect.Parameter.empty]
    
    if not all(param in parameters for param in required_params):
        raise ValueError("Required parameters are missing")
def get_error(error_message):
    """
    Log an error message.

    This function logs an error message in a global variable to be accessed later by other functions.

    Parameters:
        error_message (str): The error message to be logged.

    Example:
        >>> get_error('An error occurred')
    """
    global error_raised
    error_raised = True
    if 'errors' not in globals():
        global errors
        errors = []
    errors.append(error_message)
def log_out(log_file_path, start_id):
    """
    Update the log file with end date and status.

    This function updates the log entry with the given ID, setting the end date, status, and any error messages.

    Parameters:
        log_file_path (str): The file path of the log CSV file.
        start_id (str): The ID of the log entry to be updated.

    Example:
        >>> log_out('/path/to/log.csv', '00000001')
    """
    end_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = 'ok'
    
    if 'error_raised' in globals() and error_raised:
        status = 'ko'
    
    with open(log_file_path, mode='r+', newline='') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        
        if rows:
            rows[int(start_id) - 1]['End Date'] = end_date
            rows[int(start_id) - 1]['Status'] = status
            
            if 'errors' in globals():
                rows[int(start_id) - 1]['Error Message'] = '\n'.join(errors)
            
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            file.seek(0)
            writer.writeheader()
            writer.writerows(rows)
            print(f"Updated end date and status of entry with ID {start_id} in 'log.csv' to: {end_date}, {status}")
        else:
            print("No entries found in 'log.csv'.")

def execute(script_path, parameters):
    """
    Execute a function from a script with logging and error handling.

    This function orchestrates the execution of a function from a script, handles logging of start and end times, and records any errors that occur.

    Parameters:
        script_path (str): The file path of the Python script to be executed.
        parameters (dict): The parameters to be passed to the function.

    Returns:
        bool: True if an error occurred, False otherwise.

    Example:
        >>> execute('/path/to/script.py', {'input_path': '/path/to/input', 'output_path': '/path/to/output', 'param1': 1, 'param2': 2})
        False
    """
    error_raised = False
    log_file_path = None
    parent_dir = os.path.dirname(os.path.dirname(script_path))

    try:
        input_path = parameters.get('input_path', '')
        output_path = parameters.get('output_path', '')
        
        # Convert input_path to string if it's a dictionary
        if isinstance(input_path, dict):
            input_path = str(input_path)
        
        start_id, log_file_path = log_in(parent_dir, input_path, output_path)
        func = get_function(script_path)
        signature = get_signature(func)
        compare_signature(signature, parameters)
        
        func(**parameters)
        
    except Exception as e:
        error_raised = True
        get_error(str(e))
        
    finally:
        if log_file_path:
            log_out(log_file_path, start_id)  
    
    return error_raised
