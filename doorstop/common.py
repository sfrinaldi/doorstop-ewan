# SPDX-License-Identifier: LGPL-3.0-only

"""Common exceptions, classes, and functions for Doorstop."""

import argparse
import codecs
import csv
import glob
import io
import logging
import os
import re
import shutil

import frontmatter
import yaml

verbosity = 0  # global verbosity setting for controlling string formatting
PRINT_VERBOSITY = 0  # minimum verbosity to using `print`
STR_VERBOSITY = 3  # minimum verbosity to use verbose `__str__`
MAX_VERBOSITY = 4  # maximum verbosity level implemented


def _trace(self, message, *args, **kws):
    if self.isEnabledFor(logging.DEBUG - 1):
        self._log(logging.DEBUG - 1, message, args, **kws)  # pylint: disable=W0212


logging.addLevelName(logging.DEBUG - 1, "TRACE")
logging.Logger.trace = _trace  # type: ignore
logging.basicConfig(filename="warning_log.txt", level=logging.WARNING)
logging.captureWarnings(True)
logger = logging.getLogger
log = logger(__name__)

# exception classes ##########################################################


class DoorstopError(Exception):
    """Generic Doorstop error."""


class DoorstopFileError(DoorstopError, IOError):
    """Raised on IO errors."""


class DoorstopWarning(DoorstopError, Warning):
    """Generic Doorstop warning."""


class DoorstopInfo(DoorstopWarning, Warning):
    """Generic Doorstop info."""


