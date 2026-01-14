"""
Tests for simasm/runtime/random.py

Section 9: Random number generation (rnd.*)

Test categories:
1. RandomStream - creation and seeding
2. RandomStream - continuous distributions
3. RandomStream - discrete distributions
4. RandomStream - utility functions
5. RandomRegistry - stream management
6. RandomRegistry - seeding operations
7. Reproducibility tests
8. Error handling
"""

import pytest
import math
from typing import List

from simasm.runtime.random import (
    RandomStream, RandomRegistry, RandomError,
    get_default_registry, reset_default_registry,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def stream():
    """RandomStream with fixed seed for reproducibility."""
    return RandomStream(seed=42)


@pytest.fixture
def registry():
    """Fresh RandomRegistry."""
    return RandomRegistry()


@pytest.fixture(autouse=True)
def reset_global():
    """Reset global registry between tests."""
    reset_default_registry()
    yield
    reset_default_registry()


# ============================================================================
# Helper Functions
# ============================================================================

def mean(values: List[float]) -> float:
    """Calculate mean of values."""
    return sum(values) / len(values)


def variance(values: List[float]) -> float:
    """Calculate variance of values."""
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)


def std(values: List[float]) -> float:
    """Calculate standard deviation."""
    return math.sqrt(variance(values))


# ============================================================================
# 1. RandomStream - Creation and Seeding
# ============================================================================

class TestRandomStreamCreation:
    """Test RandomStream creation and seeding."""
    
    def test_create_with_seed(self):
        """Create stream with explicit seed."""
        stream = RandomStream(seed=42)
        assert stream.seed == 42
    
    def test_create_without_seed(self):
        """Create stream without seed."""
        stream = RandomStream()
        assert stream.seed is None
    
    def test_set_seed(self):
        """Set seed after creation."""
        stream = RandomStream()
        stream.set_seed(123)
        assert stream.seed == 123
    
    def test_reset_restores_sequence(self):
        """Reset restores random sequence."""
        stream = RandomStream(seed=42)
        
        # Generate some values
        values1 = [stream.random() for _ in range(5)]
        
        # Reset and regenerate
        stream.reset()
        values2 = [stream.random() for _ in range(5)]
        
        assert values1 == values2
    
    def test_same_seed_same_sequence(self):
        """Same seed produces same sequence."""
        stream1 = RandomStream(seed=42)
        stream2 = RandomStream(seed=42)
        
        values1 = [stream1.random() for _ in range(10)]
        values2 = [stream2.random() for _ in range(10)]
        
        assert values1 == values2
    
    def test_different_seed_different_sequence(self):
        """Different seeds produce different sequences."""
        stream1 = RandomStream(seed=42)
        stream2 = RandomStream(seed=43)
        
        values1 = [stream1.random() for _ in range(10)]
        values2 = [stream2.random() for _ in range(10)]
        
        assert values1 != values2


# ============================================================================
# 2. RandomStream - Continuous Distributions
# ============================================================================

class TestUniform:
    """Test uniform distribution."""
    
    def test_uniform_range(self, stream):
        """Uniform values are in range."""
        for _ in range(100):
            val = stream.uniform(5, 10)
            assert 5 <= val <= 10
    
    def test_uniform_mean(self, stream):
        """Uniform mean is approximately (a+b)/2."""
        values = [stream.uniform(0, 10) for _ in range(10000)]
        assert 4.5 < mean(values) < 5.5  # Expected: 5
    
    def test_uniform_degenerate(self, stream):
        """Uniform with a == b returns a."""
        val = stream.uniform(5, 5)
        assert val == 5
    
    def test_uniform_invalid_range(self, stream):
        """Uniform with a > b raises error."""
        with pytest.raises(RandomError, match="must be <="):
            stream.uniform(10, 5)


