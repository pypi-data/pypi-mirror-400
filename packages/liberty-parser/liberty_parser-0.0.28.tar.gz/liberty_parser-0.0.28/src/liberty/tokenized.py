# SPDX-FileCopyrightText: 2024 Thomas Kramer
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Iterable
from .lexer import *

def tokenize(iter, lexer):
    return Tokenized(PeekingIterator(iter), lexer)

class ParserError(Exception):
    pass

class UnexpectedToken(ParserError):

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        
class InvalidLiteral(ParserError):

    def __init__(self, literal):
        self.literal = literal
        
class UnexpectedEndOfFile(ParserError):
    pass

class Tokenized:

    def __init__(self, iter: PeekingIterator, lexer):
        assert isinstance(iter, PeekingIterator)
        self.iter = iter
        self.lexer = lexer
        self.has_current = False
        self.current_token = []

    def advance(self):
        """
        Advance to the next token.
        """
        buffer = self.current_token
        buffer.clear()
        
        self.lexer.consume_next_token(self.iter, lambda c: buffer.append(c))

        if buffer:
            self.current_token = buffer
            self.has_current = True
        else:
            self.has_current = False

    def current_token_ref(self):
        if self.has_current:
            return self.current_token
        else:
            return None

    def current_token_str(self):
        if self.has_current:
            return "".join(self.current_token)
        else:
            return None

    def current_token_copy(self):
        if self.has_current:
            self.current_token.copy()
        else:
            return None

    def take(self):
        """
        Take and consume token.
        """
        t = self.current_token
        self.current_token = []
        self.advance()
        if t:
            return t
        else:
            return None

    def take_str(self):
        t = self.take()
        if t is not None:
            return "".join(t)
        else:
            return None
        
    def expect(self, expected):
        """
        Test if the current token has the `expected` value.
        If not, raise an `UnexpectedToken` exception.
        """
        assert isinstance(expected, list)
        
        if self.current_token:
            if self.current_token == expected:
                self.advance()
            else:
                raise UnexpectedToken(expected, self.current_token)
        else:
            raise UnexpectedEndOfFile()

    def expect_str(self, expected: str):
        assert isinstance(expected, str)
        return self.expect(list(expected))        

    def peeking_test(self, expected):
        """
        Test if the current token is equal to `expected`.
        Does not consume the token.
        """
        assert isinstance(expected, list)
        
        if self.current_token:
            return self.current_token == expected
        else:
            return False
        
    def peeking_test_str(self, expected):
        return self.peeking_test(list(expected))

    def test(self, expected):
        """
        Test if the current token is equal to `expected`.
        If it matches, consume it.
        """
        assert isinstance(expected, list)

        matches = self.peeking_test(expected)
        if matches:
            self.advance()
        return matches

    def test_str(self, expected):
        assert isinstance(expected, str)
        return self.test(list(expected))

    def skip_until(self, stop_pattern):
        """
        Consume tokens until and including the `stop_pattern`.
        """
        while not self.test(stop_pattern):
            self.advance()
            
        

def test_tokenized():

    class SimpleLexer:

        def consume_next_token(self, iter, output_fn):
            whitespace =  [" ", "\t", "\n", "\r"]

            try:
                while True:
                    # Consume all whitespace.
                    if iter.peek() in whitespace:
                        next(iter)
                    else:
                        break
            except StopIteration:
                pass
            
            # Consume until whitespace.
            for c in iter:
                if c in whitespace:
                    return
                output_fn(c)

    data = "here \n are \t some words  "
    tk = tokenize(iter(data), SimpleLexer())

    tk.advance()
    assert tk.peeking_test_str("here")

    # Test exception:
    did_raise_exception = False
    try:
        tk.expect_str("expected")
    except UnexpectedToken as e:
        did_raise_exception = True
        assert e.expected == list("expected")
        assert e.actual == list("here")
    assert did_raise_exception
    
    assert tk.test_str("here")
    assert tk.current_token_str() == "are"
    tk.expect_str("are")
    tk.expect_str("some")
    tk.expect_str("words")
