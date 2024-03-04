import os
import importlib.util
import sys

# Constantes
BUILTIN_MODULES = sys.builtin_module_names


TYPES = {
    1: "Built in import: 'import os' or 'import sys' or 'import re'...",
    2: "Simple import: 'import modulo' or 'import modulo.modulo2'...",
}

def handle_import_line(import_line: str, file_path:os.PathLike = "") -> str:
    """
        This function gets the import line/lines from the file and choose the right handler.
        Returns:
            str: code to be appended to the new code
    """

    if import_line.strip().startswith("import "):
        print("Começando com import")
        return handle_direct_import(import_line, file_path)

    elif import_line.strip().startswith("from "):
        content = handle_relative_import(import_line, file_path)
        raise Exception(f'NÃO QUERO ISSO. Import: {import_line}')

    else:
        raise Exception(f'Import Line is Not Valid. Import: {import_line}')
    

def handle_direct_import(import_line: str, file_path:os.PathLike = "") -> str:
    """
        This funcion handles direct imports like:
            - import os
            - import pandas as pd
            - import modulo1.modulo2.modulo3 as m3
        If it is a built-in import, the function will return the import line as it is.
        Else, the function will return the content of the file and its dependencies.
        Returns:
            str: code to be appended to the file
    """
    content=""

    parts_of_line = import_line.split(' ')
    if any(part in BUILTIN_MODULES for part in parts_of_line):
        return import_line # Built-in import
    
    #add file folder to the path
    sys.path.append(os.path.dirname(file_path))
    
    import_path = importlib.util.find_spec(import_line.strip().split(' ')[1])
    if import_path is None:
        raise Exception(f'Error: Import is not found. Import: {import_line}') # Import not found
    
    import_path = import_path.origin
    print("Import path: ", import_path)
    
    
    with open(import_path, 'r', encoding="utf-8") as file:
        content += file.read()
    
    return content 

def handle_relative_import(import_line: str) -> str:
    pass

def handle_import_type_1(import_line, file_path:str ="") -> str:
    """
        This function handles the import of built in libs.
        For built-in imports, the function will return the import line as it is.
        Example:
            import os
            

        Returns:
            str: code to be appended to the file
    """
    import_path = importlib.util.find_spec(import_line.strip().split(' ')[1])
    if import_path is None:
        raise Exception(f'Built-in import is not found. Import: {import_line}')
    return import_line

def handle_import_type_2(import_line, file_path:str ="") -> str:
    """
        This function handles the simplest way to import a module.
        For simple imports, the function will return the content of the file.
        Example:
            import teste.teste1
            
        Returns:
            str: code to be appended to the file
    """
    import_path = importlib.util.find_spec(import_line.strip().split(' ')[1])
    if import_path is None:
        raise Exception(f'Error: Import is not found. Import: {import_line}')
    import_path = import_path.origin
    tabs = ""
    for char in import_line:
        if char == ' ':
            tabs += ' '
        else:
            break
    content = read_file(import_path)
    content = "\n".join([tabs + line for line in content.split('\n')])
    content = append_code(content, import_path)
    return content