class TestExponential:
    """Test exponential distribution."""
    
    def test_exponential_positive(self, stream):
        """Exponential values are positive."""
        for _ in range(100):
            val = stream.exponential(10)
            assert val > 0
    
    def test_exponential_mean(self, stream):
        """Exponential mean is approximately the given mean."""
        values = [stream.exponential(10) for _ in range(10000)]
        assert 9 < mean(values) < 11  # Expected: 10
    
    def test_exponential_zero_mean_error(self, stream):
        """Exponential with mean <= 0 raises error."""
        with pytest.raises(RandomError, match="must be > 0"):
            stream.exponential(0)
        with pytest.raises(RandomError, match="must be > 0"):
            stream.exponential(-5)


class TestNormal:
    """Test normal distribution."""
    
    def test_normal_mean(self, stream):
        """Normal mean is approximately the given mean."""
        values = [stream.normal(100, 15) for _ in range(10000)]
        assert 98 < mean(values) < 102  # Expected: 100
    
    def test_normal_std(self, stream):
        """Normal std is approximately the given std."""
        values = [stream.normal(0, 10) for _ in range(10000)]
        assert 9 < std(values) < 11  # Expected: 10
    
    def test_normal_zero_std(self, stream):
        """Normal with std=0 returns mean."""
        values = [stream.normal(50, 0) for _ in range(10)]
        assert all(v == 50 for v in values)
    
    def test_normal_negative_std_error(self, stream):
        """Normal with negative std raises error."""
        with pytest.raises(RandomError, match="must be >= 0"):
            stream.normal(0, -5)


class TestTriangular:
    """Test triangular distribution."""
    
    def test_triangular_range(self, stream):
        """Triangular values are in range."""
        for _ in range(100):
            val = stream.triangular(1, 5, 3)
            assert 1 <= val <= 5
    
    def test_triangular_mode(self, stream):
        """Triangular most common around mode."""
        values = [stream.triangular(0, 10, 8) for _ in range(10000)]
        # Mean should be (a + b + c) / 3 = (0 + 10 + 8) / 3 = 6
        assert 5.5 < mean(values) < 6.5
    
    def test_triangular_invalid_mode(self, stream):
        """Triangular with invalid mode raises error."""
        with pytest.raises(RandomError, match="low <= mode <= high"):
            stream.triangular(5, 10, 3)  # mode < low


class TestOtherContinuous:
    """Test other continuous distributions."""
    
    def test_lognormal_positive(self, stream):
        """Lognormal values are positive."""
        for _ in range(100):
            val = stream.lognormal(0, 1)
            assert val > 0
    
    def test_weibull_positive(self, stream):
        """Weibull values are positive."""
        for _ in range(100):
            val = stream.weibull(2, 3)
            assert val > 0
    
    def test_gamma_positive(self, stream):
        """Gamma values are positive."""
        for _ in range(100):
            val = stream.gamma(2, 3)
            assert val > 0
    
    def test_beta_range(self, stream):
        """Beta values are in [0, 1]."""
        for _ in range(100):
            val = stream.beta(2, 5)
            assert 0 <= val <= 1


# ============================================================================
# 3. RandomStream - Discrete Distributions
# ============================================================================

class TestRandint:
    """Test randint distribution."""
    
    def test_randint_range(self, stream):
        """Randint values are in range."""
        for _ in range(100):
            val = stream.randint(1, 6)
            assert 1 <= val <= 6
            assert isinstance(val, int)
    
    def test_randint_single_value(self, stream):
        """Randint with a == b returns a."""
        val = stream.randint(5, 5)
        assert val == 5
    
    def test_randint_invalid_range(self, stream):
        """Randint with a > b raises error."""
        with pytest.raises(RandomError, match="must be <="):
            stream.randint(10, 5)


class TestChoice:
    """Test choice function."""
    
    def test_choice_returns_element(self, stream):
        """Choice returns element from sequence."""
        options = ["a", "b", "c"]
        for _ in range(100):
            val = stream.choice(options)
            assert val in options
    
    def test_choice_single_element(self, stream):
        """Choice from single-element list returns that element."""
        val = stream.choice([42])
        assert val == 42
    
    def test_choice_empty_error(self, stream):
        """Choice from empty sequence raises error."""
        with pytest.raises(RandomError, match="empty"):
            stream.choice([])


