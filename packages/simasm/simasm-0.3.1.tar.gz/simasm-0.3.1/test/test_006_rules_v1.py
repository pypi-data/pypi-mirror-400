"""
Tests for simasm/core/rules.py

Section 7: Statement AST, RuleDefinition, RuleRegistry, RuleEvaluator

Test categories:
1. Statement AST nodes (frozen, repr)
2. RuleDefinition
3. RuleRegistry
4. RuleEvaluator - SkipStmt
5. RuleEvaluator - UpdateStmt
6. RuleEvaluator - SeqStmt (sequential semantics)
7. RuleEvaluator - IfStmt (with elseif, nested)
8. RuleEvaluator - WhileStmt (sequential, max iterations)
9. RuleEvaluator - ForallStmt (parallel semantics, conflicts)
10. RuleEvaluator - LetStmt
11. RuleEvaluator - RuleCallStmt (static, dynamic, recursion)
12. RuleEvaluator - PrintStmt
13. Integration tests
"""

import pytest
from typing import List, Any

from simasm.core.types import TypeRegistry, Domain
from simasm.core.state import ASMState, ASMObject, Location, UNDEF
from simasm.core.update import UpdateSet, UpdateConflictError
from simasm.core.terms import (
    Environment, TermEvaluator,
    LiteralTerm, VariableTerm, LocationTerm,
    BinaryOpTerm, UnaryOpTerm, ListTerm, NewTerm,
    LibCallTerm, ConditionalTerm,
)
from simasm.core.rules import (
    Stmt, SkipStmt, UpdateStmt, SeqStmt, IfStmt,
    WhileStmt, ForallStmt, LetStmt, RuleCallStmt, PrintStmt,
    RuleDefinition, RuleRegistry,
    RuleEvaluator, RuleEvaluatorConfig,
    RuleEvaluationError, InfiniteLoopError, MaxRecursionError,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def types():
    """Fresh TypeRegistry for each test."""
    return TypeRegistry()


@pytest.fixture
def state():
    """Fresh ASMState for each test."""
    return ASMState()


@pytest.fixture
def rules():
    """Fresh RuleRegistry for each test."""
    return RuleRegistry()


@pytest.fixture
def stdlib():
    """Minimal stdlib for tests."""
    from types import SimpleNamespace
    
    lib = SimpleNamespace()
    lib.length = lambda lst: len(lst)
    lib.get = lambda lst, idx: lst[idx]
    lib.append = lambda lst, item: lst + [item]
    
    return lib


@pytest.fixture
def term_eval(state, types, stdlib):
    """TermEvaluator for each test."""
    return TermEvaluator(state, types, stdlib)


@pytest.fixture
def evaluator(state, rules, term_eval):
    """RuleEvaluator for each test."""
    return RuleEvaluator(state, rules, term_eval)


@pytest.fixture
def env():
    """Fresh Environment for each test."""
    return Environment()


# ============================================================================
# 1. Statement AST Nodes
# ============================================================================

class TestStatementASTNodes:
    """Test Statement AST node creation and properties."""
    
    def test_skip_stmt_creation(self):
        """SkipStmt can be created."""
        stmt = SkipStmt()
        assert isinstance(stmt, Stmt)
        assert isinstance(stmt, SkipStmt)
    
    def test_skip_stmt_frozen(self):
        """SkipStmt is immutable."""
        stmt = SkipStmt()
        # SkipStmt has no fields, but is frozen
        assert hash(stmt) is not None
    
    def test_update_stmt_creation(self):
        """UpdateStmt stores location and value."""
        loc = LocationTerm("x", ())
        val = LiteralTerm(10)
        stmt = UpdateStmt(loc, val)
        assert stmt.location is loc
        assert stmt.value is val
    
    def test_update_stmt_frozen(self):
        """UpdateStmt is immutable."""
        stmt = UpdateStmt(LocationTerm("x", ()), LiteralTerm(10))
        with pytest.raises(AttributeError):
            stmt.value = LiteralTerm(20)
    
    def test_update_stmt_repr(self):
        """UpdateStmt has readable repr."""
        stmt = UpdateStmt(LocationTerm("x", ()), LiteralTerm(10))
        r = repr(stmt)
        assert "UpdateStmt" in r
        assert ":=" in r
    
    def test_seq_stmt_creation(self):
        """SeqStmt holds tuple of statements."""
        s1 = SkipStmt()
        s2 = SkipStmt()
        seq = SeqStmt((s1, s2))
        assert len(seq.statements) == 2
        assert seq.statements[0] is s1
        assert seq.statements[1] is s2
    
    def test_seq_stmt_repr(self):
        """SeqStmt repr shows count."""
        seq = SeqStmt((SkipStmt(), SkipStmt(), SkipStmt()))
        assert "3 statements" in repr(seq)
    
    def test_if_stmt_simple(self):
        """IfStmt with just condition and then body."""
        cond = LiteralTerm(True)
        body = SkipStmt()
        stmt = IfStmt(cond, body)
        assert stmt.condition is cond
        assert stmt.then_body is body
        assert stmt.elseif_branches == ()
        assert stmt.else_body is None
    
    def test_if_stmt_with_else(self):
        """IfStmt with else branch."""
        stmt = IfStmt(
            condition=LiteralTerm(True),
            then_body=SkipStmt(),
            else_body=SkipStmt()
        )
        assert stmt.else_body is not None
    
    def test_if_stmt_with_elseif(self):
        """IfStmt with multiple elseif branches."""
        stmt = IfStmt(
            condition=LiteralTerm(False),
            then_body=SkipStmt(),
            elseif_branches=(
                (LiteralTerm(False), SkipStmt()),
                (LiteralTerm(True), SkipStmt()),
            ),
            else_body=SkipStmt()
        )
        assert len(stmt.elseif_branches) == 2
    
    def test_if_stmt_repr(self):
        """IfStmt repr shows structure."""
        stmt = IfStmt(
            LiteralTerm(True),
            SkipStmt(),
            elseif_branches=((LiteralTerm(True), SkipStmt()),),
            else_body=SkipStmt()
        )
        r = repr(stmt)
        assert "IfStmt" in r
        assert "elseif" in r
        assert "else" in r
    
    def test_while_stmt_creation(self):
        """WhileStmt stores condition and body."""
        cond = LiteralTerm(True)
        body = SkipStmt()
        stmt = WhileStmt(cond, body)
        assert stmt.condition is cond
        assert stmt.body is body
    
    def test_forall_stmt_creation(self):
        """ForallStmt stores var, collection, body."""
        stmt = ForallStmt("x", ListTerm((LiteralTerm(1),)), SkipStmt())
        assert stmt.var_name == "x"
        assert isinstance(stmt.collection, ListTerm)
        assert isinstance(stmt.body, SkipStmt)
    
    def test_let_stmt_creation(self):
        """LetStmt stores var and value."""
        stmt = LetStmt("x", LiteralTerm(10))
        assert stmt.var_name == "x"
        assert isinstance(stmt.value, LiteralTerm)
    
    def test_rule_call_stmt_creation(self):
        """RuleCallStmt stores name and args."""
        stmt = RuleCallStmt(VariableTerm("my_rule"), (LiteralTerm(1), LiteralTerm(2)))
        assert isinstance(stmt.rule_name, VariableTerm)
        assert len(stmt.arguments) == 2
    
    def test_rule_call_stmt_no_args(self):
        """RuleCallStmt can have no arguments."""
        stmt = RuleCallStmt(VariableTerm("init"))
        assert stmt.arguments == ()
    
    def test_print_stmt_creation(self):
        """PrintStmt stores expression."""
        stmt = PrintStmt(LiteralTerm("hello"))
        assert isinstance(stmt.expression, LiteralTerm)


# ============================================================================
# 2. RuleDefinition
# ============================================================================

class TestRuleDefinition:
    """Test RuleDefinition creation and properties."""
    
    def test_rule_definition_simple(self):
        """RuleDefinition with name only."""
        rule = RuleDefinition("init")
        assert rule.name == "init"
        assert rule.parameters == ()
        assert rule.body is None
    
    def test_rule_definition_with_params(self):
        """RuleDefinition with parameters."""
        rule = RuleDefinition("arrive", ("load", "time"))
        assert rule.name == "arrive"
        assert rule.parameters == ("load", "time")
    
    def test_rule_definition_with_body(self):
        """RuleDefinition with body."""
        body = UpdateStmt(LocationTerm("x", ()), LiteralTerm(10))
        rule = RuleDefinition("set_x", (), body)
        assert rule.body is body
    
    def test_rule_definition_repr(self):
        """RuleDefinition has readable repr."""
        rule = RuleDefinition("process", ("item",), SkipStmt())
        r = repr(rule)
        assert "RuleDefinition" in r
        assert "process" in r
        assert "item" in r
        assert "with body" in r
    
    def test_rule_definition_str(self):
        """RuleDefinition has readable str."""
        rule = RuleDefinition("process", ("item",))
        s = str(rule)
        assert "rule process(item)" in s


# ============================================================================
# 3. RuleRegistry
# ============================================================================

class TestRuleRegistry:
    """Test RuleRegistry operations."""
    
    def test_registry_empty(self):
        """New registry is empty."""
        reg = RuleRegistry()
        assert len(reg) == 0
        assert reg.all_rules() == []
    
    def test_registry_register(self):
        """Can register rules."""
        reg = RuleRegistry()
        rule = RuleDefinition("init")
        reg.register(rule)
        assert len(reg) == 1
        assert "init" in reg
    
    def test_registry_get(self):
        """Can get registered rule."""
        reg = RuleRegistry()
        rule = RuleDefinition("init")
        reg.register(rule)
        assert reg.get("init") is rule
    
    def test_registry_get_missing(self):
        """Get returns None for missing rule."""
        reg = RuleRegistry()
        assert reg.get("missing") is None
    
    def test_registry_exists(self):
        """Exists checks rule presence."""
        reg = RuleRegistry()
        reg.register(RuleDefinition("init"))
        assert reg.exists("init") is True
        assert reg.exists("missing") is False
    
    def test_registry_contains(self):
        """Contains operator works."""
        reg = RuleRegistry()
        reg.register(RuleDefinition("init"))
        assert "init" in reg
        assert "missing" not in reg
    
    def test_registry_all_rules(self):
        """all_rules returns all names."""
        reg = RuleRegistry()
        reg.register(RuleDefinition("a"))
        reg.register(RuleDefinition("b"))
        reg.register(RuleDefinition("c"))
        names = reg.all_rules()
        assert set(names) == {"a", "b", "c"}
    
    def test_registry_duplicate_error(self):
        """Cannot register duplicate rule name."""
        reg = RuleRegistry()
        reg.register(RuleDefinition("init"))
        with pytest.raises(ValueError, match="already registered"):
            reg.register(RuleDefinition("init"))
    
    def test_registry_clear(self):
        """Clear removes all rules."""
        reg = RuleRegistry()
        reg.register(RuleDefinition("a"))
        reg.register(RuleDefinition("b"))
        reg.clear()
        assert len(reg) == 0
        assert "a" not in reg


# ============================================================================
# 4. RuleEvaluator - SkipStmt
# ============================================================================

class TestEvalSkip:
    """Test SkipStmt evaluation."""
    
    def test_skip_returns_empty_updates(self, evaluator, env):
        """Skip produces no updates."""
        updates = evaluator.eval(SkipStmt(), env)
        assert len(updates) == 0
    
    def test_skip_does_not_modify_state(self, evaluator, env, state):
        """Skip does not change state."""
        state.set_var("x", 10)
        evaluator.eval(SkipStmt(), env)
        assert state.get_var("x") == 10


# ============================================================================
# 5. RuleEvaluator - UpdateStmt
# ============================================================================

class TestEvalUpdate:
    """Test UpdateStmt evaluation."""
    
    def test_update_variable(self, evaluator, env, state):
        """Update 0-ary location (variable)."""
        stmt = UpdateStmt(LocationTerm("x", ()), LiteralTerm(42))
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 1
        # Check update content
        update = list(updates)[0]
        assert update.location == Location("x")
        assert update.value == 42
    
    def test_update_function(self, evaluator, env, state, types):
        """Update n-ary location (function)."""
        types.register(Domain("Load"))
        load = ASMObject("Load")
        env.bind("load", load)
        
        stmt = UpdateStmt(
            LocationTerm("status", (VariableTerm("load"),)),
            LiteralTerm("waiting")
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 1
        update = list(updates)[0]
        assert update.location == Location("status", (load,))
        assert update.value == "waiting"
    
    def test_update_with_expression(self, evaluator, env, state):
        """Update with computed value."""
        state.set_var("y", 10)
        stmt = UpdateStmt(
            LocationTerm("x", ()),
            BinaryOpTerm("+", LocationTerm("y", ()), LiteralTerm(5))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 15
    
    def test_update_does_not_apply(self, evaluator, env, state):
        """UpdateStmt returns updates but does not apply them."""
        stmt = UpdateStmt(LocationTerm("x", ()), LiteralTerm(42))
        updates = evaluator.eval(stmt, env)
        
        # State should not have x yet
        assert state.get_var("x") is UNDEF
        
        # Apply manually
        updates.apply_to(state)
        assert state.get_var("x") == 42


# ============================================================================
# 6. RuleEvaluator - SeqStmt (sequential semantics)
# ============================================================================

class TestEvalSeq:
    """Test SeqStmt with sequential semantics."""
    
    def test_seq_empty(self, evaluator, env):
        """Empty sequence produces no updates."""
        stmt = SeqStmt(())
        updates = evaluator.eval(stmt, env)
        assert len(updates) == 0
    
    def test_seq_single(self, evaluator, env, state):
        """Sequence with single statement."""
        stmt = SeqStmt((
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(10)),
        ))
        updates = evaluator.eval(stmt, env)
        
        # Should be applied to state
        assert state.get_var("x") == 10
    
    def test_seq_multiple(self, evaluator, env, state):
        """Sequence with multiple statements."""
        stmt = SeqStmt((
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            UpdateStmt(LocationTerm("y", ()), LiteralTerm(2)),
            UpdateStmt(LocationTerm("z", ()), LiteralTerm(3)),
        ))
        evaluator.eval(stmt, env)
        
        assert state.get_var("x") == 1
        assert state.get_var("y") == 2
        assert state.get_var("z") == 3
    
    def test_seq_sequential_semantics(self, evaluator, env, state):
        """Later statements see effects of earlier ones."""
        # x := 10
        # y := x + 5  (should see x = 10)
        stmt = SeqStmt((
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(10)),
            UpdateStmt(
                LocationTerm("y", ()),
                BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(5))
            ),
        ))
        evaluator.eval(stmt, env)
        
        assert state.get_var("x") == 10
        assert state.get_var("y") == 15  # Saw x = 10
    
    def test_seq_chained_updates(self, evaluator, env, state):
        """Chained updates in sequence."""
        # x := 1
        # x := x + 1
        # x := x + 1
        stmt = SeqStmt((
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            UpdateStmt(
                LocationTerm("x", ()),
                BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(1))
            ),
            UpdateStmt(
                LocationTerm("x", ()),
                BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(1))
            ),
        ))
        evaluator.eval(stmt, env)
        
        assert state.get_var("x") == 3
    
    def test_seq_with_skip(self, evaluator, env, state):
        """Sequence can contain skip statements."""
        stmt = SeqStmt((
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            SkipStmt(),
            UpdateStmt(LocationTerm("y", ()), LiteralTerm(2)),
        ))
        evaluator.eval(stmt, env)
        
        assert state.get_var("x") == 1
        assert state.get_var("y") == 2


