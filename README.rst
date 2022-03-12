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

Split
-----

Create an instance

.. code-block:: python

    from filesplit.split import Split

    split = Split(inputfile: str, outputdir: str)

``inputfile`` (str, Required) - Path to the original file.

``outputdir`` (str, Required) - Output directory path to write the file splits.

With the instance created, the following methods can be used on the instance


bysize (size: int, newline: Optional[bool] = False, includeheader: Optional[bool] = False, callback: Optional[Callable] = None) -> None
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Splits file by size.

Args:

``size`` (int, Required): Max size in bytes that is allowed in each split.

``newline`` (bool, Optional): Setting this to True will not produce any any incomplete lines in each split. Defaults to False.

``includeheader`` (bool, Optional): Setting this to True will include header in each split. The first line is treated as a header. Defaults to False.

``callback`` (Callable, Optional): Callback function to invoke after each split. The callback function should accept two arguments [func (str, int)] - full path to the split file, 
split file size (bytes). Defaults to None.

Returns:

``None``


bylinecount(self, linecount: int, includeheader: Optional[bool] = False, callback: Optional[Callable] = None) -> None
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Splits file by line count.

Args:

``linecount`` (int, Required): Max lines that is allowed in each split.

``includeheader`` (bool, Optional): Setting this to True will include header in each split. The first line is treated as a header. Defaults to False.

``callback`` (Callable, Optional): Callback function to invoke after each split. The callback function should accept two arguments [func (str, int)] - full path to the split file, 
split file size (bytes). Defaults to None.

Returns:

``None``

The file splits are generated in this fashion ``[original_filename]_1.ext, [original_filename]_2.ext, .., [original_filename]_n.ext``.

A manifest file is also created in the output directory to keep track of the file splits. This manifest file is required for merge operation.

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

``inputdir`` (str, Required) - Path to the original file.

``outputdir`` (str, Required) - Output directory path to write the file splits.

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
