#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__Author__ = "Ram Prakash Jayapalan"
__PyVersion__ = "3"
__Created__ = "Sep 12, 2020"

import logging
import os
import ntpath
from typing import Callable, IO, Tuple
import csv
import time


class Filesplit:
    def __init__(self) -> None:
        """
        Constructor
        """
        self.log = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self.man_filename = "fs_manifest.csv"
        self._buffer_size = 1000000  # 1 MB

    def __process_split(
        self,
        fi: IO,
        fo: IO,
        split_size: int,
        newline: bool = False,
        carry_over: str = None,
        output_encoding: str = None,
        include_header: bool = False,
        header: str = None,
    ) -> Tuple:
        """
        Process that splits the incoming stream
        :param fi: input file like object that implements read() and readline()
        method
        :param fo: file like object that implements write() method
        :param split_size: file split size in bytes
        :param newline: when True, splits at newline on top of bytes
        :param output_encoding: split file encoding
        :param include_header: when True, first line is treated as header and
        each split receives the header. This flag is dependant on newline flag
        to be set to True as well
        :param carry_over: any carry over bytes to the next file
        :param header: header from the file if any
        :return:
        """
        buffer_size = (
            split_size if split_size < self._buffer_size else self._buffer_size
        )
        buffer = 0
        if not newline:
            while True:
                if carry_over:
                    fo.write(carry_over)
                    buffer += (
                        len(carry_over)
                        if not output_encoding
                        else len(carry_over.encode(output_encoding))
                    )
                    carry_over = None
                    continue
                chunk = fi.read(buffer_size)
                if not chunk:
                    break
                chunk_size = (
                    len(chunk)
                    if not output_encoding
                    else len(chunk.encode(output_encoding))
                )
                if buffer + chunk_size <= split_size:
                    fo.write(chunk)
                    buffer += chunk_size
                else:
                    carry_over = chunk
                    break
            return carry_over, buffer, None
        else:
            if carry_over:
                if header:
                    fo.write(header)
                fo.write(carry_over)
                if header:
                    buffer += (
                        len(carry_over) + len(header)
                        if not output_encoding
                        else len(carry_over.encode(output_encoding))
                        + len(header.encode(output_encoding))
                    )
                else:
                    buffer += (
                        len(carry_over)
                        if not output_encoding
                        else len(carry_over.encode(output_encoding))
                    )
                carry_over = None
            for line in fi:
                if include_header and not header:
                    header = line
                line_size = (
                    len(line)
                    if not output_encoding
                    else len(line.encode(output_encoding))
                )
                if buffer + line_size <= split_size:
                    fo.write(line)
                    buffer += line_size
                else:
                    carry_over = line
                    break
            return carry_over, buffer, header

    def split(
        self,
        file: str,
        split_size: int,
        output_dir: str = ".",
        callback: Callable = None,
        **kwargs,
    ) -> None:
        """
        Splits the file into chunks based on the newline char in the file.
        By default uses binary mode.
        :param file: path to the source file
        :param split_size: file split size in bytes
        :param output_dir: output dir to write the split files
        :param callable callback: (Optional) callback function
        [func (str, long, long)] that accepts
        three arguments - full file path to the destination, size of the file
        in bytes and line count.
        """
        start_time = time.time()
        self.log.info("Starting file split process")

        newline = kwargs.get("newline", False)
        include_header = kwargs.get("include_header", False)
        # If include_header is provided, default newline flag to True as this
        # should apply only to structured file
        if include_header:
            newline = True
        encoding = kwargs.get("encoding", None)
        split_file_encoding = kwargs.get("split_file_encoding", None)

        f = ntpath.split(file)[1]
        filename, ext = os.path.splitext(f)
        fi, man = None, None

        # Split file encoding cannot be specified without specifying encoding
        # which is required to read the file in text mode
        if split_file_encoding and not encoding:
            raise ValueError(
                "`encoding` needs to be specified "
                "when providing `split_file_encoding`"
            )
        try:
            # Determine the splits based off bytes when newline is set to False.
            # If newline is True, split only at newline considering the bytes
            # as well.
            if encoding and not split_file_encoding:
                fi = open(file=file, mode="r", encoding=encoding)
            elif encoding and split_file_encoding:
                fi = open(file=file, mode="r", encoding=encoding)
            else:
                fi = open(file=file, mode="rb")
            # Create file handler for the manifest file
            man_file = os.path.join(output_dir, self.man_filename)
            man = open(file=man_file, mode="w+", encoding="utf-8")
            # Create man file csv dict writer object
            man_writer = csv.DictWriter(
                f=man, fieldnames=["filename", "filesize", "encoding", "header"]
            )
            # Write man file header
            man_writer.writeheader()

            split_counter, carry_over, header = 1, "", None

            while carry_over is not None:
                split_file = os.path.join(
                    output_dir, "{0}_{1}{2}".format(filename, split_counter, ext)
                )
                fo = None
                try:
                    if encoding and not split_file_encoding:
                        fo = open(file=split_file, mode="w+", encoding=encoding)
                    elif encoding and split_file_encoding:
                        fo = open(
                            file=split_file, mode="w+", encoding=split_file_encoding
                        )
                    else:
                        fo = open(file=split_file, mode="wb+")
                    carry_over, output_size, header = self.__process_split(
                        fi=fi,
                        fo=fo,
                        split_size=split_size,
                        newline=newline,
                        output_encoding=split_file_encoding,
                        carry_over=carry_over,
                        include_header=include_header,
                        header=header,
                    )
                    if callback:
                        callback(split_file, output_size)
                    # Write to manifest file
                    di = {
                        "filename": ntpath.split(split_file)[1],
                        "filesize": output_size,
                        "encoding": encoding,
                        "header": True if header else None,
                    }
                    man_writer.writerow(di)

                    split_counter += 1
                finally:
                    if fo:
                        fo.close()
        finally:
            if fi:
                fi.close()
            if man:
                man.close()

        run_time = round((time.time() - start_time) / 60)

        self.log.info(f"Process complete")
        self.log.info(f"Run time(m): {run_time}")

    def merge(
        self,
        input_dir: str,
        output_file: str = None,
        manifest_file: str = None,
        callback: Callable = None,
        cleanup: bool = False,
    ) -> None:
        """Merges the split files based off manifest file

        Args:
            input_dir (str): directory containing the split files and manifest
            file

            output_file (str): final merged output file path. If not provided,
            the final merged filename is derived from the split filename and
            placed in the same input dir

            callback (Callable): callback function
            [func (str, long)] that accepts 2 arguments - path to destination
            , size of the file in bytes

            cleanup (bool): if True, all the split files, manifest file will be
            deleted after merge leaving behind the merged file.

            manifest_file (str): path to the manifest file. If not provided,
            the process will look for the file within the input_dir
        Raises:
            FileNotFoundError: if missing manifest and split files

            NotADirectoryError: if input path is not a directory
        """
        start_time = time.time()
        self.log.info("Starting file merge process")

        if not os.path.isdir(input_dir):
            raise NotADirectoryError("Input directory is not a valid directory")

        manifest_file = (
            os.path.join(input_dir, self.man_filename)
            if not manifest_file
            else manifest_file
        )
        if not os.path.exists(manifest_file):
            raise FileNotFoundError("Unable to locate manifest file")

        fo = None
        clear_output_file = True
        header_set = False

        try:
            # Read from manifest every split and merge to single file
            with open(file=manifest_file, mode="r", encoding="utf-8") as man_fh:
                man_reader = csv.DictReader(f=man_fh)
                for line in man_reader:
                    encoding = line.get("encoding", None)
                    header_avail = line.get("header", None)
                    # Derive output filename from split file if output file
                    # not provided
                    if not output_file:
                        f, ext = ntpath.splitext(line.get("filename"))
                        output_filename = "".join([f.rsplit("_", 1)[0], ext])
                        output_file = os.path.join(input_dir, output_filename)
                    # Clear output file present before merging. This should
                    # happen only once during beginning of merge
                    if clear_output_file:
                        if os.path.exists(output_file):
                            os.remove(output_file)
                        clear_output_file = False
                    # Create write file handle based on the encoding from
                    # man file
                    if not fo:
                        if encoding:
                            fo = open(file=output_file, mode="a", encoding=encoding)
                        else:
                            fo = open(file=output_file, mode="ab")
                    # Open the split file in read more and write contents to the
                    # output file
                    try:
                        input_file = os.path.join(input_dir, line.get("filename"))
                        if encoding:
                            fi = open(file=input_file, mode="r", encoding=encoding)
                        else:
                            fi = open(file=input_file, mode="rb")
                        # Skip header if the flag is set to True
                        if header_set:
                            next(fi)
                        for line in fi:
                            if header_avail and not header_set:
                                header_set = True
                            fo.write(line)
                    finally:
                        if fi:
                            fi.close()
        finally:
            if fo:
                fo.close()

        # Clean up files if required
        if cleanup:
            # Clean up split files
            with open(file=manifest_file, mode="r", encoding="utf-8") as man_fh:
                man_reader = csv.DictReader(f=man_fh)
                for line in man_reader:
                    f = os.path.join(input_dir, line.get("filename"))
                    if os.path.exists(f):
                        os.remove(f)
            # Clean up man file
            if os.path.exists(manifest_file):
                os.remove(manifest_file)

        # Call the callback function with path and file size
        if callback:
            callback(output_file, os.stat(output_file).st_size)

        run_time = round((time.time() - start_time) / 60)

        self.log.info(f"Process complete")
        self.log.info(f"Run time(m): {run_time}")


# if __name__ == "__main__":

#     def cb(f, s):
#         print(f, s)

#     fs = Filesplit()

#     fs.split(
#         file="/Users/ram.jayapalan/Downloads/glove/glove.6B.300d.txt",
#         split_size=500000000,
#         output_dir="/Users/ram.jayapalan/Downloads/glove/",
#         callback=cb,
#         newline=True,
#     )