# ============================================================================
# 7. RuleEvaluator - IfStmt
# ============================================================================

class TestEvalIf:
    """Test IfStmt evaluation."""
    
    def test_if_true(self, evaluator, env, state):
        """If condition true, execute then body."""
        stmt = IfStmt(
            condition=LiteralTerm(True),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1))
        )
        evaluator.eval(stmt, env)
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 1
    
    def test_if_false_no_else(self, evaluator, env):
        """If condition false, no else: no updates."""
        stmt = IfStmt(
            condition=LiteralTerm(False),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1))
        )
        updates = evaluator.eval(stmt, env)
        assert len(updates) == 0
    
    def test_if_false_with_else(self, evaluator, env):
        """If condition false, execute else body."""
        stmt = IfStmt(
            condition=LiteralTerm(False),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(2))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 2
    
    def test_if_elseif_first_true(self, evaluator, env):
        """First elseif true is executed."""
        stmt = IfStmt(
            condition=LiteralTerm(False),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            elseif_branches=(
                (LiteralTerm(True), UpdateStmt(LocationTerm("x", ()), LiteralTerm(2))),
                (LiteralTerm(True), UpdateStmt(LocationTerm("x", ()), LiteralTerm(3))),
            ),
            else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(4))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 2  # First elseif
    
    def test_if_elseif_second_true(self, evaluator, env):
        """Second elseif true is executed."""
        stmt = IfStmt(
            condition=LiteralTerm(False),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            elseif_branches=(
                (LiteralTerm(False), UpdateStmt(LocationTerm("x", ()), LiteralTerm(2))),
                (LiteralTerm(True), UpdateStmt(LocationTerm("x", ()), LiteralTerm(3))),
            ),
            else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(4))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 3  # Second elseif
    
    def test_if_all_false_else(self, evaluator, env):
        """All conditions false, execute else."""
        stmt = IfStmt(
            condition=LiteralTerm(False),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            elseif_branches=(
                (LiteralTerm(False), UpdateStmt(LocationTerm("x", ()), LiteralTerm(2))),
                (LiteralTerm(False), UpdateStmt(LocationTerm("x", ()), LiteralTerm(3))),
            ),
            else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(4))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 4  # Else
    
    def test_if_condition_evaluated(self, evaluator, env, state):
        """Condition is evaluated from state."""
        state.set_var("flag", True)
        stmt = IfStmt(
            condition=LocationTerm("flag", ()),
            then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
            else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(2))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 1
    
    def test_if_nested(self, evaluator, env, state):
        """Nested if statements."""
        state.set_var("a", True)
        state.set_var("b", False)
        
        # if a then (if b then x:=1 else x:=2) else x:=3
        stmt = IfStmt(
            condition=LocationTerm("a", ()),
            then_body=IfStmt(
                condition=LocationTerm("b", ()),
                then_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)),
                else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(2))
            ),
            else_body=UpdateStmt(LocationTerm("x", ()), LiteralTerm(3))
        )
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.value == 2  # a=True, b=False -> inner else


