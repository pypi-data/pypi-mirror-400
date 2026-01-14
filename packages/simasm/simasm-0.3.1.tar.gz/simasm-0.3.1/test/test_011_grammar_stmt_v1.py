"""
Test Section 11.2: Grammar - Statements

Tests that the Lark grammar correctly parses:
- skip
- update (location := value)
- let binding
- if/elseif/else/endif
- while/endwhile
- forall/with/endforall
- choose/endchoose
- par/endpar
- rule call, lib call, rnd call (as statements)
- print
"""

import pytest
from lark import Lark
from pathlib import Path


# Load grammar
GRAMMAR_PATH = Path(__file__).parent.parent / "simasm" / "parser" / "grammar.lark"


@pytest.fixture(scope="module")
def stmt_parser():
    """Create Lark parser for single statements."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, start="stmt", parser="lalr")


@pytest.fixture(scope="module")
def block_parser():
    """Create Lark parser for statement blocks."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, start="stmt_block", parser="lalr")


class TestSkipStmt:
    """Test skip statement."""
    
    def test_skip(self, stmt_parser):
        tree = stmt_parser.parse("skip")
        assert tree.data == "skip_stmt"


class TestUpdateStmt:
    """Test update statements."""
    
    def test_simple_update(self, stmt_parser):
        tree = stmt_parser.parse("x := 5")
        assert tree.data == "update_stmt"
    
    def test_update_with_expr(self, stmt_parser):
        tree = stmt_parser.parse("x := y + 1")
        assert tree.data == "update_stmt"
    
    def test_function_location_update(self, stmt_parser):
        tree = stmt_parser.parse("f(a) := value")
        assert tree.data == "update_stmt"
    
    def test_function_multi_arg_update(self, stmt_parser):
        tree = stmt_parser.parse("matrix(i, j) := 0")
        assert tree.data == "update_stmt"
    
    def test_update_with_new(self, stmt_parser):
        tree = stmt_parser.parse("current_load := new Load")
        assert tree.data == "update_stmt"
    
    def test_update_with_lib_call(self, stmt_parser):
        tree = stmt_parser.parse("next_event := lib.pop(fel)")
        assert tree.data == "update_stmt"


class TestLetStmt:
    """Test let binding statements."""
    
    def test_let_simple(self, stmt_parser):
        tree = stmt_parser.parse("let x = 5")
        assert tree.data == "let_stmt"
    
    def test_let_with_expr(self, stmt_parser):
        tree = stmt_parser.parse("let y = x + 1")
        assert tree.data == "let_stmt"
    
    def test_let_with_new(self, stmt_parser):
        tree = stmt_parser.parse("let load = new Load")
        assert tree.data == "let_stmt"
    
    def test_let_with_func_call(self, stmt_parser):
        tree = stmt_parser.parse("let next = lib.pop(queue)")
        assert tree.data == "let_stmt"
    
    def test_let_with_tuple(self, stmt_parser):
        tree = stmt_parser.parse("let event = (vertex, time, priority)")
        assert tree.data == "let_stmt"


class TestIfStmt:
    """Test if/elseif/else/endif statements."""
    
    def test_if_then_endif(self, stmt_parser):
        tree = stmt_parser.parse("if x > 0 then skip endif")
        assert tree.data == "if_stmt"
    
    def test_if_then_else_endif(self, stmt_parser):
        tree = stmt_parser.parse("if x > 0 then x := 1 else x := 0 endif")
        assert tree.data == "if_stmt"
    
    def test_if_elseif_endif(self, stmt_parser):
        tree = stmt_parser.parse("if x > 0 then x := 1 elseif x < 0 then x := -1 endif")
        assert tree.data == "if_stmt"
    
    def test_if_elseif_else_endif(self, stmt_parser):
        tree = stmt_parser.parse(
            "if x > 0 then x := 1 elseif x < 0 then x := -1 else x := 0 endif"
        )
        assert tree.data == "if_stmt"
    
    def test_if_multiple_elseif(self, stmt_parser):
        tree = stmt_parser.parse(
            "if a then x := 1 elseif b then x := 2 elseif c then x := 3 endif"
        )
        assert tree.data == "if_stmt"
    
    def test_if_with_complex_condition(self, stmt_parser):
        tree = stmt_parser.parse("if x > 0 and y < 10 then skip endif")
        assert tree.data == "if_stmt"
    
    def test_if_with_multiple_stmts(self, block_parser):
        code = """if x > 0 then
            y := 1
            z := 2
        endif"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"


class TestWhileStmt:
    """Test while/endwhile statements."""
    
    def test_while_simple(self, stmt_parser):
        tree = stmt_parser.parse("while x > 0 do x := x - 1 endwhile")
        assert tree.data == "while_stmt"
    
    def test_while_with_complex_condition(self, stmt_parser):
        tree = stmt_parser.parse("while lib.length(queue) > 0 do skip endwhile")
        assert tree.data == "while_stmt"
    
    def test_while_multiple_stmts(self, block_parser):
        code = """while x > 0 do
            y := y + x
            x := x - 1
        endwhile"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"


