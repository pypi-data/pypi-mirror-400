"""
Tests for simasm/runtime/stdlib.py

Section 8: Standard library functions (lib.*)

Test categories:
1. List operations (add, pop, remove, get, length, sort, filter)
2. Selection operations (min_by, max_by)
3. Tuple access (first, second, third, last)
4. Set-like operations (set_add, set_contains, set_remove)
5. Rule operations (apply_rule)
6. Error handling
"""

import pytest
from dataclasses import dataclass
from typing import Any

from simasm.core.types import TypeRegistry, Domain
from simasm.core.state import ASMState, ASMObject, Location, UNDEF
from simasm.core.update import UpdateSet
from simasm.core.terms import (
    Environment, TermEvaluator,
    LiteralTerm, VariableTerm, LocationTerm,
    BinaryOpTerm,
)
from simasm.core.rules import (
    RuleDefinition, RuleRegistry, RuleEvaluator,
    UpdateStmt, SeqStmt, SkipStmt,
)
from simasm.runtime.stdlib import StandardLibrary, StdlibError


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def types():
    """Fresh TypeRegistry."""
    return TypeRegistry()


@pytest.fixture
def state():
    """Fresh ASMState."""
    return ASMState()


@pytest.fixture
def rules():
    """Fresh RuleRegistry."""
    return RuleRegistry()


@pytest.fixture
def stdlib(state, rules):
    """StandardLibrary instance."""
    return StandardLibrary(state, rules)


# Helper class for testing attribute-based operations
@dataclass(frozen=True)
class Event:
    """Test event with named attributes."""
    vertex: str
    time: float
    priority: int


@dataclass(frozen=True)
class Item:
    """Test item for filtering."""
    name: str
    value: int


# ============================================================================
# 1. List Operations
# ============================================================================

class TestListAdd:
    """Test lib.add (append to list)."""
    
    def test_add_to_empty_list(self, stdlib):
        """Add to empty list."""
        lst = []
        stdlib.add(lst, 1)
        assert lst == [1]
    
    def test_add_multiple(self, stdlib):
        """Add multiple items."""
        lst = []
        stdlib.add(lst, 1)
        stdlib.add(lst, 2)
        stdlib.add(lst, 3)
        assert lst == [1, 2, 3]
    
    def test_add_object(self, stdlib, types):
        """Add ASMObject."""
        types.register(Domain("Load"))
        load = ASMObject("Load")
        lst = []
        stdlib.add(lst, load)
        assert lst == [load]
    
    def test_add_non_list_error(self, stdlib):
        """Add to non-list raises error."""
        with pytest.raises(StdlibError, match="expected list"):
            stdlib.add("not a list", 1)


class TestListPop:
    """Test lib.pop (remove and return first)."""
    
    def test_pop_single(self, stdlib):
        """Pop from single-item list."""
        lst = [1]
        result = stdlib.pop(lst)
        assert result == 1
        assert lst == []
    
    def test_pop_multiple(self, stdlib):
        """Pop returns first, list shrinks."""
        lst = [1, 2, 3]
        result = stdlib.pop(lst)
        assert result == 1
        assert lst == [2, 3]
    
    def test_pop_fifo_order(self, stdlib):
        """Pop maintains FIFO order."""
        lst = ["a", "b", "c"]
        assert stdlib.pop(lst) == "a"
        assert stdlib.pop(lst) == "b"
        assert stdlib.pop(lst) == "c"
        assert lst == []
    
    def test_pop_empty_error(self, stdlib):
        """Pop from empty list raises error."""
        with pytest.raises(StdlibError, match="empty list"):
            stdlib.pop([])
    
    def test_pop_non_list_error(self, stdlib):
        """Pop from non-list raises error."""
        with pytest.raises(StdlibError, match="expected list"):
            stdlib.pop("not a list")


class TestListRemove:
    """Test lib.remove (remove first occurrence)."""
    
    def test_remove_found(self, stdlib):
        """Remove item that exists."""
        lst = [1, 2, 3]
        stdlib.remove(lst, 2)
        assert lst == [1, 3]
    
    def test_remove_first_occurrence(self, stdlib):
        """Remove only first occurrence."""
        lst = [1, 2, 2, 3]
        stdlib.remove(lst, 2)
        assert lst == [1, 2, 3]
    
    def test_remove_not_found_error(self, stdlib):
        """Remove non-existent item raises error."""
        lst = [1, 2, 3]
        with pytest.raises(StdlibError, match="not found"):
            stdlib.remove(lst, 99)
    
    def test_remove_non_list_error(self, stdlib):
        """Remove from non-list raises error."""
        with pytest.raises(StdlibError, match="expected list"):
            stdlib.remove("not a list", 1)


