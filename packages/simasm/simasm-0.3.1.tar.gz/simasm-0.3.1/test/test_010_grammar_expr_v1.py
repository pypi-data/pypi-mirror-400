"""
Test Section 11.1: Grammar - Terminals and Expressions

Tests that the Lark grammar correctly parses:
- Literals (numbers, strings, booleans, undef)
- Variables and function applications
- Operators (arithmetic, comparison, logical)
- Function calls (regular, lib.*, rnd.*)
- Collections (tuples, lists)
- new expressions
"""

import pytest
from lark import Lark
from pathlib import Path


# Load grammar
GRAMMAR_PATH = Path(__file__).parent.parent / "simasm" / "parser" / "grammar.lark"


@pytest.fixture(scope="module")
def parser():
    """Create Lark parser for expressions."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, start="expr", parser="lalr")


class TestLiterals:
    """Test literal parsing."""
    
    def test_integer(self, parser):
        tree = parser.parse("42")
        assert tree.data == "number"
    
    def test_float(self, parser):
        tree = parser.parse("3.14")
        assert tree.data == "number"
    
    def test_float_no_leading_digit(self, parser):
        tree = parser.parse(".5")
        assert tree.data == "number"
    
    def test_string(self, parser):
        tree = parser.parse('"hello world"')
        assert tree.data == "string"
    
    def test_string_empty(self, parser):
        tree = parser.parse('""')
        assert tree.data == "string"
    
    def test_true(self, parser):
        tree = parser.parse("true")
        assert tree.data == "true_lit"
    
    def test_false(self, parser):
        tree = parser.parse("false")
        assert tree.data == "false_lit"
    
    def test_undef(self, parser):
        tree = parser.parse("undef")
        assert tree.data == "undef_lit"


class TestVariables:
    """Test variable and location parsing."""
    
    def test_simple_variable(self, parser):
        tree = parser.parse("x")
        assert tree.data == "variable"
    
    def test_variable_with_underscore(self, parser):
        tree = parser.parse("sim_clocktime")
        assert tree.data == "variable"
    
    def test_variable_with_numbers(self, parser):
        tree = parser.parse("load1")
        assert tree.data == "variable"
    
    def test_func_application(self, parser):
        tree = parser.parse("f(x)")
        assert tree.data == "func_app"
    
    def test_func_application_multi_arg(self, parser):
        tree = parser.parse("f(x, y, z)")
        assert tree.data == "func_app"
    
    def test_func_application_no_args(self, parser):
        tree = parser.parse("f()")
        assert tree.data == "func_app"


class TestArithmeticOps:
    """Test arithmetic operators."""
    
    def test_addition(self, parser):
        tree = parser.parse("1 + 2")
        assert tree.data == "add_op"
    
    def test_subtraction(self, parser):
        tree = parser.parse("5 - 3")
        assert tree.data == "sub_op"
    
    def test_multiplication(self, parser):
        tree = parser.parse("4 * 2")
        assert tree.data == "mul_op"
    
    def test_division(self, parser):
        tree = parser.parse("10 / 2")
        assert tree.data == "div_op"
    
    def test_modulo(self, parser):
        tree = parser.parse("10 % 3")
        assert tree.data == "mod_op"
    
    def test_negation(self, parser):
        tree = parser.parse("-x")
        assert tree.data == "neg_op"
    
    def test_precedence_mul_add(self, parser):
        # 1 + 2 * 3 should parse as 1 + (2 * 3)
        tree = parser.parse("1 + 2 * 3")
        assert tree.data == "add_op"
        assert tree.children[1].data == "mul_op"
    
    def test_parentheses(self, parser):
        tree = parser.parse("(1 + 2) * 3")
        assert tree.data == "mul_op"


class TestComparisonOps:
    """Test comparison operators."""
    
    def test_equal(self, parser):
        tree = parser.parse("x == 5")
        assert tree.data == "eq_op"
    
    def test_not_equal(self, parser):
        tree = parser.parse("x != 5")
        assert tree.data == "ne_op"
    
    def test_less_than(self, parser):
        tree = parser.parse("x < 5")
        assert tree.data == "lt_op"
    
    def test_greater_than(self, parser):
        tree = parser.parse("x > 5")
        assert tree.data == "gt_op"
    
    def test_less_equal(self, parser):
        tree = parser.parse("x <= 5")
        assert tree.data == "le_op"
    
    def test_greater_equal(self, parser):
        tree = parser.parse("x >= 5")
        assert tree.data == "ge_op"


class TestLogicalOps:
    """Test logical operators."""
    
    def test_and(self, parser):
        tree = parser.parse("x and y")
        assert tree.data == "and_op"
    
    def test_or(self, parser):
        tree = parser.parse("x or y")
        assert tree.data == "or_op"
    
    def test_not(self, parser):
        tree = parser.parse("not x")
        assert tree.data == "not_op"
    
    def test_precedence_not_and(self, parser):
        # not x and y should parse as (not x) and y
        tree = parser.parse("not x and y")
        assert tree.data == "and_op"
        assert tree.children[0].data == "not_op"
    
    def test_precedence_and_or(self, parser):
        # x or y and z should parse as x or (y and z)
        tree = parser.parse("x or y and z")
        assert tree.data == "or_op"
        assert tree.children[1].data == "and_op"
    
    def test_precedence_comparison_and(self, parser):
        # x < 5 and y > 3 should work
        tree = parser.parse("x < 5 and y > 3")
        assert tree.data == "and_op"
        assert tree.children[0].data == "lt_op"
        assert tree.children[1].data == "gt_op"


class TestFunctionCalls:
    """Test function application parsing (dynamic function reads in expressions)."""
    
    def test_func_app_no_args(self, parser):
        tree = parser.parse("arrive()")
        assert tree.data == "func_app"
    
    def test_func_app_one_arg(self, parser):
        tree = parser.parse("start(load)")
        assert tree.data == "func_app"
    
    def test_func_app_multi_args(self, parser):
        tree = parser.parse("transfer(src, dst, amount)")
        assert tree.data == "func_app"
    
    def test_func_app_with_expr_args(self, parser):
        tree = parser.parse("foo(x + 1, y * 2)")
        assert tree.data == "func_app"


class TestLibCalls:
    """Test lib.* function calls."""
    
    def test_lib_add(self, parser):
        tree = parser.parse("lib.add(queue, item)")
        assert tree.data == "lib_call"
    
    def test_lib_pop(self, parser):
        tree = parser.parse("lib.pop(queue)")
        assert tree.data == "lib_call"
    
    def test_lib_length(self, parser):
        tree = parser.parse("lib.length(queue)")
        assert tree.data == "lib_call"
    
    def test_lib_min_by(self, parser):
        tree = parser.parse('lib.min_by(fel, "1")')
        assert tree.data == "lib_call"
    
    def test_lib_apply_rule(self, parser):
        tree = parser.parse("lib.apply_rule(r, params)")
        assert tree.data == "lib_call"


class TestRndCalls:
    """Test rnd.* function calls."""
    
    def test_rnd_exponential(self, parser):
        tree = parser.parse("rnd.exponential(1.0)")
        assert tree.data == "rnd_call_default"
    
    def test_rnd_uniform(self, parser):
        tree = parser.parse("rnd.uniform(0, 10)")
        assert tree.data == "rnd_call_default"
    
    def test_rnd_stream_exponential(self, parser):
        tree = parser.parse("rnd.arrivals.exponential(2.0)")
        assert tree.data == "rnd_call_stream"
    
    def test_rnd_stream_normal(self, parser):
        tree = parser.parse("rnd.service.normal(5.0, 1.0)")
        assert tree.data == "rnd_call_stream"


class TestNewExpr:
    """Test new Domain expressions."""
    
    def test_new_simple(self, parser):
        tree = parser.parse("new Load")
        assert tree.data == "new_expr"
    
    def test_new_event(self, parser):
        tree = parser.parse("new ArriveEvent")
        assert tree.data == "new_expr"


class TestCollections:
    """Test tuple and list parsing."""
    
    def test_tuple_pair(self, parser):
        tree = parser.parse("(x, y)")
        assert tree.data == "tuple_expr"
    
    def test_tuple_triple(self, parser):
        tree = parser.parse("(vertex, time, priority)")
        assert tree.data == "tuple_expr"
    
    def test_tuple_with_exprs(self, parser):
        tree = parser.parse("(x + 1, y * 2)")
        assert tree.data == "tuple_expr"
    
    def test_list_empty(self, parser):
        tree = parser.parse("[]")
        assert tree.data == "empty_list"
    
    def test_list_single(self, parser):
        tree = parser.parse("[x]")
        assert tree.data == "list_lit"
    
    def test_list_multiple(self, parser):
        tree = parser.parse("[1, 2, 3]")
        assert tree.data == "list_lit"
    
    def test_list_with_exprs(self, parser):
        tree = parser.parse("[x + 1, y * 2, z]")
        assert tree.data == "list_lit"


class TestComplexExpressions:
    """Test complex nested expressions."""
    
    def test_nested_func_calls(self, parser):
        tree = parser.parse("lib.length(lib.filter(queue, pred))")
        assert tree.data == "lib_call"
    
    def test_arithmetic_in_comparison(self, parser):
        tree = parser.parse("x + 1 <= y * 2")
        assert tree.data == "le_op"
    
    def test_func_in_arithmetic(self, parser):
        tree = parser.parse("lib.length(queue) + 1")
        assert tree.data == "add_op"
    
    def test_complex_condition(self, parser):
        tree = parser.parse("not server_busy and lib.length(queue) > 0")
        assert tree.data == "and_op"
    
    def test_fel_event_creation(self, parser):
        # Typical FEL event tuple
        tree = parser.parse("(vertex, sim_clocktime + delay, 0)")
        assert tree.data == "tuple_expr"
    
    def test_chained_comparison_style(self, parser):
        # Multiple comparisons with and
        tree = parser.parse("x >= 0 and x < 10")
        assert tree.data == "and_op"


class TestComments:
    """Test that comments are ignored."""
    
    def test_line_comment_ignored(self, parser):
        # Comments should be stripped
        tree = parser.parse("x // this is a comment")
        assert tree.data == "variable"


class TestEdgeCases:
    """Test edge cases and potential ambiguities."""
    
    def test_identifier_starting_with_keyword(self, parser):
        # 'andx' should be valid identifier, not 'and' + 'x'
        tree = parser.parse("andx")
        assert tree.data == "variable"
    
    def test_identifier_true_prefix(self, parser):
        tree = parser.parse("true_value")
        assert tree.data == "variable"
    
    def test_double_negation(self, parser):
        tree = parser.parse("--x")
        assert tree.data == "neg_op"
        assert tree.children[0].data == "neg_op"
    
    def test_double_not(self, parser):
        tree = parser.parse("not not x")
        assert tree.data == "not_op"
        assert tree.children[0].data == "not_op"
    
    def test_deeply_nested_parens(self, parser):
        tree = parser.parse("((((x))))")
        assert tree.data == "variable"
