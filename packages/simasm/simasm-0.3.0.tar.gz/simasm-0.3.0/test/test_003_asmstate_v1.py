"""
test_003_asmstate_v1.py

Unit tests for ASMState in simasm/core/state.py

Tests:
- Variable get/set
- Function get/set
- Generic Location-based access
- State operations (copy, clear, locations, contains, len)
- UNDEF handling
- Integration with TypeRegistry
"""

import pytest
from simasm.core.state import UNDEF, ASMObject, Location, ASMState
from simasm.core.types import TypeRegistry, Domain
from simasm.log.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# ASMState Creation Tests
# ============================================================================

class TestASMStateCreation:
    """Tests for ASMState initialization."""
    
    def test_create_empty_state(self):
        """Create empty state with default TypeRegistry."""
        logger.info("Testing empty state creation")
        state = ASMState()
        assert len(state) == 0
        assert state.types is not None
        logger.debug(f"Created: {repr(state)}")
    
    def test_create_state_with_registry(self, populated_registry):
        """Create state with provided TypeRegistry."""
        logger.info("Testing state creation with registry")
        state = ASMState(populated_registry)
        assert state.types is populated_registry
        assert state.types.exists("Load")
        logger.debug("State created with populated registry")
    
    def test_empty_state_repr(self):
        """Empty state repr."""
        logger.info("Testing empty state repr")
        state = ASMState()
        assert "ASMState" in repr(state)
        logger.debug(f"repr: {repr(state)}")
    
    def test_empty_state_str(self):
        """Empty state str."""
        logger.info("Testing empty state str")
        state = ASMState()
        assert "empty" in str(state)
        logger.debug(f"str: {str(state)}")


# ============================================================================
# Variable (0-ary) Tests
# ============================================================================

