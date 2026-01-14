"""
test_004_update_v1.py

Unit tests for simasm/core/update.py

Tests:
- Update dataclass
- UpdateConflictError exception
- UpdateSet operations (add, merge, apply, conflict detection)
"""

import pytest
from simasm.core.state import UNDEF, ASMObject, Location, ASMState
from simasm.core.update import Update, UpdateConflictError, UpdateSet
from simasm.log.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# Update Tests
# ============================================================================

class TestUpdate:
    """Tests for Update dataclass."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_create_update(self):
        """Create a simple update."""
        logger.info("Testing update creation")
        loc = Location("x")
        update = Update(loc, 10)
        assert update.location == loc
        assert update.value == 10
        logger.debug(f"Created: {update}")
    
    def test_update_with_object(self):
        """Create update with ASMObject value."""
        logger.info("Testing update with ASMObject")
        load = ASMObject("Load")
        loc = Location("current_load")
        update = Update(loc, load)
        assert update.value == load
        logger.debug(f"Created: {update}")
    
    def test_update_with_function_location(self):
        """Create update for function location."""
        logger.info("Testing update with function location")
        load = ASMObject("Load")
        loc = Location("status", load)
        update = Update(loc, "waiting")
        assert update.location.func_name == "status"
        assert update.location.args == (load,)
        assert update.value == "waiting"
        logger.debug(f"Created: {update}")
    
    def test_update_is_frozen(self):
        """Update should be immutable."""
        logger.info("Testing update immutability")
        update = Update(Location("x"), 10)
        with pytest.raises(AttributeError):
            update.value = 20
        logger.debug("Update is frozen")
    
    def test_update_repr(self):
        """Update repr should be readable."""
        logger.info("Testing update repr")
        update = Update(Location("x"), 10)
        r = repr(update)
        assert "Update" in r
        assert "x" in r
        assert "10" in r
        logger.debug(f"repr: {r}")
    
    def test_update_str(self):
        """Update str should show assignment."""
        logger.info("Testing update str")
        update = Update(Location("x"), 10)
        s = str(update)
        assert "x" in s
        assert ":=" in s
        assert "10" in s
        logger.debug(f"str: {s}")
    
    def test_update_hash_based_on_location(self):
        """Updates hash based on location only."""
        logger.info("Testing update hash")
        loc = Location("x")
        update1 = Update(loc, 10)
        update2 = Update(loc, 20)  # Different value, same location
        
        # Hash should be same (based on location)
        assert hash(update1) == hash(update2)
        logger.debug("Hash based on location")


# ============================================================================
# UpdateConflictError Tests
# ============================================================================

class TestUpdateConflictError:
    """Tests for UpdateConflictError exception."""
    
    def test_create_error(self):
        """Create conflict error."""
        logger.info("Testing error creation")
        loc = Location("x")
        error = UpdateConflictError(loc, 10, 20)
        assert error.location == loc
        assert error.value1 == 10
        assert error.value2 == 20
        logger.debug(f"Created error: {error}")
    
    def test_error_message(self):
        """Error message should be descriptive."""
        logger.info("Testing error message")
        loc = Location("x")
        error = UpdateConflictError(loc, 10, 20)
        msg = str(error)
        assert "x" in msg
        assert "10" in msg
        assert "20" in msg
        assert "Conflict" in msg
        logger.debug(f"Message: {msg}")
    
    def test_error_with_function_location(self):
        """Error with function location."""
        logger.info("Testing error with function location")
        ASMObject.reset_counters()
        load = ASMObject("Load")
        loc = Location("status", load)
        error = UpdateConflictError(loc, "waiting", "processing")
        msg = str(error)
        assert "status" in msg
        assert "waiting" in msg
        assert "processing" in msg
        ASMObject.reset_counters()
        logger.debug(f"Message: {msg}")


# ============================================================================
# UpdateSet Basic Tests
# ============================================================================

class TestUpdateSetBasic:
    """Basic tests for UpdateSet."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_create_empty_updateset(self):
        """Create empty UpdateSet."""
        logger.info("Testing empty UpdateSet creation")
        updates = UpdateSet()
        assert len(updates) == 0
        logger.debug(f"Created: {repr(updates)}")
    
    def test_add_update_object(self):
        """Add Update object."""
        logger.info("Testing add Update object")
        updates = UpdateSet()
        update = Update(Location("x"), 10)
        updates.add(update)
        assert len(updates) == 1
        logger.debug("Added update via add()")
    
    def test_add_update_direct(self):
        """Add update directly with location and value."""
        logger.info("Testing add_update")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        assert len(updates) == 1
        assert updates.get(Location("x")) == 10
        logger.debug("Added update via add_update()")
    
    def test_add_multiple_updates(self):
        """Add multiple updates."""
        logger.info("Testing multiple updates")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 20)
        updates.add_update(Location("z"), 30)
        assert len(updates) == 3
        logger.debug(f"Added 3 updates: {len(updates)}")
    
    def test_get_pending_value(self):
        """Get pending value for location."""
        logger.info("Testing get pending value")
        updates = UpdateSet()
        updates.add_update(Location("x"), 42)
        assert updates.get(Location("x")) == 42
        logger.debug("get() returns pending value")
    
    def test_get_missing_returns_undef(self):
        """Get for missing location returns UNDEF."""
        logger.info("Testing get missing")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        assert updates.get(Location("y")) is UNDEF
        logger.debug("get() returns UNDEF for missing")
    
    def test_contains_check(self):
        """Check if location has pending update."""
        logger.info("Testing contains")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        assert updates.contains(Location("x"))
        assert not updates.contains(Location("y"))
        logger.debug("contains() works")
    
    def test_in_operator(self):
        """Use 'in' operator for contains check."""
        logger.info("Testing 'in' operator")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        assert Location("x") in updates
        assert Location("y") not in updates
        logger.debug("'in' operator works")
    
    def test_locations(self):
        """Get all locations with pending updates."""
        logger.info("Testing locations()")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 20)
        
        locs = updates.locations()
        assert len(locs) == 2
        assert Location("x") in locs
        assert Location("y") in locs
        logger.debug(f"locations: {locs}")
    
    def test_clear(self):
        """Clear all updates."""
        logger.info("Testing clear")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 20)
        assert len(updates) == 2
        
        updates.clear()
        assert len(updates) == 0
        assert Location("x") not in updates
        logger.debug("Cleared successfully")
    
    def test_iterate(self):
        """Iterate over updates."""
        logger.info("Testing iteration")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 20)
        
        update_list = list(updates)
        assert len(update_list) == 2
        assert all(isinstance(u, Update) for u in update_list)
        logger.debug(f"Iterated: {update_list}")
    
    def test_repr(self):
        """UpdateSet repr."""
        logger.info("Testing repr")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        r = repr(updates)
        assert "UpdateSet" in r
        assert "1" in r
        logger.debug(f"repr: {r}")
    
    def test_str_empty(self):
        """UpdateSet str when empty."""
        logger.info("Testing str empty")
        updates = UpdateSet()
        s = str(updates)
        assert "empty" in s
        logger.debug(f"str: {s}")
    
    def test_str_with_updates(self):
        """UpdateSet str with updates."""
        logger.info("Testing str with updates")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 20)
        s = str(updates)
        assert "x" in s
        assert "y" in s
        assert ":=" in s
        logger.debug(f"str:\n{s}")