class TestListGet:
    """Test lib.get (access by index)."""
    
    def test_get_first(self, stdlib):
        """Get first element (index 0)."""
        lst = [10, 20, 30]
        assert stdlib.get(lst, 0) == 10
    
    def test_get_middle(self, stdlib):
        """Get middle element."""
        lst = [10, 20, 30]
        assert stdlib.get(lst, 1) == 20
    
    def test_get_last(self, stdlib):
        """Get last element."""
        lst = [10, 20, 30]
        assert stdlib.get(lst, 2) == 30
    
    def test_get_out_of_bounds_error(self, stdlib):
        """Get with invalid index raises error."""
        lst = [1, 2, 3]
        with pytest.raises(StdlibError, match="out of bounds"):
            stdlib.get(lst, 5)
    
    def test_get_negative_index_error(self, stdlib):
        """Get with negative index raises error."""
        lst = [1, 2, 3]
        with pytest.raises(StdlibError, match="out of bounds"):
            stdlib.get(lst, -1)
    
    def test_get_non_list_error(self, stdlib):
        """Get from non-list raises error."""
        with pytest.raises(StdlibError, match="expected list"):
            stdlib.get("not a list", 0)


class TestListLength:
    """Test lib.length."""
    
    def test_length_empty(self, stdlib):
        """Length of empty list."""
        assert stdlib.length([]) == 0
    
    def test_length_non_empty(self, stdlib):
        """Length of non-empty list."""
        assert stdlib.length([1, 2, 3]) == 3
    
    def test_length_non_list_error(self, stdlib):
        """Length of non-list raises error."""
        with pytest.raises(StdlibError, match="expected list"):
            stdlib.length("not a list")


class TestListSort:
    """Test lib.sort (sort by attribute name)."""
    
    def test_sort_by_attribute(self, stdlib):
        """Sort by named attribute."""
        events = [
            Event("A", 3.0, 1),
            Event("B", 1.0, 2),
            Event("C", 2.0, 3),
        ]
        stdlib.sort(events, "time")
        assert [e.vertex for e in events] == ["B", "C", "A"]
    
    def test_sort_by_priority(self, stdlib):
        """Sort by priority attribute."""
        events = [
            Event("A", 1.0, 3),
            Event("B", 2.0, 1),
            Event("C", 3.0, 2),
        ]
        stdlib.sort(events, "priority")
        assert [e.vertex for e in events] == ["B", "C", "A"]
    
    def test_sort_empty_list(self, stdlib):
        """Sort empty list (no-op)."""
        lst = []
        stdlib.sort(lst, "time")
        assert lst == []
    
    def test_sort_missing_attribute_error(self, stdlib):
        """Sort by non-existent attribute raises error."""
        events = [Event("A", 1.0, 1)]
        with pytest.raises(StdlibError, match="attribute.*not found"):
            stdlib.sort(events, "nonexistent")
    
    def test_sort_non_list_error(self, stdlib):
        """Sort non-list raises error."""
        with pytest.raises(StdlibError, match="expected list"):
            stdlib.sort("not a list", "time")