class TestASMStateVariables:
    """Tests for variable (0-ary function) access."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_get_undefined_variable(self):
        """Getting unset variable returns UNDEF."""
        logger.info("Testing get undefined variable")
        state = ASMState()
        result = state.get_var("x")
        assert result is UNDEF
        logger.debug(f"get_var('x') = {result}")
    
    def test_set_and_get_variable(self):
        """Set and retrieve variable."""
        logger.info("Testing set and get variable")
        state = ASMState()
        state.set_var("x", 10)
        assert state.get_var("x") == 10
        logger.debug("x = 10")
    
    def test_set_variable_overwrites(self):
        """Setting variable overwrites previous value."""
        logger.info("Testing variable overwrite")
        state = ASMState()
        state.set_var("x", 10)
        state.set_var("x", 20)
        assert state.get_var("x") == 20
        logger.debug("x overwritten to 20")
    
    def test_set_variable_to_undef(self):
        """Setting variable to UNDEF stores UNDEF."""
        logger.info("Testing set variable to UNDEF")
        state = ASMState()
        state.set_var("x", 10)
        state.set_var("x", UNDEF)
        
        # Value is UNDEF
        assert state.get_var("x") is UNDEF
        # But location still exists
        assert Location("x") in state
        logger.debug("x set to UNDEF but still in state")
    
    def test_multiple_variables(self):
        """Multiple independent variables."""
        logger.info("Testing multiple variables")
        state = ASMState()
        state.set_var("x", 10)
        state.set_var("y", 20)
        state.set_var("z", 30)
        
        assert state.get_var("x") == 10
        assert state.get_var("y") == 20
        assert state.get_var("z") == 30
        logger.debug("x=10, y=20, z=30")
    
    def test_variable_various_types(self):
        """Variables can hold various Python types."""
        logger.info("Testing variable types")
        state = ASMState()
        
        state.set_var("int_val", 42)
        state.set_var("float_val", 3.14)
        state.set_var("str_val", "hello")
        state.set_var("bool_val", True)
        state.set_var("list_val", [1, 2, 3])
        state.set_var("none_val", None)
        
        assert state.get_var("int_val") == 42
        assert state.get_var("float_val") == 3.14
        assert state.get_var("str_val") == "hello"
        assert state.get_var("bool_val") is True
        assert state.get_var("list_val") == [1, 2, 3]
        assert state.get_var("none_val") is None
        logger.debug("Various types stored correctly")
    
    def test_variable_holds_asm_object(self):
        """Variable can hold ASMObject."""
        logger.info("Testing variable with ASMObject")
        state = ASMState()
        load = ASMObject("Load")
        state.set_var("current_load", load)
        
        assert state.get_var("current_load") == load
        logger.debug(f"current_load = {load}")


# ============================================================================
# Function (n-ary) Tests
# ============================================================================

class TestASMStateFunctions:
    """Tests for function (n-ary) access."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_get_undefined_function(self):
        """Getting unset function location returns UNDEF."""
        logger.info("Testing get undefined function")
        state = ASMState()
        load = ASMObject("Load")
        result = state.get_func("status", (load,))
        assert result is UNDEF
        logger.debug(f"status(load) = {result}")
    
    def test_set_and_get_function(self):
        """Set and retrieve function value."""
        logger.info("Testing set and get function")
        state = ASMState()
        load = ASMObject("Load")
        state.set_func("status", (load,), "waiting")
        
        assert state.get_func("status", (load,)) == "waiting"
        logger.debug(f"status({load}) = waiting")
    
    def test_function_different_args(self):
        """Same function, different args = different locations."""
        logger.info("Testing function with different args")
        state = ASMState()
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        state.set_func("status", (load1,), "waiting")
        state.set_func("status", (load2,), "processing")
        
        assert state.get_func("status", (load1,)) == "waiting"
        assert state.get_func("status", (load2,)) == "processing"
        logger.debug(f"status({load1})=waiting, status({load2})=processing")
    
    def test_function_multiple_args(self):
        """Function with multiple arguments."""
        logger.info("Testing function with multiple args")
        state = ASMState()
        node1 = ASMObject("Node")
        node2 = ASMObject("Node")
        
        state.set_func("distance", (node1, node2), 10.5)
        state.set_func("distance", (node2, node1), 10.5)  # Symmetric
        
        assert state.get_func("distance", (node1, node2)) == 10.5
        assert state.get_func("distance", (node2, node1)) == 10.5
        # Different args = UNDEF
        assert state.get_func("distance", (node1, node1)) is UNDEF
        logger.debug("Multi-arg function works")
    
    def test_set_function_to_undef(self):
        """Setting function to UNDEF stores UNDEF."""
        logger.info("Testing set function to UNDEF")
        state = ASMState()
        load = ASMObject("Load")
        
        state.set_func("status", (load,), "waiting")
        state.set_func("status", (load,), UNDEF)
        
        assert state.get_func("status", (load,)) is UNDEF
        assert Location("status", (load,)) in state
        logger.debug("Function set to UNDEF but still in state")
    
    def test_different_functions_same_args(self):
        """Different function names with same args."""
        logger.info("Testing different functions same args")
        state = ASMState()
        obj = ASMObject("Entity")
        
        state.set_func("position", (obj,), (10, 20))
        state.set_func("velocity", (obj,), (1, 0))
        
        assert state.get_func("position", (obj,)) == (10, 20)
        assert state.get_func("velocity", (obj,)) == (1, 0)
        logger.debug("Different functions with same arg work")


# ============================================================================
# Generic Location Access Tests
# ============================================================================