# ============================================================================
# 8. RuleEvaluator - WhileStmt
# ============================================================================

class TestEvalWhile:
    """Test WhileStmt with sequential semantics."""
    
    def test_while_zero_iterations(self, evaluator, env, state):
        """While with false condition executes zero times."""
        state.set_var("x", 0)
        stmt = WhileStmt(
            condition=LiteralTerm(False),
            body=UpdateStmt(
                LocationTerm("x", ()),
                BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(1))
            )
        )
        evaluator.eval(stmt, env)
        
        assert state.get_var("x") == 0
    
    def test_while_one_iteration(self, evaluator, env, state):
        """While with condition becoming false after one iteration."""
        state.set_var("flag", True)
        stmt = WhileStmt(
            condition=LocationTerm("flag", ()),
            body=UpdateStmt(LocationTerm("flag", ()), LiteralTerm(False))
        )
        evaluator.eval(stmt, env)
        
        assert state.get_var("flag") is False
    
    def test_while_multiple_iterations(self, evaluator, env, state):
        """While counting down."""
        state.set_var("i", 5)
        state.set_var("sum", 0)
        
        # while i > 0 do sum := sum + i; i := i - 1
        stmt = WhileStmt(
            condition=BinaryOpTerm(">", LocationTerm("i", ()), LiteralTerm(0)),
            body=SeqStmt((
                UpdateStmt(
                    LocationTerm("sum", ()),
                    BinaryOpTerm("+", LocationTerm("sum", ()), LocationTerm("i", ()))
                ),
                UpdateStmt(
                    LocationTerm("i", ()),
                    BinaryOpTerm("-", LocationTerm("i", ()), LiteralTerm(1))
                ),
            ))
        )
        evaluator.eval(stmt, env)
        
        assert state.get_var("i") == 0
        assert state.get_var("sum") == 15  # 5+4+3+2+1
    
    def test_while_sequential_semantics(self, evaluator, env, state):
        """Each iteration sees previous iteration's updates."""
        state.set_var("x", 1)
        
        # while x < 10 do x := x * 2
        stmt = WhileStmt(
            condition=BinaryOpTerm("<", LocationTerm("x", ()), LiteralTerm(10)),
            body=UpdateStmt(
                LocationTerm("x", ()),
                BinaryOpTerm("*", LocationTerm("x", ()), LiteralTerm(2))
            )
        )
        evaluator.eval(stmt, env)
        
        # 1 -> 2 -> 4 -> 8 -> 16 (stops because 16 >= 10)
        assert state.get_var("x") == 16
    
    def test_while_max_iterations_exceeded(self, state, rules, term_eval):
        """Infinite loop raises InfiniteLoopError."""
        config = RuleEvaluatorConfig(max_while_iterations=10)
        evaluator = RuleEvaluator(state, rules, term_eval, config)
        
        stmt = WhileStmt(
            condition=LiteralTerm(True),
            body=SkipStmt()
        )
        
        with pytest.raises(InfiniteLoopError) as exc_info:
            evaluator.eval(stmt, Environment())
        
        assert exc_info.value.iterations == 11
        assert exc_info.value.max_iterations == 10
    
    def test_while_with_let(self, evaluator, env, state):
        """Let binding persists across iterations."""
        state.set_var("items", [1, 2, 3, 4, 5])
        state.set_var("sum", 0)
        
        # let i = 0
        # while i < length(items) do
        #     sum := sum + get(items, i)
        #     i := i + 1
        stmt = SeqStmt((
            LetStmt("i", LiteralTerm(0)),
            WhileStmt(
                condition=BinaryOpTerm(
                    "<",
                    VariableTerm("i"),
                    LibCallTerm("length", (LocationTerm("items", ()),))
                ),
                body=SeqStmt((
                    UpdateStmt(
                        LocationTerm("sum", ()),
                        BinaryOpTerm(
                            "+",
                            LocationTerm("sum", ()),
                            LibCallTerm("get", (LocationTerm("items", ()), VariableTerm("i")))
                        )
                    ),
                    LetStmt("i", BinaryOpTerm("+", VariableTerm("i"), LiteralTerm(1))),
                ))
            ),
        ))
        evaluator.eval(stmt, env)
        
        assert state.get_var("sum") == 15


