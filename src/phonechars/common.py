"""
Module with common and reusable functions.
This is including methods that cannon be easily converted to JavaScript.
"""

# Import Python standard libraries
import contextlib
import logging
import sys
import typing
from collections import defaultdict

# Import 3rd party libraries
import chardet
import unidecode

# Import local modules
from . import ipa


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


def slug_phoneme_label(label):
    """
    Return a NEXUS compatible label.
    """

    # Convert to XSAMPA and run unidecode for pure ASCII
    slug_label = ipa.ipa2xsampa(label, None)
    slug_label = unidecode.unidecode(slug_label)

    # Annotate tones, so they are easy to spot and the label
    # does not start with a number
    if slug_label[0] in "0123456":
        slug_label = "TONE_" + slug_label

    # Run a bunch of replacements for ASCII characters not accepted
    # by some of the tools (e.g., SplitsTree); we still try to
    # make the labels understandable for phonologists and reversible
    replacements = {
        "?": "_GS_",  # glottal stop
        "`": "_AP_",
        "@": "_AT_",
        ":": "_LG_",
        "~": "_TD_",
        "\\": "_SL_",
    }
    for source, target in replacements.items():
        slug_label = slug_label.replace(source, target)

    return slug_label


def chars2corr(char_data):
    """
    Builds a correspondence data structure from a chars one.
    """

    # Collect character values for each correspodence pattern
    lang_obs = defaultdict(list)
    pat_values = defaultdict(list)
    for row in char_data:
        for pattern, value in zip(row["PATTERNS"].split(), row["ALIGNMENT"].split()):
            # Skip over morphological markers
            if value == "+":
                continue

            # `pattern_idx` == 0 is used for singletons
            pattern_idx, _ = pattern.split("/")
            if pattern_idx != "0":
                lang_obs[row["DOCULECT"], pattern_idx].append(value)
                pat_values[pattern_idx].append(value)

    # Collect data for nexus/csv
    doculects = sorted(set([doculect for doculect, _ in list(lang_obs)]))
    data = []
    for pattern, values in pat_values.items():
        if len(set(values)) > 1:  # TODO: need for len?
            for doculect in doculects:
                phonemes = lang_obs.get((doculect, pattern), None)
                if phonemes:
                    # Adapt lingpy notation to NEXUS
                    if phonemes[0] == "-":
                        ref_phon = "ZERO"
                    else:
                        # TODO: should take the second part (in lingpy notation)?
                        ref_phon = slug_phoneme_label(phonemes[0].split("/")[0])

                    data.append(
                        {
                            "DOCULECT": doculect,
                            "CHAR": f'c{pattern.replace("-", "_")}',
                            "PHONEME": ref_phon,
                        }
                    )

    corr_data = sorted(data, key=lambda r: (r["CHAR"], r["DOCULECT"]))

    return corr_data


################################3
def dummy():
    return 13
