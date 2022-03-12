#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: rjayapalan
Created: March 09, 2022
"""
import os
import csv
from typing import Callable, Optional
import logging
import time

from .common import constant, error

log = logging.getLogger(__name__)


class Merge:

    def __init__(self, inputdir: str, outputdir: str, outputfilename: str) -> None:
        """Constructor

        Args:
            inputdir (str): Dir path to the split files
            outputdir (str): Dir path for the output file
            outputfilename (str): Filename for the final merged file
        """
        log.info('Starting file merge process')
        if not os.path.isdir(inputdir):
            raise NotADirectoryError(
                f'Given input directory path "{inputdir}" is not a valid directory.')
        if not os.path.isdir(outputdir):
            raise NotADirectoryError(
                f'Given output directory path "{outputdir}" is not a valid directory.')
        self._inputdir = inputdir
        self._outputdir = outputdir
        self._outputfilename = outputfilename
        self._terminate = False
        self._manfilename = constant.MANIFEST_FILE_NAME
        self._starttime = time.time()

    @property
    def terminate(self) -> bool:
        """Returns terminate flag value

        Returns:
            bool: True/False
        """
        return self._terminate

    @property
    def inputdir(self) -> str:
        """Returns path to the input dir

        Returns:
            str: Dir path
        """
        return self._inputdir

    @property
    def outputdir(self) -> str:
        """Returns output dir path

        Returns:
            str: Dir path
        """
        return self._outputdir

    @property
    def outputfilename(self) -> str:
        """Returns output filename

        Returns:
            str: Output filename
        """
        return self._outputfilename

    @property
    def manfilename(self) -> str:
        """Returns manifest filename

        Returns:
            str: Manifest filename
        """
        return self._manfilename

    @terminate.setter
    def terminate(self, value: bool) -> None:
        """Sets terminate flag that will terminate the process

        Args:
            value (bool): True/False
        """
        self._terminate = value

    @manfilename.setter
    def manfilename(self, value: str) -> None:
        """Sets manifest filename

        Args:
            value (str): Manifest filename
        """
        self._manfilename = value

    def _getmanifestpath(self) -> str:
        """Returns manifest filepath

        Returns:
            str: Manifest filepath
        """
        filepath = os.path.join(self.inputdir, self.manfilename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f'Manifest file "{self.manfilename}" not found in "{self.inputdir}"')
        return filepath

    def _getoutputfilepath(self) -> str:
        """Returns absolute path of the output file

        Returns:
            str: Output file path
        """
        filepath = os.path.join(self.outputdir, self.outputfilename)
        return filepath

    def _endprocess(self):
        """Runs statements that marks the completion of the process
        """
        endtime = time.time()
        runtime = int((endtime - self._starttime)/60)
        log.info(f'Process completed in {runtime} min(s)')

    def merge(self, cleanup: bool = False, callback: Optional[Callable] = None) -> None:
        """Merges the split files back into one single file

        Args:
            cleanup (bool, optional): If true, all the split files and manifest 
                file will be purged after successful merge. Defaults to False.
            callback (Optional[Callable], optional): Callback function to invoke 
                after all the splits have been merged. 
                The callback passes merged file path, size [str, int] as args. 
                Defaults to None.
        """
        manfile = self._getmanifestpath()
        outputfile = self._getoutputfilepath()
        with open(manfile, mode='r', encoding='utf8', newline='') as reader:
            with open(outputfile, mode='wb+') as writer:
                csvreader = csv.DictReader(reader)
                skipheader = False
                for line in csvreader:
                    if self.terminate:
                        log.info('Term flag has been set by the user.')
                        log.info('Terminating the process.')
                        break
                    splitfilename = line['filename']
                    splitfile = os.path.join(self.inputdir, splitfilename)
                    header = True if line['header'].lower(
                    ) == 'true' else False
                    with open(splitfile, mode='rb') as splitreader:
                        if skipheader:
                            next(splitreader)
                        for line in splitreader:
                            writer.write(line)
                    if header:
                        skipheader = True
        if cleanup and not self.terminate:
            with open(manfile, mode='r', encoding='utf8', newline='') as reader:
                csvreader = csv.DictReader(reader)
                for line in csvreader:
                    splitfilename = line['filename']
                    splitfile = os.path.join(self.inputdir, splitfilename)
                    if os.path.exists(splitfile):
                        os.remove(splitfile)
            if os.path.exists(manfile):
                os.remove(manfile)
        if callback:
            callback(outputfile, os.path.getsize(outputfile))
        self._endprocess()


# if __name__ == '__main__':

#     import threading
#     import time

#     def cb(path, size):
#         print(f'{path} : {size}')

#     def terminatemerge(mergeinstance: Merge, after: int):
#         time.sleep(after)
#         mergeinstance.terminate = True
#         print('terminating')

#     merge = Merge(inputdir='/Users/rjayapalan/Downloads/split_test',
#                   outputdir='/Users/rjayapalan/Downloads/split_test',
#                   outputfilename='mergedfile.csv',
#                   )

#     th = threading.Thread(target=terminatemerge, args=(merge, 2))
#     th.daemon = True
#     th.start()

#     merge.merge(cleanup=True, callback=cb)