class TestListFilter:
    """Test lib.filter (filter by predicate function)."""
    
    def test_filter_all_pass(self, stdlib, state):
        """Filter where all items pass."""
        items = [Item("a", 1), Item("b", 2), Item("c", 3)]
        # Set up predicate in state
        for item in items:
            state.set_func("is_valid", (item,), True)
        
        result = stdlib.filter(items, "is_valid")
        assert len(result) == 3
    
    def test_filter_some_pass(self, stdlib, state):
        """Filter where some items pass."""
        items = [Item("a", 1), Item("b", 2), Item("c", 3)]
        state.set_func("is_valid", (items[0],), True)
        state.set_func("is_valid", (items[1],), False)
        state.set_func("is_valid", (items[2],), True)
        
        result = stdlib.filter(items, "is_valid")
        assert len(result) == 2
        assert items[0] in result
        assert items[2] in result
    
    def test_filter_none_pass(self, stdlib, state):
        """Filter where no items pass."""
        items = [Item("a", 1), Item("b", 2)]
        state.set_func("is_valid", (items[0],), False)
        state.set_func("is_valid", (items[1],), False)
        
        result = stdlib.filter(items, "is_valid")
        assert result == []
    
    def test_filter_returns_new_list(self, stdlib, state):
        """Filter returns new list, doesn't mutate original."""
        items = [Item("a", 1), Item("b", 2)]
        state.set_func("is_valid", (items[0],), True)
        state.set_func("is_valid", (items[1],), False)
        
        original_len = len(items)
        result = stdlib.filter(items, "is_valid")
        
        assert len(items) == original_len  # Original unchanged
        assert result is not items  # Different list object
    
    def test_filter_empty_list(self, stdlib, state):
        """Filter empty list returns empty list."""
        result = stdlib.filter([], "is_valid")
        assert result == []


# ============================================================================
# 2. Selection Operations
# ============================================================================

class TestMinBy:
    """Test lib.min_by."""
    
    def test_min_by_time(self, stdlib):
        """Find event with minimum time."""
        events = [
            Event("A", 3.0, 1),
            Event("B", 1.0, 2),
            Event("C", 2.0, 3),
        ]
        result = stdlib.min_by(events, "time")
        assert result.vertex == "B"
        assert result.time == 1.0
    
    def test_min_by_priority(self, stdlib):
        """Find item with minimum priority."""
        events = [
            Event("A", 1.0, 3),
            Event("B", 2.0, 1),
            Event("C", 3.0, 2),
        ]
        result = stdlib.min_by(events, "priority")
        assert result.vertex == "B"
    
    def test_min_by_single_item(self, stdlib):
        """Min of single-item list returns that item."""
        events = [Event("A", 1.0, 1)]
        result = stdlib.min_by(events, "time")
        assert result.vertex == "A"
    
    def test_min_by_empty_error(self, stdlib):
        """Min of empty list raises error."""
        with pytest.raises(StdlibError, match="empty list"):
            stdlib.min_by([], "time")
    
    def test_min_by_missing_attribute_error(self, stdlib):
        """Min by non-existent attribute raises error."""
        events = [Event("A", 1.0, 1)]
        with pytest.raises(StdlibError, match="attribute.*not found"):
            stdlib.min_by(events, "nonexistent")


class TestMaxBy:
    """Test lib.max_by."""
    
    def test_max_by_time(self, stdlib):
        """Find event with maximum time."""
        events = [
            Event("A", 3.0, 1),
            Event("B", 1.0, 2),
            Event("C", 2.0, 3),
        ]
        result = stdlib.max_by(events, "time")
        assert result.vertex == "A"
        assert result.time == 3.0
    
    def test_max_by_priority(self, stdlib):
        """Find item with maximum priority."""
        events = [
            Event("A", 1.0, 3),
            Event("B", 2.0, 1),
            Event("C", 3.0, 2),
        ]
        result = stdlib.max_by(events, "priority")
        assert result.vertex == "A"
    
    def test_max_by_empty_error(self, stdlib):
        """Max of empty list raises error."""
        with pytest.raises(StdlibError, match="empty list"):
            stdlib.max_by([], "time")


# ============================================================================
# 3. Tuple Access
# ============================================================================

class TestTupleAccess:
    """Test lib.first, lib.second, lib.third, lib.last."""
    
    def test_first_tuple(self, stdlib):
        """Get first element of tuple."""
        tup = ("vertex", 1.0, 5)
        assert stdlib.first(tup) == "vertex"
    
    def test_first_list(self, stdlib):
        """Get first element of list."""
        lst = [10, 20, 30]
        assert stdlib.first(lst) == 10
    
    def test_second_tuple(self, stdlib):
        """Get second element of tuple."""
        tup = ("vertex", 1.0, 5)
        assert stdlib.second(tup) == 1.0
    
    def test_third_tuple(self, stdlib):
        """Get third element of tuple."""
        tup = ("vertex", 1.0, 5)
        assert stdlib.third(tup) == 5
    
    def test_last_tuple(self, stdlib):
        """Get last element of tuple."""
        tup = ("a", "b", "c", "d")
        assert stdlib.last(tup) == "d"
    
    def test_last_single_element(self, stdlib):
        """Last of single-element tuple."""
        tup = (42,)
        assert stdlib.last(tup) == 42
    
    def test_first_empty_error(self, stdlib):
        """First of empty raises error."""
        with pytest.raises(StdlibError, match="empty"):
            stdlib.first(())
    
    def test_second_too_short_error(self, stdlib):
        """Second of single-element raises error."""
        with pytest.raises(StdlibError, match="only 1 elements"):
            stdlib.second((1,))
    
    def test_third_too_short_error(self, stdlib):
        """Third of two-element raises error."""
        with pytest.raises(StdlibError, match="only 2 elements"):
            stdlib.third((1, 2))
    
    def test_first_non_tuple_error(self, stdlib):
        """First of non-tuple/list raises error."""
        with pytest.raises(StdlibError, match="expected tuple/list"):
            stdlib.first("string")


