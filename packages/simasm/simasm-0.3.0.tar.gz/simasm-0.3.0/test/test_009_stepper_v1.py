"""
Tests for simasm/runtime/stepper.py

Section 10: Step-by-step ASM execution

Test categories:
1. StepperConfig - configuration options
2. ASMStepper - basic stepping
3. ASMStepper - stop conditions
4. ASMStepper - run methods
5. ASMStepper - trace and debugging
6. DESStepper - DES-specific features
7. Integration tests - simulation patterns
"""

import pytest
from typing import Optional

from simasm.core.types import TypeRegistry, Domain
from simasm.core.state import ASMState, ASMObject, UNDEF
from simasm.core.update import UpdateSet
from simasm.core.terms import (
    Environment, TermEvaluator,
    LiteralTerm, VariableTerm, LocationTerm,
    BinaryOpTerm,
)
from simasm.core.rules import (
    RuleDefinition, RuleRegistry, RuleEvaluator,
    UpdateStmt, SeqStmt, SkipStmt, IfStmt, WhileStmt,
)
from simasm.runtime.stdlib import StandardLibrary
from simasm.runtime.stepper import (
    Stepper, ASMStepper, DESStepper,
    StepperConfig, DESStepperConfig,
    StepResult, StepperError,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def types():
    """Fresh TypeRegistry."""
    return TypeRegistry()


@pytest.fixture
def state():
    """Fresh ASMState with simulation time initialized."""
    s = ASMState()
    s.set_var("sim_clocktime", 0.0)
    return s


@pytest.fixture
def rules():
    """Fresh RuleRegistry."""
    return RuleRegistry()


@pytest.fixture
def stdlib(state, rules):
    """StandardLibrary instance."""
    return StandardLibrary(state, rules)


@pytest.fixture
def term_eval(state, types, stdlib):
    """TermEvaluator instance."""
    return TermEvaluator(state, types, stdlib)


@pytest.fixture
def rule_eval(state, rules, term_eval):
    """RuleEvaluator instance."""
    return RuleEvaluator(state, rules, term_eval)


def make_counter_rule():
    """
    Create a simple counter rule that increments x each step.
    
    rule main = x := x + 1
    """
    return RuleDefinition(
        name="main",
        parameters=(),
        body=UpdateStmt(
            LocationTerm("x", ()),
            BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(1))
        )
    )


def make_time_advance_rule():
    """
    Create a rule that advances time by 1.0 each step.
    
    rule main =
        sim_clocktime := sim_clocktime + 1.0
    """
    return RuleDefinition(
        name="main",
        parameters=(),
        body=UpdateStmt(
            LocationTerm("sim_clocktime", ()),
            BinaryOpTerm("+", LocationTerm("sim_clocktime", ()), LiteralTerm(1.0))
        )
    )


def make_counter_and_time_rule():
    """
    Create a rule that increments counter and advances time.
    
    rule main =
        x := x + 1
        sim_clocktime := sim_clocktime + 1.0
    """
    return RuleDefinition(
        name="main",
        parameters=(),
        body=SeqStmt((
            UpdateStmt(
                LocationTerm("x", ()),
                BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(1))
            ),
            UpdateStmt(
                LocationTerm("sim_clocktime", ()),
                BinaryOpTerm("+", LocationTerm("sim_clocktime", ()), LiteralTerm(1.0))
            ),
        ))
    )


def make_fixpoint_rule():
    """
    Create a rule that does nothing (for fixpoint testing).
    
    rule main = skip
    """
    return RuleDefinition(
        name="main",
        parameters=(),
        body=SkipStmt()
    )


# ============================================================================
# 1. StepperConfig Tests
# ============================================================================

class TestStepperConfig:
    """Test StepperConfig options."""
    
    def test_default_config(self):
        """Default configuration values."""
        config = StepperConfig()
        assert config.time_var == "sim_clocktime"
        assert config.max_steps is None
        assert config.end_time is None
        assert config.stop_on_fixpoint is False
        assert config.trace_enabled is False
    
    def test_custom_config(self):
        """Custom configuration values."""
        config = StepperConfig(
            time_var="clock",
            max_steps=100,
            end_time=50.0,
            stop_on_fixpoint=True,
            trace_enabled=True,
        )
        assert config.time_var == "clock"
        assert config.max_steps == 100
        assert config.end_time == 50.0
        assert config.stop_on_fixpoint is True
        assert config.trace_enabled is True


