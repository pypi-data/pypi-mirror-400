"""
Test Section 11.3: Grammar - Declarations and Program Structure

Tests that the Lark grammar correctly parses:
- import
- domain (simple and with parent)
- const, var
- static/dynamic/derived function
- rule, main rule
- init block
- complete program
"""

import pytest
from lark import Lark
from pathlib import Path


# Load grammar
GRAMMAR_PATH = Path(__file__).parent.parent / "simasm" / "parser" / "grammar.lark"


@pytest.fixture(scope="module")
def decl_parser():
    """Create Lark parser for single declarations."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, start="declaration", parser="lalr")


@pytest.fixture(scope="module")
def program_parser():
    """Create Lark parser for complete programs."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, start="program", parser="lalr")


@pytest.fixture(scope="module")
def type_parser():
    """Create Lark parser for type expressions."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(grammar, start="type_expr", parser="lalr")


class TestTypeExpr:
    """Test type expression parsing."""
    
    def test_simple_type(self, type_parser):
        tree = type_parser.parse("Int")
        assert tree.data == "simple_type"
    
    def test_simple_type_real(self, type_parser):
        tree = type_parser.parse("Real")
        assert tree.data == "simple_type"
    
    def test_param_type_list(self, type_parser):
        tree = type_parser.parse("List<Event>")
        assert tree.data == "param_type"
    
    def test_nested_param_type(self, type_parser):
        tree = type_parser.parse("List<List<Int>>")
        assert tree.data == "param_type"


class TestImportDecl:
    """Test import declaration parsing."""
    
    def test_import_simple(self, decl_parser):
        tree = decl_parser.parse("import Random as rnd")
        assert tree.data == "import_decl"
    
    def test_import_stdlib(self, decl_parser):
        tree = decl_parser.parse("import Stdlib as lib")
        assert tree.data == "import_decl"


class TestDomainDecl:
    """Test domain declaration parsing."""
    
    def test_domain_simple(self, decl_parser):
        tree = decl_parser.parse("domain Load")
        assert tree.data == "domain_simple"
    
    def test_domain_extends(self, decl_parser):
        tree = decl_parser.parse("domain ArriveEvent <: Event")
        assert tree.data == "domain_extends"
    
    def test_domain_extends_builtin(self, decl_parser):
        tree = decl_parser.parse("domain PositiveReal <: Real")
        assert tree.data == "domain_extends"


class TestConstDecl:
    """Test constant declaration parsing."""
    
    def test_const_simple(self, decl_parser):
        tree = decl_parser.parse("const queue: Queue")
        assert tree.data == "const_decl"
    
    def test_const_with_param_type(self, decl_parser):
        tree = decl_parser.parse("const servers: List<Server>")
        assert tree.data == "const_decl"


class TestVarDecl:
    """Test variable declaration parsing."""
    
    def test_var_simple(self, decl_parser):
        tree = decl_parser.parse("var sim_clocktime: Real")
        assert tree.data == "var_decl"
    
    def test_var_bool(self, decl_parser):
        tree = decl_parser.parse("var server_busy: Bool")
        assert tree.data == "var_decl"
    
    def test_var_with_param_type(self, decl_parser):
        tree = decl_parser.parse("var future_event_list: List<Event>")
        assert tree.data == "var_decl"


class TestStaticFuncDecl:
    """Test static function declaration parsing."""
    
    def test_static_func_no_params(self, decl_parser):
        tree = decl_parser.parse("static function count(): Nat")
        assert tree.data == "static_func_decl"
    
    def test_static_func_one_param(self, decl_parser):
        tree = decl_parser.parse("static function id(obj: Object): Nat")
        assert tree.data == "static_func_decl"
    
    def test_static_func_multi_params(self, decl_parser):
        tree = decl_parser.parse("static function distance(a: Point, b: Point): Real")
        assert tree.data == "static_func_decl"


class TestDynamicFuncDecl:
    """Test dynamic function declaration parsing."""
    
    def test_dynamic_func_no_params(self, decl_parser):
        tree = decl_parser.parse("dynamic function state(): State")
        assert tree.data == "dynamic_func_decl"
    
    def test_dynamic_func_one_param(self, decl_parser):
        tree = decl_parser.parse("dynamic function queues(q: Queue): List<Load>")
        assert tree.data == "dynamic_func_decl"
    
    def test_dynamic_func_multi_params(self, decl_parser):
        tree = decl_parser.parse("dynamic function matrix(i: Nat, j: Nat): Real")
        assert tree.data == "dynamic_func_decl"


class TestDerivedFuncDecl:
    """Test derived function declaration parsing."""
    
    def test_derived_func_simple(self, decl_parser):
        tree = decl_parser.parse("derived function queue_length(): Nat = lib.length(queue)")
        assert tree.data == "derived_func_decl"
    
    def test_derived_func_with_param(self, decl_parser):
        tree = decl_parser.parse("derived function enabled(e: Event): Bool = time(e) <= sim_clocktime")
        assert tree.data == "derived_func_decl"
    
    def test_derived_func_complex_expr(self, decl_parser):
        tree = decl_parser.parse(
            "derived function utilization(): Real = busy_time / sim_clocktime"
        )
        assert tree.data == "derived_func_decl"


class TestRuleDecl:
    """Test rule declaration parsing."""
    
    def test_rule_no_params(self, decl_parser):
        tree = decl_parser.parse("rule arrive() = skip endrule")
        assert tree.data == "rule_decl"
    
    def test_rule_one_param(self, decl_parser):
        tree = decl_parser.parse("rule start(load: Load) = skip endrule")
        assert tree.data == "rule_decl"
    
    def test_rule_multi_params(self, decl_parser):
        tree = decl_parser.parse("rule transfer(src: Queue, dst: Queue) = skip endrule")
        assert tree.data == "rule_decl"
    
    def test_rule_with_body(self, decl_parser):
        code = """rule arrive() =
            let load = new Load
            lib.add(queue, load)
        endrule"""
        tree = decl_parser.parse(code)
        assert tree.data == "rule_decl"
    
    def test_rule_with_complex_body(self, decl_parser):
        code = """rule arrive() =
            let load = new Load
            lib.add(queue, load)
            if not server_busy then
                server_busy := true
                start(load)
            endif
        endrule"""
        tree = decl_parser.parse(code)
        assert tree.data == "rule_decl"


class TestMainRuleDecl:
    """Test main rule declaration parsing."""
    
    def test_main_rule_simple(self, decl_parser):
        tree = decl_parser.parse("main rule main = skip endrule")
        assert tree.data == "main_rule_decl"
    
    def test_main_rule_with_body(self, decl_parser):
        code = """main rule main =
            let next = lib.min_by(fel, "1")
            sim_clocktime := lib.second(next)
            lib.apply_rule(lib.first(next), [])
        endrule"""
        tree = decl_parser.parse(code)
        assert tree.data == "main_rule_decl"


class TestInitBlock:
    """Test init block parsing."""
    
    def test_init_simple(self, decl_parser):
        tree = decl_parser.parse("init: skip endinit")
        assert tree.data == "init_block"
    
    def test_init_with_assignments(self, decl_parser):
        code = """init:
            sim_clocktime := 0.0
            server_busy := false
        endinit"""
        tree = decl_parser.parse(code)
        assert tree.data == "init_block"
    
    def test_init_with_scheduling(self, decl_parser):
        code = """init:
            sim_clocktime := 0.0
            let first_arrival = rnd.exponential(2.0)
            lib.add(fel, (arrive, first_arrival, 0))
        endinit"""
        tree = decl_parser.parse(code)
        assert tree.data == "init_block"


class TestProgram:
    """Test complete program parsing."""
    
    def test_empty_program(self, program_parser):
        tree = program_parser.parse("")
        assert tree.data == "program"
        assert len(tree.children) == 0
    
    def test_single_domain(self, program_parser):
        tree = program_parser.parse("domain Load")
        assert tree.data == "program"
        assert len(tree.children) == 1
    
    def test_multiple_domains(self, program_parser):
        code = """domain Load
        domain Event
        domain ArriveEvent <: Event"""
        tree = program_parser.parse(code)
        assert tree.data == "program"
        assert len(tree.children) == 3
    
    def test_imports_and_domains(self, program_parser):
        code = """import Random as rnd
        import Stdlib as lib
        domain Load
        domain Event"""
        tree = program_parser.parse(code)
        assert tree.data == "program"
        assert len(tree.children) == 4
    
    def test_minimal_model(self, program_parser):
        code = """domain Load
        
        var sim_clocktime: Real
        var server_busy: Bool
        
        rule arrive() =
            skip
        endrule
        
        main rule main =
            skip
        endrule"""
        tree = program_parser.parse(code)
        assert tree.data == "program"
    
    def test_mm1_queue_structure(self, program_parser):
        code = """// M/M/1 Queue Model
        import Random as rnd
        import Stdlib as lib
        
        domain Load
        domain Event
        domain ArriveEvent <: Event
        domain DepartEvent <: Event
        
        var sim_clocktime: Real
        var server_busy: Bool
        dynamic function queue(): List<Load>
        dynamic function fel(): List<Event>
        
        rule arrive() =
            let load = new Load
            lib.add(queue(), load)
            if not server_busy then
                server_busy := true
            endif
        endrule
        
        rule depart() =
            server_busy := false
        endrule
        
        main rule main =
            let next = lib.min_by(fel(), "1")
            sim_clocktime := lib.second(next)
        endrule
        
        init:
            sim_clocktime := 0.0
            server_busy := false
        endinit"""
        tree = program_parser.parse(code)
        assert tree.data == "program"


class TestProgramWithComments:
    """Test that comments are properly ignored in programs."""
    
    def test_line_comments(self, program_parser):
        code = """// This is a comment
        domain Load  // Another comment
        // More comments
        domain Event"""
        tree = program_parser.parse(code)
        assert tree.data == "program"
        assert len(tree.children) == 2
    
    def test_block_comments(self, program_parser):
        code = """/* Block comment */
        domain Load
        /* Multi
           line
           comment */
        domain Event"""
        tree = program_parser.parse(code)
        assert tree.data == "program"
        assert len(tree.children) == 2