# ============================================================================
# 4. Set-like Operations
# ============================================================================

class TestSetAdd:
    """Test lib.set_add (add if not present)."""
    
    def test_set_add_new(self, stdlib):
        """Add new item."""
        lst = [1, 2]
        stdlib.set_add(lst, 3)
        assert lst == [1, 2, 3]
    
    def test_set_add_duplicate(self, stdlib):
        """Add duplicate does nothing."""
        lst = [1, 2, 3]
        stdlib.set_add(lst, 2)
        assert lst == [1, 2, 3]  # Unchanged
    
    def test_set_add_to_empty(self, stdlib):
        """Add to empty list."""
        lst = []
        stdlib.set_add(lst, 1)
        assert lst == [1]


class TestSetContains:
    """Test lib.set_contains."""
    
    def test_contains_found(self, stdlib):
        """Item is in list."""
        lst = [1, 2, 3]
        assert stdlib.set_contains(lst, 2) is True
    
    def test_contains_not_found(self, stdlib):
        """Item not in list."""
        lst = [1, 2, 3]
        assert stdlib.set_contains(lst, 99) is False
    
    def test_contains_empty(self, stdlib):
        """Empty list contains nothing."""
        assert stdlib.set_contains([], 1) is False


class TestSetRemove:
    """Test lib.set_remove (remove if present, no error)."""
    
    def test_set_remove_found(self, stdlib):
        """Remove item that exists."""
        lst = [1, 2, 3]
        stdlib.set_remove(lst, 2)
        assert lst == [1, 3]
    
    def test_set_remove_not_found(self, stdlib):
        """Remove non-existent item (no error)."""
        lst = [1, 2, 3]
        stdlib.set_remove(lst, 99)  # Should not raise
        assert lst == [1, 2, 3]  # Unchanged
    
    def test_set_remove_from_empty(self, stdlib):
        """Remove from empty list (no error)."""
        lst = []
        stdlib.set_remove(lst, 1)  # Should not raise
        assert lst == []


# ============================================================================
# 5. Rule Operations
# ============================================================================

class TestApplyRule:
    """Test lib.apply_rule."""
    
    def test_apply_rule_no_args(self, state, rules, types):
        """Apply rule with no arguments."""
        stdlib = StandardLibrary(state, rules)
        
        # Register rule
        rule = RuleDefinition(
            "init",
            (),
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(42))
        )
        rules.register(rule)
        
        # Create evaluator and set it
        term_eval = TermEvaluator(state, types, stdlib)
        evaluator = RuleEvaluator(state, rules, term_eval)
        stdlib.set_evaluator(evaluator)
        
        # Apply rule
        stdlib.apply_rule("init", [])
        
        assert state.get_var("x") == 42
    
    def test_apply_rule_with_args(self, state, rules, types):
        """Apply rule with arguments."""
        stdlib = StandardLibrary(state, rules)
        types.register(Domain("Item"))
        item = ASMObject("Item")
        
        # Register rule: process(x) = done(x) := true
        rule = RuleDefinition(
            "process",
            ("x",),
            UpdateStmt(
                LocationTerm("done", (VariableTerm("x"),)),
                LiteralTerm(True)
            )
        )
        rules.register(rule)
        
        # Create evaluator
        term_eval = TermEvaluator(state, types, stdlib)
        evaluator = RuleEvaluator(state, rules, term_eval)
        stdlib.set_evaluator(evaluator)
        
        # Apply rule
        stdlib.apply_rule("process", [item])
        
        assert state.get_func("done", (item,)) is True
    
    def test_apply_rule_no_evaluator_error(self, stdlib):
        """Apply rule without evaluator set raises error."""
        with pytest.raises(StdlibError, match="evaluator not set"):
            stdlib.apply_rule("some_rule", [])
    
    def test_apply_rule_non_string_error(self, state, rules, types):
        """Apply rule with non-string name raises error."""
        stdlib = StandardLibrary(state, rules)
        term_eval = TermEvaluator(state, types, stdlib)
        evaluator = RuleEvaluator(state, rules, term_eval)
        stdlib.set_evaluator(evaluator)
        
        with pytest.raises(StdlibError, match="must be string"):
            stdlib.apply_rule(123, [])
    
    def test_apply_rule_non_list_params_error(self, state, rules, types):
        """Apply rule with non-list params raises error."""
        stdlib = StandardLibrary(state, rules)
        term_eval = TermEvaluator(state, types, stdlib)
        evaluator = RuleEvaluator(state, rules, term_eval)
        stdlib.set_evaluator(evaluator)
        
        with pytest.raises(StdlibError, match="params must be list"):
            stdlib.apply_rule("rule", "not a list")


