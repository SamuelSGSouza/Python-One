import os
import re
import sys
import importlib.util

import pkgutil

# Constantes
DEFAULT_MODULES = list(sys.builtin_module_names)
DEFAULT_PACKAGES = ['handlers','_asyncio', '_bz2', '_ctypes', '_ctypes_test', 
                    '_decimal', '_elementtree', '_hashlib', '_lzma', '_msi', 
                    '_multiprocessing', '_overlapped', '_queue', '_socket', 
                    '_sqlite3', '_ssl', '_testbuffer', '_testcapi', '_testconsole',
                      '_testimportmultiple', '_testinternalcapi', '_testmultiphase', 
                      '_tkinter', '_uuid', '_zoneinfo', 'pyexpat', 'select', 
                      'unicodedata', 'winsound', '__future__', '_aix_support', 
                      '_bootlocale', '_bootsubprocess', '_collections_abc', 
                      '_compat_pickle', '_compression', '_markupbase',
                        '_osx_support', '_py_abc', '_pydecimal', '_pyio',
                          '_sitebuiltins', '_strptime', '_threading_local',
                            '_weakrefset', 'abc', 'aifc', 'antigravity', 'argparse', 
                            'ast', 'asynchat', 'asyncio', 'asyncore', 'base64', 
                            'bdb', 'binhex', 'bisect', 'bz2', 'cProfile', 'calendar', 
                            'cgi', 'cgitb', 'chunk', 'cmd', 'code', 'codecs', 
                            'codeop', 'collections', 'colorsys', 'compileall', 
                            'concurrent', 'configparser', 'contextlib', 'contextvars', 
                            'copy', 'copyreg', 'crypt', 'csv', 'ctypes', 'curses', 
                            'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 
                            'dis', 'distutils', 'doctest', 'email', 'encodings', 
                            'ensurepip', 'enum', 'filecmp', 'fileinput', 'fnmatch', 
                            'formatter', 'fractions', 'ftplib', 'functools', 
                            'genericpath', 'getopt', 'getpass', 'gettext', 'glob', 
                            'graphlib', 'gzip', 'hashlib', 'heapq', 'hmac', 'html', 
                            'http', 'idlelib', 'imaplib', 'imghdr', 'imp', 'importlib', 
                            'inspect', 'io', 'ipaddress', 'json', 'keyword', 'lib2to3', 
                            'linecache', 'locale', 'logging', 'lzma', 'mailbox', 
                            'mailcap', 'mimetypes', 'modulefinder', 'msilib', 
                            'multiprocessing', 'netrc', 'nntplib', 'ntpath', 
                            'nturl2path', 'numbers', 'opcode', 'operator', 
                            'optparse', 'os', 'pathlib', 'pdb', 'pickle', 
                            'pickletools', 'pipes', 'pkgutil', 'platform', 
                            'plistlib', 'poplib', 'posixpath', 'pprint', 'profile',
                              'pstats', 'pty', 'py_compile', 'pyclbr', 'pydoc', 
                              'pydoc_data', 'queue', 'quopri', 'random', 're',
                                'reprlib', 'rlcompleter', 'runpy', 'sched', 'secrets',
                                  'selectors', 'shelve', 'shlex', 'shutil', 'signal', 
                                  'site', 'smtpd', 'smtplib', 'sndhdr', 
                                  'socket', 'socketserver', 'sqlite3', 
                                  'sre_compile', 'sre_constants', 'sre_parse',
                                    'ssl', 'stat', 'statistics', 'string', 'stringprep',
                                      'struct', 'subprocess', 'sunau', 'symbol', 
                                      'symtable', 'sysconfig', 'tabnanny', 'tarfile', 
                                      'telnetlib', 'tempfile', 'test', 'textwrap', 
                                      'this', 'threading', 'timeit', 'tkinter', 
                                      'token', 'tokenize', 'trace', 'traceback', 
                                      'tracemalloc', 'tty', 'turtle', 'turtledemo', 
                                      'types', 'typing', 'unittest', 'urllib', 'uu', 
                                      'uuid', 'venv', 'warnings', 'wave', 'weakref', 
                                      'webbrowser', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 
                                      'zipapp', 'zipfile', 'zipimport', 'zoneinfo', 
                                      '_distutils_hack', 'pip', 'pkg_resources', 
                                      'setuptools']
BUILTIN_MODULES = DEFAULT_MODULES + DEFAULT_PACKAGES

TYPES = {
    1: "Built in import: 'import os' or 'import sys' or 'import re'...",
    2: "Simple import: 'import modulo' or 'import modulo.modulo2'...",
}


def handle_import_line(import_line: str,USED_ROOT_MODULES: list, file_path:os.PathLike = "") -> str:
    """
        This function gets the import line/lines from the file and choose the right handler.
        
        Returns:
            str: code to be appended to the new code
    """

    if import_line.strip().startswith("import "):
        return handle_direct_import(import_line, file_path, USED_ROOT_MODULES)
        

    elif import_line.strip().startswith("from "):
        return handle_relative_import(import_line, file_path, USED_ROOT_MODULES)

    else:
        raise Exception(f'Import Line is Not Valid. Import: {import_line}')
    
