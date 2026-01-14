"""
Test Section 12: Loader - Program AST to Runtime

Tests that ProgramLoader correctly converts parsed Program AST
into executable runtime objects.
"""

import pytest
from pathlib import Path
import tempfile

from simasm.parser import parse_string, Program
from simasm.parser.loader import (
    ProgramLoader,
    LoadedProgram,
    LoadError,
    load_program,
    load_string,
    load_file,
)
from simasm.core.types import TypeRegistry
from simasm.core.state import ASMState, Location, UNDEF
from simasm.core.rules import RuleRegistry, RuleDefinition
from simasm.core.terms import Environment
from simasm.runtime.stdlib import StandardLibrary
from simasm.runtime.random import RandomStream
from simasm.parser.loader import SimASMRandom


class TestProgramLoader:
    """Test ProgramLoader class."""
    
    def test_create_loader(self):
        loader = ProgramLoader()
        assert loader is not None
    
    def test_create_loader_with_seed(self):
        loader = ProgramLoader(seed=12345)
        assert loader._seed == 12345
    
    def test_load_empty_program(self):
        program = parse_string("")
        loader = ProgramLoader()
        loaded = loader.load(program)
        
        assert isinstance(loaded, LoadedProgram)
        assert isinstance(loaded.types, TypeRegistry)
        assert isinstance(loaded.state, ASMState)
        assert isinstance(loaded.rules, RuleRegistry)


class TestLoadDomains:
    """Test domain loading."""
    
    def test_load_simple_domain(self):
        loaded = load_string("domain Load")
        
        assert loaded.types.exists("Load")
        assert not loaded.types.is_builtin("Load")
    
    def test_load_multiple_domains(self):
        loaded = load_string("""
            domain Load
            domain Event
            domain Server
        """)
        
        assert loaded.types.exists("Load")
        assert loaded.types.exists("Event")
        assert loaded.types.exists("Server")
    
    def test_load_domain_with_parent(self):
        loaded = load_string("""
            domain Event
            domain ArriveEvent <: Event
            domain DepartEvent <: Event
        """)
        
        assert loaded.types.exists("Event")
        assert loaded.types.exists("ArriveEvent")
        assert loaded.types.is_subtype("ArriveEvent", "Event")
        assert loaded.types.is_subtype("DepartEvent", "Event")
    
    def test_load_domain_builtin_parent(self):
        loaded = load_string("domain PositiveReal <: Real")
        
        assert loaded.types.exists("PositiveReal")
        assert loaded.types.is_subtype("PositiveReal", "Real")


class TestLoadImports:
    """Test import loading."""
    
    def test_load_random_import(self):
        loaded = load_string("import Random as rnd")
        
        assert "rnd" in loaded.imports
        assert loaded.imports["rnd"] == "Random"
    
    def test_load_stdlib_import(self):
        loaded = load_string("import Stdlib as lib")
        
        assert "lib" in loaded.imports
        assert loaded.imports["lib"] == "Stdlib"
    
    def test_load_both_imports(self):
        loaded = load_string("""
            import Random as rnd
            import Stdlib as lib
        """)
        
        assert len(loaded.imports) == 2
        assert loaded.imports["rnd"] == "Random"
        assert loaded.imports["lib"] == "Stdlib"
    
    def test_unknown_module_raises(self):
        with pytest.raises(LoadError) as exc_info:
            load_string("import Unknown as foo")
        assert "Unknown module" in str(exc_info.value)


class TestLoadRules:
    """Test rule loading."""
    
    def test_load_simple_rule(self):
        loaded = load_string("""
            rule test() =
                skip
            endrule
        """)
        
        assert loaded.rules.exists("test")
        rule = loaded.rules.get("test")
        assert rule.name == "test"
        assert rule.parameters == []
    
    def test_load_rule_with_params(self):
        loaded = load_string("""
            domain Load
            rule process(load: Load) =
                skip
            endrule
        """)
        
        assert loaded.rules.exists("process")
        rule = loaded.rules.get("process")
        assert rule.parameters == ["load"]
    
    def test_load_multiple_rules(self):
        loaded = load_string("""
            rule arrive() = skip endrule
            rule depart() = skip endrule
            rule process() = skip endrule
        """)
        
        assert loaded.rules.exists("arrive")
        assert loaded.rules.exists("depart")
        assert loaded.rules.exists("process")
    
    def test_load_main_rule(self):
        loaded = load_string("""
            main rule main =
                skip
            endrule
        """)
        
        assert loaded.main_rule_name == "main"
        assert loaded.rules.exists("main")


class TestLoadInit:
    """Test init block execution."""
    
    def test_init_sets_variable(self):
        loaded = load_string("""
            var counter: Int
            init:
                counter := 0
            endinit
        """)
        
        loc = Location("counter", ())
        assert loaded.state.get(loc) == 0
    
    def test_init_sets_multiple_variables(self):
        loaded = load_string("""
            var x: Int
            var y: Real
            var flag: Bool
            init:
                x := 42
                y := 3.14
                flag := true
            endinit
        """)
        
        assert loaded.state.get(Location("x", ())) == 42
        assert loaded.state.get(Location("y", ())) == 3.14
        assert loaded.state.get(Location("flag", ())) == True
    
    def test_init_with_expression(self):
        loaded = load_string("""
            var x: Int
            var y: Int
            init:
                x := 10
                y := x + 5
            endinit
        """)
        
        assert loaded.state.get(Location("x", ())) == 10
        assert loaded.state.get(Location("y", ())) == 15
    
    def test_init_with_lib_call(self):
        loaded = load_string("""
            import Stdlib as lib
            var total: Int
            init:
                total := lib.length([1, 2, 3, 4, 5])
            endinit
        """)
        
        assert loaded.state.get(Location("total", ())) == 5


