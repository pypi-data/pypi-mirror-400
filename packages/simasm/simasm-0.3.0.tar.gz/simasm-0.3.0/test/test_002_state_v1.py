"""
test_002_state_v1.py

Unit tests for simasm/core/state.py (UNDEF, ASMObject, Location)

Tests:
- UNDEF singleton and behavior
- ASMObject creation, equality, hashing
- Location creation, auto-wrapping, properties
"""

import pytest
from simasm.core.state import UNDEF, Undefined, ASMObject, Location
from simasm.log.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# UNDEF Tests
# ============================================================================

class TestUndefined:
    """Tests for UNDEF singleton."""
    
    def test_undef_is_singleton(self):
        """Only one UNDEF instance should exist."""
        logger.info("Testing UNDEF singleton")
        undef1 = Undefined()
        undef2 = Undefined()
        assert undef1 is undef2
        assert undef1 is UNDEF
        logger.debug("UNDEF singleton verified")
    
    def test_undef_repr(self):
        """UNDEF repr should be 'undef'."""
        logger.info("Testing UNDEF repr")
        assert repr(UNDEF) == "undef"
        assert str(UNDEF) == "undef"
        logger.debug(f"repr(UNDEF) = {repr(UNDEF)}")
    
    def test_undef_is_falsy(self):
        """UNDEF should be falsy."""
        logger.info("Testing UNDEF falsy")
        assert not UNDEF
        assert bool(UNDEF) is False
        logger.debug("UNDEF is falsy")
    
    def test_undef_equality_with_itself(self):
        """UNDEF == UNDEF should be True."""
        logger.info("Testing UNDEF equality with itself")
        assert UNDEF == UNDEF
        assert not (UNDEF != UNDEF)
        logger.debug("UNDEF equals itself")
    
    def test_undef_inequality_with_other_values(self):
        """UNDEF should not equal other values."""
        logger.info("Testing UNDEF inequality with other values")
        assert UNDEF != None
        assert UNDEF != False
        assert UNDEF != 0
        assert UNDEF != ""
        assert UNDEF != []
        logger.debug("UNDEF not equal to None, False, 0, '', []")
    
    def test_undef_identity_check(self):
        """'is' check should work for UNDEF."""
        logger.info("Testing UNDEF identity check")
        value = UNDEF
        assert value is UNDEF
        
        other = None
        assert other is not UNDEF
        logger.debug("Identity check works")
    
    def test_undef_is_hashable(self):
        """UNDEF should be usable in sets and as dict key."""
        logger.info("Testing UNDEF hashability")
        s = {UNDEF}
        assert UNDEF in s
        
        d = {UNDEF: "undefined"}
        assert d[UNDEF] == "undefined"
        logger.debug("UNDEF is hashable")
    
    def test_undef_in_conditional(self):
        """UNDEF should work in if statements."""
        logger.info("Testing UNDEF in conditional")
        value = UNDEF
        
        if value:
            result = "truthy"
        else:
            result = "falsy"
        
        assert result == "falsy"
        logger.debug("UNDEF works in conditionals")


# ============================================================================
# ASMObject Tests
# ============================================================================

