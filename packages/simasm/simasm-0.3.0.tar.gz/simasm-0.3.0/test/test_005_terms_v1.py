"""
test_005_terms_v1.py

Unit tests for simasm/core/terms.py

Tests:
- Environment (lexical scoping)
- Term AST nodes
- TermEvaluator
"""

import pytest
from simasm.core.types import TypeRegistry, Domain
from simasm.core.state import ASMState, ASMObject, Location, UNDEF
from simasm.core.terms import (
    Environment,
    Term, LiteralTerm, VariableTerm, LocationTerm,
    BinaryOpTerm, UnaryOpTerm, ListTerm, NewTerm,
    LibCallTerm, ConditionalTerm,
    TermEvaluator, TermEvaluationError,
)
from simasm.log.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# Mock StandardLibrary for testing
# ============================================================================

class MockStdLib:
    """Mock standard library for testing LibCallTerm."""
    
    def length(self, lst):
        """Return length of list."""
        return len(lst)
    
    def add(self, lst, item):
        """Add item to list (modifies in place, returns None)."""
        lst.append(item)
        return None
    
    def get(self, lst, index):
        """Get item at index."""
        return lst[index]
    
    def sum(self, lst):
        """Sum all elements."""
        return sum(lst)


# ============================================================================
# Environment Tests
# ============================================================================

class TestEnvironment:
    """Tests for Environment class."""
    
    def test_create_empty_environment(self):
        """Create empty environment."""
        logger.info("Testing empty environment")
        env = Environment()
        assert env.depth == 0
        assert env.parent is None
        logger.debug(f"Created: {env}")
    
    def test_bind_and_lookup(self):
        """Bind and look up variable."""
        logger.info("Testing bind and lookup")
        env = Environment()
        env.bind("x", 10)
        assert env.lookup("x") == 10
        logger.debug("Bind/lookup works")
    
    def test_lookup_undefined_raises(self):
        """Looking up undefined variable raises NameError."""
        logger.info("Testing undefined lookup")
        env = Environment()
        with pytest.raises(NameError) as exc_info:
            env.lookup("x")
        assert "Undefined variable" in str(exc_info.value)
        logger.debug("NameError raised correctly")
    
    def test_contains(self):
        """Test contains method."""
        logger.info("Testing contains")
        env = Environment()
        env.bind("x", 10)
        assert env.contains("x")
        assert not env.contains("y")
        logger.debug("Contains works")
    
    def test_child_scope(self):
        """Child scope sees parent bindings."""
        logger.info("Testing child scope")
        parent = Environment()
        parent.bind("x", 10)
        
        child = parent.child()
        assert child.lookup("x") == 10
        assert child.parent is parent
        assert child.depth == 1
        logger.debug("Child sees parent bindings")
    
    def test_child_bindings_dont_affect_parent(self):
        """Child bindings don't affect parent."""
        logger.info("Testing child isolation")
        parent = Environment()
        parent.bind("x", 10)
        
        child = parent.child()
        child.bind("y", 20)
        
        assert child.contains("y")
        assert not parent.contains("y")
        logger.debug("Child bindings isolated")
    
    def test_shadowing(self):
        """Child can shadow parent bindings."""
        logger.info("Testing shadowing")
        parent = Environment()
        parent.bind("x", 10)
        
        child = parent.child()
        child.bind("x", 99)
        
        assert child.lookup("x") == 99
        assert parent.lookup("x") == 10
        logger.debug("Shadowing works")
    
    def test_rebind_in_same_scope(self):
        """Rebind variable in same scope."""
        logger.info("Testing rebind same scope")
        env = Environment()
        env.bind("x", 10)
        env.rebind("x", 20)
        assert env.lookup("x") == 20
        logger.debug("Rebind in same scope works")
    
    def test_rebind_in_parent_scope(self):
        """Rebind variable in parent scope."""
        logger.info("Testing rebind parent scope")
        parent = Environment()
        parent.bind("x", 10)
        
        child = parent.child()
        child.rebind("x", 99)
        
        # Both should see new value
        assert child.lookup("x") == 99
        assert parent.lookup("x") == 99
        logger.debug("Rebind in parent scope works")
    
    def test_rebind_undefined_raises(self):
        """Rebind undefined variable raises NameError."""
        logger.info("Testing rebind undefined")
        env = Environment()
        with pytest.raises(NameError) as exc_info:
            env.rebind("x", 10)
        assert "Cannot rebind" in str(exc_info.value)
        logger.debug("NameError raised correctly")
    
    def test_local_names(self):
        """Get names bound locally only."""
        logger.info("Testing local_names")
        parent = Environment()
        parent.bind("x", 10)
        
        child = parent.child()
        child.bind("y", 20)
        
        assert child.local_names() == {"y"}
        assert parent.local_names() == {"x"}
        logger.debug("local_names works")
    
    def test_all_names(self):
        """Get all names including parents."""
        logger.info("Testing all_names")
        parent = Environment()
        parent.bind("x", 10)
        
        child = parent.child()
        child.bind("y", 20)
        
        assert child.all_names() == {"x", "y"}
        assert parent.all_names() == {"x"}
        logger.debug("all_names works")
    
    def test_multiple_levels(self):
        """Test multiple scope levels."""
        logger.info("Testing multiple levels")
        root = Environment()
        root.bind("a", 1)
        
        level1 = root.child()
        level1.bind("b", 2)
        
        level2 = level1.child()
        level2.bind("c", 3)
        
        assert level2.depth == 2
        assert level2.lookup("a") == 1
        assert level2.lookup("b") == 2
        assert level2.lookup("c") == 3
        logger.debug("Multiple levels work")
    
    def test_repr(self):
        """Test repr."""
        logger.info("Testing repr")
        env = Environment()
        env.bind("x", 10)
        r = repr(env)
        assert "Environment" in r
        assert "depth=0" in r
        logger.debug(f"repr: {r}")


