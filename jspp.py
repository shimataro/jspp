#!/usr/bin/python2.7
# coding: utf-8
""" JavaScript Preprocessor

format:
$ jspp [options]

options:
    -s|--semicolon
    -i|--input <input-filename>
    -o|--output <output-filename>
"""
import os, sys, re, getopt
re_include = re.compile(r"^\s*//\s*#include\s+\"(.+)\"\s*$")

# status code
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
# http://www.freebsd.org/cgi/man.cgi?query=sysexits
EX_USAGE = 64
EX_IOERR = 74

def main():
    """ main function """
    try:
        # parse options
        options = parse_args()

        file_in, file_out = get_inout(options)
        with file_in, file_out:
            parse_file(file_in, file_out, options)

        return EXIT_SUCCESS

    except getopt.GetoptError as err:
        # option error
        print_err(err.msg)
        return EX_USAGE

    except IOError as err:
        # file error
        print_err("{message}: {filename}".format(message = err.strerror, filename = err.filename))
        return EX_IOERR


def parse_args():
    """ parse arguments

    @return: parse result
    @raise: getopt.GetoptError
    """
    opts, args = getopt.getopt(sys.argv[1:], "si:o:", ["semicolon", "input=", "output="])
    options = {
        "semicolon": False,
    }
    for o, a in opts:
        if o in ("-s", "--semicolon"):
            # add semicolon
            options["semicolon"] = True
            continue

        if o in ("-i", "--input"):
            # input file
            options["input" ] = a
            continue

        if o in ("-o", "--output"):
            # output file
            options["output"] = a
            continue

    return options


def get_inout(options):
    """ get input/output objects

    @param options: parse result
    @return: input, output (specified files or stdin/stdout)
    @raise: IOError
    """
    # open files
    file_in  = sys.stdin
    file_out = sys.stdout
    try:
        if "input"  in options:
            file_in  = open(options["input"] , "r")
            dirname = os.path.dirname(options["input"])
            if dirname != "":
                os.chdir(dirname)

        if "output" in options:
            file_out = open(options["output"], "w")

        return file_in, file_out

    except:
        file_in .close()
        file_out.close()
        raise


def parse_file(file_in, file_out, options):
    """ parse file and output result

    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @raise: IOError
    """
    for line in file_in:
        if parse_include(line, file_in, file_out, options):
            continue

        file_out.write(line)


def parse_include(line, file_in, file_out, options):
    """ parse "include" directive

    @param line: current line
    @param file_in: input file object
    @param file_out: output file object
    @param options: options
    @raise: IOError
    """
    m = re_include.match(line)
    if not m:
        # no match
        return False
    
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

    return True


def print_err(message):
    """ output message (and linefeed) to stdout

    @param message: message to be output
    """
    sys.stderr.write(message)
    sys.stderr.write("\n")


if __name__ == "__main__":
    status = main()
    sys.exit(status)