class TestBernoulli:
    """Test Bernoulli distribution."""
    
    def test_bernoulli_returns_bool(self, stream):
        """Bernoulli returns boolean."""
        val = stream.bernoulli(0.5)
        assert isinstance(val, bool)
    
    def test_bernoulli_probability(self, stream):
        """Bernoulli frequency matches probability."""
        successes = sum(stream.bernoulli(0.7) for _ in range(10000))
        rate = successes / 10000
        assert 0.67 < rate < 0.73  # Expected: 0.7
    
    def test_bernoulli_zero(self, stream):
        """Bernoulli with p=0 always returns False."""
        results = [stream.bernoulli(0) for _ in range(100)]
        assert all(not r for r in results)
    
    def test_bernoulli_one(self, stream):
        """Bernoulli with p=1 always returns True."""
        results = [stream.bernoulli(1) for _ in range(100)]
        assert all(r for r in results)
    
    def test_bernoulli_invalid_p(self, stream):
        """Bernoulli with invalid p raises error."""
        with pytest.raises(RandomError, match="must be in"):
            stream.bernoulli(-0.1)
        with pytest.raises(RandomError, match="must be in"):
            stream.bernoulli(1.1)


class TestGeometric:
    """Test geometric distribution."""
    
    def test_geometric_positive(self, stream):
        """Geometric values are >= 1."""
        for _ in range(100):
            val = stream.geometric(0.3)
            assert val >= 1
            assert isinstance(val, int)
    
    def test_geometric_mean(self, stream):
        """Geometric mean is approximately 1/p."""
        values = [stream.geometric(0.5) for _ in range(10000)]
        # Expected mean = 1/0.5 = 2
        assert 1.8 < mean(values) < 2.2


class TestPoisson:
    """Test Poisson distribution."""
    
    def test_poisson_non_negative(self, stream):
        """Poisson values are >= 0."""
        for _ in range(100):
            val = stream.poisson(5)
            assert val >= 0
            assert isinstance(val, int)
    
    def test_poisson_mean(self, stream):
        """Poisson mean is approximately lambda."""
        values = [stream.poisson(5) for _ in range(10000)]
        assert 4.7 < mean(values) < 5.3  # Expected: 5


# ============================================================================
# 4. RandomStream - Utility Functions
# ============================================================================

class TestUtility:
    """Test utility functions."""
    
    def test_random_range(self, stream):
        """Random returns values in [0, 1)."""
        for _ in range(100):
            val = stream.random()
            assert 0 <= val < 1
    
    def test_shuffle_modifies_list(self, stream):
        """Shuffle modifies list in place."""
        lst = [1, 2, 3, 4, 5]
        original = lst.copy()
        stream.shuffle(lst)
        
        # Same elements, possibly different order
        assert sorted(lst) == sorted(original)
    
    def test_shuffle_reproducible(self):
        """Shuffle is reproducible with same seed."""
        stream1 = RandomStream(seed=42)
        stream2 = RandomStream(seed=42)
        
        lst1 = [1, 2, 3, 4, 5]
        lst2 = [1, 2, 3, 4, 5]
        
        stream1.shuffle(lst1)
        stream2.shuffle(lst2)
        
        assert lst1 == lst2
    
    def test_sample_size(self, stream):
        """Sample returns correct number of items."""
        population = list(range(100))
        result = stream.sample(population, 10)
        assert len(result) == 10
    
    def test_sample_no_duplicates(self, stream):
        """Sample has no duplicates."""
        population = list(range(100))
        result = stream.sample(population, 10)
        assert len(result) == len(set(result))
    
    def test_sample_k_too_large(self, stream):
        """Sample with k > population size raises error."""
        with pytest.raises(RandomError, match="exceeds population"):
            stream.sample([1, 2, 3], 5)


# ============================================================================
# 5. RandomRegistry - Stream Management
# ============================================================================

