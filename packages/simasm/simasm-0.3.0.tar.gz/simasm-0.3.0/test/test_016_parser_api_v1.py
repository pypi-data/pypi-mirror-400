"""
Test Section 11.7: Parser API + Integration

Tests the high-level parser API:
- SimASMParser class
- parse_string() function
- parse_file() function
- Error handling
- Integration with full programs
"""

import pytest
from pathlib import Path
import tempfile

from simasm.parser import (
    SimASMParser,
    ParseError,
    parse_string,
    parse_file,
    Program,
    DomainDecl,
    VarDecl,
    RuleDecl,
)


class TestSimASMParser:
    """Test SimASMParser class."""
    
    def test_create_parser(self):
        parser = SimASMParser()
        assert parser is not None
    
    def test_parse_empty(self):
        parser = SimASMParser()
        result = parser.parse("")
        assert isinstance(result, Program)
    
    def test_parse_simple(self):
        parser = SimASMParser()
        result = parser.parse("domain Load")
        assert isinstance(result, Program)
        assert len(result.domains) == 1
    
    def test_parse_with_filename(self):
        parser = SimASMParser()
        result = parser.parse("domain Load", filename="test.simasm")
        assert isinstance(result, Program)
    
    def test_parse_syntax_error(self):
        parser = SimASMParser()
        with pytest.raises(ParseError) as exc_info:
            parser.parse("domain")  # Missing name
        assert "Parse error" in str(exc_info.value)
    
    def test_parse_syntax_error_with_filename(self):
        parser = SimASMParser()
        with pytest.raises(ParseError) as exc_info:
            parser.parse("domain", filename="bad.simasm")
        assert "bad.simasm" in str(exc_info.value)


class TestParseFile:
    """Test parse_file functionality."""
    
    def test_parse_file_success(self):
        parser = SimASMParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.simasm', delete=False) as f:
            f.write("domain Load\nvar x: Int")
            f.flush()
            
            result = parser.parse_file(f.name)
            assert isinstance(result, Program)
            assert len(result.domains) == 1
            assert len(result.variables) == 1
        
        Path(f.name).unlink()  # Cleanup
    
    def test_parse_file_not_found(self):
        parser = SimASMParser()
        with pytest.raises(ParseError) as exc_info:
            parser.parse_file("nonexistent.simasm")
        assert "File not found" in str(exc_info.value)
    
    def test_parse_file_path_object(self):
        parser = SimASMParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.simasm', delete=False) as f:
            f.write("domain Event")
            f.flush()
            
            result = parser.parse_file(Path(f.name))
            assert isinstance(result, Program)
        
        Path(f.name).unlink()