# ============================================================================
# 9. RuleEvaluator - ForallStmt
# ============================================================================

class TestEvalForall:
    """Test ForallStmt with parallel semantics."""
    
    def test_forall_empty_collection(self, evaluator, env, state):
        """Forall over empty collection produces no updates."""
        state.set_var("items", [])
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("y", ()), VariableTerm("x"))
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 0
    
    def test_forall_single_item(self, evaluator, env, state, types):
        """Forall over single item."""
        types.register(Domain("Item"))
        item = ASMObject("Item")
        state.set_var("items", [item])
        
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("processed", (VariableTerm("x"),)), LiteralTerm(True))
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 1
        update = list(updates)[0]
        assert update.location == Location("processed", (item,))
        assert update.value is True
    
    def test_forall_multiple_items_different_locations(self, evaluator, env, state, types):
        """Forall updating different locations (no conflict)."""
        types.register(Domain("Item"))
        item1 = ASMObject("Item")
        item2 = ASMObject("Item")
        item3 = ASMObject("Item")
        state.set_var("items", [item1, item2, item3])
        
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("done", (VariableTerm("x"),)), LiteralTerm(True))
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 3
        # All items should have done(item) := True
        updates.apply_to(state)
        assert state.get_func("done", (item1,)) is True
        assert state.get_func("done", (item2,)) is True
        assert state.get_func("done", (item3,)) is True
    
    def test_forall_parallel_semantics(self, evaluator, env, state):
        """All iterations see original state, not each other's updates."""
        state.set_var("counter", 0)
        state.set_var("items", [1, 2, 3])
        
        # forall x in items do
        #     result(x) := counter  // All should see counter = 0
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(
                LocationTerm("result", (VariableTerm("x"),)),
                LocationTerm("counter", ())
            )
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        # All iterations saw counter = 0
        assert state.get_func("result", (1,)) == 0
        assert state.get_func("result", (2,)) == 0
        assert state.get_func("result", (3,)) == 0
    
    def test_forall_conflict_same_location_different_values(self, evaluator, env, state):
        """Forall conflict when same location gets different values."""
        state.set_var("items", [1, 2, 3])
        
        # forall x in items do
        #     shared := x  // Conflict! Different values
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("shared", ()), VariableTerm("x"))
        )
        
        with pytest.raises(RuleEvaluationError, match="conflicting"):
            evaluator.eval(stmt, env)
    
    def test_forall_no_conflict_same_value(self, evaluator, env, state):
        """Forall no conflict when same location gets same value."""
        state.set_var("items", [1, 2, 3])
        
        # forall x in items do
        #     shared := 42  // Same value, no conflict
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("shared", ()), LiteralTerm(42))
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 1
        update = list(updates)[0]
        assert update.value == 42
    
    def test_forall_with_list_literal(self, evaluator, env):
        """Forall over inline list."""
        stmt = ForallStmt(
            "x",
            ListTerm((LiteralTerm(1), LiteralTerm(2), LiteralTerm(3))),
            UpdateStmt(LocationTerm("done", (VariableTerm("x"),)), LiteralTerm(True))
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 3
    
    def test_forall_non_list_error(self, evaluator, env, state):
        """Forall over non-list raises error."""
        state.set_var("items", 42)  # Not a list!
        
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            SkipStmt()
        )
        
        with pytest.raises(RuleEvaluationError, match="list or tuple"):
            evaluator.eval(stmt, env)
    
    def test_forall_with_guard_all_pass(self, evaluator, env, state):
        """Forall with guard where all items pass."""
        state.set_var("items", [1, 2, 3])
        
        # forall x in items with x > 0 do result(x) := true
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("result", (VariableTerm("x"),)), LiteralTerm(True)),
            guard=BinaryOpTerm(">", VariableTerm("x"), LiteralTerm(0))
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        assert state.get_func("result", (1,)) is True
        assert state.get_func("result", (2,)) is True
        assert state.get_func("result", (3,)) is True
    
    def test_forall_with_guard_some_pass(self, evaluator, env, state):
        """Forall with guard where some items pass."""
        state.set_var("items", [1, 2, 3, 4, 5])
        
        # forall x in items with x > 3 do result(x) := true
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("result", (VariableTerm("x"),)), LiteralTerm(True)),
            guard=BinaryOpTerm(">", VariableTerm("x"), LiteralTerm(3))
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        # Only 4 and 5 pass the guard
        assert len(updates) == 2
        assert state.get_func("result", (4,)) is True
        assert state.get_func("result", (5,)) is True
        assert state.get_func("result", (1,)) is UNDEF
        assert state.get_func("result", (2,)) is UNDEF
        assert state.get_func("result", (3,)) is UNDEF
    
    def test_forall_with_guard_none_pass(self, evaluator, env, state):
        """Forall with guard where no items pass."""
        state.set_var("items", [1, 2, 3])
        
        # forall x in items with x > 10 do result(x) := true
        stmt = ForallStmt(
            "x",
            LocationTerm("items", ()),
            UpdateStmt(LocationTerm("result", (VariableTerm("x"),)), LiteralTerm(True)),
            guard=BinaryOpTerm(">", VariableTerm("x"), LiteralTerm(10))
        )
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 0
    
    def test_forall_with_guard_complex_condition(self, evaluator, env, state, types):
        """Forall with complex guard using state lookup."""
        types.register(Domain("Edge"))
        
        edge1 = ASMObject("Edge")
        edge2 = ASMObject("Edge")
        edge3 = ASMObject("Edge")
        
        # Set up edge_enabled function
        state.set_func("enabled", (edge1,), True)
        state.set_func("enabled", (edge2,), False)
        state.set_func("enabled", (edge3,), True)
        state.set_var("edges", [edge1, edge2, edge3])
        
        # forall e in edges with enabled(e) do scheduled(e) := true
        stmt = ForallStmt(
            "e",
            LocationTerm("edges", ()),
            UpdateStmt(LocationTerm("scheduled", (VariableTerm("e"),)), LiteralTerm(True)),
            guard=LocationTerm("enabled", (VariableTerm("e"),))
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        # Only edge1 and edge3 should be scheduled
        assert state.get_func("scheduled", (edge1,)) is True
        assert state.get_func("scheduled", (edge2,)) is UNDEF
        assert state.get_func("scheduled", (edge3,)) is True
    
    def test_forall_guard_sees_loop_variable(self, evaluator, env, state):
        """Guard can access the loop variable."""
        state.set_var("items", [(1, True), (2, False), (3, True)])
        
        # Tuples: (value, is_enabled)
        # forall item in items with lib.second(item) do ...
        # We'll simulate this with a simpler pattern since we don't have lib.second yet
        state.set_var("values", [1, 2, 3, 4])
        state.set_var("threshold", 2)
        
        # forall x in values with x >= threshold do result(x) := x * 2
        stmt = ForallStmt(
            "x",
            LocationTerm("values", ()),
            UpdateStmt(
                LocationTerm("result", (VariableTerm("x"),)),
                BinaryOpTerm("*", VariableTerm("x"), LiteralTerm(2))
            ),
            guard=BinaryOpTerm(">=", VariableTerm("x"), LocationTerm("threshold", ()))
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        assert state.get_func("result", (1,)) is UNDEF  # 1 < 2
        assert state.get_func("result", (2,)) == 4      # 2 >= 2
        assert state.get_func("result", (3,)) == 6      # 3 >= 2
        assert state.get_func("result", (4,)) == 8      # 4 >= 2


# ============================================================================
# 10. RuleEvaluator - LetStmt
# ============================================================================

class TestEvalLet:
    """Test LetStmt evaluation."""
    
    def test_let_binds_variable(self, evaluator, env):
        """Let binds variable in environment."""
        stmt = LetStmt("x", LiteralTerm(42))
        evaluator.eval(stmt, env)
        
        assert env.lookup("x") == 42
    
    def test_let_returns_empty_updates(self, evaluator, env):
        """Let produces no updates."""
        stmt = LetStmt("x", LiteralTerm(42))
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 0
    
    def test_let_with_expression(self, evaluator, env, state):
        """Let with computed value."""
        state.set_var("y", 10)
        stmt = LetStmt("x", BinaryOpTerm("+", LocationTerm("y", ()), LiteralTerm(5)))
        evaluator.eval(stmt, env)
        
        assert env.lookup("x") == 15
    
    def test_let_scope_in_sequence(self, evaluator, env, state):
        """Let binding visible to later statements in sequence."""
        stmt = SeqStmt((
            LetStmt("x", LiteralTerm(42)),
            UpdateStmt(LocationTerm("result", ()), VariableTerm("x")),
        ))
        evaluator.eval(stmt, env)
        
        assert state.get_var("result") == 42
    
    def test_let_shadowing(self, evaluator, env):
        """Later let can shadow earlier binding."""
        stmt = SeqStmt((
            LetStmt("x", LiteralTerm(1)),
            LetStmt("x", LiteralTerm(2)),  # Shadows
        ))
        evaluator.eval(stmt, env)
        
        assert env.lookup("x") == 2
    
    def test_let_with_new(self, evaluator, env, types):
        """Let binding new object."""
        types.register(Domain("Load"))
        stmt = LetStmt("load", NewTerm("Load"))
        evaluator.eval(stmt, env)
        
        load = env.lookup("load")
        assert isinstance(load, ASMObject)
        assert load.domain == "Load"


# ============================================================================
# 11. RuleEvaluator - RuleCallStmt
# ============================================================================

class TestEvalRuleCall:
    """Test RuleCallStmt evaluation."""
    
    def test_call_rule_no_args(self, evaluator, env, state, rules):
        """Call rule with no arguments."""
        rule = RuleDefinition(
            "init",
            (),
            UpdateStmt(LocationTerm("x", ()), LiteralTerm(42))
        )
        rules.register(rule)
        
        stmt = RuleCallStmt(VariableTerm("init"))
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 1
        assert list(updates)[0].value == 42
    
    def test_call_rule_with_args(self, evaluator, env, state, rules, types):
        """Call rule with arguments."""
        types.register(Domain("Item"))
        item = ASMObject("Item")
        
        rule = RuleDefinition(
            "process",
            ("x",),
            UpdateStmt(LocationTerm("done", (VariableTerm("x"),)), LiteralTerm(True))
        )
        rules.register(rule)
        
        env.bind("item", item)
        stmt = RuleCallStmt(VariableTerm("process"), (VariableTerm("item"),))
        updates = evaluator.eval(stmt, env)
        
        update = list(updates)[0]
        assert update.location == Location("done", (item,))
    
    def test_call_rule_wrong_arity(self, evaluator, env, rules):
        """Call rule with wrong number of arguments."""
        rule = RuleDefinition("process", ("x", "y"), SkipStmt())
        rules.register(rule)
        
        stmt = RuleCallStmt(VariableTerm("process"), (LiteralTerm(1),))  # Missing arg
        
        with pytest.raises(RuleEvaluationError, match="expects 2 arguments"):
            evaluator.eval(stmt, env)
    
    def test_call_unknown_rule(self, evaluator, env):
        """Call unknown rule raises error."""
        stmt = RuleCallStmt(VariableTerm("unknown"))
        
        with pytest.raises(RuleEvaluationError, match="Unknown rule"):
            evaluator.eval(stmt, env)
    
    def test_call_rule_dynamic_dispatch(self, evaluator, env, state, rules):
        """Dynamic dispatch: rule name from state."""
        rule_a = RuleDefinition("rule_a", (), UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)))
        rule_b = RuleDefinition("rule_b", (), UpdateStmt(LocationTerm("x", ()), LiteralTerm(2)))
        rules.register(rule_a)
        rules.register(rule_b)
        
        state.set_var("which_rule", "rule_b")
        
        stmt = RuleCallStmt(LocationTerm("which_rule", ()))
        updates = evaluator.eval(stmt, env)
        
        assert list(updates)[0].value == 2
    
    def test_call_rule_recursive(self, evaluator, env, state, rules):
        """Recursive rule call."""
        # countdown(n) = if n > 0 then result := n; countdown(n-1) else skip
        rule = RuleDefinition(
            "countdown",
            ("n",),
            IfStmt(
                condition=BinaryOpTerm(">", VariableTerm("n"), LiteralTerm(0)),
                then_body=SeqStmt((
                    UpdateStmt(
                        LocationTerm("result", (VariableTerm("n"),)),
                        VariableTerm("n")
                    ),
                    RuleCallStmt(
                        VariableTerm("countdown"),
                        (BinaryOpTerm("-", VariableTerm("n"), LiteralTerm(1)),)
                    ),
                )),
                else_body=SkipStmt()
            )
        )
        rules.register(rule)
        
        stmt = RuleCallStmt(VariableTerm("countdown"), (LiteralTerm(3),))
        evaluator.eval(stmt, env)
        
        assert state.get_func("result", (3,)) == 3
        assert state.get_func("result", (2,)) == 2
        assert state.get_func("result", (1,)) == 1
    
    def test_call_rule_max_recursion(self, state, rules, term_eval):
        """Excessive recursion raises MaxRecursionError."""
        config = RuleEvaluatorConfig(max_recursion_depth=5)
        evaluator = RuleEvaluator(state, rules, term_eval, config)
        
        # Infinite recursion: loop() = loop()
        rule = RuleDefinition(
            "loop",
            (),
            RuleCallStmt(VariableTerm("loop"))
        )
        rules.register(rule)
        
        with pytest.raises(MaxRecursionError) as exc_info:
            evaluator.eval(RuleCallStmt(VariableTerm("loop")), Environment())
        
        assert exc_info.value.rule_name == "loop"
        assert exc_info.value.max_depth == 5
    
    def test_call_stack_tracking(self, evaluator, env, rules):
        """Call stack is tracked during execution."""
        # outer() = inner()
        # inner() = skip
        inner = RuleDefinition("inner", (), SkipStmt())
        outer = RuleDefinition("outer", (), RuleCallStmt(VariableTerm("inner")))
        rules.register(inner)
        rules.register(outer)
        
        # Call outer
        evaluator.eval(RuleCallStmt(VariableTerm("outer")), env)
        
        # After execution, call stack should be empty
        assert evaluator.get_call_stack() == []