class TestASMObject:
    """Tests for ASMObject."""
    
    @pytest.fixture(autouse=True)
    def reset_counters(self):
        """Reset counters before each test."""
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_create_object(self):
        """Create a simple object."""
        logger.info("Testing object creation")
        obj = ASMObject("Load")
        assert obj.domain == "Load"
        assert obj.internal_id == 1
        logger.debug(f"Created: {obj}")
    
    def test_domain_specific_counters(self):
        """Each domain has its own counter."""
        logger.info("Testing domain-specific counters")
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        event1 = ASMObject("Event")
        
        assert load1.internal_id == 1
        assert load2.internal_id == 2
        assert event1.internal_id == 1  # Event starts at 1
        logger.debug(f"load1={load1}, load2={load2}, event1={event1}")
    
    def test_repr(self):
        """Object repr should be 'Domain#id'."""
        logger.info("Testing object repr")
        obj = ASMObject("Server")
        assert repr(obj) == "Server#1"
        assert str(obj) == "Server#1"
        logger.debug(f"repr: {repr(obj)}")
    
    def test_equality_same_object(self):
        """Object equals itself."""
        logger.info("Testing object self-equality")
        obj = ASMObject("Load")
        assert obj == obj
        logger.debug("Object equals itself")
    
    def test_equality_same_domain_and_id(self):
        """Two references to logically same object are equal."""
        logger.info("Testing logical equality")
        # Create two objects, reset, create again
        obj1 = ASMObject("Load")
        ASMObject.reset_counters()
        obj2 = ASMObject("Load")
        
        # Both have id=1 and domain="Load"
        assert obj1 == obj2
        logger.debug(f"{obj1} == {obj2}")
    
    def test_inequality_different_id(self):
        """Objects with different IDs are not equal."""
        logger.info("Testing inequality by ID")
        obj1 = ASMObject("Load")
        obj2 = ASMObject("Load")
        assert obj1 != obj2
        logger.debug(f"{obj1} != {obj2}")
    
    def test_inequality_different_domain(self):
        """Objects with different domains are not equal."""
        logger.info("Testing inequality by domain")
        load = ASMObject("Load")
        ASMObject.reset_counters()
        event = ASMObject("Event")
        
        # Both have id=1 but different domains
        assert load != event
        logger.debug(f"{load} != {event}")
    
    def test_comparison_with_non_object_raises(self):
        """Comparing with non-ASMObject raises TypeError."""
        logger.info("Testing comparison with non-ASMObject")
        obj = ASMObject("Load")
        
        with pytest.raises(TypeError, match="Cannot compare ASMObject"):
            obj == "Load#1"
        
        with pytest.raises(TypeError, match="Cannot compare ASMObject"):
            obj == 1
        
        with pytest.raises(TypeError, match="Cannot compare ASMObject"):
            obj == None
        
        logger.debug("TypeError raised for non-ASMObject comparison")
    
    def test_hashable(self):
        """Objects should be usable as dict keys."""
        logger.info("Testing hashability")
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        data = {load1: "first", load2: "second"}
        assert data[load1] == "first"
        assert data[load2] == "second"
        logger.debug("Objects work as dict keys")
    
    def test_hashable_in_set(self):
        """Objects should be usable in sets."""
        logger.info("Testing set membership")
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        s = {load1, load2}
        assert len(s) == 2
        assert load1 in s
        assert load2 in s
        logger.debug("Objects work in sets")
    
    def test_reset_counters(self):
        """Reset counters should clear all domain counters."""
        logger.info("Testing counter reset")
        ASMObject("Load")
        ASMObject("Load")
        ASMObject("Event")
        
        assert ASMObject.get_counter("Load") == 2
        assert ASMObject.get_counter("Event") == 1
        
        ASMObject.reset_counters()
        
        assert ASMObject.get_counter("Load") == 0
        assert ASMObject.get_counter("Event") == 0
        logger.debug("Counters reset successfully")
    
    def test_get_counter(self):
        """Get counter returns current count for domain."""
        logger.info("Testing get_counter")
        assert ASMObject.get_counter("Load") == 0
        
        ASMObject("Load")
        assert ASMObject.get_counter("Load") == 1
        
        ASMObject("Load")
        assert ASMObject.get_counter("Load") == 2
        
        # Other domains unaffected
        assert ASMObject.get_counter("Event") == 0
        logger.debug("get_counter works correctly")
    
    def test_reproducible_ids(self):
        """Same creation order produces same IDs."""
        logger.info("Testing reproducibility")
        # First run
        ASMObject.reset_counters()
        run1_objs = [
            ASMObject("Load"),
            ASMObject("Event"),
            ASMObject("Load"),
        ]
        run1_ids = [(o.domain, o.internal_id) for o in run1_objs]
        
        # Second run (same order)
        ASMObject.reset_counters()
        run2_objs = [
            ASMObject("Load"),
            ASMObject("Event"),
            ASMObject("Load"),
        ]
        run2_ids = [(o.domain, o.internal_id) for o in run2_objs]
        
        assert run1_ids == run2_ids
        logger.debug(f"Reproducible: {run1_ids}")