class TestASMStateLocationAccess:
    """Tests for generic Location-based access."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_get_variable_via_location(self):
        """Get variable using Location."""
        logger.info("Testing get variable via Location")
        state = ASMState()
        state.set_var("x", 42)
        
        loc = Location("x")
        assert state.get(loc) == 42
        logger.debug(f"get(Location('x')) = 42")
    
    def test_set_variable_via_location(self):
        """Set variable using Location."""
        logger.info("Testing set variable via Location")
        state = ASMState()
        
        loc = Location("x")
        state.set(loc, 42)
        
        assert state.get_var("x") == 42
        logger.debug("set via Location works for variable")
    
    def test_get_function_via_location(self):
        """Get function using Location."""
        logger.info("Testing get function via Location")
        state = ASMState()
        load = ASMObject("Load")
        state.set_func("status", (load,), "waiting")
        
        loc = Location("status", load)
        assert state.get(loc) == "waiting"
        logger.debug("get via Location works for function")
    
    def test_set_function_via_location(self):
        """Set function using Location."""
        logger.info("Testing set function via Location")
        state = ASMState()
        load = ASMObject("Load")
        
        loc = Location("status", load)
        state.set(loc, "done")
        
        assert state.get_func("status", (load,)) == "done"
        logger.debug("set via Location works for function")
    
    def test_location_consistency(self):
        """Location access consistent with direct access."""
        logger.info("Testing Location consistency")
        state = ASMState()
        load = ASMObject("Load")
        
        # Set via direct, get via Location
        state.set_var("x", 10)
        state.set_func("status", (load,), "waiting")
        
        assert state.get(Location("x")) == 10
        assert state.get(Location("status", load)) == "waiting"
        
        # Set via Location, get via direct
        state.set(Location("y"), 20)
        state.set(Location("data", load), "info")
        
        assert state.get_var("y") == 20
        assert state.get_func("data", (load,)) == "info"
        logger.debug("Direct and Location access are consistent")


# ============================================================================
# State Operations Tests
# ============================================================================

class TestASMStateOperations:
    """Tests for state operations (copy, clear, locations, etc.)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_len_empty(self):
        """Empty state has length 0."""
        logger.info("Testing len empty")
        state = ASMState()
        assert len(state) == 0
        logger.debug("len(empty) = 0")
    
    def test_len_with_data(self):
        """Length counts all locations."""
        logger.info("Testing len with data")
        state = ASMState()
        load = ASMObject("Load")
        
        state.set_var("x", 10)
        state.set_var("y", 20)
        state.set_func("status", (load,), "waiting")
        
        assert len(state) == 3
        logger.debug("len = 3")
    
    def test_contains_variable(self):
        """Contains check for variable."""
        logger.info("Testing contains variable")
        state = ASMState()
        state.set_var("x", 10)
        
        assert Location("x") in state
        assert Location("y") not in state
        logger.debug("contains works for variable")
    
    def test_contains_function(self):
        """Contains check for function."""
        logger.info("Testing contains function")
        state = ASMState()
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        state.set_func("status", (load1,), "waiting")
        
        assert Location("status", load1) in state
        assert Location("status", load2) not in state
        logger.debug("contains works for function")
    
    def test_contains_after_set_undef(self):
        """Location still 'in' state after set to UNDEF."""
        logger.info("Testing contains after UNDEF")
        state = ASMState()
        state.set_var("x", 10)
        state.set_var("x", UNDEF)
        
        assert Location("x") in state
        logger.debug("x still in state after UNDEF")
    
    def test_locations_empty(self):
        """Empty state has no locations."""
        logger.info("Testing locations empty")
        state = ASMState()
        assert state.locations() == set()
        logger.debug("locations() = {}")
    
    def test_locations_with_data(self):
        """Locations returns all defined locations."""
        logger.info("Testing locations with data")
        state = ASMState()
        load = ASMObject("Load")
        
        state.set_var("x", 10)
        state.set_func("status", (load,), "waiting")
        
        locs = state.locations()
        assert len(locs) == 2
        assert Location("x") in locs
        assert Location("status", load) in locs
        logger.debug(f"locations = {locs}")
    
    def test_clear(self):
        """Clear removes all data."""
        logger.info("Testing clear")
        state = ASMState()
        load = ASMObject("Load")
        
        state.set_var("x", 10)
        state.set_func("status", (load,), "waiting")
        assert len(state) == 2
        
        state.clear()
        assert len(state) == 0
        assert state.get_var("x") is UNDEF
        assert state.get_func("status", (load,)) is UNDEF
        logger.debug("State cleared")
    
    def test_clear_preserves_types(self, populated_registry):
        """Clear preserves TypeRegistry."""
        logger.info("Testing clear preserves types")
        state = ASMState(populated_registry)
        state.set_var("x", 10)
        
        state.clear()
        
        assert state.types is populated_registry
        assert state.types.exists("Load")
        logger.debug("Types preserved after clear")
    
    def test_copy_basic(self):
        """Copy creates independent state."""
        logger.info("Testing copy basic")
        state1 = ASMState()
        state1.set_var("x", 10)
        
        state2 = state1.copy()
        
        # Same initial value
        assert state2.get_var("x") == 10
        
        # Independent
        state2.set_var("x", 20)
        assert state1.get_var("x") == 10
        assert state2.get_var("x") == 20
        logger.debug("Copy is independent")
    
    def test_copy_deep(self):
        """Copy is deep (lists are independent)."""
        logger.info("Testing copy deep")
        state1 = ASMState()
        state1.set_var("items", [1, 2, 3])
        
        state2 = state1.copy()
        
        # Modify copy
        state2.get_var("items").append(4)
        
        # Original unchanged
        assert state1.get_var("items") == [1, 2, 3]
        assert state2.get_var("items") == [1, 2, 3, 4]
        logger.debug("Deep copy works")
    
    def test_copy_shares_types(self, populated_registry):
        """Copy shares TypeRegistry reference."""
        logger.info("Testing copy shares types")
        state1 = ASMState(populated_registry)
        state2 = state1.copy()
        
        assert state1.types is state2.types
        logger.debug("TypeRegistry shared")
    
    def test_copy_with_functions(self):
        """Copy includes function data."""
        logger.info("Testing copy with functions")
        state1 = ASMState()
        load = ASMObject("Load")
        state1.set_func("status", (load,), "waiting")
        
        state2 = state1.copy()
        
        assert state2.get_func("status", (load,)) == "waiting"
        
        # Independent
        state2.set_func("status", (load,), "done")
        assert state1.get_func("status", (load,)) == "waiting"
        logger.debug("Functions copied correctly")