# ============================================================================
# Term AST Tests
# ============================================================================

class TestTermAST:
    """Tests for Term AST node classes."""
    
    def test_literal_term(self):
        """Create LiteralTerm."""
        logger.info("Testing LiteralTerm")
        term = LiteralTerm(42)
        assert term.value == 42
        assert "42" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_variable_term(self):
        """Create VariableTerm."""
        logger.info("Testing VariableTerm")
        term = VariableTerm("x")
        assert term.name == "x"
        assert "x" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_location_term_0ary(self):
        """Create 0-ary LocationTerm."""
        logger.info("Testing LocationTerm 0-ary")
        term = LocationTerm("counter")
        assert term.func_name == "counter"
        assert term.arguments == ()
        assert "counter" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_location_term_nary(self):
        """Create n-ary LocationTerm."""
        logger.info("Testing LocationTerm n-ary")
        arg = VariableTerm("load")
        term = LocationTerm("status", (arg,))
        assert term.func_name == "status"
        assert len(term.arguments) == 1
        logger.debug(f"Created: {term}")
    
    def test_binary_op_term(self):
        """Create BinaryOpTerm."""
        logger.info("Testing BinaryOpTerm")
        left = LiteralTerm(10)
        right = LiteralTerm(5)
        term = BinaryOpTerm("+", left, right)
        assert term.operator == "+"
        assert term.left == left
        assert term.right == right
        logger.debug(f"Created: {term}")
    
    def test_unary_op_term(self):
        """Create UnaryOpTerm."""
        logger.info("Testing UnaryOpTerm")
        operand = LiteralTerm(10)
        term = UnaryOpTerm("-", operand)
        assert term.operator == "-"
        assert term.operand == operand
        logger.debug(f"Created: {term}")
    
    def test_list_term_empty(self):
        """Create empty ListTerm."""
        logger.info("Testing ListTerm empty")
        term = ListTerm(())
        assert term.elements == ()
        assert "[]" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_list_term_with_elements(self):
        """Create ListTerm with elements."""
        logger.info("Testing ListTerm with elements")
        elems = (LiteralTerm(1), LiteralTerm(2), LiteralTerm(3))
        term = ListTerm(elems)
        assert len(term.elements) == 3
        logger.debug(f"Created: {term}")
    
    def test_new_term(self):
        """Create NewTerm."""
        logger.info("Testing NewTerm")
        term = NewTerm("Load")
        assert term.domain == "Load"
        assert "Load" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_lib_call_term(self):
        """Create LibCallTerm."""
        logger.info("Testing LibCallTerm")
        arg = VariableTerm("queue")
        term = LibCallTerm("length", (arg,))
        assert term.func_name == "length"
        assert len(term.arguments) == 1
        assert "lib.length" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_conditional_term(self):
        """Create ConditionalTerm."""
        logger.info("Testing ConditionalTerm")
        cond = BinaryOpTerm(">", VariableTerm("x"), LiteralTerm(0))
        then_expr = VariableTerm("x")
        else_expr = UnaryOpTerm("-", VariableTerm("x"))
        term = ConditionalTerm(cond, then_expr, else_expr)
        assert term.condition == cond
        assert "if" in repr(term)
        logger.debug(f"Created: {term}")
    
    def test_terms_are_frozen(self):
        """Terms should be immutable."""
        logger.info("Testing term immutability")
        term = LiteralTerm(42)
        with pytest.raises(AttributeError):
            term.value = 99
        logger.debug("Terms are frozen")


