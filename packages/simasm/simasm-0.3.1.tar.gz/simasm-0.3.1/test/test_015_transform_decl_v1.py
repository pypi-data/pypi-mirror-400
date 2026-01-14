"""
Test Section 11.6: Transformer - Declarations

Tests that the SimASMTransformer correctly converts parse trees
to AST nodes for declarations and complete programs.
"""

import pytest
from lark import Lark
from pathlib import Path

from simasm.parser.transformer import SimASMTransformer
from simasm.parser.ast import (
    SimpleType, ParamType, Param,
    ImportDecl, DomainDecl, ConstDecl, VarDecl,
    StaticFuncDecl, DynamicFuncDecl, DerivedFuncDecl,
    RuleDecl, MainRuleDecl, InitBlock, Program,
)
from simasm.core.terms import LiteralTerm, VariableTerm, LibCallTerm
from simasm.core.rules import SkipStmt, UpdateStmt, SeqStmt


# Load grammar and create parsers
GRAMMAR_PATH = Path(__file__).parent.parent / "simasm" / "parser" / "grammar.lark"


@pytest.fixture(scope="module")
def decl_parser():
    """Create Lark parser with transformer for declarations."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(
        grammar,
        start="declaration",
        parser="lalr",
        transformer=SimASMTransformer()
    )


@pytest.fixture(scope="module")
def program_parser():
    """Create Lark parser with transformer for complete programs."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(
        grammar,
        start="program",
        parser="lalr",
        transformer=SimASMTransformer()
    )


@pytest.fixture(scope="module")
def type_parser():
    """Create Lark parser with transformer for type expressions."""
    grammar = GRAMMAR_PATH.read_text()
    return Lark(
        grammar,
        start="type_expr",
        parser="lalr",
        transformer=SimASMTransformer()
    )


class TestTypeExprTransform:
    """Test type expression transformation."""
    
    def test_simple_type(self, type_parser):
        result = type_parser.parse("Int")
        assert isinstance(result, SimpleType)
        assert result.name == "Int"
    
    def test_simple_type_domain(self, type_parser):
        result = type_parser.parse("Load")
        assert isinstance(result, SimpleType)
        assert result.name == "Load"
    
    def test_param_type(self, type_parser):
        result = type_parser.parse("List<Event>")
        assert isinstance(result, ParamType)
        assert result.name == "List"
        assert isinstance(result.param, SimpleType)
        assert result.param.name == "Event"
    
    def test_nested_param_type(self, type_parser):
        result = type_parser.parse("List<List<Int>>")
        assert isinstance(result, ParamType)
        assert result.name == "List"
        assert isinstance(result.param, ParamType)
        assert result.param.name == "List"


class TestImportTransform:
    """Test import declaration transformation."""
    
    def test_import(self, decl_parser):
        result = decl_parser.parse("import Random as rnd")
        assert isinstance(result, ImportDecl)
        assert result.module == "Random"
        assert result.alias == "rnd"


class TestDomainTransform:
    """Test domain declaration transformation."""
    
    def test_domain_simple(self, decl_parser):
        result = decl_parser.parse("domain Load")
        assert isinstance(result, DomainDecl)
        assert result.name == "Load"
        assert result.parent is None
    
    def test_domain_extends(self, decl_parser):
        result = decl_parser.parse("domain ArriveEvent <: Event")
        assert isinstance(result, DomainDecl)
        assert result.name == "ArriveEvent"
        assert result.parent == "Event"


class TestConstVarTransform:
    """Test const and var declaration transformation."""
    
    def test_const(self, decl_parser):
        result = decl_parser.parse("const queue: Queue")
        assert isinstance(result, ConstDecl)
        assert result.name == "queue"
        assert isinstance(result.type_expr, SimpleType)
        assert result.type_expr.name == "Queue"
    
    def test_var(self, decl_parser):
        result = decl_parser.parse("var sim_clocktime: Real")
        assert isinstance(result, VarDecl)
        assert result.name == "sim_clocktime"
        assert result.type_expr.name == "Real"
    
    def test_var_param_type(self, decl_parser):
        result = decl_parser.parse("var fel: List<Event>")
        assert isinstance(result, VarDecl)
        assert isinstance(result.type_expr, ParamType)


class TestStaticFuncTransform:
    """Test static function declaration transformation."""
    
    def test_static_no_params(self, decl_parser):
        result = decl_parser.parse("static function count(): Nat")
        assert isinstance(result, StaticFuncDecl)
        assert result.name == "count"
        assert result.params == ()
        assert result.return_type.name == "Nat"
    
    def test_static_with_params(self, decl_parser):
        result = decl_parser.parse("static function id(obj: Object): Nat")
        assert isinstance(result, StaticFuncDecl)
        assert result.name == "id"
        assert len(result.params) == 1
        assert result.params[0].name == "obj"
        assert result.params[0].type_expr.name == "Object"


class TestDynamicFuncTransform:
    """Test dynamic function declaration transformation."""
    
    def test_dynamic_no_params(self, decl_parser):
        result = decl_parser.parse("dynamic function state(): State")
        assert isinstance(result, DynamicFuncDecl)
        assert result.name == "state"
        assert result.params == ()
    
    def test_dynamic_with_params(self, decl_parser):
        result = decl_parser.parse("dynamic function queues(q: Queue): List<Load>")
        assert isinstance(result, DynamicFuncDecl)
        assert result.name == "queues"
        assert len(result.params) == 1


