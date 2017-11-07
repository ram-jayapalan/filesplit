File split made easy for python programmers!

A python module that can split files of any size into multiple chunks, with optimum use of memory and without compromising on performance. The module determines the splits based on the new line character in the file, therefore not writing incomplete lines to the file splits.

## System Requirements ##

Operating System: Windows/Linux/Mac

Python version: 2.7 and above (Python 3 recommended)

## Usage Instructions ##

The module is available as a part of PyPI and can be easily installed using `pip`

````
pip install filesplit
````

Create an instance of the FileSplit object by passing file path and split size as arguments.

````
from fsplit.filesplit import FileSplit

fs = FileSplit(file='path/to/file', splitsize=500000000, output_dir='/path/to/output directory/')

````

* "file" and "splitsize" are required. "output_dir" is optional and defaults to current directory.
* "splitsize" should be given in bytes.

With the instance created, any of the following methods can be invoked

### split (include_header=False, callback=None) ###

Method that splits the file into multiple chunks. This method works in binary mode under the hood which keeps the 
formatting and encoding of splits as-is to that of the source which should be sufficient to handle any
file types.

````
fs.split()
````

In case, if the file contains a header and if you want the header to be available in all of your
splits, you can optionally set the flag "include_header" to True. By default it is set to False.

````
fs.split(include_header=True)

````

Also, you can pass a callback function (optional) [func (str, long, long)] that accepts three arguments - full path to the split, 
split file size (bytes) and line count. The callback function will be called after each file split.

````
def func(f, s, c):
    print("file: {0}, size: {1}, count: {2}".format(f, s, c))
    
fs.split(callback=func)

````

### splitbyencoding (rencoding="utf-8", wencoding="utf-8", include_header=False, callback=None) ###

This method is similar to the above ``split()`` method, except that the file encoding of the splits can be explicitly specified.
This is helpful if the file chunks has to be of specific encoding standard. This method accepts two additional arguments
to that of the ``split()`` method - 
- "rencoding" - encoding of the source file (default : 'utf-8')
- "wencoding" - encoding of the output file chunks (default: 'utf-8')
