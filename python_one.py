"""This library uses the `importlib` library to import the libraries and the `inspect` library to get the source code of the libraries. It then creates a new file and writes the source code of the libraries in it. It also adds a `__all__` variable to the file to make it easier to import the libraries."""
import importlib
import os
import re
import importlib.util
from handlers import handle_import_line

OK                  = 0
FILE_NOT_FOUND      = 1
FILE_IS_NOT_PYTHON  = 2
IMPORT_IS_NOT_FOUND = 3

dict_errors = {
    FILE_NOT_FOUND: 'File not found',
    FILE_IS_NOT_PYTHON: 'File is not a Python file',
    IMPORT_IS_NOT_FOUND: 'Import is not found'
}

USED_MODULES = []

def verify_file(start_file: os.PathLike) -> int:
    """
        Verify if the file exists and if it is a Python file.
        Returns:
            OK: If the file exists and is a Python file
            FILE_NOT_FOUND: If the file does not exist
            FILE_IS_NOT_PYTHON: If the file is not a Python file

    """
    if not os.path.exists(start_file):
        print(dict_errors[FILE_NOT_FOUND])
        return FILE_NOT_FOUND
    
    if not start_file.endswith('.py'):
        print(dict_errors[FILE_IS_NOT_PYTHON])
        return FILE_IS_NOT_PYTHON
    global ACTUAL_DIR
    ACTUAL_DIR = os.path.dirname(os.path.abspath(start_file))
    return OK

def clean_file(content: str) -> str:
    content = content.replace('\\\n', '\n')
    content = content.replace('\\\r', '\r')

    #se depois do " import " tiver um "(" e um ")" é uma importação de um módulo que está em outro arquivo
    #substituir o "(" e tudo  dentro por *
    content = re.sub(r'import \((\s+.*,\n)+\s+\)', 'import *', content)
    return content

def read_file(start_file: os.PathLike) -> str:
    """
        Read the file and return its content.
        Returns:
            str: The content of the file
        Raises:
            Exception: If the file does not exist or is not a Python file.
    """
    print("*"*20)
    print("Reading file " + start_file)
    print("*"*20)
    print("\n")
    file_status = verify_file(start_file)
    if file_status != OK:
        raise Exception(f'Error: {file_status}. File: {start_file}')
    
    content = ''
    with open(start_file, 'r', encoding="utf-8") as file:
        content = file.read()

    content = clean_file(content)
    return content

def convert_imports_to_code(import_line: str, file_path:os.PathLike = "") -> str:
    """
        Convert the imports to code.
        Returns:
            str: The code of the imports
    """
    tabs = ""
    for char in import_line:
        if char == ' ':
            tabs += ' '
        else:
            break
    
    content = handle_import_line(import_line, file_path)
    content = "\n".join([tabs + line for line in content.split('\n')])
    content = append_code(content, file_path)
    return content

def append_code(content: str, file_path:str) -> str:
    """
        Get the imports of the file.
        Returns:
            None
    """
    new_code = ''
    line_n=0
    for line in content.split('\n'):
        #pegando os tabs no inicio da linha
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            new_code += convert_imports_to_code(line, file_path) + '\n'
        else:
            new_code = new_code + line + '\n'
        line_n += 1
    return new_code


"""
fluxo:
    read_file -> verify_file -> append_code -> convert_imports_to_code -> generate_new_code
                                        ^                |
                                        |                v
                                             read_file 
"""     


def main(start_file: os.PathLike) -> None:
    """
        Main function
    """
    abs_path = os.path.abspath(start_file)
    content = read_file(abs_path)
    content = append_code(content, start_file)
    print(content)

if __name__ == '__main__':
    main('tests/test_import_type_2.py')