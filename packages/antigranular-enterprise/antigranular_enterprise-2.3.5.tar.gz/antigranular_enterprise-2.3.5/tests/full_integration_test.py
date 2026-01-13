import nbformat
from nbclient import NotebookClient
import re
import sys

def execute_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Custom exception handling
    def custom_exception_handler(runtime, exception):
        """
        This function logs the exception and continues the execution of the remaining cells.
        """
        # Continue execution by returning the error and outputs
        return (exception, runtime.result)

    client = NotebookClient(
        nb,
        timeout=600,
        kernel_name='python3',
        allow_errors=True  # allow continued execution despite errors
    )
    client.exception_handler = custom_exception_handler  # Assign the custom exception handler

    print(f"Executing {notebook_path}...")
    
    # The execute method does not need to be wrapped in a try/except block since we're handling exceptions per cell
    client.execute()

    output_path = f"{notebook_path.split('.')[0]}_executed.ipynb"
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    
    print(f"Execution completed. Output saved to {output_path}")
    
    return output_path

def compare_strings_ignore_numbers_and_ids(str1, str2):
    # Regular expression to find and replace numerical values and UUIDs in a string
    num_pattern = re.compile(r'\b\d+(\.\d+)?\b')

    # Remove numerical values
    str1_no_num = num_pattern.sub('', str1)
    str2_no_num = num_pattern.sub('', str2)
    
    return str1_no_num.strip() != str2_no_num.strip()


def validate_notebook_execution(original_nb_path, executed_nb_path):
    with open(original_nb_path, 'r', encoding='utf-8') as f:
        original_nb = nbformat.read(f, as_version=4)

    with open(executed_nb_path, 'r', encoding='utf-8') as f:
        executed_nb = nbformat.read(f, as_version=4)

    errors = []

    for idx, (orig_cell, executed_cell) in enumerate(zip(original_nb.cells, executed_nb.cells)):
        if orig_cell.cell_type == 'code':
            if "Connected to Antigranular server session id" in str(orig_cell.outputs):
                print(executed_cell.outputs)
                continue
            
            # empty list matching
            if bool(orig_cell.outputs) != bool(executed_cell.outputs): 
                    errors.append({
                        'cell_index': idx,
                        'expected_output': orig_cell.outputs,
                        'actual_output': executed_cell.outputs,
                        'input': orig_cell.source
                    })
            
            for orig_output, exec_output in zip(orig_cell.outputs, executed_cell.outputs):
                # Handle stream outputs
                if (orig_output.get('output_type') == 'stream' and exec_output.get('output_type') == 'error') or (orig_output.get('output_type') == 'error' and exec_output.get('output_type') == 'stream'):
                    errors.append({
                        'cell_index': idx,
                        'expected_output': orig_output.get('text', ''),
                        'actual_output': {'ename': exec_output.get('ename', ''), 'evalue': exec_output.get('evalue', '')},
                        'input': orig_cell.source,
                        'error_in_output': True
                    })

                if exec_output.get('output_type') == 'stream':
                    orig_text = orig_output.get('text', '')
                    exec_text = exec_output.get('text', '')
                    if compare_strings_ignore_numbers_and_ids(orig_text, exec_text):
                        errors.append({
                            'cell_index': idx,
                            'expected_output': orig_text,
                            'actual_output': exec_text,
                            'input': orig_cell.source 
                        })

                # Handle error outputs
                elif exec_output.get('output_type') == 'error':
                    orig_ename = orig_output.get('ename', '')
                    orig_evalue = orig_output.get('evalue', '')
                    exec_ename = exec_output.get('ename', '')
                    exec_evalue = exec_output.get('evalue', '')
                    
                    if orig_ename != exec_ename or compare_strings_ignore_numbers_and_ids(orig_evalue, exec_evalue):
                        errors.append({
                            'cell_index': idx,
                            'expected_output': {'ename': orig_ename, 'evalue': orig_evalue},
                            'actual_output': {'ename': exec_ename, 'evalue': exec_evalue},
                            'input': orig_cell.source
                        })
    
    return errors


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python full_integration_test.py [dev|prod]")
        sys.exit(1)
    
    env_name = sys.argv[1]
    list_of_notebooks = []
    
    if env_name == 'dev':
        list_of_notebooks = [
            "Sample_Example_RecordLinkage_dev.ipynb",
            "car evaluation.ipynb",
            "test negative scenarios dev.ipynb",
            "Sample_Example__SPLink.ipynb"
        ]
    elif env_name == 'prod':
        list_of_notebooks = [
             'car evaluation.ipynb',
             'DP Hypothesis Testing.ipynb', 
             'Drug Classification using 3 models.ipynb',
             'Exploration_ Adult population Dataset.ipynb', 
             'Exploring Patient Recovery Times.ipynb', 
             'Exploring the Wine Dataset and Trying Multiple ML Models for Prediction.ipynb', 
             'Iris classification using Random Forest (1).ipynb', 
             'Mastering AG Fundamentals - Quick overview of what to expect in AG.ipynb',
             'Mastering Privacy-First RecordLinkage _ Complete Guide (1).ipynb', 
             'Sample_Example_RecordLinkage.ipynb', 
             'Sample_Example__SPLink.ipynb',
             'test negative scenarios.ipynb',
             'Understanding the Use of SmartNoise Synthesizers.ipynb'
        ]

    found_discrepancies = False
    error_in_output = False
    for sample_notebook_path in list_of_notebooks:
        sample_notebook_path = env_name + '/' + sample_notebook_path
        executed_notebook_path = execute_notebook(sample_notebook_path) 
        discrepancies = validate_notebook_execution(sample_notebook_path, executed_notebook_path)
        print("----", end="\n\n")
        if discrepancies:
            found_discrepancies = True
            for error in discrepancies:
                if error.get('error_in_output', False):
                    error_in_output = True
                print(f"Discrepancy in cell {error['cell_index']}:")
                print(f"Expected Output: {error['expected_output']}")
                print(f"Actual Output: {error['actual_output']}")
                print(f"Input: {error['input']}")
                print("----", end="\n")
        else:
            print("No discrepancies found!")
            print(f"Integration test passed for {executed_notebook_path} 🎉")

    if found_discrepancies and error_in_output:
        sys.exit(1)