# ============================================================================
# 12. RuleEvaluator - PrintStmt
# ============================================================================

class TestEvalPrint:
    """Test PrintStmt evaluation."""
    
    def test_print_returns_empty_updates(self, evaluator, env):
        """Print produces no updates."""
        stmt = PrintStmt(LiteralTerm("hello"))
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 0
    
    def test_print_with_callback(self, state, rules, term_eval):
        """Print calls configured callback."""
        printed: List[Any] = []
        config = RuleEvaluatorConfig(print_callback=lambda x: printed.append(x))
        evaluator = RuleEvaluator(state, rules, term_eval, config)
        
        stmt = PrintStmt(LiteralTerm("hello"))
        evaluator.eval(stmt, Environment())
        
        assert printed == ["hello"]
    
    def test_print_evaluates_expression(self, state, rules, term_eval):
        """Print evaluates expression before printing."""
        state.set_var("x", 42)
        
        printed: List[Any] = []
        config = RuleEvaluatorConfig(print_callback=lambda x: printed.append(x))
        evaluator = RuleEvaluator(state, rules, term_eval, config)
        
        stmt = PrintStmt(BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(8)))
        evaluator.eval(stmt, Environment())
        
        assert printed == [50]
    
    def test_print_multiple(self, state, rules, term_eval):
        """Multiple prints in sequence."""
        printed: List[Any] = []
        config = RuleEvaluatorConfig(print_callback=lambda x: printed.append(x))
        evaluator = RuleEvaluator(state, rules, term_eval, config)
        
        stmt = SeqStmt((
            PrintStmt(LiteralTerm(1)),
            PrintStmt(LiteralTerm(2)),
            PrintStmt(LiteralTerm(3)),
        ))
        evaluator.eval(stmt, Environment())
        
        assert printed == [1, 2, 3]


