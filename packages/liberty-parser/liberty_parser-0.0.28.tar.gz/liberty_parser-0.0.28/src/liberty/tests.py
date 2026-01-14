# SPDX-FileCopyrightText: 2022 Thomas Kramer
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .parser import parse_liberty
from .types import *


def test_select_timing_group_1():
    data = r"""
pin(Y){ 
    timing() {
        test_label: 1;
        related_pin: "A";
        when: "A & B";
        cell_rise() {
            test_label: 11;
        }
    }
    timing() {
        test_label: 2;
        related_pin: "A";
        when: "!B";
        cell_rise() {
            test_label: 21;
        }
    }
    timing() {
        test_label: 3;
        related_pin: B; // Unescaped string
        when: A; // Unescaped string
        cell_rise() {
            test_label: 31;
        }
    }
}
"""
    pin_group = parse_liberty(data)
    assert isinstance(pin_group, Group)

    timing_group = select_timing_group(pin_group, related_pin="A")
    assert timing_group['test_label'] == 1

    timing_group = select_timing_group(pin_group, related_pin="A", when='B & A') # Note: A and B are swapped in `when` expression.
    assert timing_group['test_label'] == 1

    timing_group = select_timing_group(pin_group, related_pin="A", when='!B')
    assert timing_group['test_label'] == 2

    timing_group = select_timing_group(pin_group, related_pin="B")
    assert timing_group['test_label'] == 3

    assert select_timing_table(pin_group, related_pin="A", when='!B', table_name='cell_rise')['test_label'] == 21
    # Test with unescaped strings.
    assert select_timing_table(pin_group, related_pin="B", when='A', table_name='cell_rise')['test_label'] == 31

def test_replace_array():
    """
    'set_array' should replace existing arrays instead of appending a new one.
    
    See: https://codeberg.org/tok/liberty-parser/issues/16
    """

    data = r"""
    group() {
        myArray ( \
    "0, 0, 0", \
    "0, 0, 0" \
    );
    }
    """

    group = parse_liberty(data)
    assert isinstance(group, Group)

    assert len(group.attributes) == 1

    group.set_array("myArray", np.array([1, 2, 3]))

    assert len(group.attributes) == 1
    assert (group.get_array("myArray") == [1, 2, 3]).all()


def test_select_timing_group_by_timing_type():
    """
    Select timing groups by their `timing_type` attribute.

    Test fix proposed in https://codeberg.org/tok/liberty-parser/issues/16.
    """

    data = r"""
        pin(Y) {
            timing() {
                related_pin : "CLK";
                timing_type : hold_falling;
            }
            timing() {
                related_pin : "CLK";
                timing_type : setup_falling;
            }
            timing() {
                related_pin : "CLK";
                timing_type : "fantasy_escaped_string";
            }
        }    
    """

    pin = parse_liberty(data)
    assert isinstance(pin, Group)


    timing_hold_falling = select_timing_group(pin, related_pin = "CLK", timing_type = "hold_falling")
    assert isinstance(timing_hold_falling, Group)
    assert timing_hold_falling.get_attribute("timing_type") == "hold_falling"

    timing_setup_falling = select_timing_group(pin, related_pin = "CLK", timing_type = "setup_falling")
    assert isinstance(timing_setup_falling, Group)
    assert timing_setup_falling.get_attribute("timing_type") == "setup_falling"

    # Test if timing type is escaped.
    should_not_fail = select_timing_group(pin, related_pin = "CLK", timing_type = "fantasy_escaped_string")
    
    try:
        should_fail = select_timing_group(pin, related_pin = "CLK", timing_type = "doesnotexist")
    except Exception as e:
        # Error message should hint to existing timing types.
        assert "hold_falling" in str(e)
    



def test_library_colon_in_group_argument():
    """
    See https://codeberg.org/tok/liberty-parser/issues/15
    """

    data = r"""
        library(mylib) {
            input_ccb (FOO:a) {}
        }
    """

    lib = parse_liberty(data)
    assert isinstance(lib, Group)


def test_library_name_begins_with_digit():
    """
    See https://codeberg.org/tok/liberty-parser/issues/17
    """

    data = r"""
        library(0V95XXX) {
        
        }
    """

    lib = parse_liberty(data)
    assert isinstance(lib, Group)
    
def test_library_name_with_minus():
    """
    See issue 18.
    """

    data = r"""
        library(some_lib_-10C) {
        
        }
    """

    lib = parse_liberty(data)
    assert isinstance(lib, Group)

def test_format_multiline_string():
    """
    See https://codeberg.org/tok/liberty-parser/issues/19
    """

    data = r"""somegroup () {
  table : "line 1, \
line 2, \
line 3";
}"""
    group = parse_liberty(data)
    assert isinstance(group, Group)

    expected = r"""line 1, \
line 2, \
line 3"""
    assert group["table"] == expected

    # Format again and check for equality with original input.
    formatted = str(group)

    assert formatted == data


def test_without_space_after_colon():
    """
    See https://codeberg.org/tok/liberty-parser/issues/21
    """

    data = r"""
    timing(){ 
        timing_type :"min_pulse_width"; 
    }
    """
    
    group = parse_liberty(data)
    assert isinstance(group, Group)

#def test_two_dimensional_bus_pins():
#    """
#    See: https://codeberg.org/tok/liberty-parser/issues/22
#    """
#
#    data = r"""
#    library(test) {
#        cell(somecell) {
#          bus( x_if[0].y ) {
#            pin("x_if[0].y[0]") {
#                content: asdf ;
#            }
#          }
#        }
#    }
#    """
#
#    group = parse_liberty(data)
#    assert isinstance(group, Group)

def test_semicolon_after_group():
    """
    See https://codeberg.org/tok/liberty-parser/issues/24
    """

    data = r"""
 group( ) {
     inner1() {};
     inner2() {}
 };
    """
    
    group = parse_liberty(data)
    assert isinstance(group, Group)

def test_empty_escaped_string():
    """
    See https://codeberg.org/tok/liberty-parser/issues/25
    """

    data = r"""
    group() {
        comment: "";
    }
"""
    group = parse_liberty(data)
    assert isinstance(group, Group)
    assert group["comment"] == EscapedString("")

def test_issue50_pin_name_with_slash():
    # See: https://codeberg.org/tok/liberty-parser/issues/50

    data ="""library (mylib){
    cell (mycell){
        pinname : a/b ;
        commentorname1a : /*comment*/ name ;
        commentorname1b : /*comment*/name ;
        commentorname2a : name /*comment*/ ;
        commentorname2b : name/*comment*/ ; // This is not a comment.
    }
}
    """

    group = parse_liberty(data)
    assert isinstance(group, Group)
    assert group.get_group("cell", "mycell")["pinname"] == "a/b"
    assert group.get_group("cell", "mycell")["commentorname1a"] == "name"
    assert group.get_group("cell", "mycell")["commentorname1b"] == "name"
    assert group.get_group("cell", "mycell")["commentorname2a"] == "name"
    assert group.get_group("cell", "mycell")["commentorname2b"] == "name/*comment*/"
