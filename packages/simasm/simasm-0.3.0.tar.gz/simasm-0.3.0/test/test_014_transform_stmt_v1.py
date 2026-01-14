"""
Test Section 11.5: Transformer - Statements

Tests that the SimASMTransformer correctly converts parse trees
to AST nodes for statements.
"""

import pytest
from lark import Lark
from pathlib import Path

from simasm.parser.transformer import SimASMTransformer
from simasm.core.terms import (
    LiteralTerm, VariableTerm, LocationTerm, BinaryOpTerm,
    NewTerm, LibCallTerm, RndCallTerm,
)
from simasm.core.rules import (
    SkipStmt, UpdateStmt, SeqStmt, IfStmt,
    WhileStmt, ForallStmt, LetStmt, RuleCallStmt, PrintStmt,
    ChooseStmt, ParStmt,
    LibCallStmt as LibCallStatement,
    RndCallStmt as RndCallStatement,
)


# Load grammar and create parsers
GRAMMAR_PATH = Path(__file__).parent.parent / "simasm" / "parser" / "grammar.lark"


@pytest.fixture(scope="module")
def stmt_parser():
    """Create Lark parser with transformer for single statements."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(
        grammar,
        start="stmt",
        parser="lalr",
        transformer=SimASMTransformer()
    )


@pytest.fixture(scope="module")
def block_parser():
    """Create Lark parser with transformer for statement blocks."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(
        grammar,
        start="stmt_block",
        parser="lalr",
        transformer=SimASMTransformer()
    )


class TestSkipTransform:
    """Test skip statement transformation."""
    
    def test_skip(self, stmt_parser):
        result = stmt_parser.parse("skip")
        assert isinstance(result, SkipStmt)


class TestUpdateTransform:
    """Test update statement transformation."""
    
    def test_simple_update(self, stmt_parser):
        result = stmt_parser.parse("x := 5")
        assert isinstance(result, UpdateStmt)
        assert isinstance(result.location, LocationTerm)
        assert result.location.func_name == "x"
        assert result.value == LiteralTerm(5)
    
    def test_update_with_expr(self, stmt_parser):
        result = stmt_parser.parse("x := y + 1")
        assert isinstance(result, UpdateStmt)
        assert isinstance(result.value, BinaryOpTerm)
    
    def test_func_location_update(self, stmt_parser):
        result = stmt_parser.parse("status(load) := value")
        assert isinstance(result, UpdateStmt)
        assert result.location.func_name == "status"
        assert len(result.location.arguments) == 1


class TestLetTransform:
    """Test let binding transformation."""
    
    def test_let_simple(self, stmt_parser):
        result = stmt_parser.parse("let x = 5")
        assert isinstance(result, LetStmt)
        assert result.var_name == "x"
        assert result.value == LiteralTerm(5)
    
    def test_let_with_new(self, stmt_parser):
        result = stmt_parser.parse("let load = new Load")
        assert isinstance(result, LetStmt)
        assert result.var_name == "load"
        assert isinstance(result.value, NewTerm)


class TestIfTransform:
    """Test if statement transformation."""
    
    def test_if_then(self, stmt_parser):
        result = stmt_parser.parse("if x > 0 then skip endif")
        assert isinstance(result, IfStmt)
        assert isinstance(result.condition, BinaryOpTerm)
        assert isinstance(result.then_body, SkipStmt)
        assert result.elseif_branches == ()
        assert result.else_body is None
    
    def test_if_then_else(self, stmt_parser):
        result = stmt_parser.parse("if x > 0 then x := 1 else x := 0 endif")
        assert isinstance(result, IfStmt)
        assert isinstance(result.then_body, UpdateStmt)
        assert result.else_body is not None
        assert isinstance(result.else_body, UpdateStmt)
    
    def test_if_elseif(self, stmt_parser):
        result = stmt_parser.parse(
            "if x > 0 then x := 1 elseif x < 0 then x := -1 endif"
        )
        assert isinstance(result, IfStmt)
        assert len(result.elseif_branches) == 1
        cond, body = result.elseif_branches[0]
        assert isinstance(cond, BinaryOpTerm)
        assert isinstance(body, UpdateStmt)
    
    def test_if_elseif_else(self, stmt_parser):
        result = stmt_parser.parse(
            "if a then x := 1 elseif b then x := 2 else x := 3 endif"
        )
        assert isinstance(result, IfStmt)
        assert len(result.elseif_branches) == 1
        assert result.else_body is not None


class TestWhileTransform:
    """Test while statement transformation."""
    
    def test_while_simple(self, stmt_parser):
        result = stmt_parser.parse("while x > 0 do x := x - 1 endwhile")
        assert isinstance(result, WhileStmt)
        assert isinstance(result.condition, BinaryOpTerm)
        assert isinstance(result.body, UpdateStmt)


class TestForallTransform:
    """Test forall statement transformation."""
    
    def test_forall_simple(self, stmt_parser):
        result = stmt_parser.parse("forall x in items do skip endforall")
        assert isinstance(result, ForallStmt)
        assert result.var_name == "x"
        assert isinstance(result.collection, VariableTerm)
        assert result.guard is None
    
    def test_forall_with_guard(self, stmt_parser):
        result = stmt_parser.parse(
            "forall e in edges with enabled(e) do skip endforall"
        )
        assert isinstance(result, ForallStmt)
        assert result.var_name == "e"
        assert result.guard is not None
        assert isinstance(result.guard, LocationTerm)