class TestLoadedProgramComponents:
    """Test that LoadedProgram has all components."""
    
    def test_has_stdlib(self):
        loaded = load_string("domain Test")
        assert isinstance(loaded.stdlib, StandardLibrary)
    
    def test_has_rng(self):
        loaded = load_string("domain Test")
        assert isinstance(loaded.rng, SimASMRandom)
    
    def test_has_term_evaluator(self):
        loaded = load_string("domain Test")
        assert loaded.term_evaluator is not None
    
    def test_has_rule_evaluator(self):
        loaded = load_string("domain Test")
        assert loaded.rule_evaluator is not None
    
    def test_rng_uses_seed(self):
        loaded1 = load_string("domain Test", seed=42)
        loaded2 = load_string("domain Test", seed=42)
        
        # Same seed should give same random values
        val1 = loaded1.rng.uniform(0, 100)
        val2 = loaded2.rng.uniform(0, 100)
        assert val1 == val2


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_load_program_function(self):
        program = parse_string("domain Load")
        loaded = load_program(program)
        
        assert isinstance(loaded, LoadedProgram)
        assert loaded.types.exists("Load")
    
    def test_load_string_function(self):
        loaded = load_string("domain Event")
        
        assert isinstance(loaded, LoadedProgram)
        assert loaded.types.exists("Event")
    
    def test_load_file_function(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.simasm', delete=False) as f:
            f.write("domain FileTest\nvar x: Int\ninit: x := 99 endinit")
            f.flush()
            
            loaded = load_file(f.name)
            assert loaded.types.exists("FileTest")
            assert loaded.state.get(Location("x", ())) == 99
        
        Path(f.name).unlink()


class TestIntegrationMM1:
    """Integration test with M/M/1 queue structure."""
    
    MM1_SOURCE = """
    import Random as rnd
    import Stdlib as lib
    
    domain Load
    domain Event
    
    var sim_clocktime: Real
    var server_busy: Bool
    var loads_processed: Int
    
    dynamic function queue(): List<Load>
    
    rule arrive() =
        let load = new Load
        lib.add(queue(), load)
        if not server_busy then
            server_busy := true
        endif
    endrule
    
    rule depart() =
        loads_processed := loads_processed + 1
        if lib.length(queue()) > 0 then
            lib.remove_first(queue())
            server_busy := true
        else
            server_busy := false
        endif
    endrule
    
    main rule main =
        skip
    endrule
    
    init:
        sim_clocktime := 0.0
        server_busy := false
        loads_processed := 0
        queue() := []
    endinit
    """
    
    def test_load_mm1_model(self):
        loaded = load_string(self.MM1_SOURCE)
        
        # Check domains
        assert loaded.types.exists("Load")
        assert loaded.types.exists("Event")
        
        # Check imports
        assert loaded.imports["rnd"] == "Random"
        assert loaded.imports["lib"] == "Stdlib"
        
        # Check rules
        assert loaded.rules.exists("arrive")
        assert loaded.rules.exists("depart")
        assert loaded.rules.exists("main")
        assert loaded.main_rule_name == "main"
        
        # Check init executed
        assert loaded.state.get(Location("sim_clocktime", ())) == 0.0
        assert loaded.state.get(Location("server_busy", ())) == False
        assert loaded.state.get(Location("loads_processed", ())) == 0
    
    def test_run_arrive_rule(self):
        loaded = load_string(self.MM1_SOURCE)
        
        # Execute arrive rule
        env = Environment()
        updates = loaded.rule_evaluator.invoke_rule("arrive", [], env)
        updates.apply_to(loaded.state)
        
        # Server should now be busy
        assert loaded.state.get(Location("server_busy", ())) == True
        
        # Queue should have one load
        queue = loaded.state.get(Location("queue", ()))
        assert len(queue) == 1


class TestIntegrationEventGraph:
    """Integration test with Event Graph pattern."""
    
    EG_SOURCE = """
    import Stdlib as lib
    
    domain Vertex
    
    var sim_clocktime: Real
    var events_fired: Int
    
    dynamic function fel(): List<Vertex>
    
    rule fire(v: Vertex) =
        events_fired := events_fired + 1
    endrule
    
    init:
        sim_clocktime := 0.0
        events_fired := 0
    endinit
    """
    
    def test_load_event_graph(self):
        loaded = load_string(self.EG_SOURCE)
        
        assert loaded.types.exists("Vertex")
        assert loaded.rules.exists("fire")
        assert loaded.state.get(Location("events_fired", ())) == 0
    
    def test_fire_event(self):
        loaded = load_string(self.EG_SOURCE)
        
        # Create a vertex
        from simasm.core.state import ASMObject
        vertex = ASMObject("Vertex")
        
        # Fire event
        env = Environment()
        updates = loaded.rule_evaluator.invoke_rule("fire", [vertex], env)
        updates.apply_to(loaded.state)
        
        assert loaded.state.get(Location("events_fired", ())) == 1


class TestModuleImports:
    """Test that loader items are importable from simasm.parser."""
    
    def test_import_loader_class(self):
        from simasm.parser import ProgramLoader
        assert ProgramLoader is not None
    
    def test_import_loaded_program(self):
        from simasm.parser import LoadedProgram
        assert LoadedProgram is not None
    
    def test_import_load_error(self):
        from simasm.parser import LoadError
        assert LoadError is not None
    
    def test_import_convenience_functions(self):
        from simasm.parser import load_program, load_string, load_file
        assert load_program is not None
        assert load_string is not None
        assert load_file is not None
