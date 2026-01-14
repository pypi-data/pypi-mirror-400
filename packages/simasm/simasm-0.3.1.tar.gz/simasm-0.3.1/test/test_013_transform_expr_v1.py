"""
Test Section 11.4: Transformer - Expressions

Tests that the SimASMTransformer correctly converts parse trees
to AST nodes for expressions.
"""

import pytest
from lark import Lark
from pathlib import Path

from simasm.parser.transformer import SimASMTransformer
from simasm.core.state import UNDEF
from simasm.core.terms import (
    LiteralTerm, VariableTerm, LocationTerm,
    BinaryOpTerm, UnaryOpTerm, ListTerm, TupleTerm,
    NewTerm, LibCallTerm, RndCallTerm,
)


# Load grammar and create parser with transformer
GRAMMAR_PATH = Path(__file__).parent.parent / "simasm" / "parser" / "grammar.lark"


@pytest.fixture(scope="module")
def parser():
    """Create Lark parser with transformer for expressions."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(
        grammar,
        start="expr",
        parser="lalr",
        transformer=SimASMTransformer()
    )


class TestLiteralTransform:
    """Test literal transformation."""
    
    def test_integer(self, parser):
        result = parser.parse("42")
        assert result == LiteralTerm(42)
    
    def test_float(self, parser):
        result = parser.parse("3.14")
        assert result == LiteralTerm(3.14)
    
    def test_string(self, parser):
        result = parser.parse('"hello"')
        assert result == LiteralTerm("hello")
    
    def test_string_empty(self, parser):
        result = parser.parse('""')
        assert result == LiteralTerm("")
    
    def test_true(self, parser):
        result = parser.parse("true")
        assert result == LiteralTerm(True)
    
    def test_false(self, parser):
        result = parser.parse("false")
        assert result == LiteralTerm(False)
    
    def test_undef(self, parser):
        result = parser.parse("undef")
        assert result == LiteralTerm(UNDEF)


class TestVariableTransform:
    """Test variable transformation."""
    
    def test_simple_variable(self, parser):
        result = parser.parse("x")
        assert result == VariableTerm("x")
    
    def test_underscore_variable(self, parser):
        result = parser.parse("sim_clocktime")
        assert result == VariableTerm("sim_clocktime")


class TestLocationTransform:
    """Test location (function application) transformation."""
    
    def test_func_no_args(self, parser):
        result = parser.parse("queue()")
        assert isinstance(result, LocationTerm)
        assert result.func_name == "queue"
        assert result.arguments == ()
    
    def test_func_one_arg(self, parser):
        result = parser.parse("status(load)")
        assert isinstance(result, LocationTerm)
        assert result.func_name == "status"
        assert len(result.arguments) == 1
        assert result.arguments[0] == VariableTerm("load")
    
    def test_func_multi_args(self, parser):
        result = parser.parse("matrix(i, j)")
        assert isinstance(result, LocationTerm)
        assert result.func_name == "matrix"
        assert len(result.arguments) == 2


class TestArithmeticOpTransform:
    """Test arithmetic operator transformation."""
    
    def test_add(self, parser):
        result = parser.parse("1 + 2")
        assert result == BinaryOpTerm('+', LiteralTerm(1), LiteralTerm(2))
    
    def test_sub(self, parser):
        result = parser.parse("5 - 3")
        assert result == BinaryOpTerm('-', LiteralTerm(5), LiteralTerm(3))
    
    def test_mul(self, parser):
        result = parser.parse("4 * 2")
        assert result == BinaryOpTerm('*', LiteralTerm(4), LiteralTerm(2))
    
    def test_div(self, parser):
        result = parser.parse("10 / 2")
        assert result == BinaryOpTerm('/', LiteralTerm(10), LiteralTerm(2))
    
    def test_mod(self, parser):
        result = parser.parse("10 % 3")
        assert result == BinaryOpTerm('%', LiteralTerm(10), LiteralTerm(3))
    
    def test_neg(self, parser):
        result = parser.parse("-x")
        assert result == UnaryOpTerm('-', VariableTerm("x"))
    
    def test_precedence(self, parser):
        # 1 + 2 * 3 should be 1 + (2 * 3)
        result = parser.parse("1 + 2 * 3")
        assert isinstance(result, BinaryOpTerm)
        assert result.operator == '+'
        assert result.left == LiteralTerm(1)
        assert isinstance(result.right, BinaryOpTerm)
        assert result.right.operator == '*'


class TestComparisonOpTransform:
    """Test comparison operator transformation."""
    
    def test_eq(self, parser):
        result = parser.parse("x == 5")
        assert result == BinaryOpTerm('==', VariableTerm("x"), LiteralTerm(5))
    
    def test_ne(self, parser):
        result = parser.parse("x != 5")
        assert result == BinaryOpTerm('!=', VariableTerm("x"), LiteralTerm(5))
    
    def test_lt(self, parser):
        result = parser.parse("x < 5")
        assert result == BinaryOpTerm('<', VariableTerm("x"), LiteralTerm(5))
    
    def test_gt(self, parser):
        result = parser.parse("x > 5")
        assert result == BinaryOpTerm('>', VariableTerm("x"), LiteralTerm(5))
    
    def test_le(self, parser):
        result = parser.parse("x <= 5")
        assert result == BinaryOpTerm('<=', VariableTerm("x"), LiteralTerm(5))
    
    def test_ge(self, parser):
        result = parser.parse("x >= 5")
        assert result == BinaryOpTerm('>=', VariableTerm("x"), LiteralTerm(5))


class TestLogicalOpTransform:
    """Test logical operator transformation."""
    
    def test_and(self, parser):
        result = parser.parse("x and y")
        assert result == BinaryOpTerm('and', VariableTerm("x"), VariableTerm("y"))
    
    def test_or(self, parser):
        result = parser.parse("x or y")
        assert result == BinaryOpTerm('or', VariableTerm("x"), VariableTerm("y"))
    
    def test_not(self, parser):
        result = parser.parse("not x")
        assert result == UnaryOpTerm('not', VariableTerm("x"))
    
    def test_precedence_not_and(self, parser):
        # not x and y should be (not x) and y
        result = parser.parse("not x and y")
        assert isinstance(result, BinaryOpTerm)
        assert result.operator == 'and'
        assert isinstance(result.left, UnaryOpTerm)
        assert result.left.operator == 'not'


class TestCollectionTransform:
    """Test collection transformation."""
    
    def test_empty_list(self, parser):
        result = parser.parse("[]")
        assert result == ListTerm(())
    
    def test_list_single(self, parser):
        result = parser.parse("[1]")
        assert result == ListTerm((LiteralTerm(1),))
    
    def test_list_multiple(self, parser):
        result = parser.parse("[1, 2, 3]")
        assert result == ListTerm((LiteralTerm(1), LiteralTerm(2), LiteralTerm(3)))
    
    def test_tuple_pair(self, parser):
        result = parser.parse("(x, y)")
        assert result == TupleTerm((VariableTerm("x"), VariableTerm("y")))
    
    def test_tuple_triple(self, parser):
        result = parser.parse("(a, b, c)")
        assert result == TupleTerm((
            VariableTerm("a"), VariableTerm("b"), VariableTerm("c")
        ))


class TestLibCallTransform:
    """Test lib.* call transformation."""
    
    def test_lib_length(self, parser):
        result = parser.parse("lib.length(queue)")
        assert isinstance(result, LibCallTerm)
        assert result.func_name == "length"
        assert len(result.arguments) == 1
        assert result.arguments[0] == VariableTerm("queue")
    
    def test_lib_add(self, parser):
        result = parser.parse("lib.add(queue, item)")
        assert isinstance(result, LibCallTerm)
        assert result.func_name == "add"
        assert len(result.arguments) == 2
    
    def test_lib_no_args(self, parser):
        result = parser.parse("lib.now()")
        assert isinstance(result, LibCallTerm)
        assert result.func_name == "now"
        assert result.arguments == ()


class TestRndCallTransform:
    """Test rnd.* call transformation."""
    
    def test_rnd_default_stream(self, parser):
        result = parser.parse("rnd.exponential(1.0)")
        assert isinstance(result, RndCallTerm)
        assert result.func_name == "exponential"
        assert result.stream is None
        assert len(result.arguments) == 1
    
    def test_rnd_named_stream(self, parser):
        result = parser.parse("rnd.arrivals.exponential(2.0)")
        assert isinstance(result, RndCallTerm)
        assert result.func_name == "exponential"
        assert result.stream == "arrivals"
        assert len(result.arguments) == 1
    
    def test_rnd_uniform(self, parser):
        result = parser.parse("rnd.uniform(0, 10)")
        assert isinstance(result, RndCallTerm)
        assert result.func_name == "uniform"
        assert len(result.arguments) == 2


class TestNewExprTransform:
    """Test new expression transformation."""
    
    def test_new_simple(self, parser):
        result = parser.parse("new Load")
        assert result == NewTerm("Load")
    
    def test_new_event(self, parser):
        result = parser.parse("new ArriveEvent")
        assert result == NewTerm("ArriveEvent")


class TestComplexExpressionTransform:
    """Test complex expression transformation."""
    
    def test_nested_arithmetic(self, parser):
        result = parser.parse("(x + 1) * (y - 2)")
        assert isinstance(result, BinaryOpTerm)
        assert result.operator == '*'
        assert isinstance(result.left, BinaryOpTerm)
        assert isinstance(result.right, BinaryOpTerm)
    
    def test_comparison_with_arithmetic(self, parser):
        result = parser.parse("x + 1 <= y * 2")
        assert isinstance(result, BinaryOpTerm)
        assert result.operator == '<='
    
    def test_complex_condition(self, parser):
        result = parser.parse("not server_busy and lib.length(queue) > 0")
        assert isinstance(result, BinaryOpTerm)
        assert result.operator == 'and'
    
    def test_fel_event_tuple(self, parser):
        result = parser.parse("(vertex, sim_clocktime + delay, 0)")
        assert isinstance(result, TupleTerm)
        assert len(result.elements) == 3
        # Middle element is addition
        assert isinstance(result.elements[1], BinaryOpTerm)
        assert result.elements[1].operator == '+'