# ============================================================================
# UpdateSet Conflict Tests
# ============================================================================

class TestUpdateSetConflicts:
    """Tests for conflict detection."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_idempotent_same_value(self):
        """Same location, same value is OK (idempotent)."""
        logger.info("Testing idempotent update")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("x"), 10)  # Should not raise
        assert len(updates) == 1  # Still just one update
        logger.debug("Idempotent update OK")
    
    def test_conflict_different_values(self):
        """Same location, different values raises error."""
        logger.info("Testing conflict detection")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        
        with pytest.raises(UpdateConflictError) as exc_info:
            updates.add_update(Location("x"), 20)
        
        assert exc_info.value.location == Location("x")
        assert exc_info.value.value1 == 10
        assert exc_info.value.value2 == 20
        logger.debug("Conflict detected correctly")
    
    def test_conflict_with_function_location(self):
        """Conflict detection for function locations."""
        logger.info("Testing conflict with function location")
        load = ASMObject("Load")
        loc = Location("status", load)
        
        updates = UpdateSet()
        updates.add_update(loc, "waiting")
        
        with pytest.raises(UpdateConflictError):
            updates.add_update(loc, "processing")
        logger.debug("Function location conflict detected")
    
    def test_no_conflict_different_locations(self):
        """Different locations never conflict."""
        logger.info("Testing no conflict for different locations")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 10)  # Same value, different location - OK
        updates.add_update(Location("z"), 20)  # Different value, different location - OK
        assert len(updates) == 3
        logger.debug("No conflict for different locations")
    
    def test_conflict_incomparable_types(self):
        """Incomparable types (TypeError) treated as conflict."""
        logger.info("Testing conflict with incomparable types")
        load = ASMObject("Load")
        
        updates = UpdateSet()
        updates.add_update(Location("x"), load)
        
        # ASMObject compared to string raises TypeError
        # Should be treated as conflict
        with pytest.raises(UpdateConflictError):
            updates.add_update(Location("x"), "string_value")
        logger.debug("Incomparable types treated as conflict")
    
    def test_conflict_undef_vs_value(self):
        """UNDEF vs actual value is conflict."""
        logger.info("Testing UNDEF vs value conflict")
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        
        with pytest.raises(UpdateConflictError):
            updates.add_update(Location("x"), UNDEF)
        logger.debug("UNDEF vs value is conflict")
    
    def test_idempotent_undef(self):
        """Same location, both UNDEF is OK."""
        logger.info("Testing idempotent UNDEF")
        updates = UpdateSet()
        updates.add_update(Location("x"), UNDEF)
        updates.add_update(Location("x"), UNDEF)  # Should not raise
        assert len(updates) == 1
        logger.debug("Idempotent UNDEF OK")
    
    def test_idempotent_same_object(self):
        """Same location, same ASMObject is OK."""
        logger.info("Testing idempotent same object")
        load = ASMObject("Load")
        
        updates = UpdateSet()
        updates.add_update(Location("current"), load)
        updates.add_update(Location("current"), load)  # Same object - OK
        assert len(updates) == 1
        logger.debug("Idempotent same object OK")
    
    def test_conflict_different_objects(self):
        """Same location, different ASMObjects raises error."""
        logger.info("Testing conflict with different objects")
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        
        updates = UpdateSet()
        updates.add_update(Location("current"), load1)
        
        with pytest.raises(UpdateConflictError):
            updates.add_update(Location("current"), load2)
        logger.debug("Different objects conflict detected")


# ============================================================================
# UpdateSet Merge Tests
# ============================================================================

class TestUpdateSetMerge:
    """Tests for merging UpdateSets."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_merge_empty_into_empty(self):
        """Merge empty into empty."""
        logger.info("Testing merge empty into empty")
        updates1 = UpdateSet()
        updates2 = UpdateSet()
        updates1.merge(updates2)
        assert len(updates1) == 0
        logger.debug("Merged empty sets")
    
    def test_merge_into_empty(self):
        """Merge updates into empty set."""
        logger.info("Testing merge into empty")
        updates1 = UpdateSet()
        updates2 = UpdateSet()
        updates2.add_update(Location("x"), 10)
        updates2.add_update(Location("y"), 20)
        
        updates1.merge(updates2)
        assert len(updates1) == 2
        assert updates1.get(Location("x")) == 10
        assert updates1.get(Location("y")) == 20
        logger.debug("Merged into empty set")
    
    def test_merge_disjoint(self):
        """Merge disjoint update sets."""
        logger.info("Testing merge disjoint")
        updates1 = UpdateSet()
        updates1.add_update(Location("x"), 10)
        
        updates2 = UpdateSet()
        updates2.add_update(Location("y"), 20)
        
        updates1.merge(updates2)
        assert len(updates1) == 2
        assert updates1.get(Location("x")) == 10
        assert updates1.get(Location("y")) == 20
        logger.debug("Merged disjoint sets")
    
    def test_merge_overlapping_same_value(self):
        """Merge with overlapping locations, same values."""
        logger.info("Testing merge overlapping same value")
        updates1 = UpdateSet()
        updates1.add_update(Location("x"), 10)
        
        updates2 = UpdateSet()
        updates2.add_update(Location("x"), 10)  # Same value
        updates2.add_update(Location("y"), 20)
        
        updates1.merge(updates2)  # Should not raise
        assert len(updates1) == 2
        logger.debug("Merged overlapping with same value")
    
    def test_merge_overlapping_conflict(self):
        """Merge with overlapping locations, different values raises error."""
        logger.info("Testing merge conflict")
        updates1 = UpdateSet()
        updates1.add_update(Location("x"), 10)
        
        updates2 = UpdateSet()
        updates2.add_update(Location("x"), 99)  # Different value!
        
        with pytest.raises(UpdateConflictError) as exc_info:
            updates1.merge(updates2)
        
        assert exc_info.value.location == Location("x")
        logger.debug("Merge conflict detected")
    
    def test_merge_does_not_modify_source(self):
        """Merge does not modify source UpdateSet."""
        logger.info("Testing merge doesn't modify source")
        updates1 = UpdateSet()
        updates2 = UpdateSet()
        updates2.add_update(Location("x"), 10)
        
        updates1.merge(updates2)
        
        # Modify updates1
        updates1.add_update(Location("y"), 20)
        
        # updates2 should be unchanged
        assert len(updates2) == 1
        assert Location("y") not in updates2
        logger.debug("Source not modified")