class TestForallStmt:
    """Test forall/endforall statements."""
    
    def test_forall_simple(self, stmt_parser):
        tree = stmt_parser.parse("forall x in items do skip endforall")
        assert tree.data == "forall_stmt"
    
    def test_forall_with_guard(self, stmt_parser):
        tree = stmt_parser.parse("forall e in edges with enabled(e) do skip endforall")
        assert tree.data == "forall_stmt"
    
    def test_forall_with_lib_expr(self, stmt_parser):
        tree = stmt_parser.parse(
            "forall item in lib.filter(items, pred) do process(item) endforall"
        )
        assert tree.data == "forall_stmt"
    
    def test_forall_multiple_stmts(self, block_parser):
        code = """forall e in events do
            process(e)
            count := count + 1
        endforall"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"


class TestChooseStmt:
    """Test choose/endchoose statements (nondeterministic selection)."""
    
    def test_choose_simple(self, stmt_parser):
        tree = stmt_parser.parse("choose x in items do skip endchoose")
        assert tree.data == "choose_stmt"
    
    def test_choose_with_guard(self, stmt_parser):
        tree = stmt_parser.parse(
            "choose server in servers with not busy(server) do start(server) endchoose"
        )
        assert tree.data == "choose_stmt"


class TestParStmt:
    """Test par/endpar statements (explicit parallelism)."""
    
    def test_par_simple(self, stmt_parser):
        tree = stmt_parser.parse("par x := 1 endpar")
        assert tree.data == "par_stmt"
    
    def test_par_multiple_stmts(self, block_parser):
        code = """par
            x := 1
            y := 2
            z := 3
        endpar"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"


class TestRuleCallStmt:
    """Test rule call statements."""
    
    def test_rule_call_no_args(self, stmt_parser):
        tree = stmt_parser.parse("arrive()")
        assert tree.data == "rule_call_stmt"
    
    def test_rule_call_one_arg(self, stmt_parser):
        tree = stmt_parser.parse("start(load)")
        assert tree.data == "rule_call_stmt"
    
    def test_rule_call_multi_args(self, stmt_parser):
        tree = stmt_parser.parse("transfer(src, dst, amount)")
        assert tree.data == "rule_call_stmt"
    
    def test_rule_call_with_exprs(self, stmt_parser):
        tree = stmt_parser.parse("schedule(event, time + delay)")
        assert tree.data == "rule_call_stmt"


class TestLibCallStmt:
    """Test lib.* call statements."""
    
    def test_lib_add(self, stmt_parser):
        tree = stmt_parser.parse("lib.add(queue, item)")
        assert tree.data == "lib_call_stmt"
    
    def test_lib_remove(self, stmt_parser):
        tree = stmt_parser.parse("lib.remove(queue, item)")
        assert tree.data == "lib_call_stmt"
    
    def test_lib_sort(self, stmt_parser):
        tree = stmt_parser.parse('lib.sort(fel, "1")')
        assert tree.data == "lib_call_stmt"


class TestRndCallStmt:
    """Test rnd.* call statements (for side effects like seeding)."""
    
    def test_rnd_seed(self, stmt_parser):
        tree = stmt_parser.parse("rnd.seed(42)")
        assert tree.data == "rnd_stmt_default"
    
    def test_rnd_stream_seed(self, stmt_parser):
        tree = stmt_parser.parse("rnd.arrivals.seed(123)")
        assert tree.data == "rnd_stmt_stream"


class TestPrintStmt:
    """Test print statements."""
    
    def test_print_string(self, stmt_parser):
        tree = stmt_parser.parse('print("hello")')
        assert tree.data == "print_stmt"
    
    def test_print_variable(self, stmt_parser):
        tree = stmt_parser.parse("print(x)")
        assert tree.data == "print_stmt"
    
    def test_print_expr(self, stmt_parser):
        tree = stmt_parser.parse("print(x + y)")
        assert tree.data == "print_stmt"


class TestStatementBlocks:
    """Test statement block parsing (multiple statements)."""
    
    def test_two_statements(self, block_parser):
        code = """x := 1
        y := 2"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"
        assert len(tree.children) == 2
    
    def test_mixed_statements(self, block_parser):
        code = """let x = 5
        y := x + 1
        print(y)"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"
        assert len(tree.children) == 3
    
    def test_nested_if(self, block_parser):
        code = """if x > 0 then
            if y > 0 then
                z := 1
            endif
        endif"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"


class TestComplexStatements:
    """Test complex nested statements."""
    
    def test_if_with_while(self, block_parser):
        code = """if lib.length(queue) > 0 then
            while lib.length(queue) > 0 do
                let item = lib.pop(queue)
                process(item)
            endwhile
        endif"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"
    
    def test_forall_with_if(self, block_parser):
        code = """forall e in events do
            if enabled(e) then
                fire(e)
            endif
        endforall"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"
    
    def test_typical_event_routine(self, block_parser):
        code = """let load = new Load
        lib.add(queue, load)
        if not server_busy then
            server_busy := true
            let service_time = rnd.exponential(1.0)
            lib.add(fel, (depart, sim_clocktime + service_time, 0))
        endif
        let iat = rnd.exponential(2.0)
        lib.add(fel, (arrive, sim_clocktime + iat, 0))"""
        tree = block_parser.parse(code)
        assert tree.data == "stmt_block"
