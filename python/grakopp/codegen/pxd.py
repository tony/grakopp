# python/grakopp/codegen/pxd.py - Grako++ code generator backend for grako -*- coding: utf-8 -*-
# Copyright (C) 2014 semantics Kommunikationsmanagement GmbH
# Written by Marcus Brinkmann <m.brinkmann@semantics.de>
#
# This file is part of Grako++.  Grako++ is free software; you can
# redistribute it and/or modify it under the terms of the 2-clause
# BSD license, see file LICENSE.TXT.

# The Python parts in this file is based on Grako's code generators.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

"""
C++ code generation for models defined with grako.model
"""

from grako.util import indent, trim, timestamp
from grako.exceptions import CodegenError
from grako.model import Node
from grako.codegen.cgbase import ModelRenderer, CodeGenerator


class PxdCodeGenerator(CodeGenerator):
    def _find_renderer_class(self, item):
        if not isinstance(item, Node):
            return None

        name = item.__class__.__name__
        renderer = globals().get(name, None)
        if not renderer or not issubclass(renderer, ModelRenderer):
            raise CodegenError('Renderer for %s not found' % name)
        return renderer


def codegen(model):
    return PxdCodeGenerator().render(model)


class Grammar(ModelRenderer):
    def render_fields(self, fields):
        abstract_template = trim(self.abstract_rule_template)
        abstract_rules = [
            abstract_template.format(parsername=fields['name'], name=rule.name)
            for rule in self.node.rules
        ]
        abstract_rules = indent(''.join(abstract_rules), 2)

        rule_template = trim(self.rule_template)
        rules = [
            rule_template.format(parsername=fields['name'], name=rule.name)
            for rule in self.node.rules
        ]
        rules = indent(''.join(rules), 2)

        if self.node.statetype is None:
            statetype_arg = ", int"
        else:
            statetype_arg = ", " + self.node.statetype

        version = str(tuple(int(n) for n in str(timestamp()).split('.')))

        fields.update(abstract_rules=abstract_rules,
                      rules=rules,
                      version=version,
                      statetype_arg=statetype_arg)

    # FIXME.  Clarify interface (avoid copies). 
    abstract_rule_template = '''
            AstPtr _{name}_ (AstPtr& ast) nogil
            '''

    rule_template = '''
            AstPtr _{name}_() nogil
            '''

    template = '''\
                # -*- coding: utf-8 -*-
                # CAVEAT UTILITOR
                #
                # This file was automatically generated by Grako++.
                # https://pypi.python.org/pypi/grakopp/
                #
                # Any changes you make to it will be overwritten the next time
                # the file is generated.
                
                # Version: {version}

                from grakopp.ast cimport AstPtr
                from grakopp.parser cimport Parser

                cdef extern from "_{name}Parser.hpp":

                    cdef cppclass {name}Semantics:
                {abstract_rules}

                    cdef cppclass {name}Parser(Parser[{name}Semantics{statetype_arg}]):
                        AstPtr {name}Parser() nogil
                        AstPtr {name}Parser({name}Semantics* semantics) nogil
                        # ctypedef AstPtr (nameParser::*rule_method_t) () nogil
                        # rule_method_t find_rule(const string& name) nogil
                {rules}
               '''