class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    def test_parse_string_simple(self):
        result = parse_string("domain Load")
        assert isinstance(result, Program)
        assert len(result.domains) == 1
    
    def test_parse_string_multiline(self):
        result = parse_string("""
            domain Load
            var counter: Int
            
            rule increment() =
                counter := counter + 1
            endrule
        """)
        assert isinstance(result, Program)
        assert len(result.domains) == 1
        assert len(result.variables) == 1
        assert len(result.rules) == 1
    
    def test_parse_file_function(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.simasm', delete=False) as f:
            f.write("domain Test")
            f.flush()
            
            result = parse_file(f.name)
            assert isinstance(result, Program)
        
        Path(f.name).unlink()


class TestParserReusability:
    """Test that parser can be reused."""
    
    def test_parse_multiple_sources(self):
        parser = SimASMParser()
        
        result1 = parser.parse("domain A")
        result2 = parser.parse("domain B")
        result3 = parser.parse("domain C")
        
        assert result1.domains[0].name == "A"
        assert result2.domains[0].name == "B"
        assert result3.domains[0].name == "C"


class TestIntegrationMM1Queue:
    """Integration test with M/M/1 queue model."""
    
    MM1_SOURCE = """
    // M/M/1 Queue Model
    import Random as rnd
    import Stdlib as lib
    
    // Domains
    domain Load
    domain Event
    domain ArriveEvent <: Event
    domain DepartEvent <: Event
    
    // State variables
    var sim_clocktime: Real
    var server_busy: Bool
    
    // Dynamic functions
    dynamic function queue(): List<Load>
    dynamic function fel(): List<Event>
    dynamic function event_time(e: Event): Real
    dynamic function event_rule(e: Event): String
    
    // Rules
    rule arrive() =
        let load = new Load
        lib.add(queue(), load)
        if not server_busy then
            server_busy := true
        endif
    endrule
    
    rule depart() =
        server_busy := false
        if lib.length(queue()) > 0 then
            server_busy := true
        endif
    endrule
    
    main rule main =
        // Get next event
        let next = lib.first(fel())
        sim_clocktime := event_time(next)
        lib.remove(fel(), next)
    endrule
    
    init:
        sim_clocktime := 0.0
        server_busy := false
    endinit
    """
    
    def test_parse_mm1_model(self):
        result = parse_string(self.MM1_SOURCE)
        
        assert isinstance(result, Program)
        
        # Check imports
        assert len(result.imports) == 2
        assert result.imports[0].module == "Random"
        assert result.imports[0].alias == "rnd"
        
        # Check domains
        assert len(result.domains) == 4
        domain_names = [d.name for d in result.domains]
        assert "Load" in domain_names
        assert "Event" in domain_names
        assert "ArriveEvent" in domain_names
        
        # Check inheritance
        arrive_event = next(d for d in result.domains if d.name == "ArriveEvent")
        assert arrive_event.parent == "Event"
        
        # Check variables
        assert len(result.variables) == 2
        var_names = [v.name for v in result.variables]
        assert "sim_clocktime" in var_names
        assert "server_busy" in var_names
        
        # Check dynamic functions
        assert len(result.dynamic_funcs) == 4
        
        # Check rules
        assert len(result.rules) == 2
        rule_names = [r.name for r in result.rules]
        assert "arrive" in rule_names
        assert "depart" in rule_names
        
        # Check main rule
        assert result.main_rule is not None
        assert result.main_rule.name == "main"
        
        # Check init
        assert result.init is not None


class TestIntegrationEventGraph:
    """Integration test with Event Graph pattern."""
    
    EG_SOURCE = """
    // Event Graph Pattern
    import Random as rnd
    import Stdlib as lib
    
    domain Vertex
    domain Edge
    
    var sim_clocktime: Real
    dynamic function fel(): List<Vertex>
    dynamic function out_edges(v: Vertex): List<Edge>
    dynamic function target(e: Edge): Vertex
    dynamic function delay(e: Edge): Real
    dynamic function condition(e: Edge): Bool
    dynamic function vertex_rule(v: Vertex): String
    
    rule fire_vertex(v: Vertex) =
        forall e in out_edges(v) with condition(e) do
            let next_time = sim_clocktime + delay(e)
            lib.add(fel(), (target(e), next_time))
        endforall
    endrule
    
    main rule step =
        choose v in fel() with event_time(v) <= sim_clocktime do
            lib.remove(fel(), v)
            fire_vertex(v)
        endchoose
    endrule
    """
    
    def test_parse_event_graph(self):
        result = parse_string(self.EG_SOURCE)
        
        assert isinstance(result, Program)
        assert len(result.domains) == 2
        assert len(result.dynamic_funcs) == 6
        assert len(result.rules) == 1
        assert result.main_rule is not None
        
        # Check forall in rule body
        fire_rule = result.rules[0]
        assert fire_rule.name == "fire_vertex"
        assert len(fire_rule.params) == 1


class TestErrorMessages:
    """Test that error messages are helpful."""
    
    def test_unexpected_token(self):
        with pytest.raises(ParseError) as exc_info:
            parse_string("domain 123")  # Number instead of name
        # Should contain error info
        assert "Parse error" in str(exc_info.value)
    
    def test_unclosed_block(self):
        with pytest.raises(ParseError):
            parse_string("rule test() = skip")  # Missing endrule
    
    def test_missing_type(self):
        with pytest.raises(ParseError):
            parse_string("var x")  # Missing : Type


class TestModuleImports:
    """Test that all expected items are importable from simasm.parser."""
    
    def test_import_parser_class(self):
        from simasm.parser import SimASMParser
        assert SimASMParser is not None
    
    def test_import_parse_error(self):
        from simasm.parser import ParseError
        assert ParseError is not None
    
    def test_import_functions(self):
        from simasm.parser import parse_string, parse_file
        assert parse_string is not None
        assert parse_file is not None
    
    def test_import_ast_nodes(self):
        from simasm.parser import (
            Program, DomainDecl, VarDecl, RuleDecl,
            SimpleType, ParamType
        )
        assert Program is not None
        assert DomainDecl is not None