# ============================================================================
# TermEvaluator Tests - Literals and Variables
# ============================================================================

class TestTermEvaluatorBasic:
    """Basic tests for TermEvaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator with state and types."""
        types = TypeRegistry()
        types.register(Domain("Load"))
        types.register(Domain("Event"))
        state = ASMState(types)
        return TermEvaluator(state, types)
    
    @pytest.fixture
    def env(self):
        """Create empty environment."""
        return Environment()
    
    def test_eval_literal_int(self, evaluator, env):
        """Evaluate integer literal."""
        logger.info("Testing eval literal int")
        term = LiteralTerm(42)
        assert evaluator.eval(term, env) == 42
        logger.debug("Literal int evaluated")
    
    def test_eval_literal_float(self, evaluator, env):
        """Evaluate float literal."""
        logger.info("Testing eval literal float")
        term = LiteralTerm(3.14)
        assert evaluator.eval(term, env) == 3.14
        logger.debug("Literal float evaluated")
    
    def test_eval_literal_string(self, evaluator, env):
        """Evaluate string literal."""
        logger.info("Testing eval literal string")
        term = LiteralTerm("hello")
        assert evaluator.eval(term, env) == "hello"
        logger.debug("Literal string evaluated")
    
    def test_eval_literal_bool(self, evaluator, env):
        """Evaluate boolean literal."""
        logger.info("Testing eval literal bool")
        assert evaluator.eval(LiteralTerm(True), env) == True
        assert evaluator.eval(LiteralTerm(False), env) == False
        logger.debug("Literal bool evaluated")
    
    def test_eval_literal_undef(self, evaluator, env):
        """Evaluate UNDEF literal."""
        logger.info("Testing eval literal UNDEF")
        term = LiteralTerm(UNDEF)
        assert evaluator.eval(term, env) is UNDEF
        logger.debug("Literal UNDEF evaluated")
    
    def test_eval_variable(self, evaluator, env):
        """Evaluate variable from environment."""
        logger.info("Testing eval variable")
        env.bind("x", 100)
        term = VariableTerm("x")
        assert evaluator.eval(term, env) == 100
        logger.debug("Variable evaluated")
    
    def test_eval_variable_undefined_raises(self, evaluator, env):
        """Undefined variable raises error."""
        logger.info("Testing eval undefined variable")
        term = VariableTerm("unknown")
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Undefined variable" in str(exc_info.value)
        logger.debug("TermEvaluationError raised")


# ============================================================================
# TermEvaluator Tests - Locations
# ============================================================================

