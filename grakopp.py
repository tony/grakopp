# -*- coding: utf-8 -*-
"""
Parse and translate an EBNF grammar into a C++ parser for
the described language.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import grako
from codegen import codegen


# From grako.tool:

import codecs
import argparse
import os
import pickle
import sys

from grako.util import eval_escapes
from grako.exceptions import GrakoException
from grako.parser import GrakoGrammarGenerator

DESCRIPTION = ('GRAKO (for "grammar compiler") takes grammars'
               ' in a variation of EBNF as input, and outputs a memoizing'
               ' PEG/Packrat parser in Python.'
               )


argparser = argparse.ArgumentParser(prog='grako',
                                    description=DESCRIPTION
                                    )
argparser.add_argument('filename',
                       metavar='GRAMMAR',
                       help='The filename of the Grako grammar'
                       )
argparser.add_argument('-n', '--no-nameguard',
                       help='allow tokens that are prefixes of others',
                       dest="nameguard", action='store_false', default=True
                       )
argparser.add_argument('-m', '--name',
                       nargs=1,
                       metavar='NAME',
                       help='Name for the grammar (defaults to GRAMMAR base name)'
                       )
argparser.add_argument('-o', '--output',
                       metavar='FILE',
                       help='output file (default is stdout)'
                       )
argparser.add_argument('-t', '--trace',
                       help='produce verbose parsing output',
                       action='store_true'
                       )
argparser.add_argument('-w', '--whitespace',
                       metavar='CHARACTERS',
                       help='characters to skip during parsing (use "" to disable)',
                       default=None
                       )


def genmodel(name, grammar, trace=False, filename=None):
    parser = GrakoGrammarGenerator(name, trace=trace)
    return parser.parse(grammar, filename=filename)


def gencode(name, grammar, trace=False, filename=None):
    model = genmodel(name, grammar, trace=trace, filename=filename)
    return codegen(model)


def _error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    try:
        args = argparser.parse_args()
    except Exception as e:
        _error(str(e))
        sys.exit(2)

    filename = args.filename
    name = args.name
    nameguard = args.nameguard
    outfile = args.output
    trace = args.trace
    whitespace = args.whitespace

    if whitespace:
        whitespace = eval_escapes(args.whitespace)

    if name is None:
        name = os.path.splitext(os.path.basename(filename))[0]

    if outfile and os.path.isfile(outfile):
        os.unlink(outfile)

    grammar = codecs.open(filename, 'r', encoding='utf-8').read()

    if outfile:
        dirname = os.path.dirname(outfile)
        if dirname and not os.path.isdir(dirname):
            os.makedirs(dirname)

    try:
        model = genmodel(name, grammar, trace=trace, filename=filename)
        model.whitespace = whitespace
        model.nameguard = nameguard

        result = codegen(model)

        if outfile:
            with codecs.open(outfile, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result)
    except GrakoException as e:
        _error(e)
        sys.exit(1)

if __name__ == '__main__':
    main()