class TestDESStepperConfig:
    """Test DESStepperConfig options."""
    
    def test_default_des_config(self):
        """Default DES configuration values."""
        config = DESStepperConfig()
        assert config.fel_var == "future_event_list"
        assert config.empty_fel_stops is True
    
    def test_custom_des_config(self):
        """Custom DES configuration."""
        config = DESStepperConfig(
            fel_var="FEL",
            empty_fel_stops=False,
        )
        assert config.fel_var == "FEL"
        assert config.empty_fel_stops is False


# ============================================================================
# 2. ASMStepper - Basic Stepping
# ============================================================================

class TestASMStepperBasic:
    """Test basic ASMStepper functionality."""
    
    def test_create_stepper(self, state, rule_eval):
        """Create stepper with main rule."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        assert stepper.step_count == 0
        assert stepper.sim_time == 0.0
        assert stepper.can_step()
    
    def test_single_step(self, state, rule_eval):
        """Execute single step."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        result = stepper.step()
        
        assert result.step_number == 1
        assert result.updates_count == 1
        assert state.get_var("x") == 1
        assert stepper.step_count == 1
    
    def test_multiple_steps(self, state, rule_eval):
        """Execute multiple steps."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        for i in range(5):
            stepper.step()
        
        assert state.get_var("x") == 5
        assert stepper.step_count == 5
    
    def test_time_advances(self, state, rule_eval):
        """Simulation time advances with rule."""
        main_rule = make_time_advance_rule()
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        assert stepper.sim_time == 0.0
        stepper.step()
        assert stepper.sim_time == 1.0
        stepper.step()
        assert stepper.sim_time == 2.0
    
    def test_initializes_time_if_undef(self, rules, types, stdlib):
        """Stepper initializes time variable if UNDEF."""
        state = ASMState()  # No time set
        term_eval = TermEvaluator(state, types, stdlib)
        rule_eval = RuleEvaluator(state, rules, term_eval)
        main_rule = make_fixpoint_rule()
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        assert state.get_var("sim_clocktime") == 0.0
    
    def test_current_state(self, state, rule_eval):
        """current_state returns state reference."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        assert stepper.current_state() is state
        assert stepper.state is state


# ============================================================================
# 3. ASMStepper - Stop Conditions
# ============================================================================

class TestASMStepperStopConditions:
    """Test stop condition handling."""
    
    def test_stop_on_max_steps(self, state, rule_eval):
        """Stop when max_steps reached."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        config = StepperConfig(max_steps=5)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        
        for _ in range(5):
            assert stepper.can_step()
            stepper.step()
        
        assert not stepper.can_step()
        assert "max_steps" in stepper.stop_reason
    
    def test_stop_on_end_time(self, state, rule_eval):
        """Stop when end_time reached."""
        main_rule = make_time_advance_rule()
        config = StepperConfig(end_time=3.5)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        
        # Steps: time goes 0->1->2->3->4
        # Should stop when time >= 3.5 (after 4th step)
        while stepper.can_step():
            stepper.step()
        
        assert stepper.sim_time >= 3.5
        assert "end_time" in stepper.stop_reason
    
    def test_stop_on_custom_condition(self, state, rule_eval):
        """Stop on custom condition."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        # Stop when x reaches 7
        def stop_at_7(s):
            return s.get_var("x") >= 7
        
        stepper = ASMStepper(state, main_rule, rule_eval, stop_condition=stop_at_7)
        
        while stepper.can_step():
            stepper.step()
        
        assert state.get_var("x") == 7
        assert "stop_condition" in stepper.stop_reason
    
    def test_stop_on_fixpoint(self, state, rule_eval):
        """Stop when no updates (fixpoint)."""
        main_rule = make_fixpoint_rule()
        config = StepperConfig(stop_on_fixpoint=True)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        
        result = stepper.step()
        
        assert result.is_fixpoint
        assert not stepper.can_step()
        assert "fixpoint" in stepper.stop_reason
    
    def test_step_after_stopped_raises_error(self, state, rule_eval):
        """Step after stopping raises error."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        config = StepperConfig(max_steps=1)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        stepper.step()
        
        with pytest.raises(StepperError, match="Cannot step"):
            stepper.step()


# ============================================================================
# 4. ASMStepper - Run Methods
# ============================================================================

class TestASMStepperRunMethods:
    """Test run() and run_until() methods."""
    
    def test_run_with_max_steps(self, state, rule_eval):
        """run() with max_steps argument."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        result_state = stepper.run(max_steps=10)
        
        assert result_state is state
        assert state.get_var("x") == 10
        assert stepper.step_count == 10
    
    def test_run_with_config_max_steps(self, state, rule_eval):
        """run() respects config.max_steps."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        config = StepperConfig(max_steps=5)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        stepper.run()
        
        assert state.get_var("x") == 5
    
    def test_run_until_time(self, state, rule_eval):
        """run_until() stops at specified time."""
        main_rule = make_time_advance_rule()
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        stepper.run_until(end_time=5.0)
        
        assert stepper.sim_time >= 5.0
    
    def test_run_until_can_extend(self, state, rule_eval):
        """run_until() can extend previous run."""
        main_rule = make_time_advance_rule()
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        # First run to time 3
        stepper.run_until(3.0)
        assert stepper.sim_time >= 3.0
        steps1 = stepper.step_count
        
        # Extend to time 6
        stepper.run_until(6.0)
        assert stepper.sim_time >= 6.0
        assert stepper.step_count > steps1
    
    def test_run_returns_state(self, state, rule_eval):
        """run() returns final state."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        result = stepper.run(max_steps=5)
        
        assert result is state


