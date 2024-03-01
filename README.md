# Python-One
An library to convert python libraries in one-file libraries

## Explanation
This library is a simple library to convert python libraries in one-file libraries. It's useful to use in projects that you want to use a library but you don't want to install it.
If you already have some problems with the installation of a library, this library is for you.

## How to use
To use this library, you need to install it using pip:
```bash
pip install python-one
```
After that, you can use the library in your project. To use it, you need to import the library and use the function `convert`:
```python
import python_one

python_one.convert('start_file.py')
```
The function `convert` will convert the library in one file and will save it in the same directory of the `one_start_file.py`.