def handle_direct_import(import_line: str, file_path:os.PathLike = "",USED_ROOT_MODULES: list = []) -> str:
    """
        This funcion handles direct imports like:
            - import os
            - import pandas as pd
            - import modulo1.modulo2.modulo3 as m3
        If it is a built-in import, the function will return the import line as it is.
        Otherwise, the function will handle the import as a class.
        
        Returns:
            str: code to be appended to the file
    """
    content=""

    import_cores = re.sub(r'^import ', '', import_line.strip()).split(",")
    for import_core in import_cores:
        import_core = import_core.strip()
        namespace = ""
        if " as " in import_core:
            parts = import_core.split(" as ")
            import_core = parts[0].strip()
            namespace = parts[1].strip()

        if import_core.strip() in BUILTIN_MODULES:
            content += "import " + import_core + "\n" # Built-in import
            continue
        
        sys.path.append(os.path.dirname(file_path)) #add file folder to the path

        import_path = importlib.util.find_spec(import_core)
        if import_path is None:
            raise Exception(f'Error: Import is not found. Import: {import_line}') # Import not found
    
        import_path = import_path.origin
        
        with open(import_path, 'r', encoding="utf-8") as file:
            content += file.read()

        classes_to_create = import_core.split('.')
        for class_name in reversed(classes_to_create):
            if class_name in USED_ROOT_MODULES:
               class_content = "class " + class_name + "(" + classes_to_create[0] + "):\n"
            else:
                class_content = "class " + class_name + ":\n"
                if class_name == classes_to_create[0]:
                    USED_ROOT_MODULES.append(classes_to_create[0])
            #fazendo cada linha receber um tab
            lines = "\n".join([f"   {line}" for line in content.split('\n')])
            class_content += lines
            content = class_content + "\n"        
        
        if namespace:
            content += namespace + " = " + import_core + "\n"

        sys.path.remove(os.path.dirname(file_path))
    return content

def handle_relative_import(import_line: str, file_path:os.PathLike = "" ,USED_ROOT_MODULES: list = []) -> str:
    """
        This function handles relative imports like:
            - from modulo_folder.modulo import Bolinho as bolinho
            - from modulo_folder.modulo import pastel
            - from modulo_folder import modulo

        Here, the function will convert the relative import to a direct import.

        Returns:
            str: code to be appended to the file

        Raises:
            Exception: If the import is not found
    """
    start_tabs = re.search(r'^\s*', import_line).group()
    import_origin = import_line.strip().split(" ")[1].strip()
    print("IMPORT ORIGIN:", import_origin)
    abs_dir = ""

    BACKUP_SYS_PATH = sys.path.copy()
    

    if import_origin.startswith("."):
        sys.path = []
        dots = re.search(r'^\.*', import_origin).group()
        
        abs_path = os.path.abspath(file_path)
        abs_dir = os.path.dirname(abs_path)
        for _ in range(len(dots)-1):
            abs_dir = os.path.dirname(abs_dir)
        
        import_origin = re.sub(r'^\.*', '', import_origin)

    elif import_origin.startswith("_"):
        return import_line
    else:
        import_dir_path = os.path.dirname(file_path)
        sys.path.append(import_dir_path)

        abs_dir = importlib.util.find_spec(import_origin)
        if abs_dir is None:
            raise Exception(f'Error: Import is not found. Import: {import_line}') # Import not found
    
        abs_dir = abs_dir.origin

    if abs_dir: #add temporary path to the sys.path
        sys.path.append(abs_dir)

    direct_import = convert_to_direct(import_line, file_path, USED_ROOT_MODULES)
    

    sys.path = BACKUP_SYS_PATH
    return direct_import

def convert_to_direct(import_line: str, file_path:os.PathLike = "" ,USED_ROOT_MODULES: list = []) -> str:
    """
        This function converts a relative import to a direct import.
        Then, the direct import will be handled by the handle_direct_import function.
        To the final code will be appended the alias of the import.
        
        Returns:
            str: code to be appended to the file
    """
    import_line = re.sub(r'\s*import\s*', '.', import_line)
    import_line = import_line.replace("from ", "import ")
    alias_dict = {}

    valid_module = False
    

    if " as " in import_line:
        alias_dict["alias"] = import_line.split(" as ")[1].strip()
        import_line = import_line.split(" as ")[0].strip()
    else:
        alias_dict['alias'] = import_line.replace("import ", "").split(".")[-1]

    import_get = import_line.replace("import ", "").split(".")
    alias_dict['to'] = ".".join(import_get)
    

    for _ in range(len(import_get)):
        try:
            path = importlib.util.find_spec(".".join(import_get))
        except ModuleNotFoundError:
            path = None
        if path:
            valid_module = True
            break
        else:
            import_get = import_get[:-1]

    if valid_module:
        import_line = ".".join(import_get)
    
    code = handle_direct_import(import_line, file_path, USED_ROOT_MODULES)

    code += f"\n{alias_dict['alias']} = {alias_dict['to']}\n"
    return code