# ============================================================================
# 13. Integration Tests
# ============================================================================

class TestRulesIntegration:
    """Integration tests combining multiple constructs."""
    
    def test_mm1_queue_step(self, evaluator, env, state, rules, types):
        """Simulate one step of M/M/1 queue processing."""
        types.register(Domain("Load"))
        
        # Initial state
        load1 = ASMObject("Load")
        load2 = ASMObject("Load")
        state.set_var("queue", [load1, load2])
        state.set_var("server_busy", False)
        
        # start_service rule
        start_service = RuleDefinition(
            "start_service",
            (),
            IfStmt(
                condition=BinaryOpTerm(
                    "and",
                    UnaryOpTerm("not", LocationTerm("server_busy", ())),
                    BinaryOpTerm(">", LibCallTerm("length", (LocationTerm("queue", ()),)), LiteralTerm(0))
                ),
                then_body=SeqStmt((
                    # Get first load
                    LetStmt("load", LibCallTerm("get", (LocationTerm("queue", ()), LiteralTerm(0)))),
                    # Remove from queue (simplified: just set to tail)
                    UpdateStmt(LocationTerm("server_busy", ()), LiteralTerm(True)),
                    UpdateStmt(LocationTerm("serving", ()), VariableTerm("load")),
                ))
            )
        )
        rules.register(start_service)
        
        # Execute
        stmt = RuleCallStmt(VariableTerm("start_service"))
        evaluator.eval(stmt, env)
        
        assert state.get_var("server_busy") is True
        assert state.get_var("serving") is load1
    
    def test_event_graph_pattern(self, evaluator, env, state, rules, types):
        """Pattern matching Event Graph event execution."""
        types.register(Domain("Event"))
        
        # Setup events with rules
        arrive_event = ASMObject("Event")
        start_event = ASMObject("Event")
        
        state.set_func("event_rule", (arrive_event,), "handle_arrive")
        state.set_func("event_rule", (start_event,), "handle_start")
        state.set_var("processed", [])
        
        # Define handlers
        handle_arrive = RuleDefinition(
            "handle_arrive",
            (),
            UpdateStmt(
                LocationTerm("processed", ()),
                LibCallTerm("append", (LocationTerm("processed", ()), LiteralTerm("arrive")))
            )
        )
        handle_start = RuleDefinition(
            "handle_start",
            (),
            UpdateStmt(
                LocationTerm("processed", ()),
                LibCallTerm("append", (LocationTerm("processed", ()), LiteralTerm("start")))
            )
        )
        rules.register(handle_arrive)
        rules.register(handle_start)
        
        # Execute event (dynamic dispatch)
        env.bind("current_event", arrive_event)
        stmt = RuleCallStmt(
            LocationTerm("event_rule", (VariableTerm("current_event"),))
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        assert state.get_var("processed") == ["arrive"]
    
    def test_acd_scanning_pattern(self, evaluator, env, state, rules, types):
        """Pattern matching ACD scanning phase."""
        types.register(Domain("Activity"))
        
        # Setup: activities with conditions
        state.set_var("servers_available", 2)
        state.set_var("queue_length", 3)
        state.set_var("started", 0)
        
        # Scanning: while can_start do start_activity
        scan = RuleDefinition(
            "scan",
            (),
            WhileStmt(
                condition=BinaryOpTerm(
                    "and",
                    BinaryOpTerm(">", LocationTerm("servers_available", ()), LiteralTerm(0)),
                    BinaryOpTerm(">", LocationTerm("queue_length", ()), LiteralTerm(0))
                ),
                body=SeqStmt((
                    UpdateStmt(
                        LocationTerm("servers_available", ()),
                        BinaryOpTerm("-", LocationTerm("servers_available", ()), LiteralTerm(1))
                    ),
                    UpdateStmt(
                        LocationTerm("queue_length", ()),
                        BinaryOpTerm("-", LocationTerm("queue_length", ()), LiteralTerm(1))
                    ),
                    UpdateStmt(
                        LocationTerm("started", ()),
                        BinaryOpTerm("+", LocationTerm("started", ()), LiteralTerm(1))
                    ),
                ))
            )
        )
        rules.register(scan)
        
        # Execute scan
        evaluator.eval(RuleCallStmt(VariableTerm("scan")), env)
        
        # Should start 2 activities (limited by servers)
        assert state.get_var("started") == 2
        assert state.get_var("servers_available") == 0
        assert state.get_var("queue_length") == 1
    
    def test_forall_schedule_events(self, evaluator, env, state, rules, types):
        """Forall pattern for scheduling multiple events."""
        types.register(Domain("Edge"))
        
        # Setup edges
        edge1 = ASMObject("Edge")
        edge2 = ASMObject("Edge")
        edge3 = ASMObject("Edge")
        
        state.set_func("delay", (edge1,), 1.0)
        state.set_func("delay", (edge2,), 2.0)
        state.set_func("delay", (edge3,), 3.0)
        state.set_var("edges", [edge1, edge2, edge3])
        state.set_var("current_time", 10.0)
        
        # Schedule events for all edges
        stmt = ForallStmt(
            "e",
            LocationTerm("edges", ()),
            UpdateStmt(
                LocationTerm("scheduled_time", (VariableTerm("e"),)),
                BinaryOpTerm(
                    "+",
                    LocationTerm("current_time", ()),
                    LocationTerm("delay", (VariableTerm("e"),))
                )
            )
        )
        updates = evaluator.eval(stmt, env)
        updates.apply_to(state)
        
        assert state.get_func("scheduled_time", (edge1,)) == 11.0
        assert state.get_func("scheduled_time", (edge2,)) == 12.0
        assert state.get_func("scheduled_time", (edge3,)) == 13.0
    
    def test_complex_rule_composition(self, evaluator, env, state, rules, types):
        """Complex rule with multiple constructs."""
        types.register(Domain("Job"))
        
        # Setup
        job1 = ASMObject("Job")
        job2 = ASMObject("Job")
        job3 = ASMObject("Job")
        
        state.set_func("priority", (job1,), 3)
        state.set_func("priority", (job2,), 1)
        state.set_func("priority", (job3,), 2)
        state.set_var("jobs", [job1, job2, job3])
        state.set_var("high_priority_count", 0)
        
        # Process jobs: count high priority, mark all as processed
        process_all = RuleDefinition(
            "process_all",
            (),
            SeqStmt((
                # First: forall to mark processed
                ForallStmt(
                    "j",
                    LocationTerm("jobs", ()),
                    UpdateStmt(LocationTerm("processed", (VariableTerm("j"),)), LiteralTerm(True))
                ),
                # Then: while loop to count high priority
                LetStmt("i", LiteralTerm(0)),
                WhileStmt(
                    condition=BinaryOpTerm(
                        "<",
                        VariableTerm("i"),
                        LibCallTerm("length", (LocationTerm("jobs", ()),))
                    ),
                    body=SeqStmt((
                        LetStmt("job", LibCallTerm("get", (LocationTerm("jobs", ()), VariableTerm("i")))),
                        IfStmt(
                            condition=BinaryOpTerm(
                                ">=",
                                LocationTerm("priority", (VariableTerm("job"),)),
                                LiteralTerm(2)
                            ),
                            then_body=UpdateStmt(
                                LocationTerm("high_priority_count", ()),
                                BinaryOpTerm("+", LocationTerm("high_priority_count", ()), LiteralTerm(1))
                            )
                        ),
                        LetStmt("i", BinaryOpTerm("+", VariableTerm("i"), LiteralTerm(1))),
                    ))
                ),
            ))
        )
        rules.register(process_all)
        
        evaluator.eval(RuleCallStmt(VariableTerm("process_all")), env)
        
        # All marked processed
        assert state.get_func("processed", (job1,)) is True
        assert state.get_func("processed", (job2,)) is True
        assert state.get_func("processed", (job3,)) is True
        
        # 2 high priority (priority >= 2): job1 (3), job3 (2)
        assert state.get_var("high_priority_count") == 2


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Edge cases and error conditions."""
    
    def test_unknown_statement_type(self, evaluator, env):
        """Unknown statement type raises error."""
        class FakeStmt(Stmt):
            pass
        
        with pytest.raises(RuleEvaluationError, match="Unknown statement type"):
            evaluator.eval(FakeStmt(), env)
    
    def test_rule_with_no_body(self, evaluator, env, rules):
        """Rule with no body returns empty updates."""
        rule = RuleDefinition("empty", ())  # No body
        rules.register(rule)
        
        updates = evaluator.eval(RuleCallStmt(VariableTerm("empty")), env)
        assert len(updates) == 0
    
    def test_deeply_nested_if(self, evaluator, env, state):
        """Deeply nested if statements work correctly."""
        # if true then (if true then (if true then x:=1))
        stmt = IfStmt(
            LiteralTerm(True),
            IfStmt(
                LiteralTerm(True),
                IfStmt(
                    LiteralTerm(True),
                    IfStmt(
                        LiteralTerm(True),
                        UpdateStmt(LocationTerm("x", ()), LiteralTerm(42))
                    )
                )
            )
        )
        updates = evaluator.eval(stmt, env)
        
        assert list(updates)[0].value == 42
    
    def test_empty_forall_body(self, evaluator, env, state):
        """Forall with skip body produces no updates."""
        state.set_var("items", [1, 2, 3])
        
        stmt = ForallStmt("x", LocationTerm("items", ()), SkipStmt())
        updates = evaluator.eval(stmt, env)
        
        assert len(updates) == 0
    
    def test_while_modifies_collection(self, evaluator, env, state):
        """While loop that modifies the collection it checks."""
        state.set_var("items", [1, 2, 3, 4, 5])
        state.set_var("processed", 0)
        
        # Process until items empty (pop first each time)
        # Simplified: just count and truncate
        stmt = WhileStmt(
            condition=BinaryOpTerm(
                ">",
                LibCallTerm("length", (LocationTerm("items", ()),)),
                LiteralTerm(0)
            ),
            body=SeqStmt((
                UpdateStmt(
                    LocationTerm("processed", ()),
                    BinaryOpTerm("+", LocationTerm("processed", ()), LiteralTerm(1))
                ),
                # Remove first item (simplified: set to empty after count reaches 5)
                IfStmt(
                    BinaryOpTerm(">=", LocationTerm("processed", ()), LiteralTerm(5)),
                    UpdateStmt(LocationTerm("items", ()), LiteralTerm([]))
                ),
            ))
        )
        evaluator.eval(stmt, env)
        
        assert state.get_var("processed") == 5
        assert state.get_var("items") == []
    
    def test_rule_call_with_literal_name(self, evaluator, env, rules):
        """Rule call with literal string name."""
        rule = RuleDefinition("my_rule", (), UpdateStmt(LocationTerm("x", ()), LiteralTerm(1)))
        rules.register(rule)
        
        stmt = RuleCallStmt(LiteralTerm("my_rule"))
        updates = evaluator.eval(stmt, env)
        
        assert list(updates)[0].value == 1
    
    def test_rule_call_non_string_name(self, evaluator, env, state):
        """Rule call with non-string name raises error."""
        state.set_var("rule_ref", 123)  # Not a string!
        
        stmt = RuleCallStmt(LocationTerm("rule_ref", ()))
        
        with pytest.raises(RuleEvaluationError, match="must be string"):
            evaluator.eval(stmt, env)


class TestConfigDefaults:
    """Test RuleEvaluatorConfig defaults."""
    
    def test_default_max_iterations(self):
        """Default max_while_iterations is 10000."""
        config = RuleEvaluatorConfig()
        assert config.max_while_iterations == 10000
    
    def test_default_max_recursion(self):
        """Default max_recursion_depth is 1000."""
        config = RuleEvaluatorConfig()
        assert config.max_recursion_depth == 1000
    
    def test_default_print_callback(self):
        """Default print_callback is None."""
        config = RuleEvaluatorConfig()
        assert config.print_callback is None
    
    def test_custom_config(self):
        """Custom config values are used."""
        callback = lambda x: None
        config = RuleEvaluatorConfig(
            max_while_iterations=100,
            max_recursion_depth=50,
            print_callback=callback
        )
        assert config.max_while_iterations == 100
        assert config.max_recursion_depth == 50
        assert config.print_callback is callback