# ============================================================================
# 5. ASMStepper - Trace and Debugging
# ============================================================================

class TestASMStepperTrace:
    """Test trace and debugging features."""
    
    def test_trace_disabled_by_default(self, state, rule_eval):
        """Trace is empty when disabled."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        stepper.run(max_steps=5)
        
        assert len(stepper.trace) == 0
    
    def test_trace_enabled(self, state, rule_eval):
        """Trace records steps when enabled."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        config = StepperConfig(trace_enabled=True)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        stepper.run(max_steps=5)
        
        assert len(stepper.trace) == 5
        assert stepper.trace[0].step_number == 1
        assert stepper.trace[4].step_number == 5
    
    def test_trace_contains_step_results(self, state, rule_eval):
        """Trace entries are StepResult objects."""
        main_rule = make_counter_and_time_rule()
        state.set_var("x", 0)
        config = StepperConfig(trace_enabled=True)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        stepper.run(max_steps=3)
        
        for i, result in enumerate(stepper.trace):
            assert isinstance(result, StepResult)
            assert result.step_number == i + 1
            assert result.sim_time == float(i + 1)
            assert result.updates_count == 2  # x and time
    
    def test_reset_clears_trace(self, state, rule_eval):
        """reset() clears trace."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        config = StepperConfig(trace_enabled=True)
        
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        stepper.run(max_steps=5)
        
        stepper.reset()
        
        assert len(stepper.trace) == 0
        assert stepper.step_count == 0
    
    def test_reset_with_new_state(self, state, rule_eval, types, stdlib, rules):
        """reset() with new state."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        stepper.run(max_steps=5)
        
        # Create new state
        new_state = ASMState()
        new_state.set_var("sim_clocktime", 0.0)
        new_state.set_var("x", 100)
        
        # Need new evaluators for new state
        new_stdlib = StandardLibrary(new_state, rules)
        new_term_eval = TermEvaluator(new_state, types, new_stdlib)
        new_rule_eval = RuleEvaluator(new_state, rules, new_term_eval)
        
        new_stepper = ASMStepper(new_state, main_rule, new_rule_eval)
        new_stepper.run(max_steps=3)
        
        assert new_state.get_var("x") == 103


# ============================================================================
# 6. DESStepper - DES-specific Features
# ============================================================================