# logging classes ############################################################


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Command-line help text formatter with wider help text."""

    def __init__(self, *args, **kwargs):
        kwargs["max_help_position"] = 40
        super().__init__(*args, **kwargs)


class WarningFormatter(logging.Formatter):
    """Logging formatter that displays verbose formatting for WARNING+."""

    def __init__(self, default_format, verbose_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_format = default_format
        self.verbose_format = verbose_format

    def format(self, record):
        """Python 3 hack to change the formatting style dynamically."""
        if record.levelno > logging.INFO:
            self._style._fmt = self.verbose_format  # pylint: disable=W0212
        else:
            self._style._fmt = self.default_format  # pylint: disable=W0212
        return super().format(record)


# disk helper functions ######################################################


def create_dirname(path):
    """Ensure a parent directory exists for a path."""
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.isdir(dirpath):
        log.info("creating directory {}...".format(dirpath))
        os.makedirs(dirpath)


def read_lines(path, encoding="utf-8"):
    """Read lines of text from a file.

    :param path: file to write lines
    :param encoding: output file encoding

    :return: path of new file

    """
    log.trace("reading lines from '{}'...".format(path))  # type: ignore
    with open(path, "r", encoding=encoding) as stream:
        for line in stream:
            yield line


def read_text(path):
    """Read text from a file.

    :param path: file path to read from
    :param encoding: input file encoding

    :return: string

    """
    log.trace("reading text from '{}'...".format(path))  # type: ignore
    try:
        with codecs.open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        msg = "reading '{}' failed: {}".format(path, e)
        raise DoorstopError(msg)


def load_yaml(text, path, loader=yaml.SafeLoader):
    """Parse a dictionary from YAML text.

    :param text: string containing dumped YAML data
    :param path: file path for error messages

    :return: dictionary

    """
    # Load the YAML data
    try:
        data = yaml.load(text, Loader=loader) or {}
    except yaml.error.YAMLError as exc:
        msg = "invalid contents: {}:\n{}".format(path, exc)
        raise DoorstopError(msg) from None
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        msg = "invalid contents: {}".format(path)
        raise DoorstopError(msg)
    # Return the parsed data
    return data


def load_markdown(text, path, textattributekeys):
    """Parse a dictionary from Markdown file with YAML frontmatter.

    :param text: string containing markdown data with yaml frontmatter
    :param path: file path for error messages

    :return: dictionary

    """
    # Load YAML-frontmatter data from text
    try:
        data, content = frontmatter.parse(text, handler=frontmatter.YAMLHandler())
    except yaml.error.YAMLError as exc:
        msg = "invalid yaml contents: {}:\n{}".format(path, exc)
        raise DoorstopError(msg) from None
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        msg = "invalid contents: {}".format(path)
        raise DoorstopError(msg)

    # parse content and update data dictionariy accordingly
    update_data_from_markdown_content(data, content, textattributekeys)

    # Return the parsed data
    return data


def write_lines(lines, path, end="\n", encoding="utf-8", *, executable=False):
    """Write lines of text to a file.

    :param lines: iterator of strings
    :param path: file to write lines
    :param end: string to end lines
    :param encoding: output file encoding

    :return: path of new file

    """
    log.trace("writing lines to '{}'...".format(path))  # type: ignore
    with open(path, "wb") as stream:
        for line in lines:
            data = (line + end).encode(encoding)
            stream.write(data)
    if executable and os.path.isfile(path):
        os.chmod(path, 0o775)
    return path


def write_text(text, path, end="\n"):
    """Write text to a file.

    :param text: string
    :param path: file to write text
    :param end: string to end lines
    :param encoding: output file encoding

    :return: path of new file

    """
    if text:
        log.trace("writing text to '{}'...".format(path))  # type: ignore
    with open(path, "w", encoding="utf-8", newline=end) as f:
        f.write(text)
    return path


def write_csv(table, path, delimiter=",", newline="", encoding="utf-8"):
    """Write table to a file.

    :param table: iterator of rows
    :param path: file to write lines
    :param delimiter: string to end cells
    :param newline: string to end lines
    :param encoding: output file encoding

    :return: path of new file

    """
    log.trace("writing table to '{}'...".format(path))  # type: ignore
    with open(path, "w", newline=newline, encoding=encoding) as stream:
        writer = csv.writer(stream, delimiter=delimiter)
        for row in table:
            writer.writerow(row)
    return path


def touch(path):
    """Ensure a file exists."""
    if not os.path.exists(path):
        log.trace("creating empty '{}'...".format(path))  # type: ignore
        write_text("", path)


def copy_dir_contents(src, dst):
    """Copy the contents of a directory."""
    for fpath in glob.glob("{}/*".format(src)):
        dest_path = os.path.join(dst, os.path.split(fpath)[-1])
        if os.path.exists(dest_path):
            if os.path.basename(fpath) == "doorstop":
                msg = "Skipping '{}' as this directory name is required by doorstop".format(
                    fpath
                )
            else:
                msg = "Skipping '{}' as a file or directory with this name already exists".format(
                    fpath
                )
            log.warning(msg)
        else:
            if os.path.isdir(fpath):
                shutil.copytree(fpath, dest_path)
            else:
                shutil.copyfile(fpath, dest_path)


def delete(path):
    """Delete a file or directory with error handling."""
    if os.path.isdir(path):
        try:
            log.trace("deleting '{}'...".format(path))  # type: ignore
            shutil.rmtree(path)
        except IOError:
            # bug: http://code.activestate.com/lists/python-list/159050
            msg = "unable to delete: {}".format(path)
            log.warning(msg)
    elif os.path.isfile(path):
        log.trace("deleting '{}'...".format(path))  # type: ignore
        os.remove(path)


def delete_contents(dirname):
    """Delete the contents of a directory."""
    for file in glob.glob("{}/*".format(dirname)):
        if os.path.isdir(file):
            shutil.rmtree(os.path.join(dirname, file))
        else:
            try:
                os.remove(os.path.join(dirname, file))
            except FileExistsError:
                log.warning(
                    "Two assets folders have files or directories with the same name"
                )
                raise


def update_data_from_markdown_content(data, content, textattributekeys):
    """Update data dictionary based on text content and attribute keys to look for within the content."""
    h1 = re.compile(r"^#{1}\s+(.*)")
    # for line based iteration
    s = io.StringIO(content)
    # final text
    header = None
    text = ""

    if "header" in textattributekeys:
        # search for first content line and check
        # if it is a h1 header
        for l in s:
            # skip empty lines
            if len(l.strip()) == 0:
                continue
            # check if first found line is a header
            m = h1.match(l.strip())
            if m:
                # header found
                header = m.group(1)
            else:
                # no header found, add to normal text
                text += l
            break

        # if header was found, skip empty lines before main text
        if header:
            for l in s:
                if len(l.strip()) != 0:
                    text += l
                    break

    # remaining content is normal text
    for l in s:
        text += l

    if "header" in textattributekeys and header:
        data["header"] = header

    if "text" in textattributekeys:
        data["text"] = text


def dump_markdown(data, textattr):
    content = ""
    if "header" in textattr and textattr["header"].strip() != "":
        content += "# {}\n".format(textattr["header"].strip())
        content += "\n"

    content += textattr["text"]

    text = frontmatter.dumps(
        frontmatter.Post(content, **data), Dumper=yaml.dumper.Dumper
    )
    return text
