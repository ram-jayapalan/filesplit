#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: rjayapalan
Created: March 05, 2022
"""
from typing import Callable, Optional
from io import BytesIO
import ntpath
import os
import csv
import time
import logging

from .common import constant, error

log = logging.getLogger(__name__)


class Split:

    def __init__(self, inputfile: str, outputdir: str) -> None:
        """Constructor

        Args:
            inputfile (str): Path to the original file
            outputdir (str): Output directory path to write the file splits
        """
        log.info('Starting file split process')
        if not os.path.exists(inputfile):
            raise FileNotFoundError(
                f'Given input file path "{inputfile}" does not exist.')
        if not os.path.isdir(outputdir):
            raise NotADirectoryError(
                f'Given output directory path "{outputdir}" is not a valid directory.')
        self._terminate = False
        self._inputfile = inputfile
        self._outputdir = outputdir
        self._splitdelimiter = constant.SPLIT_DELIMITER
        self._manfilename = constant.MANIFEST_FILE_NAME
        self._starttime = time.time()

    @property
    def terminate(self) -> bool:
        """Returns terminate flag value

        Returns:
            bool: Terminate flag value
        """
        return self._terminate

    @property
    def inputfile(self) -> str:
        """Returns input file path

        Returns:
            str: Input file path
        """
        return self._inputfile

    @property
    def outputdir(self) -> str:
        """Returns output dir path

        Returns:
            str: Output dir path
        """
        return self._outputdir

    @property
    def splitdelimiter(self) -> str:
        """Returns split file suffix char

        Returns:
            str: Split file suffix char
        """
        return self._splitdelimiter

    @property
    def manfilename(self) -> str:
        """Returns manifest filename

        Returns:
            str: Manifest filename
        """
        return self._manfilename

    @terminate.setter
    def terminate(self, value: bool) -> None:
        """Sets terminate flag. Once flag is set
        the running process will safely terminate.

        Args:
            value (bool): True/False
        """
        self._terminate = value

    @splitdelimiter.setter
    def splitdelimiter(self, value: str) -> None:
        """Sets split file suffix char

        Args:
            value (str): Any character
        """
        self._splitdelimiter = value

    @manfilename.setter
    def manfilename(self, value: str) -> None:
        """Sets manifest filename

        Args:
            value (str): Manifest filename
        """
        self._manfilename = value

    @staticmethod
    def _getreadbuffersize(splitsize: int) -> int:
        """Returns buffer size to be used with the file reader

        Args:
            splitsize (int): Split size

        Returns:
            int: Buffer size
        """
        defaultchunksize = constant.DEFAULT_CHUNK_SIZE
        if splitsize < defaultchunksize:
            return splitsize
        return defaultchunksize

    def _getnextsplit(self, splitnum: int) -> str:
        """Returns next split filename

        Args:
            splitnum (int): Next split number

        Returns:
            str: Split filename
        """
        filename = ntpath.split(self.inputfile)[1]
        fname, ext = ntpath.splitext(filename)
        splitfilename = f'{fname}{self.splitdelimiter}{splitnum}{ext}'
        return splitfilename

    def _getmanifestpath(self) -> str:
        """Returns manifest filepath

        Returns:
            str: Manifest filepath
        """
        return os.path.join(self.outputdir, self.manfilename)

    def _process(self, reader: BytesIO, limit: int,
                 splitby: str, newline: bool, includeheader: bool,
                 callback: Optional[Callable], **kwargs) -> None:
        """Process that handles the file split

        Args:
            reader (BytesIO): File like object
            limit (int): Size or Number of lines
            splitby (str): "size" or "linecount"
            newline (bool): Set to True if the split should not contain any incomplete lines
            includeheader (bool): Set to true to include header in each split
            callback (Optional[Callable]): callback function to invoke after each split that accepts
                split file path, size [str, int] as args

        Raises:
            ValueError: Unsupported split type
        """
        splitnum: int = kwargs.get('splitnum', 1)
        carryover: bytes = kwargs.get('carryover', None)
        header: bytes = kwargs.get('header', None)
        manifest: csv.DictWriter = kwargs.get('manifest', None)
        processed = 0
        splitfilename = self._getnextsplit(splitnum)
        splitfile = os.path.join(self.outputdir, splitfilename)
        if includeheader and not header:
            newline = True
            header = reader.readline()
        writer = open(splitfile, mode='wb+')
        try:
            if header:
                writer.write(header)
                processed += len(header) if splitby == 'size' else 1
            if carryover:
                writer.write(carryover)
                processed += len(carryover) if splitby == 'size' else 1
                carryover = None
            if splitby == 'size':
                buffersize = Split._getreadbuffersize(splitsize=limit)
                while 1:
                    if self.terminate:
                        log.info('Term flag has been set by the user.')
                        log.info('Terminating the process.')
                        break
                    if newline:
                        chunk = reader.readline()
                    else:
                        chunk = reader.read(buffersize)
                    if not chunk:
                        break
                    chunksize = len(chunk)
                    if processed + chunksize <= limit:
                        writer.write(chunk)
                        processed += chunksize
                    else:
                        carryover = chunk
                        break
            elif splitby == 'linecount':
                while 1:
                    if self.terminate:
                        log.info('Term flag has been set by the user.')
                        log.info('Terminating the process.')
                        break
                    chunk = reader.readline()
                    if not chunk:
                        break
                    processed += 1
                    if processed <= limit:
                        writer.write(chunk)
                    else:
                        carryover = chunk
                        break
            else:
                raise ValueError('Unsupported split type provided.')
        finally:
            writer.close()
        splitsize = os.path.getsize(splitfile)
        if manifest:
            manifest.writerow(
                {'filename': splitfilename, 'filesize': splitsize, 'header': includeheader})
        if callback:
            callback(splitfile, splitsize)
        if carryover:
            splitnum += 1
            self._process(reader, limit, splitby, newline, includeheader, callback,
                          splitnum=splitnum, carryover=carryover, header=header,
                          manifest=manifest)

    def _endprocess(self):
        """Runs statements that marks the completion of the process
        """
        endtime = time.time()
        runtime = int((endtime - self._starttime)/60)
        log.info(f'Process completed in {runtime} min(s)')

    def bysize(self, size: int, newline: bool = False,
               includeheader: bool = False, callback: Callable = None) -> None:
        """Splits by size

        Args:
            size (int): Max size in bytes allowed in each split
            newline (bool, optional): Set to true to avoid any incomplete lines
                in each split. Defaults to False.
            includeheader (bool, optional): Set to true to include header with each split.
                Defaults to False.
            callback (Callable, optional): Callback function to invoke after each split that passes
                split file path, size [str, int] as args. Defaults to None.
        """
        with open(self.inputfile, mode='rb') as reader:
            with open(self._getmanifestpath(), mode='w+', encoding='utf8', newline='') as writer:
                fieldnames = ['filename', 'filesize', 'header']
                manifest = csv.DictWriter(
                    writer, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                manifest.writeheader()
                self._process(reader, size, 'size', newline,
                              includeheader, callback, manifest=manifest)
        self._endprocess()

    def bylinecount(self, linecount: int, includeheader: bool = False,
                    callback: Callable = None) -> None:
        """Splits by line count

        Args:
            linecount (int): Max number of allowed lines in each split
            includeheader (bool, optional): Set to true to include header with each split.
                Defaults to False.
            callback (Callable, optional): Callback function to invoke after each split that passes
                split file path, size [str, int] as args. Defaults to None.
        """
        with open(self.inputfile, mode='rb') as reader:
            with open(self._getmanifestpath(), mode='w+', encoding='utf8', newline='') as writer:
                fieldnames = ['filename', 'filesize', 'header']
                manifest = csv.DictWriter(
                    writer, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                manifest.writeheader()
                self._process(reader, linecount, 'linecount', True,
                              includeheader, callback, manifest=manifest)
        self._endprocess()


# if __name__ == '__main__':

#     import threading
#     import time

#     inputfile = '/Users/rjayapalan/Downloads/test.txt'
#     outputdir = '/Users/rjayapalan/Downloads/split_test'

#     def cb(filepath: str, filesize: int):
#         print(f'{filepath} : {filesize}')

#     def terminatesplit(splitinstance: Split, after: int):
#         time.sleep(after)
#         splitinstance.terminate = True
#         print('terminating')

#     split = Split(inputfile, outputdir)

#     th = threading.Thread(target=terminatesplit, args=(split, 1))
#     th.daemon = True
#     th.start()

#     split.bysize(10, includeheader=True, callback=cb)

#     th.join()