# ============================================================================
# UpdateSet Apply Tests
# ============================================================================

class TestUpdateSetApply:
    """Tests for applying updates to state."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_apply_to_empty_state(self):
        """Apply updates to empty state."""
        logger.info("Testing apply to empty state")
        state = ASMState()
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        updates.add_update(Location("y"), 20)
        
        updates.apply_to(state)
        
        assert state.get_var("x") == 10
        assert state.get_var("y") == 20
        logger.debug("Applied to empty state")
    
    def test_apply_overwrites_existing(self):
        """Apply updates overwrites existing values."""
        logger.info("Testing apply overwrites")
        state = ASMState()
        state.set_var("x", 100)
        
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        
        updates.apply_to(state)
        
        assert state.get_var("x") == 10
        logger.debug("Applied overwrite")
    
    def test_apply_function_updates(self):
        """Apply updates for function locations."""
        logger.info("Testing apply function updates")
        state = ASMState()
        load = ASMObject("Load")
        
        updates = UpdateSet()
        updates.add_update(Location("status", load), "waiting")
        
        updates.apply_to(state)
        
        assert state.get_func("status", (load,)) == "waiting"
        logger.debug("Applied function update")
    
    def test_apply_undef(self):
        """Apply UNDEF update."""
        logger.info("Testing apply UNDEF")
        state = ASMState()
        state.set_var("x", 100)
        
        updates = UpdateSet()
        updates.add_update(Location("x"), UNDEF)
        
        updates.apply_to(state)
        
        assert state.get_var("x") is UNDEF
        assert Location("x") in state  # Still tracked
        logger.debug("Applied UNDEF update")
    
    def test_apply_empty_updateset(self):
        """Apply empty UpdateSet does nothing."""
        logger.info("Testing apply empty")
        state = ASMState()
        state.set_var("x", 100)
        
        updates = UpdateSet()
        updates.apply_to(state)
        
        assert state.get_var("x") == 100
        logger.debug("Empty apply did nothing")
    
    def test_apply_does_not_clear(self):
        """Apply does not clear the UpdateSet."""
        logger.info("Testing apply doesn't clear")
        state = ASMState()
        updates = UpdateSet()
        updates.add_update(Location("x"), 10)
        
        updates.apply_to(state)
        
        # UpdateSet still has the update
        assert len(updates) == 1
        assert updates.get(Location("x")) == 10
        logger.debug("UpdateSet not cleared after apply")


# ============================================================================
# Integration Tests
# ============================================================================

class TestUpdateIntegration:
    """Integration tests for update module."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_simulate_rule_execution(self):
        """Simulate collecting updates from rule execution."""
        logger.info("Testing rule execution simulation")
        state = ASMState()
        state.set_var("x", 0)
        state.set_var("y", 0)
        
        # "Rule" collects updates
        updates = UpdateSet()
        x_val = state.get_var("x")
        y_val = state.get_var("y")
        updates.add_update(Location("x"), x_val + 1)
        updates.add_update(Location("y"), y_val + 2)
        
        # Apply atomically
        updates.apply_to(state)
        
        assert state.get_var("x") == 1
        assert state.get_var("y") == 2
        logger.debug("Rule execution simulated")
    
    def test_simulate_nested_rules(self):
        """Simulate nested rule calls merging updates."""
        logger.info("Testing nested rules simulation")
        
        # Outer rule
        outer_updates = UpdateSet()
        outer_updates.add_update(Location("x"), 10)
        
        # Inner rule
        inner_updates = UpdateSet()
        inner_updates.add_update(Location("y"), 20)
        inner_updates.add_update(Location("z"), 30)
        
        # Merge inner into outer
        outer_updates.merge(inner_updates)
        
        # Apply all
        state = ASMState()
        outer_updates.apply_to(state)
        
        assert state.get_var("x") == 10
        assert state.get_var("y") == 20
        assert state.get_var("z") == 30
        logger.debug("Nested rules simulated")
    
    def test_simulate_step_sequence(self):
        """Simulate multiple steps with state snapshots."""
        logger.info("Testing step sequence simulation")
        state = ASMState()
        state.set_var("counter", 0)
        
        # Step 1
        updates1 = UpdateSet()
        updates1.add_update(Location("counter"), state.get_var("counter") + 1)
        updates1.apply_to(state)
        assert state.get_var("counter") == 1
        
        # Step 2
        updates2 = UpdateSet()
        updates2.add_update(Location("counter"), state.get_var("counter") + 1)
        updates2.apply_to(state)
        assert state.get_var("counter") == 2
        
        # Step 3
        updates3 = UpdateSet()
        updates3.add_update(Location("counter"), state.get_var("counter") + 1)
        updates3.apply_to(state)
        assert state.get_var("counter") == 3
        
        logger.debug("Step sequence simulated")
    
    def test_object_tracking_across_updates(self):
        """Track objects through multiple updates."""
        logger.info("Testing object tracking")
        state = ASMState()
        
        # Create objects and track in state
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        queue = ASMObject("Queue")
        
        # Step 1: Initialize
        updates1 = UpdateSet()
        updates1.add_update(Location("items", queue), [])
        updates1.add_update(Location("status", load1), "arriving")
        updates1.apply_to(state)
        
        # Step 2: Add to queue
        updates2 = UpdateSet()
        items = state.get_func("items", (queue,)).copy()
        items.append(load1)
        updates2.add_update(Location("items", queue), items)
        updates2.add_update(Location("status", load1), "waiting")
        updates2.apply_to(state)
        
        # Verify
        assert state.get_func("status", (load1,)) == "waiting"
        assert load1 in state.get_func("items", (queue,))
        logger.debug("Object tracking works")
