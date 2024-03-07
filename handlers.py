import os
import importlib.util
import sys
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

def handle_import_line(import_line: str, file_path:os.PathLike = "") -> str:
    """
        This function gets the import line/lines from the file and choose the right handler.
        Returns:
            str: code to be appended to the new code
    """

    if import_line.strip().startswith("import "):
        return handle_direct_import(import_line, file_path)
        

    elif import_line.strip().startswith("from "):
        return handle_relative_import(import_line, file_path)

    else:
        raise Exception(f'Import Line is Not Valid. Import: {import_line}')
    

def handle_direct_import(import_line: str, file_path:os.PathLike = "") -> str:
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

    parts_of_line = import_line.split(' ')
    if any(part in BUILTIN_MODULES for part in parts_of_line):
        return import_line # Built-in import
    
    sys.path.append(os.path.dirname(file_path)) #add file folder to the path
    
    import_path = importlib.util.find_spec(import_line.strip().split(' ')[1])
    if import_path is None:
        raise Exception(f'Error: Import is not found. Import: {import_line}') # Import not found
    
    import_path = import_path.origin
    
    with open(import_path, 'r', encoding="utf-8") as file:
        content += file.read()

    import_core = import_line.split(' ')[1]
    classes_to_create = import_core.split('.')
    for class_name in reversed(classes_to_create):
        class_content = "class " + class_name + ":\n"
        #fazendo cada linha receber um tab
        lines = "\n".join([f"   {line}" for line in content.split('\n')])
        class_content += lines
        content = class_content

    sys.path.remove(os.path.dirname(file_path))
    return content

def handle_relative_import(import_line: str, file_path:os.PathLike = "") -> str:
    pass