class TestRegistryManagement:
    """Test RandomRegistry stream management."""
    
    def test_create_stream(self, registry):
        """Create named stream."""
        stream = registry.create("arrivals", seed=42)
        assert stream is not None
        assert stream.seed == 42
    
    def test_get_stream(self, registry):
        """Get existing stream."""
        registry.create("arrivals", seed=42)
        stream = registry.get("arrivals")
        assert stream is not None
    
    def test_get_missing_stream_error(self, registry):
        """Get non-existent stream raises error."""
        with pytest.raises(RandomError, match="not found"):
            registry.get("nonexistent")
    
    def test_exists(self, registry):
        """Check stream existence."""
        registry.create("arrivals")
        assert registry.exists("arrivals") is True
        assert registry.exists("nonexistent") is False
    
    def test_contains(self, registry):
        """Contains operator works."""
        registry.create("arrivals")
        assert "arrivals" in registry
        assert "nonexistent" not in registry
    
    def test_len(self, registry):
        """Length returns number of streams."""
        assert len(registry) == 0
        registry.create("a")
        assert len(registry) == 1
        registry.create("b")
        assert len(registry) == 2
    
    def test_all_streams(self, registry):
        """Get all stream names."""
        registry.create("arrivals")
        registry.create("service")
        names = registry.all_streams()
        assert set(names) == {"arrivals", "service"}
    
    def test_create_duplicate_error(self, registry):
        """Create duplicate stream raises error."""
        registry.create("arrivals")
        with pytest.raises(RandomError, match="already exists"):
            registry.create("arrivals")
    
    def test_clear(self, registry):
        """Clear removes all streams."""
        registry.create("a")
        registry.create("b")
        registry.clear()
        assert len(registry) == 0


# ============================================================================
# 6. RandomRegistry - Seeding Operations
# ============================================================================

class TestRegistrySeeding:
    """Test RandomRegistry seeding operations."""
    
    def test_set_seed(self, registry):
        """Set seed for specific stream."""
        registry.create("arrivals", seed=1)
        registry.set_seed("arrivals", 42)
        
        stream = registry.get("arrivals")
        assert stream.seed == 42
    
    def test_set_all_seeds(self, registry):
        """Set all seeds from base seed."""
        registry.create("arrivals")
        registry.create("service")
        registry.create("routing")
        
        registry.set_all_seeds(base_seed=12345)
        
        # All streams should now have seeds
        for name in registry.all_streams():
            stream = registry.get(name)
            assert stream.seed is not None
    
    def test_set_all_seeds_reproducible(self):
        """set_all_seeds is reproducible."""
        reg1 = RandomRegistry()
        reg1.create("a")
        reg1.create("b")
        reg1.set_all_seeds(42)
        
        reg2 = RandomRegistry()
        reg2.create("a")
        reg2.create("b")
        reg2.set_all_seeds(42)
        
        # Both should produce same sequences
        vals1 = [reg1.get("a").random() for _ in range(5)]
        vals2 = [reg2.get("a").random() for _ in range(5)]
        assert vals1 == vals2
    
    def test_reset_single(self, registry):
        """Reset single stream."""
        registry.create("arrivals", seed=42)
        stream = registry.get("arrivals")
        
        val1 = stream.random()
        val2 = stream.random()
        
        registry.reset("arrivals")
        
        assert stream.random() == val1
        assert stream.random() == val2
    
    def test_reset_all(self, registry):
        """Reset all streams."""
        registry.create("arrivals", seed=42)
        registry.create("service", seed=123)
        
        # Generate some values
        registry.get("arrivals").random()
        registry.get("service").random()
        
        # Reset all
        registry.reset_all()
        
        # Should start from beginning again
        stream1 = RandomStream(seed=42)
        stream2 = RandomStream(seed=123)
        
        assert registry.get("arrivals").random() == stream1.random()
        assert registry.get("service").random() == stream2.random()


# ============================================================================
# 7. Reproducibility Tests
# ============================================================================

