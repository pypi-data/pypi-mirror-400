# Copyright (c) 2019-2021 Thomas Kramer.
# SPDX-FileCopyrightText: 2022 Thomas Kramer
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List
from lark import Lark, Transformer, v_args
import sympy
from sympy.logic import boolalg
from functools import reduce

"""
Parsing boolean functions of liberty format

Operator precedence: First XOR, then AND then OR

Operator Description
’ Invert previous expression
! Invert following expression
^ Logical XOR
* Logical AND
& Logical AND
space Logical AND
+ Logical OR
| Logical OR
1 Signal tied to logic 1
0 Signal tied to logic 0
"""

boolean_function_grammar = r"""

    ?start: or_expr

    ?or_expr: and_expr ([ "+" | "|" ] and_expr)*

    ?and_expr: xor_expr ([ "&" | "*" ]? xor_expr)*

    ?xor_expr: atom
        | xor_expr "^" xor_expr

    ?atom: "0" -> constant_false
        | "1" -> constant_true
        | CNAME -> name
        | "!" atom -> not_expr
        | atom "'" -> not_expr
        | "(" or_expr ")"

    %import common.CNAME
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)
class BooleanFunctionTransformer(Transformer):
    from operator import __inv__
    
    def constant_false(self):
        return boolalg.BooleanFalse()

    def constant_true(self):
        return boolalg.BooleanTrue()
    
    not_expr = __inv__
    
    def or_expr(self, *exprs):
        from operator import __or__
        return reduce(__or__, exprs)

    def and_expr(self, *exprs):
        from operator import __and__
        return reduce(__and__, exprs)

    def xor_expr(self, *exprs):
        from operator import __xor__
        return reduce(__xor__, exprs)

    def name(self, n):
        return sympy.Symbol(n)


# Singleton object of the parser.
_liberty_parser = Lark(boolean_function_grammar,
                       parser='lalr',
                       #lexer='basic',
                       transformer=BooleanFunctionTransformer()
                       )


def parse_boolean_function(data: str):
    """
    Parse a boolean function into a sympy formula.
    :param data: String representation of boolean expression as defined in liberty format.
    :return: sympy formula
    """

    function = _liberty_parser.parse(data)
    return function


def test_parse_boolean_function():
    f_str =    a, b, c, d, e, f, g, h, i = sympy.symbols('A B C D E F G H I')

    test_vector = [
        ( "0", False ),
        ( "1", True ),
        ( "A", a ),
        ( "( (( A) )) ", a),
        ( "!A", ~a ),
        ( "!    A", ~a ),
        ( "A'", ~a ),
        ( "A & B", a & b ),
        ( "!(A & B)", ~(a & b) ),
        ( "(A & B)'", ~(a & b) ),
        ( "A B", a & b ),
        ( "A | B", a | b ),
        ( "A + B", a | b ),
        ( "A ^ B'", a ^ ~b ),
        ( "A' ^ B", ~a ^ b ),
        ( "A B'", a & ~b ),
        ( "(A B)'", ~(a & b) ),
        ( "A & B ^ C", a & (b ^ c)), # XOR before AND
        ( "A | B ^ C", a | (b ^ c)), # XOR before OR
        ( "A | B & C", a | (b & c)), # AND before OR
        ( "A' + B + C & D + E ^ F * G | (H + I)",
             ~a | b | c & d | (e ^ f) & g | (h | i)
        ),
    ]
    
    for f_str, f_exp in test_vector:
    
        f_actual = parse_boolean_function(f_str)
        
        assert f_actual == f_exp


def format_boolean_function(function: boolalg.Boolean) -> str:
    """
    Format a sympy boolean expression using the liberty format.
    :param function: Sympy boolean expression.
    :return: Formatted string.
    """

    def _format(exp) -> str:
        if isinstance(exp, boolalg.BooleanFalse):
            return "0"
        elif isinstance(exp, boolalg.BooleanTrue):
            return "1"
        elif isinstance(exp, sympy.Symbol):
            return exp.name
        elif isinstance(exp, sympy.Not):
            return '!{}'.format(_format(exp.args[0]))
        elif isinstance(exp, sympy.Or):
            return "({})".format(" + ".join([_format(a) for a in exp.args]))
        elif isinstance(exp, sympy.And):
            return "({})".format(" & ".join([_format(a) for a in exp.args]))
        elif isinstance(exp, sympy.Xor):
            return "({})".format(" ^ ".join([_format(a) for a in exp.args]))
        else:
            assert False, '`{}` not supported.'.format(type(exp))

    s = '({})'.format(_format(function))

    s.replace('~', '!')
    s.replace(' ', '')
    s.replace('|', '+')
    s.replace('&', ' ')

    return s


def test_format_boolean_function():
    a, b, c, d, e, f, g, h, i = sympy.symbols('A B C D E F G H I')
    
    functions = [
        boolalg.BooleanFalse(),
        boolalg.BooleanTrue(),
        a,
        ~a,
        a & b,
        a | b,
        a ^ b,
        ~(a & b),
        ~(a | b),
        ~(a ^ b),
        ~(a & ~b),
        ~a | ~b,
        ~(a & b) | (c & d),
        (a & b) | (b & c) | (c & a),
        ~a | b | c & d | (e ^ f) & g | (h | i)
    ]

    for f in functions:
        # Convert to string.
        s = format_boolean_function(f)

        print(s)
        # Parse again.
        f_parsed = parse_boolean_function(s)

        assert f == f_parsed
    
def test_format_boolean_function_issue14():
    a, b = sympy.symbols("A B")
    f = ~(a & b)
    
    assert f == parse_boolean_function(format_boolean_function(f))
    