class TestDESStepper:
    """Test DESStepper DES-specific features."""
    
    def test_stops_on_empty_fel(self, state, rule_eval):
        """Stops when FEL becomes empty."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        state.set_var("future_event_list", [])  # Empty FEL
        
        config = DESStepperConfig()
        stepper = DESStepper(state, main_rule, rule_eval, config)
        
        assert not stepper.can_step()
        assert "FEL empty" in stepper.stop_reason
    
    def test_runs_with_non_empty_fel(self, state, rule_eval):
        """Runs when FEL has events."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        state.set_var("future_event_list", ["event1", "event2"])
        
        config = DESStepperConfig(max_steps=1)
        stepper = DESStepper(state, main_rule, rule_eval, config)
        
        assert stepper.can_step()
        stepper.step()
        assert stepper.events_processed == 1
    
    def test_empty_fel_stops_disabled(self, state, rule_eval):
        """Can disable FEL empty stop."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        state.set_var("future_event_list", [])  # Empty FEL
        
        config = DESStepperConfig(
            empty_fel_stops=False,
            max_steps=3,
        )
        stepper = DESStepper(state, main_rule, rule_eval, config)
        
        stepper.run()
        
        assert stepper.step_count == 3
        assert stepper.events_processed == 3
    
    def test_custom_fel_var(self, state, rule_eval):
        """Custom FEL variable name."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        state.set_var("FEL", [])  # Using custom name
        
        config = DESStepperConfig(fel_var="FEL")
        stepper = DESStepper(state, main_rule, rule_eval, config)
        
        assert not stepper.can_step()  # FEL is empty
    
    def test_events_processed_count(self, state, rule_eval):
        """Tracks events processed."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        state.set_var("future_event_list", ["a", "b", "c"])
        
        config = DESStepperConfig(max_steps=5)
        stepper = DESStepper(state, main_rule, rule_eval, config)
        
        stepper.run()
        
        assert stepper.events_processed == 5
    
    def test_reset_clears_events_processed(self, state, rule_eval):
        """Reset clears events processed count."""
        main_rule = make_counter_rule()
        state.set_var("x", 0)
        state.set_var("future_event_list", ["a"])
        
        config = DESStepperConfig(max_steps=3, empty_fel_stops=False)
        stepper = DESStepper(state, main_rule, rule_eval, config)
        
        stepper.run()
        assert stepper.events_processed == 3
        
        stepper.reset()
        assert stepper.events_processed == 0


# ============================================================================
# 7. Integration Tests
# ============================================================================

class TestStepperIntegration:
    """Integration tests for simulation patterns."""
    
    def test_simple_counter_simulation(self, state, rule_eval):
        """Simple counter simulation."""
        main_rule = make_counter_and_time_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        stepper.run_until(10.0)
        
        assert stepper.sim_time >= 10.0
        assert state.get_var("x") >= 10
    
    def test_conditional_rule(self, state, rules, types, stdlib):
        """Rule with conditional behavior."""
        # Rule: if x < 10 then x := x + 1 else skip
        body = IfStmt(
            condition=BinaryOpTerm("<", LocationTerm("x", ()), LiteralTerm(10)),
            then_body=UpdateStmt(
                LocationTerm("x", ()),
                BinaryOpTerm("+", LocationTerm("x", ()), LiteralTerm(1))
            ),
            else_body=SkipStmt(),
        )
        main_rule = RuleDefinition("main", (), body)
        
        state.set_var("x", 0)
        term_eval = TermEvaluator(state, types, stdlib)
        rule_eval = RuleEvaluator(state, rules, term_eval)
        
        config = StepperConfig(stop_on_fixpoint=True)
        stepper = ASMStepper(state, main_rule, rule_eval, config)
        
        stepper.run(max_steps=100)
        
        # Should stop at fixpoint when x reaches 10
        assert state.get_var("x") == 10
        assert "fixpoint" in stepper.stop_reason
    
    def test_multiple_replications(self, rules, types):
        """Run multiple replications with reset."""
        results = []
        
        for rep in range(3):
            # Fresh state for each replication
            state = ASMState()
            state.set_var("sim_clocktime", 0.0)
            state.set_var("x", rep * 10)  # Different starting point
            
            stdlib = StandardLibrary(state, rules)
            term_eval = TermEvaluator(state, types, stdlib)
            rule_eval = RuleEvaluator(state, rules, term_eval)
            
            main_rule = make_counter_rule()
            stepper = ASMStepper(state, main_rule, rule_eval)
            
            stepper.run(max_steps=5)
            results.append(state.get_var("x"))
        
        # Each should add 5 to its starting value
        assert results == [5, 15, 25]
    
    def test_warm_up_pattern(self, state, rule_eval):
        """Warm-up period pattern."""
        main_rule = make_counter_and_time_rule()
        state.set_var("x", 0)
        
        stepper = ASMStepper(state, main_rule, rule_eval)
        
        # Warm-up: run until time 10
        stepper.run_until(10.0)
        warmup_x = state.get_var("x")
        
        # Reset counter (but not time) for production run
        state.set_var("x", 0)
        
        # Production: run until time 20
        stepper.run_until(20.0)
        production_x = state.get_var("x")
        
        # Verify pattern worked
        assert warmup_x >= 10
        assert production_x >= 10
        assert stepper.sim_time >= 20.0