# ============================================================================
# Location Tests
# ============================================================================

class TestLocation:
    """Tests for Location."""
    
    @pytest.fixture(autouse=True)
    def reset_counters(self):
        """Reset ASMObject counters for tests that use objects."""
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_create_variable_location(self):
        """Create 0-ary location (variable)."""
        logger.info("Testing variable location")
        loc = Location("x")
        assert loc.func_name == "x"
        assert loc.args == ()
        assert loc.arity == 0
        assert loc.is_variable is True
        logger.debug(f"Created: {loc}")
    
    def test_create_variable_with_empty_tuple(self):
        """Create 0-ary location with explicit empty tuple."""
        logger.info("Testing variable with empty tuple")
        loc = Location("x", ())
        assert loc.func_name == "x"
        assert loc.args == ()
        assert loc.is_variable is True
        logger.debug(f"Created: {loc}")
    
    def test_create_unary_location(self):
        """Create 1-ary location."""
        logger.info("Testing unary location")
        obj = ASMObject("Queue")
        loc = Location("queues", (obj,))
        assert loc.func_name == "queues"
        assert loc.args == (obj,)
        assert loc.arity == 1
        assert loc.is_variable is False
        logger.debug(f"Created: {loc}")
    
    def test_create_binary_location(self):
        """Create 2-ary location."""
        logger.info("Testing binary location")
        obj1 = ASMObject("Node")
        obj2 = ASMObject("Node")
        loc = Location("distance", (obj1, obj2))
        assert loc.func_name == "distance"
        assert loc.args == (obj1, obj2)
        assert loc.arity == 2
        logger.debug(f"Created: {loc}")
    
    def test_auto_wrap_single_arg(self):
        """Single non-tuple arg should be auto-wrapped."""
        logger.info("Testing auto-wrap single arg")
        obj = ASMObject("Server")
        loc = Location("status", obj)  # Not a tuple
        assert loc.args == (obj,)
        assert loc.arity == 1
        logger.debug(f"Auto-wrapped: {loc}")
    
    def test_auto_wrap_primitive(self):
        """Primitive values should also be auto-wrapped."""
        logger.info("Testing auto-wrap primitive")
        loc = Location("data", 42)
        assert loc.args == (42,)
        
        loc2 = Location("name", "test")
        assert loc2.args == ("test",)
        logger.debug("Primitives auto-wrapped")
    
    def test_auto_wrap_none(self):
        """None should become empty tuple."""
        logger.info("Testing auto-wrap None")
        loc = Location("x", None)
        assert loc.args == ()
        assert loc.is_variable is True
        logger.debug("None becomes empty tuple")
    
    def test_location_is_frozen(self):
        """Location should be immutable."""
        logger.info("Testing location immutability")
        loc = Location("x")
        with pytest.raises(AttributeError):
            loc.func_name = "y"
        with pytest.raises(AttributeError):
            loc.args = (1,)
        logger.debug("Location is frozen")
    
    def test_location_equality(self):
        """Locations with same name and args are equal."""
        logger.info("Testing location equality")
        loc1 = Location("x", ())
        loc2 = Location("x", ())
        assert loc1 == loc2
        
        obj = ASMObject("Load")
        loc3 = Location("status", (obj,))
        loc4 = Location("status", (obj,))
        assert loc3 == loc4
        logger.debug("Equal locations are equal")
    
    def test_location_inequality_by_name(self):
        """Locations with different names are not equal."""
        logger.info("Testing inequality by name")
        loc1 = Location("x")
        loc2 = Location("y")
        assert loc1 != loc2
        logger.debug("Different names -> not equal")
    
    def test_location_inequality_by_args(self):
        """Locations with different args are not equal."""
        logger.info("Testing inequality by args")
        obj1 = ASMObject("Load")
        obj2 = ASMObject("Load")
        loc1 = Location("status", (obj1,))
        loc2 = Location("status", (obj2,))
        assert loc1 != loc2
        logger.debug("Different args -> not equal")
    
    def test_location_hashable(self):
        """Locations should be usable as dict keys."""
        logger.info("Testing location hashability")
        loc1 = Location("x")
        loc2 = Location("y")
        
        d = {loc1: 10, loc2: 20}
        assert d[loc1] == 10
        assert d[loc2] == 20
        logger.debug("Locations work as dict keys")
    
    def test_location_in_set(self):
        """Locations should be usable in sets."""
        logger.info("Testing location in set")
        loc1 = Location("x")
        loc2 = Location("x")  # Same as loc1
        loc3 = Location("y")
        
        s = {loc1, loc2, loc3}
        assert len(s) == 2  # loc1 and loc2 are equal
        logger.debug("Locations work in sets")
    
    def test_repr_variable(self):
        """Repr for variable location."""
        logger.info("Testing variable repr")
        loc = Location("x")
        assert repr(loc) == "Location('x')"
        logger.debug(f"repr: {repr(loc)}")
    
    def test_repr_unary(self):
        """Repr for unary location."""
        logger.info("Testing unary repr")
        obj = ASMObject("Load")
        loc = Location("status", (obj,))
        assert repr(loc) == f"Location('status', ({obj!r},))"
        logger.debug(f"repr: {repr(loc)}")
    
    def test_repr_binary(self):
        """Repr for binary location."""
        logger.info("Testing binary repr")
        obj1 = ASMObject("Node")
        obj2 = ASMObject("Node")
        loc = Location("edge", (obj1, obj2))
        assert repr(loc) == f"Location('edge', ({obj1!r}, {obj2!r}))"
        logger.debug(f"repr: {repr(loc)}")
    
    def test_str_variable(self):
        """Str for variable location."""
        logger.info("Testing variable str")
        loc = Location("x")
        assert str(loc) == "x"
        logger.debug(f"str: {str(loc)}")
    
    def test_str_unary(self):
        """Str for unary location."""
        logger.info("Testing unary str")
        obj = ASMObject("Load")
        loc = Location("status", (obj,))
        assert str(loc) == f"status({obj})"
        logger.debug(f"str: {str(loc)}")
    
    def test_str_binary(self):
        """Str for binary location."""
        logger.info("Testing binary str")
        obj1 = ASMObject("Node")
        obj2 = ASMObject("Node")
        loc = Location("edge", (obj1, obj2))
        assert str(loc) == f"edge({obj1}, {obj2})"
        logger.debug(f"str: {str(loc)}")
    
    def test_location_with_undef_arg(self):
        """Location can have UNDEF as argument."""
        logger.info("Testing location with UNDEF arg")
        loc = Location("data", (UNDEF,))
        assert loc.args == (UNDEF,)
        assert loc.arity == 1
        logger.debug(f"Created: {loc}")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining UNDEF, ASMObject, Location."""
    
    @pytest.fixture(autouse=True)
    def reset_counters(self):
        """Reset ASMObject counters."""
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_location_as_state_key(self):
        """Locations should work as keys in a state-like dict."""
        logger.info("Testing locations as state keys")
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        # Simulate state: location -> value
        state = {}
        state[Location("x")] = 10
        state[Location("status", load1)] = "waiting"
        state[Location("status", load2)] = "processing"
        
        assert state[Location("x")] == 10
        assert state[Location("status", load1)] == "waiting"
        assert state[Location("status", load2)] == "processing"
        
        # Undefined location
        loc_undef = Location("y")
        assert state.get(loc_undef, UNDEF) is UNDEF
        logger.debug("Locations work as state keys")
    
    def test_object_identity_in_location(self):
        """Same object in location should match."""
        logger.info("Testing object identity in location")
        obj = ASMObject("Server")
        
        loc1 = Location("status", obj)
        loc2 = Location("status", obj)
        
        assert loc1 == loc2
        assert hash(loc1) == hash(loc2)
        logger.debug("Same object -> same location")
    
    def test_different_objects_different_locations(self):
        """Different objects should create different locations."""
        logger.info("Testing different objects -> different locations")
        obj1 = ASMObject("Server")
        obj2 = ASMObject("Server")
        
        loc1 = Location("status", obj1)
        loc2 = Location("status", obj2)
        
        assert loc1 != loc2
        logger.debug("Different objects -> different locations")
