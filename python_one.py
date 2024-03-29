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
USED_IMPORTS = []

ONE_CODE = ""

DEPTH_MODULES_DICT = {}

def verify_file(start_file: os.PathLike) -> int:
    """
        Verify if the file exists and if it is a Python file.
        Returns:
            OK: If the file exists and is a Python file
            FILE_NOT_FOUND: If the file does not exist
            FILE_IS_NOT_PYTHON: If the file is not a Python file

    """
    if not os.path.exists(start_file):
        return FILE_NOT_FOUND
    
    if not start_file.endswith('.py'):
        return FILE_IS_NOT_PYTHON
    global ACTUAL_DIR
    ACTUAL_DIR = os.path.dirname(os.path.abspath(start_file))
    return OK

def clean_file(content: str) -> str:
    content = content.replace('\\\n', ' ')
    content = content.replace('\\\r', ' ')
    content = re.sub(r'#.*\n', '\n', content) #pegando todas as ocorrencias de comentarios com quebra de linha

    #pegando todas as ocorrencias de parenteses com quebra de linha
    pattern = r'import\s*\(.*?\)'
    parenteses = re.findall(pattern, content, re.DOTALL)
    for parentese in parenteses:
        content = content.replace(parentese, parentese.replace('\n',' '))
    with open('result.txt', 'w') as file:
        file.write(content)
    return content

def read_file(start_file: os.PathLike) -> str:
    """
        Read the file and return its content.
        Returns:
            str: The content of the file
        Raises:
            Exception: If the file does not exist or is not a Python file.
    """
    file_status = verify_file(start_file)
    if file_status != OK:
        raise Exception(f'Error: {file_status}. File: {start_file}')
    
    content = ''
    with open(start_file, 'r', encoding="utf-8") as file:
        content = file.read()

    content = clean_file(content)
    return content

def convert_imports_to_code(import_line: str, profundidade:int, file_path:os.PathLike = "") -> str:
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
    
    content = handle_import_line(import_line,DEPTH_MODULES_DICT[profundidade], file_path)
    content = "\n".join([tabs + line for line in content.split('\n')])
    content = append_code(content, file_path, profundidade+1)
    
    return content

def append_code(content: str, file_path:str, profundidade:int) -> str:
    """
        Get the imports of the file.
        Returns:
            None
    """
    DEPTH_MODULES_DICT[profundidade] = []
    new_code = ''
    line_n=0
    for line in content.split('\n'):
        #pegando os tabs no inicio da linha
        if (line.strip().startswith("from ") or line.strip().startswith("import ")) and line.strip() not in USED_IMPORTS:
            USED_IMPORTS.append(line.strip())
            print("\n","*"*50,"\n",)
            
            content = convert_imports_to_code(line,profundidade, file_path)
            if profundidade > 0:
                DEPTH_MODULES_DICT[profundidade] = []
            content+= '\n'
            new_code += content
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
    
    PROFUNDIDADE = 0
    abs_path = os.path.abspath(start_file)
    content = read_file(abs_path)
    content = append_code(content, start_file, PROFUNDIDADE)
    file_name = os.path.basename(start_file).split('.')[0].split('\\')[-1]
    new_file = open(f'{file_name}_one.py', 'w', encoding="utf-8")
    new_file.write(content)
    new_file.close()


if __name__ == '__main__':
    #listando arquivos na pasta test
    print("CORRIGIR A IDENTAÇÃO DO ARQUIVO GERADO")
    main("tests/test_6.py")