class TestTermEvaluatorLocations:
    """Tests for location evaluation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    @pytest.fixture
    def evaluator(self):
        types = TypeRegistry()
        types.register(Domain("Load"))
        state = ASMState(types)
        state.set_var("counter", 42)
        return TermEvaluator(state, types)
    
    @pytest.fixture
    def env(self):
        return Environment()
    
    def test_eval_location_0ary(self, evaluator, env):
        """Evaluate 0-ary location (variable)."""
        logger.info("Testing eval 0-ary location")
        term = LocationTerm("counter")
        assert evaluator.eval(term, env) == 42
        logger.debug("0-ary location evaluated")
    
    def test_eval_location_undefined_returns_undef(self, evaluator, env):
        """Undefined location returns UNDEF."""
        logger.info("Testing eval undefined location")
        term = LocationTerm("unknown_var")
        assert evaluator.eval(term, env) is UNDEF
        logger.debug("Undefined location returns UNDEF")
    
    def test_eval_location_nary(self, evaluator, env):
        """Evaluate n-ary location (function)."""
        logger.info("Testing eval n-ary location")
        load = ASMObject("Load")
        evaluator.state.set_func("status", (load,), "waiting")
        
        # Bind load to environment so we can reference it
        env.bind("load", load)
        
        # status(load)
        term = LocationTerm("status", (VariableTerm("load"),))
        assert evaluator.eval(term, env) == "waiting"
        logger.debug("N-ary location evaluated")
    
    def test_eval_location_nested_args(self, evaluator, env):
        """Evaluate location with computed arguments."""
        logger.info("Testing eval location nested args")
        load = ASMObject("Load")
        evaluator.state.set_func("data", (load,), 999)
        
        env.bind("obj", load)
        
        # data(obj) where obj is from env
        term = LocationTerm("data", (VariableTerm("obj"),))
        assert evaluator.eval(term, env) == 999
        logger.debug("Nested args evaluated")


# ============================================================================
# TermEvaluator Tests - Operators
# ============================================================================

class TestTermEvaluatorOperators:
    """Tests for operator evaluation."""
    
    @pytest.fixture
    def evaluator(self):
        types = TypeRegistry()
        state = ASMState(types)
        return TermEvaluator(state, types)
    
    @pytest.fixture
    def env(self):
        return Environment()
    
    # Arithmetic operators
    
    def test_eval_add(self, evaluator, env):
        """Evaluate addition."""
        logger.info("Testing +")
        term = BinaryOpTerm("+", LiteralTerm(10), LiteralTerm(5))
        assert evaluator.eval(term, env) == 15
    
    def test_eval_subtract(self, evaluator, env):
        """Evaluate subtraction."""
        logger.info("Testing -")
        term = BinaryOpTerm("-", LiteralTerm(10), LiteralTerm(3))
        assert evaluator.eval(term, env) == 7
    
    def test_eval_multiply(self, evaluator, env):
        """Evaluate multiplication."""
        logger.info("Testing *")
        term = BinaryOpTerm("*", LiteralTerm(6), LiteralTerm(7))
        assert evaluator.eval(term, env) == 42
    
    def test_eval_divide(self, evaluator, env):
        """Evaluate division."""
        logger.info("Testing /")
        term = BinaryOpTerm("/", LiteralTerm(10), LiteralTerm(4))
        assert evaluator.eval(term, env) == 2.5
    
    def test_eval_floor_divide(self, evaluator, env):
        """Evaluate floor division."""
        logger.info("Testing //")
        term = BinaryOpTerm("//", LiteralTerm(10), LiteralTerm(3))
        assert evaluator.eval(term, env) == 3
    
    def test_eval_modulo(self, evaluator, env):
        """Evaluate modulo."""
        logger.info("Testing %")
        term = BinaryOpTerm("%", LiteralTerm(10), LiteralTerm(3))
        assert evaluator.eval(term, env) == 1
    
    def test_eval_divide_by_zero(self, evaluator, env):
        """Division by zero raises error."""
        logger.info("Testing division by zero")
        term = BinaryOpTerm("/", LiteralTerm(10), LiteralTerm(0))
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Division by zero" in str(exc_info.value)
    
    # Comparison operators
    
    def test_eval_equal(self, evaluator, env):
        """Evaluate equality."""
        logger.info("Testing ==")
        assert evaluator.eval(BinaryOpTerm("==", LiteralTerm(5), LiteralTerm(5)), env) == True
        assert evaluator.eval(BinaryOpTerm("==", LiteralTerm(5), LiteralTerm(3)), env) == False
    
    def test_eval_not_equal(self, evaluator, env):
        """Evaluate inequality."""
        logger.info("Testing !=")
        assert evaluator.eval(BinaryOpTerm("!=", LiteralTerm(5), LiteralTerm(3)), env) == True
        assert evaluator.eval(BinaryOpTerm("!=", LiteralTerm(5), LiteralTerm(5)), env) == False
    
    def test_eval_less_than(self, evaluator, env):
        """Evaluate less than."""
        logger.info("Testing <")
        assert evaluator.eval(BinaryOpTerm("<", LiteralTerm(3), LiteralTerm(5)), env) == True
        assert evaluator.eval(BinaryOpTerm("<", LiteralTerm(5), LiteralTerm(3)), env) == False
    
    def test_eval_greater_than(self, evaluator, env):
        """Evaluate greater than."""
        logger.info("Testing >")
        assert evaluator.eval(BinaryOpTerm(">", LiteralTerm(5), LiteralTerm(3)), env) == True
        assert evaluator.eval(BinaryOpTerm(">", LiteralTerm(3), LiteralTerm(5)), env) == False
    
    def test_eval_less_equal(self, evaluator, env):
        """Evaluate less or equal."""
        logger.info("Testing <=")
        assert evaluator.eval(BinaryOpTerm("<=", LiteralTerm(3), LiteralTerm(5)), env) == True
        assert evaluator.eval(BinaryOpTerm("<=", LiteralTerm(5), LiteralTerm(5)), env) == True
        assert evaluator.eval(BinaryOpTerm("<=", LiteralTerm(6), LiteralTerm(5)), env) == False
    
    def test_eval_greater_equal(self, evaluator, env):
        """Evaluate greater or equal."""
        logger.info("Testing >=")
        assert evaluator.eval(BinaryOpTerm(">=", LiteralTerm(5), LiteralTerm(3)), env) == True
        assert evaluator.eval(BinaryOpTerm(">=", LiteralTerm(5), LiteralTerm(5)), env) == True
        assert evaluator.eval(BinaryOpTerm(">=", LiteralTerm(4), LiteralTerm(5)), env) == False
    
    # Logical operators
    
    def test_eval_and(self, evaluator, env):
        """Evaluate logical and."""
        logger.info("Testing and")
        assert evaluator.eval(BinaryOpTerm("and", LiteralTerm(True), LiteralTerm(True)), env) == True
        assert evaluator.eval(BinaryOpTerm("and", LiteralTerm(True), LiteralTerm(False)), env) == False
        assert evaluator.eval(BinaryOpTerm("and", LiteralTerm(False), LiteralTerm(True)), env) == False
    
    def test_eval_or(self, evaluator, env):
        """Evaluate logical or."""
        logger.info("Testing or")
        assert evaluator.eval(BinaryOpTerm("or", LiteralTerm(False), LiteralTerm(True)), env) == True
        assert evaluator.eval(BinaryOpTerm("or", LiteralTerm(True), LiteralTerm(False)), env) == True
        assert evaluator.eval(BinaryOpTerm("or", LiteralTerm(False), LiteralTerm(False)), env) == False
    
    def test_eval_and_short_circuit(self, evaluator, env):
        """And should short-circuit."""
        logger.info("Testing and short-circuit")
        # If left is False, right should not be evaluated
        # Using division by zero to detect if right is evaluated
        right = BinaryOpTerm("/", LiteralTerm(1), LiteralTerm(0))
        term = BinaryOpTerm("and", LiteralTerm(False), right)
        # Should not raise - right not evaluated
        assert evaluator.eval(term, env) == False
    
    def test_eval_or_short_circuit(self, evaluator, env):
        """Or should short-circuit."""
        logger.info("Testing or short-circuit")
        right = BinaryOpTerm("/", LiteralTerm(1), LiteralTerm(0))
        term = BinaryOpTerm("or", LiteralTerm(True), right)
        # Should not raise - right not evaluated
        assert evaluator.eval(term, env) == True
    
    # Unary operators
    
    def test_eval_negate(self, evaluator, env):
        """Evaluate unary negation."""
        logger.info("Testing unary -")
        term = UnaryOpTerm("-", LiteralTerm(42))
        assert evaluator.eval(term, env) == -42
    
    def test_eval_not(self, evaluator, env):
        """Evaluate logical not."""
        logger.info("Testing not")
        assert evaluator.eval(UnaryOpTerm("not", LiteralTerm(True)), env) == False
        assert evaluator.eval(UnaryOpTerm("not", LiteralTerm(False)), env) == True
    
    def test_unknown_binary_op_raises(self, evaluator, env):
        """Unknown binary operator raises error."""
        logger.info("Testing unknown binary op")
        term = BinaryOpTerm("???", LiteralTerm(1), LiteralTerm(2))
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Unknown binary operator" in str(exc_info.value)
    
    def test_unknown_unary_op_raises(self, evaluator, env):
        """Unknown unary operator raises error."""
        logger.info("Testing unknown unary op")
        term = UnaryOpTerm("???", LiteralTerm(1))
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Unknown unary operator" in str(exc_info.value)


# ============================================================================
# TermEvaluator Tests - Complex Terms
# ============================================================================

class TestTermEvaluatorComplex:
    """Tests for complex term evaluation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    @pytest.fixture
    def evaluator(self):
        types = TypeRegistry()
        types.register(Domain("Load"))
        types.register(Domain("Event"))
        state = ASMState(types)
        return TermEvaluator(state, types)
    
    @pytest.fixture
    def env(self):
        return Environment()
    
    def test_eval_list_empty(self, evaluator, env):
        """Evaluate empty list."""
        logger.info("Testing empty list")
        term = ListTerm(())
        assert evaluator.eval(term, env) == []
    
    def test_eval_list_with_literals(self, evaluator, env):
        """Evaluate list with literals."""
        logger.info("Testing list with literals")
        term = ListTerm((LiteralTerm(1), LiteralTerm(2), LiteralTerm(3)))
        assert evaluator.eval(term, env) == [1, 2, 3]
    
    def test_eval_list_with_variables(self, evaluator, env):
        """Evaluate list with variables."""
        logger.info("Testing list with variables")
        env.bind("a", 10)
        env.bind("b", 20)
        term = ListTerm((VariableTerm("a"), VariableTerm("b")))
        assert evaluator.eval(term, env) == [10, 20]
    
    def test_eval_new(self, evaluator, env):
        """Evaluate new expression."""
        logger.info("Testing new")
        term = NewTerm("Load")
        result = evaluator.eval(term, env)
        assert isinstance(result, ASMObject)
        assert result.domain == "Load"
        logger.debug(f"Created: {result}")
    
    def test_eval_new_unknown_domain_raises(self, evaluator, env):
        """New with unknown domain raises error."""
        logger.info("Testing new unknown domain")
        term = NewTerm("UnknownDomain")
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Unknown domain" in str(exc_info.value)
    
    def test_eval_conditional_true(self, evaluator, env):
        """Evaluate conditional when true."""
        logger.info("Testing conditional true")
        term = ConditionalTerm(
            LiteralTerm(True),
            LiteralTerm(1),
            LiteralTerm(2)
        )
        assert evaluator.eval(term, env) == 1
    
    def test_eval_conditional_false(self, evaluator, env):
        """Evaluate conditional when false."""
        logger.info("Testing conditional false")
        term = ConditionalTerm(
            LiteralTerm(False),
            LiteralTerm(1),
            LiteralTerm(2)
        )
        assert evaluator.eval(term, env) == 2
    
    def test_eval_conditional_short_circuit(self, evaluator, env):
        """Conditional should only evaluate chosen branch."""
        logger.info("Testing conditional short-circuit")
        # then branch has division by zero
        then_expr = BinaryOpTerm("/", LiteralTerm(1), LiteralTerm(0))
        term = ConditionalTerm(
            LiteralTerm(False),
            then_expr,
            LiteralTerm(42)
        )
        # Should not raise - then branch not evaluated
        assert evaluator.eval(term, env) == 42
    
    def test_eval_nested_expression(self, evaluator, env):
        """Evaluate complex nested expression."""
        logger.info("Testing nested expression")
        # (10 + 5) * 2 - 3
        inner = BinaryOpTerm("+", LiteralTerm(10), LiteralTerm(5))
        mult = BinaryOpTerm("*", inner, LiteralTerm(2))
        term = BinaryOpTerm("-", mult, LiteralTerm(3))
        assert evaluator.eval(term, env) == 27


