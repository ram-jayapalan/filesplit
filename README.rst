.. image:: https://badge.fury.io/py/filesplit.png
    :target: https://badge.fury.io/py/filesplit

filesplit
==========

File splitting and merging made easy for python programmers!

This module 
    * Can split files of any size into multiple chunks and also merge them back. 
    * Can handle both structured and unstructured files.


System Requirements
--------------------

**Operating System**: Windows/Linux/Mac

**Python version**: 3.x.x


Installation
------------

The module is available as a part of PyPI and can be easily installed
using ``pip``

::

    pip install filesplit

Creating File Splits with Split
-------------------------------

To split a file, create an instance of the Split class with the ``inputfile`` and ``outputdir`` arguments:

``inputfile`` (str, Required) - Path to the original file.

``outputdir`` (str, Required) - Output directory path to write the file splits.


.. code-block:: python

    from filesplit.split import Split

    split = Split(inputfile="path/to/original_file", outputdir="path/to/output_directory")



Once you have created an instance of ``Split``, you can use the following methods to split the file:


bysize: Splits the file based on a maximum size.
-------------------------------------------------

.. code-block:: python

    split.bysize(size=1000000, newline=False, includeheader=False, callback=None)



``size`` (int, required): The maximum size of each split in bytes.

``newline`` (bool, optional, default False): If True, the last line in each split will not be incomplete.

``includeheader`` (bool, optional, default False): If True, the first line of the file will be treated as a header and
included in each split.

``callback`` (Callable, optional, default None): A callback function that is called after each split is generated. The
function should take two arguments: the full path to the split file and the size of the split in bytes.


bylinecount: Splits the file based on a maximum line count.
----------------------------------------------------------

.. code-block:: python

    split.bylinecount(linecount=10000, includeheader=False, callback=None)


``linecount`` (int, required): The maximum number of lines in each split.

``includeheader`` (bool, optional, default False): If True, the first line of the file will be treated as a header
and included in each split.

``callback`` (Callable, optional, default None): A callback function that is called after each split is generated. The
function should take two arguments: the full path to the split file and the size of the split in bytes.

The file splits will be named ``[original_filename]_1.ext``, ``[original_filename]_2.ext``, etc., and will be saved in the specified ``outputdir``.

Moreover, 
    * The delimiter for the generated splits can be changed by setting ``splitdelimiter`` property like ``split.splitdelimiter='$'``. Default is ``_`` (underscore).
    * The manifest file name for the generated splits can be changed by setting ``manfilename`` property like ``split.manfilename='man'``. Default is ``manifest``.
    * To forcefully and safely terminate the process set the property ``terminate`` to True while the process is running.


Merge
-----

Create an instance

.. code-block:: python

    from filesplit.merge import Merge

    merge = Merge(inputdir: str, outputdir: str, outputfilename: str)

``inputdir`` (str, Required) - Path to the directory containing file splits.

``outputdir`` (str, Required) - Output directory path to write the merged file.

``outputfilename`` (str, Required) - Name to use for the merged file.

With the instance created, the following method can be used on the instance


merge(cleanup: Optional[bool] = False, callback: Optional[Callable] = None) -> None
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Merges the split files back into one single file.

Args:

``cleanup`` (bool, Optional): If True, all the split files and manifest file will be purged after successful merge. Defaults to False.

``callback`` (Callable, Optional): Callback function to invoke after merge. The callback function should accept two arguments [func (str, int)] - full path to the merged file, 
merged file size (bytes). Defaults to None.

Returns:

``None``

Moreover, 
    * The manifest file name can be changed by setting ``manfilename`` property like ``merge.manfilename='man'``. 
      The manifest file name should match with the one used during the file split process and should be available in the same directory as that of file splits. Default is ``manifest``.
    * To forcefully and safely terminate the process set the property ``terminate`` to True while the process is running.
