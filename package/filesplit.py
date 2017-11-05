#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__Author__ = 'Ram Jayapalan'
__Version__ = '3.6.x'
__Created__ = 'Aug 14, 2017'

import logging
import os
import ntpath


class FileSplit(object):

    def __init__(self, file, splitsize, output_dir="."):
        """
        Constructor
        :param str file: full path to the input file
        :param long splitsize: file split size in bytes
        :param str output_dir: path to the output directory
        """
        self.log = logging.getLogger(__name__)
        self.log.info("Initializing file split module.")
        if not os.path.isfile(file):
            raise FileNotFoundError("The given file path '{0}' is not valid".format(file))
        self.file = file
        self.log.info("Given input file : '{0}'".format(self.file))
        if not os.path.exists(output_dir):
            raise NotADirectoryError("The given output path '{0}' is not a valid directory".format(output_dir))
        self.output_dir = output_dir
        self.log.info("Given output directory: '{0}'".format(self.output_dir))
        self._buffer_size = 1000000  # 1MB
        self._header = None
        self._carryover = None
        self._split_size = splitsize

    def split(self, include_header=False, callback=None):
        """
        Method to split the file to chunks based on the given encoding. Use this function if the file needs to be
        read be written to chucks as-is
        :param bool include_header: set to True to include header in each splits. Default: False
        :param callable callback: (Optional) callback function [func (str, long, long)] that accepts
        three arguments - full file path to the destination, size of the file in bytes and line count.
        """
        self.log.info("Total file size in bytes: {0}".format(os.path.getsize(self.file)))
        self.log.info("Given split size: {0} bytes".format(self._split_size))
        directory, file = ntpath.split(self.file)
        filename, ext = os.path.splitext(file)
        # Keep track of file splits and increment the file counter accordingly
        filecounter = 1
        # Open the file in read-only mode with the given encoding
        with open(file=self.file, mode="rb") as f:
            # Iterate and write to file in append mode.
            while filecounter is not None:
                outfile = os.path.join(self.output_dir, "{0}_{1}{2}".format(filename, filecounter, ext))
                # Remove any existing file with the generated file name if exists in the output directory. This
                # should automatically clean up existing files that needs to be regenerated.
                if os.path.exists(outfile):
                    self.log.debug("Removing an existing file with the filename '{0}'".format(outfile))
                    os.remove(outfile)
                with open(file=outfile, mode="ab") as of:
                    self.log.info("Writing to file '{0}'".format(outfile))
                    total_size, line_count, carryover = self._process_(f, of, include_header)
                # Log the file details
                self.log.info("Wrote to file '{0}' with {1} bytes of data".format(outfile, total_size))
                # Return the file details to the callback function if applicable
                if callback is not None:
                    callback(outfile, total_size, line_count)
                # Check if there is any carryover to the next file; if yes increment the filecounter and iterate again
                # else exit
                if carryover:
                    filecounter += 1
                else:
                    break
        self.log.info("File split complete.")

    def splitbyencoding(self, rencoding="utf-8", wencoding="utf-8", include_header=False, callback=None):
        """
        Method to split the file to chunks based on the given encoding. Use this function if the file needs to be
        read and be written to chucks of specific encoding format
        :param str rencoding: encoding of the input file; default utf-8
        :param str wencoding: encoding of the output file; default utf-8
        :param bool include_header: set to True to include header in each splits
        :param callable callback: (Optional) callback function [func (str, long, long)] that accepts
        three arguments - full file path to the destination, size of the file in bytes and line count.
        :return: None
        """
        self.log.info("Total file size in bytes: {0}".format(os.path.getsize(self.file)))
        self.log.info("Given split size: {0} bytes".format(self._split_size))
        directory, file = ntpath.split(self.file)
        filename, ext = os.path.splitext(file)
        # Keep track of file splits and increment the file counter accordingly
        filecounter = 1
        # Open the file in read-only mode with the given encoding
        with open(file=self.file, mode="r", encoding=rencoding) as f:
            # Iterate and write to file in append mode.
            while filecounter is not None:
                outfile = os.path.join(self.output_dir, "{0}_{1}{2}".format(filename, filecounter, ext))
                # Remove any existing file with the generated file name if exists in the output directory. This
                # should automatically clean up existing files that needs to be regenerated.
                if os.path.exists(outfile):
                    self.log.debug("Removing an existing file with the filename '{0}'".format(outfile))
                    os.remove(outfile)
                with open(file=outfile, mode="a", encoding=wencoding) as of:
                    self.log.info("Writing to file '{0}'".format(outfile))
                    total_size, line_count, carryover = self._process_(f, of, include_header, wencoding)
                # Log the file details
                self.log.info("Wrote to file '{0}' with {1} bytes of data".format(outfile, total_size))
                # Return the file details to the callback function if applicable
                if callback is not None:
                    callback(outfile, total_size, line_count)
                # Check if there is any carryover to the next file; if yes increment the filecounter and iterate again
                # else exit
                if carryover:
                    filecounter += 1
                else:
                    break
        self.log.info("File split complete.")

    def _process_(self, f, of, include_header, wenc=None):
        """
        Private function to handle the file splits
        :param f: read file object stream
        :param of: write file object stream
        :param include_header: set to True if header needs to be included in the split files
        :param wenc: encoding of the split files; default 'None' if the file needs to be written in binary mode
        :return tuple: total size, line count, carryover (bool)
        """
        total_size = 0
        li = []
        current_size = 0
        line_count = 0
        # If the header needs to be included, treat the first line as header and capture the value beforehand
        if include_header & (self._header is None):
            self._header = f.readline()
        # If the header is set to True, write header to each file splits
        if self._header is not None:
            of.write(self._header)
            size = len(self._header.encode(wenc)) if wenc is not None else len(self._header)
            current_size += size
            total_size += size
            line_count += 1
        if self._carryover is not None:
            of.write(self._carryover)
            size = len(self._carryover.encode(wenc)) if wenc is not None else len(self._carryover)
            current_size += size
            total_size += size
            self._carryover = None
            line_count += 1
        for line in f:
            size = len(line.encode(wenc)) if wenc is not None else len(line)
            current_size += size
            total_size += size
            line_count += 1
            # Keep writing to the buffer list as long as the total byte size is within the limits
            # of buffer and total split size
            if (current_size <= self._buffer_size) & (total_size <= self._split_size):
                li.append(line)
                continue
            # Write the buffer contents to the file if the total byte size exceeds the buffer size
            # but is within the split size. Reset the total size and the buffer contents to empty.
            elif (current_size > self._buffer_size) & (total_size <= self._split_size):
                li.append(line)
                of.write("".join(li)) if wenc is not None else of.write(b"".join(li))
                current_size = 0
                li = []
            # If the split size threshold is reached, we don't want to write the current line to the
            # current file. Instead, we carry over the line to the next file.
            else:
                self._carryover = line
                self._total_size = total_size - size
                line_count = line_count - 1
                break
        # Empty buffer contents to file before exiting if at all there exists any that did not fit
        # into the above if..elif..else logic.
        of.write("".join(li)) if wenc is not None else of.write(b"".join(li))
        # Set the carryover flag if there are lines pending to be written next split
        carryover = True if self._carryover is not None else False
        return total_size, line_count, carryover