class TestDerivedFuncTransform:
    """Test derived function declaration transformation."""
    
    def test_derived_simple(self, decl_parser):
        result = decl_parser.parse("derived function queue_length(): Nat = lib.length(queue)")
        assert isinstance(result, DerivedFuncDecl)
        assert result.name == "queue_length"
        assert result.params == ()
        assert isinstance(result.body, LibCallTerm)
    
    def test_derived_with_param(self, decl_parser):
        result = decl_parser.parse("derived function enabled(e: Event): Bool = time(e) <= sim_clocktime")
        assert isinstance(result, DerivedFuncDecl)
        assert result.name == "enabled"
        assert len(result.params) == 1


class TestRuleDeclTransform:
    """Test rule declaration transformation."""
    
    def test_rule_no_params(self, decl_parser):
        result = decl_parser.parse("rule arrive() = skip endrule")
        assert isinstance(result, RuleDecl)
        assert result.name == "arrive"
        assert result.params == ()
        assert isinstance(result.body, SkipStmt)
    
    def test_rule_with_params(self, decl_parser):
        result = decl_parser.parse("rule start(load: Load) = skip endrule")
        assert isinstance(result, RuleDecl)
        assert result.name == "start"
        assert len(result.params) == 1
        assert result.params[0].name == "load"
    
    def test_rule_with_body(self, decl_parser):
        code = """rule arrive() =
            let load = new Load
            lib.add(queue, load)
        endrule"""
        result = decl_parser.parse(code)
        assert isinstance(result, RuleDecl)
        assert isinstance(result.body, SeqStmt)


class TestMainRuleTransform:
    """Test main rule declaration transformation."""
    
    def test_main_rule(self, decl_parser):
        result = decl_parser.parse("main rule main = skip endrule")
        assert isinstance(result, MainRuleDecl)
        assert result.name == "main"
        assert isinstance(result.body, SkipStmt)


class TestInitBlockTransform:
    """Test init block transformation."""
    
    def test_init_simple(self, decl_parser):
        result = decl_parser.parse("init: skip endinit")
        assert isinstance(result, InitBlock)
        assert isinstance(result.body, SkipStmt)
    
    def test_init_with_assignments(self, decl_parser):
        code = """init:
            sim_clocktime := 0.0
            server_busy := false
        endinit"""
        result = decl_parser.parse(code)
        assert isinstance(result, InitBlock)
        assert isinstance(result.body, SeqStmt)


class TestProgramTransform:
    """Test complete program transformation."""
    
    def test_empty_program(self, program_parser):
        result = program_parser.parse("")
        assert isinstance(result, Program)
        assert result.imports == []
        assert result.domains == []
    
    def test_single_domain(self, program_parser):
        result = program_parser.parse("domain Load")
        assert isinstance(result, Program)
        assert len(result.domains) == 1
        assert result.domains[0].name == "Load"
    
    def test_multiple_domains(self, program_parser):
        code = """domain Load
        domain Event
        domain ArriveEvent <: Event"""
        result = program_parser.parse(code)
        assert len(result.domains) == 3
    
    def test_imports_and_domains(self, program_parser):
        code = """import Random as rnd
        import Stdlib as lib
        domain Load"""
        result = program_parser.parse(code)
        assert len(result.imports) == 2
        assert len(result.domains) == 1
    
    def test_complete_model(self, program_parser):
        code = """// M/M/1 Queue Model
        import Random as rnd
        import Stdlib as lib
        
        domain Load
        domain Event
        
        var sim_clocktime: Real
        var server_busy: Bool
        dynamic function queue(): List<Load>
        
        rule arrive() =
            let load = new Load
            lib.add(queue(), load)
        endrule
        
        main rule main =
            skip
        endrule
        
        init:
            sim_clocktime := 0.0
            server_busy := false
        endinit"""
        result = program_parser.parse(code)
        
        assert isinstance(result, Program)
        assert len(result.imports) == 2
        assert len(result.domains) == 2
        assert len(result.variables) == 2
        assert len(result.dynamic_funcs) == 1
        assert len(result.rules) == 1
        assert result.main_rule is not None
        assert result.init is not None
    
    def test_program_repr(self, program_parser):
        code = """domain Load
        var x: Int
        rule test() = skip endrule"""
        result = program_parser.parse(code)
        repr_str = repr(result)
        assert "1 domains" in repr_str
        assert "1 variables" in repr_str
        assert "1 rules" in repr_str


class TestProgramCategorization:
    """Test that declarations are properly categorized in Program."""
    
    def test_all_declaration_types(self, program_parser):
        code = """import Random as rnd
        domain Load
        const MAX_QUEUE: Int
        var counter: Int
        static function id(x: Load): Int
        dynamic function queue(): List<Load>
        derived function size(): Int = lib.length(queue())
        rule process() = skip endrule
        main rule main = skip endrule
        init: counter := 0 endinit"""
        
        result = program_parser.parse(code)
        
        assert len(result.imports) == 1
        assert len(result.domains) == 1
        assert len(result.constants) == 1
        assert len(result.variables) == 1
        assert len(result.static_funcs) == 1
        assert len(result.dynamic_funcs) == 1
        assert len(result.derived_funcs) == 1
        assert len(result.rules) == 1
        assert result.main_rule is not None
        assert result.init is not None
