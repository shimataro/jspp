#!/usr/bin/python2.7
# coding: utf-8
""" JavaScript Preprocessor

format:
$ jspp [options]

options:
    -s|--semicolon
    -d|--define <symbol>
    -i|--input <input-filename>
    -o|--output <output-filename>
"""
import os
import sys
import re
import getopt

# directive patterns
re_include = re.compile(r"^\s*//\s*#include\s+\"(.+)\"\s*$")
re_ifdef = re.compile(r"^\s*//\s*#ifdef\s+(\w+)\s*$")
re_ifndef = re.compile(r"^\s*//\s*#ifndef\s+(\w+)\s*$")
re_endif = re.compile(r"^\s*//\s*#endif\s*$")

# max depth of "include" (for recursive inclusion)
MAX_DEPTH_INCLUDE = 100


def main():
    """ main function """
    try:
        # parse options
        options = parse_args()

        file_in, file_out = get_inout(options)
        with file_in, file_out:
            parse_file(file_in, file_out, options)

        if options["depth_if"] != 0:
            raise JsppError(
                JsppError.EX_IF_NOMATCH, "#if(n)def - #endif not matched")

        return os.EX_OK

    except JsppError as err:
        print_err(err.message)
        return err.status

    except getopt.GetoptError as err:
        # option error
        print_err(err.msg)
        return os.EX_USAGE

    except IOError as err:
        # file error
        print_err("{message}: {filename}".format(
            message=err.strerror, filename=err.filename))
        return os.EX_IOERR


def parse_args():
    """ parse arguments

    @return: parse result
    @raise: getopt.GetoptError
    """
    opts, args = getopt.getopt(
        sys.argv[1:],
        "sd:i:o:",
        ["semicolon", "define=", "input=", "output="])

    options = {
        "semicolon": False,
        "defined": {},

        "if_true": None,
        "depth_if": 0,
        "depth_include": 0,
    }
    for o, a in opts:
        if o in ("-s", "--semicolon"):
            # add semicolon
            options["semicolon"] = True
            continue

        if o in ("-d", "--define"):
            # define symbol
            options["defined"][a] = True
            continue

        if o in ("-i", "--input"):
            # input file
            options["input"] = a
            continue

        if o in ("-o", "--output"):
            # output file
            options["output"] = a
            continue

    return options


def get_inout(options):
    """ get input/output objects

    @param options: parse result
    @return: input, output
    @raise: IOError
    """
    # open files
    file_in = sys.stdin
    file_out = sys.stdout
    try:
        if "input" in options:
            file_in = open(options["input"], "r")
            dirname = os.path.dirname(options["input"])
            if dirname != "":
                os.chdir(dirname)

        if "output" in options:
            file_out = open(options["output"], "w")

        return file_in, file_out

    except:
        file_in.close()
        file_out.close()
        raise


def parse_file(file_in, file_out, options):
    """ parse file and output result

    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @raise: JsppError
    @raise: IOError
    """
    for line in file_in:
        if parse_include(line, file_in, file_out, options):
            continue

        if parse_ifdef(line, file_in, file_out, options):
            continue

        if parse_ifndef(line, file_in, file_out, options):
            continue

        if parse_endif(line, file_in, file_out, options):
            # escape!
            return

        if options["if_true"] == False:
            # ignore this line
            continue

        file_out.write(line)


def parse_include(line, file_in, file_out, options):
    """ parse "include" directive

    @param line: current line
    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @return: processed #include or not
    @raise: JsppError
    @raise: IOError
    """
    m = re_include.match(line)
    if not m:
        # no match
        return False

    if options["if_true"] == False:
        # ignore
        return True

    if options["depth_include"] >= MAX_DEPTH_INCLUDE:
        raise JsppError(
            JsppError.EX_MAX_INCLUDES_DEPTH, "#include reached to max depth")

    options["depth_include"] += 1

    # save current directory
    curdir = os.getcwd()

    # recursive call!
    filename = m.group(1)
    with open(filename, "r") as file_in_new:
        dirname = os.path.dirname(filename)
        if dirname != "":
            os.chdir(dirname)

        parse_file(file_in_new, file_out, options)

    # output semicolon
    if options["semicolon"]:
        file_out.write(";\n")

    # restore current directory
    os.chdir(curdir)

    options["depth_include"] -= 1
    return True


def parse_ifdef(line, file_in, file_out, options):
    """ parse "ifdef" directive

    @param line: current line
    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @return: processed #ifdef or not
    @raise: IOError
    """
    m = re_ifdef.match(line)
    if not m:
        # no match
        return False

    options["if_true"] = False
    symbol = m.group(1)
    if symbol in options["defined"]:
        # defined!
        options["if_true"] = True

    # recursive call!
    options["depth_if"] += 1
    parse_file(file_in, file_out, options)
    return True


def parse_ifndef(line, file_in, file_out, options):
    """ parse "ifndef" directive

    @param line: current line
    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @return: processed #ifndef or not
    @raise: IOError
    """
    m = re_ifndef.match(line)
    if not m:
        # no match
        return False

    options["if_true"] = True
    symbol = m.group(1)
    if symbol in options["defined"]:
        # defined!
        options["if_true"] = False

    # recursive call!
    options["depth_if"] += 1
    parse_file(file_in, file_out, options)
    return True


def parse_endif(line, file_in, file_out, options):
    """ parse "endif" directive

    @param line: current line
    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @raise: JsppError
    """
    m = re_endif.match(line)
    if not m:
        # no match
        return False

    options["if_true"] = None
    options["depth_if"] -= 1
    if options["depth_if"] < 0:
        # too many endif
        raise JsppError(
            JsppError.EX_IF_NOMATCH, "#if(n)def - #endif not matched")

    return True


def print_err(message):
    """ output message (and linefeed) to stderr

    @param message: message to be output
    """
    sys.stderr.write(message)
    sys.stderr.write("\n")


class JsppError(Exception):
    """ JSPP particular error """
    # exit status
    EX_MAX_INCLUDES_DEPTH = 2
    EX_IF_NOMATCH = 3

    def __init__(self, status, message):
        self.status = status
        self.message = message


if __name__ == "__main__":
    sys.exit(main())