# ============================================================================
# TermEvaluator Tests - Library Calls
# ============================================================================

class TestTermEvaluatorLibCall:
    """Tests for library call evaluation."""
    
    @pytest.fixture
    def evaluator(self):
        types = TypeRegistry()
        state = ASMState(types)
        evaluator = TermEvaluator(state, types)
        evaluator.set_stdlib(MockStdLib())
        return evaluator
    
    @pytest.fixture
    def env(self):
        return Environment()
    
    def test_eval_lib_length(self, evaluator, env):
        """Evaluate lib.length."""
        logger.info("Testing lib.length")
        env.bind("queue", [1, 2, 3, 4, 5])
        term = LibCallTerm("length", (VariableTerm("queue"),))
        assert evaluator.eval(term, env) == 5
    
    def test_eval_lib_add(self, evaluator, env):
        """Evaluate lib.add (modifies list)."""
        logger.info("Testing lib.add")
        lst = [1, 2]
        env.bind("lst", lst)
        term = LibCallTerm("add", (VariableTerm("lst"), LiteralTerm(3)))
        result = evaluator.eval(term, env)
        assert result is None
        assert lst == [1, 2, 3]
    
    def test_eval_lib_get(self, evaluator, env):
        """Evaluate lib.get."""
        logger.info("Testing lib.get")
        env.bind("lst", [10, 20, 30])
        term = LibCallTerm("get", (VariableTerm("lst"), LiteralTerm(1)))
        assert evaluator.eval(term, env) == 20
    
    def test_eval_lib_sum(self, evaluator, env):
        """Evaluate lib.sum."""
        logger.info("Testing lib.sum")
        env.bind("nums", [1, 2, 3, 4, 5])
        term = LibCallTerm("sum", (VariableTerm("nums"),))
        assert evaluator.eval(term, env) == 15
    
    def test_eval_lib_unknown_raises(self, evaluator, env):
        """Unknown library function raises error."""
        logger.info("Testing unknown lib function")
        term = LibCallTerm("unknown_function", ())
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Unknown library function" in str(exc_info.value)
    
    def test_eval_lib_without_stdlib_raises(self, env):
        """Library call without stdlib raises error."""
        logger.info("Testing lib call without stdlib")
        types = TypeRegistry()
        state = ASMState(types)
        evaluator = TermEvaluator(state, types)  # No stdlib set
        
        term = LibCallTerm("length", (LiteralTerm([1, 2, 3]),))
        with pytest.raises(TermEvaluationError) as exc_info:
            evaluator.eval(term, env)
        assert "Standard library not set" in str(exc_info.value)


