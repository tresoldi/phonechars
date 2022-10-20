"""
Module with common and reusable functions.
This is including methods that cannon be easily converted to JavaScript.
"""

# Import Python standard libraries
import contextlib
import logging
import sys
import typing

# Import 3rd party libraries
import chardet


@contextlib.contextmanager
def smart_open(
    filename: str, mode: str = "r", *args: object, **kwargs: object
) -> typing.IO:
    """
    Open files and i/o streams transparently.
    Code originally from https://stackoverflow.com/a/45735618.
    @param filename: The full path to the file to be opened; if "-",
        it will open `sys.stdin` when in reading mode and `sys.stdout`
        when in writing mode.
    @param mode: The mode for opening the file, accepting normal values
        such as "r", "rb", "w", and "wb".
    @param args: Additional arguments for opening the stream, as passed
        to `open()`.
    @param kwargs: Any additional argument for opening the stream, as passed
        to `open()`.
    """

    if filename == "-":
        if mode == "r":
            fh = sys.stdin
        elif mode == "w":
            fh = sys.stdout
        elif mode == "rb":
            fh = sys.stdin.buffer
        elif mode == "wb":
            fh = sys.stdout.buffer
        else:
            raise ValueError("Invalid stream mode.")

        close = False
    else:
        fh = open(filename, mode, *args, **kwargs)
        close = True

    try:
        yield fh
    finally:
        if close:
            try:
                fh.close()
            except AttributeError:
                pass

def fetch_stream_data(input_source: str, encoding: str = "auto") -> str:
    """
    Read the input data as a string.
    The function takes care of handling input from both stdin and
    files, decoding the stream of bytes according to the user-specified
    character encoding (including automatic detection if necessary).
    @param input_source: The input source file; "-", as handled by
        `smart_open()`, indicates stdin/stdout.
    @param encoding: The encoding for the stream of data, with "auto"
        for autodetection via `chardet`.
    @return: A string with the full source for the data, encoded
        according to the specified charset encoding.
    """

    # Fetch all input as a sequence of bytes, so that we don't consume stdout
    # and can still run auto-detection on format and encoding
    with smart_open(input_source, "rb") as handler:
        logging.debug("Reading contents from `%s`.", input_source)
        raw_source = handler.read()

        # Detect encoding if necessary, building a string
        if encoding != "auto":
            logging.debug("Using `%s` character encoding.", encoding)
        else:
            detect = chardet.detect(raw_source)
            encoding = detect["encoding"]
            logging.debug(
                "Encoding detected as `%s` (confidence: %.2f)",
                detect["encoding"],
                detect["confidence"],
            )

        source = raw_source.decode(encoding)

    return source


################################3
def dummy():
    return 13