# ============================================================================
# 6. Integration Tests
# ============================================================================

class TestStdlibIntegration:
    """Integration tests combining multiple stdlib functions."""
    
    def test_fel_operations(self, stdlib):
        """Simulate FEL operations for DES."""
        # FEL is list of events
        fel = []
        
        # Schedule events
        stdlib.add(fel, Event("arrive", 1.0, 1))
        stdlib.add(fel, Event("start", 3.0, 2))
        stdlib.add(fel, Event("depart", 2.0, 1))
        
        assert stdlib.length(fel) == 3
        
        # Get next event (min time)
        next_event = stdlib.min_by(fel, "time")
        assert next_event.vertex == "arrive"
        
        # Remove it
        stdlib.remove(fel, next_event)
        assert stdlib.length(fel) == 2
        
        # Get next
        next_event = stdlib.min_by(fel, "time")
        assert next_event.vertex == "depart"
    
    def test_queue_operations(self, stdlib, types):
        """Simulate queue operations."""
        types.register(Domain("Load"))
        
        queue = []
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        load3 = ASMObject("Load")
        
        # Enqueue
        stdlib.add(queue, load1)
        stdlib.add(queue, load2)
        stdlib.add(queue, load3)
        
        # Dequeue (FIFO)
        first = stdlib.pop(queue)
        assert first is load1
        
        second = stdlib.pop(queue)
        assert second is load2
        
        assert stdlib.length(queue) == 1
    
    def test_visited_set(self, stdlib, types):
        """Simulate visited set for graph traversal."""
        types.register(Domain("Node"))
        
        visited = []
        node1 = ASMObject("Node")
        node2 = ASMObject("Node")
        
        # Check and add
        assert not stdlib.set_contains(visited, node1)
        stdlib.set_add(visited, node1)
        assert stdlib.set_contains(visited, node1)
        
        # Add again (no duplicate)
        stdlib.set_add(visited, node1)
        assert stdlib.length(visited) == 1
        
        # Add another
        stdlib.set_add(visited, node2)
        assert stdlib.length(visited) == 2
    
    def test_tuple_event_handling(self, stdlib):
        """Handle events as tuples."""
        # Events as (vertex, time, priority) tuples
        event = ("arrive", 1.5, 3)
        
        vertex = stdlib.first(event)
        time = stdlib.second(event)
        priority = stdlib.third(event)
        
        assert vertex == "arrive"
        assert time == 1.5
        assert priority == 3
    
    def test_filter_enabled_edges(self, stdlib, state, types):
        """Filter edges by enabled predicate."""
        types.register(Domain("Edge"))
        
        edge1 = ASMObject("Edge")
        edge2 = ASMObject("Edge")
        edge3 = ASMObject("Edge")
        
        edges = [edge1, edge2, edge3]
        
        # Set enabled status
        state.set_func("enabled", (edge1,), True)
        state.set_func("enabled", (edge2,), False)
        state.set_func("enabled", (edge3,), True)
        
        # Filter
        enabled_edges = stdlib.filter(edges, "enabled")
        
        assert len(enabled_edges) == 2
        assert edge1 in enabled_edges
        assert edge2 not in enabled_edges
        assert edge3 in enabled_edges