# ============================================================================
# Integration Tests
# ============================================================================

class TestTermsIntegration:
    """Integration tests for terms module."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        ASMObject.reset_counters()
        yield
        ASMObject.reset_counters()
    
    def test_simulate_queue_check(self):
        """Simulate checking if queue is empty."""
        logger.info("Testing queue check simulation")
        types = TypeRegistry()
        state = ASMState(types)
        evaluator = TermEvaluator(state, types)
        evaluator.set_stdlib(MockStdLib())
        
        env = Environment()
        queue = [1, 2, 3]
        env.bind("queue", queue)
        
        # lib.length(queue) == 0
        len_call = LibCallTerm("length", (VariableTerm("queue"),))
        is_empty = BinaryOpTerm("==", len_call, LiteralTerm(0))
        
        assert evaluator.eval(is_empty, env) == False
        
        # Empty the queue
        queue.clear()
        assert evaluator.eval(is_empty, env) == True
        logger.debug("Queue check simulation complete")
    
    def test_simulate_object_creation_and_lookup(self):
        """Simulate creating objects and storing data."""
        logger.info("Testing object creation simulation")
        types = TypeRegistry()
        types.register(Domain("Load"))
        state = ASMState(types)
        evaluator = TermEvaluator(state, types)
        
        env = Environment()
        
        # Create load
        new_load = NewTerm("Load")
        load = evaluator.eval(new_load, env)
        
        # Store in state
        state.set_func("status", (load,), "waiting")
        state.set_func("arrival_time", (load,), 10.5)
        
        # Bind to environment
        env.bind("load", load)
        
        # Look up status(load)
        status_term = LocationTerm("status", (VariableTerm("load"),))
        assert evaluator.eval(status_term, env) == "waiting"
        
        # Look up arrival_time(load)
        time_term = LocationTerm("arrival_time", (VariableTerm("load"),))
        assert evaluator.eval(time_term, env) == 10.5
        logger.debug("Object creation simulation complete")
    
    def test_simulate_conditional_dispatch(self):
        """Simulate conditional logic based on state."""
        logger.info("Testing conditional dispatch simulation")
        types = TypeRegistry()
        state = ASMState(types)
        state.set_var("server_busy", False)
        state.set_var("queue_length", 3)
        
        evaluator = TermEvaluator(state, types)
        env = Environment()
        
        # if not server_busy and queue_length > 0 then "start" else "wait"
        not_busy = UnaryOpTerm("not", LocationTerm("server_busy"))
        has_work = BinaryOpTerm(">", LocationTerm("queue_length"), LiteralTerm(0))
        can_start = BinaryOpTerm("and", not_busy, has_work)
        
        action = ConditionalTerm(
            can_start,
            LiteralTerm("start"),
            LiteralTerm("wait")
        )
        
        assert evaluator.eval(action, env) == "start"
        
        # Now server is busy
        state.set_var("server_busy", True)
        assert evaluator.eval(action, env) == "wait"
        logger.debug("Conditional dispatch simulation complete")