class TestChooseTransform:
    """Test choose statement transformation."""
    
    def test_choose_simple(self, stmt_parser):
        result = stmt_parser.parse("choose x in items do skip endchoose")
        assert isinstance(result, ChooseStmt)
        assert result.var_name == "x"
        assert result.guard is None
    
    def test_choose_with_guard(self, stmt_parser):
        result = stmt_parser.parse(
            "choose s in servers with not busy(s) do assign(s) endchoose"
        )
        assert isinstance(result, ChooseStmt)
        assert result.guard is not None


class TestParTransform:
    """Test parallel block transformation."""
    
    def test_par_single(self, stmt_parser):
        result = stmt_parser.parse("par x := 1 endpar")
        assert isinstance(result, ParStmt)
        assert isinstance(result.body, UpdateStmt)
    
    def test_par_multiple(self, block_parser):
        code = """par
            x := 1
            y := 2
        endpar"""
        result = block_parser.parse(code)
        assert isinstance(result, ParStmt)
        assert isinstance(result.body, SeqStmt)
        assert len(result.body.statements) == 2


class TestRuleCallTransform:
    """Test rule call transformation."""
    
    def test_rule_call_no_args(self, stmt_parser):
        result = stmt_parser.parse("arrive()")
        assert isinstance(result, RuleCallStmt)
        assert result.rule_name == LiteralTerm("arrive")
        assert result.arguments == ()
    
    def test_rule_call_with_args(self, stmt_parser):
        result = stmt_parser.parse("start(load, server)")
        assert isinstance(result, RuleCallStmt)
        assert result.rule_name == LiteralTerm("start")
        assert len(result.arguments) == 2


class TestLibCallStmtTransform:
    """Test lib.* call statement transformation."""
    
    def test_lib_add(self, stmt_parser):
        result = stmt_parser.parse("lib.add(queue, item)")
        assert isinstance(result, LibCallStatement)
        assert result.func_name == "add"
        assert len(result.arguments) == 2
    
    def test_lib_sort(self, stmt_parser):
        result = stmt_parser.parse('lib.sort(fel, "1")')
        assert isinstance(result, LibCallStatement)
        assert result.func_name == "sort"


class TestRndCallStmtTransform:
    """Test rnd.* call statement transformation."""
    
    def test_rnd_seed(self, stmt_parser):
        result = stmt_parser.parse("rnd.seed(42)")
        assert isinstance(result, RndCallStatement)
        assert result.func_name == "seed"
        assert result.stream is None
    
    def test_rnd_stream_seed(self, stmt_parser):
        result = stmt_parser.parse("rnd.arrivals.seed(123)")
        assert isinstance(result, RndCallStatement)
        assert result.func_name == "seed"
        assert result.stream == "arrivals"


class TestPrintTransform:
    """Test print statement transformation."""
    
    def test_print_string(self, stmt_parser):
        result = stmt_parser.parse('print("hello")')
        assert isinstance(result, PrintStmt)
        assert result.expression == LiteralTerm("hello")
    
    def test_print_expr(self, stmt_parser):
        result = stmt_parser.parse("print(x + y)")
        assert isinstance(result, PrintStmt)
        assert isinstance(result.expression, BinaryOpTerm)


class TestBlockTransform:
    """Test statement block transformation."""
    
    def test_single_stmt_no_seq(self, block_parser):
        result = block_parser.parse("skip")
        # Single statement should not be wrapped in SeqStmt
        assert isinstance(result, SkipStmt)
    
    def test_multiple_stmts_seq(self, block_parser):
        code = """x := 1
        y := 2
        z := 3"""
        result = block_parser.parse(code)
        assert isinstance(result, SeqStmt)
        assert len(result.statements) == 3
    
    def test_mixed_stmts(self, block_parser):
        code = """let x = 5
        y := x + 1
        print(y)"""
        result = block_parser.parse(code)
        assert isinstance(result, SeqStmt)
        assert isinstance(result.statements[0], LetStmt)
        assert isinstance(result.statements[1], UpdateStmt)
        assert isinstance(result.statements[2], PrintStmt)


class TestNestedStmtTransform:
    """Test nested statement transformation."""
    
    def test_if_with_block(self, block_parser):
        code = """if x > 0 then
            y := 1
            z := 2
        endif"""
        result = block_parser.parse(code)
        assert isinstance(result, IfStmt)
        assert isinstance(result.then_body, SeqStmt)
    
    def test_nested_if(self, block_parser):
        code = """if x > 0 then
            if y > 0 then
                z := 1
            endif
        endif"""
        result = block_parser.parse(code)
        assert isinstance(result, IfStmt)
        assert isinstance(result.then_body, IfStmt)
    
    def test_forall_with_if(self, block_parser):
        code = """forall e in events do
            if enabled(e) then
                fire(e)
            endif
        endforall"""
        result = block_parser.parse(code)
        assert isinstance(result, ForallStmt)
        assert isinstance(result.body, IfStmt)
