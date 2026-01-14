# SPDX-FileCopyrightText: 2024 Thomas Kramer
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Iterable, Callable

class PeekingIterator:

    def __init__(self, iter: Iterable):
        assert isinstance(iter, Iterable)
        self.iter = iter
        self.has_peeked_value: bool = False
        self.peeked_value = None

    def __iter__(self):
        return self
    
    def __next__(self):
        result = None
        if self.has_peeked_value:
            result = self.peeked_value
            self.peeked_value = None
            self.has_peeked_value = False
        else:
            result = next(self.iter)

        return result

    def peek(self):
        if not self.has_peeked_value:
            self.peeked_value = next(self.iter)
            self.has_peeked_value = True
        return self.peeked_value

        
def test_peekable_iter():
    l = [1, 2, 3]
    i = PeekingIterator(iter(l))

    assert i.peek() == 1
    assert i.peek() == 1
    assert next(i) == 1
    assert i.peek() == 2
    assert next(i) == 2
    assert next(i) == 3
    
class LibertyLexer:

    def __init__(self):
        self.default_terminal_chars = bytearray(b',{}()[];:')
        self.set_default_terminal_chars()

    def set_default_terminal_chars(self):
        self.terminal_chars = self.default_terminal_chars.copy()
        
    def enable_terminal_char(self, char):
        assert len(char) == 1
        c = ord(char)
        if c not in self.terminal_chars:
            self.terminal_chars.append(c)

    def disable_terminal_char(self, char):
        self.terminal_chars.remove(ord(char))
    
    def consume_next_token(self, iter: PeekingIterator, output_fn: Callable):
        try:
            while True:
                self._skip_whitespace(iter)

                c = next(iter)

                if c == '#':
                    # Skip comment
                    self._consume_line(iter)
                elif c == '/':
                    if iter.peek() == '*':
                        next(iter)
                        self._skip_comment_multiline(iter)
                    elif iter.peek() == '/':
                        next(iter)
                        self._consume_line(iter)
                    else:
                        output_fn(c)
                elif c == '\\':
                    # Escape character
                    if iter.peek() == '\\':
                        output_fn('\\')
                        next(iter)
                    elif iter.peek() == '\n':
                        # Ignore masked newline.
                        next(iter)
                    elif iter.peek() == '\r':
                        # Ignore masked newline.
                        next(iter)
                        if iter.peek() == '\n':
                            next(iter)
                    else:
                        output_fn('\\')
                elif c in ['"', "'"]:
                    # Quoted strings.
                    quote_char = c
                    return self._read_quoted_string(quote_char, output_fn, iter)
                else:
                    # Normal token
                    first_char = c
                    return self._read_normal_token(first_char, output_fn, iter)
                        
        except StopIteration:
            pass
            

    def _skip_whitespace(self, iter):
        try:
            while self._is_whitespace(iter.peek()):
                next(iter)
        except StopIteration:
            pass

    def _skip_comment_multiline(self, iter):
        while True:
            # Consume until next '*'
            for c in iter:
                if c == '*':
                    break

            try:
                if iter.peek() == '/':
                    next(iter)
                    # End of comment
                    break
            except StopIteration:
                # End of file.
                break

    def _consume_line(self, iter):
        try:
            for c in iter:
                if c == '\n':
                    break
        except StopIteration:
            pass

    def _is_whitespace(self, c):
        return c.isspace()
    
    def _is_terminal_char(self, c):
        c = ord(c)
        return c < 256 and c in self.terminal_chars

    def _read_quoted_string(self, quote_char, output_fn, iter):
        output_fn(quote_char)
      
        prev = None
        while True:
            c = next(iter)
            output_fn(c)
            if prev != '\\' and c == quote_char:
                # Abort on umasked quote char.
                break
            prev = c
    
    def _read_normal_token(self, first_char, output_fn, iter):
        output_fn(first_char)
        prev = first_char
        if self._is_terminal_char(first_char):
            return

        try:
            while True:
                if self._is_terminal_char(iter.peek()):
                    break
                c = next(iter)
                if prev != '\\' and (self._is_whitespace(c) or self._is_terminal_char(c)):
                    # Abort on unmasked whitespace or terminal character.
                    break
                output_fn(c)
                prev = c
                
        except StopIteration:
            pass
                

def test_skip_comments():

    data = """
      # single line comment 1

      // single line comment 2

     /* multi
    line
    comment */
    """

    lex = LibertyLexer()

    it = PeekingIterator(iter(data))

    buf = []

    def output_fn(c):
        buf.append(c)

    lex.consume_next_token(it, output_fn)
    assert buf == []
    
def test_read_tokens():

    data = r"""
      # single line comment 1

     library (library_name){
        var1 : "quoted_string1";
        var2 : 'quoted_string2';
      // single line comment 2

    /**/
    
    # Masked newline should be ignored.
    \
    
     /* multi
    line
    comment */

    }
    """

    lex = LibertyLexer()

    it = PeekingIterator(iter(data))

    tokens = []
    while True:
        
        buf = []

        def output_fn(c):
            buf.append(c)

        lex.consume_next_token(it, output_fn)

        if not buf:
            break # End of file.
 
        tokens.append("".join(buf)) # Convert to string

    expected_tokens = [
        "library", "(", "library_name", ")", "{",
         "var1", ":", '"quoted_string1"', ";",
         "var2", ":", "'quoted_string2'", ";",
         "}"
    ]

    assert tokens == expected_tokens