# ============================================================================
# String Representation Tests
# ============================================================================

class TestASMStateRepr:
    """Tests for __repr__ and __str__."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_repr_with_data(self):
        """Repr shows counts."""
        logger.info("Testing repr with data")
        state = ASMState()
        state.set_var("x", 10)
        state.set_func("f", (1,), 20)
        
        r = repr(state)
        assert "ASMState" in r
        assert "variables" in r
        assert "functions" in r
        logger.debug(f"repr: {r}")
    
    def test_str_with_data(self):
        """Str shows detailed contents."""
        logger.info("Testing str with data")
        state = ASMState()
        state.set_var("x", 10)
        state.set_var("y", 20)
        
        s = str(state)
        assert "x = 10" in s
        assert "y = 20" in s
        logger.debug(f"str:\n{s}")
    
    def test_str_with_functions(self):
        """Str shows function values."""
        logger.info("Testing str with functions")
        state = ASMState()
        load = ASMObject("Load")
        state.set_func("status", (load,), "waiting")
        
        s = str(state)
        assert "status" in s
        assert "waiting" in s
        logger.debug(f"str:\n{s}")


# ============================================================================
# Integration Tests
# ============================================================================

class TestASMStateIntegration:
    """Integration tests for ASMState."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_simulate_simple_step(self):
        """Simulate a simple state transition."""
        logger.info("Testing simple step simulation")
        state = ASMState()
        
        # Initial state
        state.set_var("x", 0)
        state.set_var("running", True)
        
        # Step: x := x + 1
        old_x = state.get_var("x")
        state.set_var("x", old_x + 1)
        
        assert state.get_var("x") == 1
        logger.debug("Simple step works")
    
    def test_simulate_with_objects(self):
        """Simulate state transition with objects."""
        logger.info("Testing step with objects")
        state = ASMState()
        
        # Create queue
        queue = ASMObject("Queue")
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        # Initialize
        state.set_func("items", (queue,), [])
        
        # Add to queue
        items = state.get_func("items", (queue,))
        items.append(load1)
        items.append(load2)
        state.set_func("items", (queue,), items)
        
        # Verify
        result = state.get_func("items", (queue,))
        assert len(result) == 2
        assert load1 == result[0]
        assert load2 == result[1]
        logger.debug("Queue simulation works")
    
    def test_state_snapshot(self):
        """Take snapshot and continue simulation."""
        logger.info("Testing state snapshot")
        state = ASMState()
        
        # Initial
        state.set_var("step", 0)
        state.set_var("value", 100)
        
        # Take snapshot
        snapshot = state.copy()
        
        # Continue simulation
        for i in range(5):
            step = state.get_var("step")
            value = state.get_var("value")
            state.set_var("step", step + 1)
            state.set_var("value", value - 10)
        
        # Original state changed
        assert state.get_var("step") == 5
        assert state.get_var("value") == 50
        
        # Snapshot preserved
        assert snapshot.get_var("step") == 0
        assert snapshot.get_var("value") == 100
        logger.debug("Snapshot preserved correctly")
    
    def test_with_populated_fixture(self, populated_state):
        """Test with populated_state fixture."""
        logger.info("Testing with populated_state fixture")
        state, objs = populated_state
        
        assert state.get_var("x") == 10
        assert state.get_var("y") == 20
        assert state.get_func("status", (objs['load1'],)) == "waiting"
        assert state.get_func("status", (objs['load2'],)) == "processing"
        
        queue = state.get_func("queue", (objs['server1'],))
        assert len(queue) == 2
        logger.debug("Populated fixture works")