class TestReproducibility:
    """Test reproducibility for simulation replications."""
    
    def test_multiple_replications(self):
        """Simulate multiple replications with reset."""
        stream = RandomStream(seed=42)
        
        # Replication 1
        rep1_values = [stream.exponential(10) for _ in range(100)]
        
        # Reset for replication 2
        stream.reset()
        rep2_values = [stream.exponential(10) for _ in range(100)]
        
        assert rep1_values == rep2_values
    
    def test_independent_streams(self):
        """Independent streams don't affect each other."""
        registry = RandomRegistry()
        registry.create("arrivals", seed=42)
        registry.create("service", seed=42)  # Same seed
        
        arrivals = registry.get("arrivals")
        service = registry.get("service")
        
        # Generate from arrivals
        arrivals.random()
        arrivals.random()
        arrivals.random()
        
        # Service should still be at start of its sequence
        fresh = RandomStream(seed=42)
        assert service.random() == fresh.random()
    
    def test_deterministic_simulation_pattern(self):
        """Pattern for deterministic DES simulation."""
        registry = RandomRegistry()
        registry.create("interarrival", seed=1)
        registry.create("service", seed=2)
        
        def simulate_arrivals(n):
            stream = registry.get("interarrival")
            return [stream.exponential(10) for _ in range(n)]
        
        def simulate_service(n):
            stream = registry.get("service")
            return [stream.exponential(8) for _ in range(n)]
        
        # Run 1
        arrivals1 = simulate_arrivals(10)
        services1 = simulate_service(10)
        
        # Reset for run 2
        registry.reset_all()
        arrivals2 = simulate_arrivals(10)
        services2 = simulate_service(10)
        
        assert arrivals1 == arrivals2
        assert services1 == services2


# ============================================================================
# 8. Default Registry
# ============================================================================

class TestDefaultRegistry:
    """Test default global registry."""
    
    def test_get_default_registry(self):
        """Get default registry."""
        reg = get_default_registry()
        assert isinstance(reg, RandomRegistry)
    
    def test_default_registry_singleton(self):
        """Default registry is singleton."""
        reg1 = get_default_registry()
        reg2 = get_default_registry()
        assert reg1 is reg2
    
    def test_reset_default_registry(self):
        """Reset default registry."""
        reg1 = get_default_registry()
        reg1.create("test")
        
        reset_default_registry()
        
        reg2 = get_default_registry()
        assert reg2 is not reg1
        assert len(reg2) == 0


# ============================================================================
# 9. Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for DES patterns."""
    
    def test_mm1_queue_pattern(self):
        """M/M/1 queue arrival and service times."""
        registry = RandomRegistry()
        registry.create("arrivals", seed=42)
        registry.create("service", seed=123)
        
        arrival_rate = 0.8  # arrivals per time unit
        service_rate = 1.0  # services per time unit
        
        arrivals = registry.get("arrivals")
        service = registry.get("service")
        
        # Generate interarrival and service times
        interarrivals = [arrivals.exponential(1/arrival_rate) for _ in range(100)]
        service_times = [service.exponential(1/service_rate) for _ in range(100)]
        
        # Check means are reasonable
        assert 0.8 / arrival_rate < mean(interarrivals) < 1.5 / arrival_rate
        assert 0.8 / service_rate < mean(service_times) < 1.5 / service_rate
    
    def test_branching_with_bernoulli(self):
        """Use Bernoulli for routing decisions."""
        stream = RandomStream(seed=42)
        
        route_a_prob = 0.6
        routes = []
        
        for _ in range(1000):
            if stream.bernoulli(route_a_prob):
                routes.append("A")
            else:
                routes.append("B")
        
        a_count = routes.count("A")
        rate = a_count / len(routes)
        assert 0.55 < rate < 0.65  # Should be around 0.6
    
    def test_batch_arrivals_with_poisson(self):
        """Use Poisson for batch sizes."""
        stream = RandomStream(seed=42)
        
        batch_sizes = [stream.poisson(5) for _ in range(100)]
        
        assert 4 < mean(batch_sizes) < 6  # Expected: 5
        assert all(b >= 0 for b in batch_sizes)
