"""
test_001_types_v1.py

Unit tests for simasm/core/types.py

Tests:
- Domain dataclass
- TypeRegistry registration
- Subtype checking
- Ancestor retrieval
"""

import pytest
from simasm.core.types import Domain, TypeRegistry, BUILTIN_TYPES
from simasm.log.logger import get_logger

logger = get_logger(__name__)


class TestDomain:
    """Tests for Domain dataclass."""
    
    def test_domain_without_parent(self):
        """Domain with no parent."""
        logger.info("Testing domain without parent")
        d = Domain("Object")
        assert d.name == "Object"
        assert d.parent is None
        logger.debug(f"Created domain: {d}")
    
    def test_domain_with_parent(self):
        """Domain with parent."""
        logger.info("Testing domain with parent")
        d = Domain("Load", "Object")
        assert d.name == "Load"
        assert d.parent == "Object"
        logger.debug(f"Created domain: {d}")
    
    def test_domain_is_frozen(self):
        """Domain should be immutable."""
        logger.info("Testing domain immutability")
        d = Domain("Object")
        with pytest.raises(AttributeError):
            d.name = "Changed"
        logger.debug("Domain correctly rejected mutation")
    
    def test_domain_equality(self):
        """Same name and parent should be equal."""
        logger.info("Testing domain equality")
        d1 = Domain("Load", "Object")
        d2 = Domain("Load", "Object")
        assert d1 == d2
        logger.debug(f"Domains are equal: {d1} == {d2}")
    
    def test_domain_inequality(self):
        """Different domains should not be equal."""
        logger.info("Testing domain inequality")
        d1 = Domain("Load", "Object")
        d2 = Domain("Event", "Object")
        assert d1 != d2
        logger.debug(f"Domains are not equal: {d1} != {d2}")
    
    def test_domain_hashable(self):
        """Domain should be usable in sets/dicts."""
        logger.info("Testing domain hashability")
        d = Domain("Load", "Object")
        s = {d}
        assert d in s
        logger.debug(f"Domain {d} is hashable and found in set")


class TestBuiltinTypes:
    """Tests for built-in types."""
    
    def test_builtin_types_exist(self):
        """Check all expected built-in types are defined."""
        logger.info("Testing built-in types existence")
        expected = {"Nat", "Int", "Real", "Bool", "String", "List", "Any", "Rule"}
        assert expected == BUILTIN_TYPES
        logger.debug(f"Built-in types: {BUILTIN_TYPES}")
    
    def test_builtins_registered(self):
        """Built-in types should be pre-registered."""
        logger.info("Testing built-ins pre-registration")
        reg = TypeRegistry()
        for builtin in BUILTIN_TYPES:
            assert reg.exists(builtin), f"Built-in {builtin} not registered"
        logger.debug("All built-in types are pre-registered")


class TestTypeRegistryRegistration:
    """Tests for TypeRegistry.register()."""
    
    def test_register_simple_domain(self, empty_registry):
        """Register domain without parent."""
        logger.info("Testing simple domain registration")
        empty_registry.register(Domain("Object"))
        assert empty_registry.exists("Object")
        logger.debug("Domain 'Object' registered successfully")
    
    def test_register_domain_with_parent(self, empty_registry):
        """Register domain with parent."""
        logger.info("Testing domain registration with parent")
        empty_registry.register(Domain("Object"))
        empty_registry.register(Domain("Load", "Object"))
        assert empty_registry.exists("Load")
        assert empty_registry.get("Load").parent == "Object"
        logger.debug("Domain 'Load' with parent 'Object' registered successfully")
    
    def test_register_chain(self, empty_registry):
        """Register chain of domains."""
        logger.info("Testing domain chain registration")
        empty_registry.register(Domain("Object"))
        empty_registry.register(Domain("Event", "Object"))
        empty_registry.register(Domain("ArriveEvent", "Event"))
        
        assert empty_registry.exists("Object")
        assert empty_registry.exists("Event")
        assert empty_registry.exists("ArriveEvent")
        logger.debug("Domain chain registered: Object -> Event -> ArriveEvent")
    
    def test_register_duplicate_raises(self, empty_registry):
        """Registering same domain twice should raise."""
        logger.info("Testing duplicate registration error")
        empty_registry.register(Domain("Object"))
        with pytest.raises(ValueError, match="already registered"):
            empty_registry.register(Domain("Object"))
        logger.debug("Duplicate registration correctly raised ValueError")
    
    def test_register_missing_parent_raises(self, empty_registry):
        """Registering domain with unknown parent should raise."""
        logger.info("Testing missing parent error")
        with pytest.raises(ValueError, match="not registered"):
            empty_registry.register(Domain("Load", "Object"))
        logger.debug("Missing parent registration correctly raised ValueError")
    
    def test_register_extend_builtin(self, empty_registry):
        """Should allow extending built-in types."""
        logger.info("Testing extending built-in type")
        empty_registry.register(Domain("PositiveReal", "Real"))
        assert empty_registry.exists("PositiveReal")
        assert empty_registry.get("PositiveReal").parent == "Real"
        logger.debug("Extended built-in 'Real' with 'PositiveReal'")
    
    def test_register_extend_builtin_nat(self, empty_registry):
        """Should allow extending Nat."""
        logger.info("Testing extending Nat")
        empty_registry.register(Domain("Counter", "Nat"))
        assert empty_registry.exists("Counter")
        assert empty_registry.is_subtype("Counter", "Nat")
        logger.debug("Extended built-in 'Nat' with 'Counter'")


class TestTypeRegistrySubtype:
    """Tests for TypeRegistry.is_subtype()."""
    
    def test_is_subtype_reflexive(self, empty_registry):
        """A domain is subtype of itself."""
        logger.info("Testing reflexive subtype")
        empty_registry.register(Domain("Object"))
        assert empty_registry.is_subtype("Object", "Object")
        logger.debug("Object <: Object is True (reflexive)")
    
    def test_is_subtype_builtin_reflexive(self, empty_registry):
        """Built-in types are subtypes of themselves."""
        logger.info("Testing built-in reflexive subtype")
        assert empty_registry.is_subtype("Nat", "Nat")
        assert empty_registry.is_subtype("Real", "Real")
        logger.debug("Built-ins are subtypes of themselves")
    
    def test_is_subtype_direct_parent(self, empty_registry):
        """Direct child is subtype of parent."""
        logger.info("Testing direct parent subtype")
        empty_registry.register(Domain("Object"))
        empty_registry.register(Domain("Load", "Object"))
        assert empty_registry.is_subtype("Load", "Object")
        assert not empty_registry.is_subtype("Object", "Load")
        logger.debug("Load <: Object is True, Object <: Load is False")
    
    def test_is_subtype_transitive(self, populated_registry):
        """Transitive subtyping: A <: B <: C implies A <: C."""
        logger.info("Testing transitive subtype")
        # ArriveEvent <: Event <: Object
        assert populated_registry.is_subtype("ArriveEvent", "Event")
        assert populated_registry.is_subtype("ArriveEvent", "Object")
        assert populated_registry.is_subtype("Event", "Object")
        logger.debug("Transitive subtyping works correctly")
    
    def test_is_subtype_unrelated(self, populated_registry):
        """Unrelated domains are not subtypes."""
        logger.info("Testing unrelated domains")
        assert not populated_registry.is_subtype("Load", "Event")
        assert not populated_registry.is_subtype("Event", "Load")
        assert not populated_registry.is_subtype("ArriveEvent", "Load")
        logger.debug("Unrelated domains are not subtypes")
    
    def test_is_subtype_siblings(self, populated_registry):
        """Sibling domains are not subtypes of each other."""
        logger.info("Testing sibling domains")
        # ArriveEvent and StartEvent are both <: Event
        assert not populated_registry.is_subtype("ArriveEvent", "StartEvent")
        assert not populated_registry.is_subtype("StartEvent", "ArriveEvent")
        logger.debug("Siblings are not subtypes of each other")
    
    def test_is_subtype_unknown_domain(self, empty_registry):
        """Unknown domain returns False."""
        logger.info("Testing unknown domain subtype")
        assert not empty_registry.is_subtype("Unknown", "Object")
        assert not empty_registry.is_subtype("Nat", "Unknown")
        logger.debug("Unknown domains return False")


class TestTypeRegistryHelpers:
    """Tests for TypeRegistry helper methods."""
    
    def test_is_builtin(self, empty_registry):
        """Check built-in type detection."""
        logger.info("Testing is_builtin")
        assert empty_registry.is_builtin("Nat")
        assert empty_registry.is_builtin("Real")
        assert empty_registry.is_builtin("Rule")
        assert not empty_registry.is_builtin("Object")
        assert not empty_registry.is_builtin("Unknown")
        logger.debug("is_builtin correctly identifies built-in types")
    
    def test_get_existing(self, populated_registry):
        """Get existing domain."""
        logger.info("Testing get existing domain")
        domain = populated_registry.get("Event")
        assert domain is not None
        assert domain.name == "Event"
        assert domain.parent == "Object"
        logger.debug(f"Got domain: {domain}")
    
    def test_get_nonexistent(self, empty_registry):
        """Get non-existent domain returns None."""
        logger.info("Testing get non-existent domain")
        domain = empty_registry.get("Unknown")
        assert domain is None
        logger.debug("Non-existent domain returns None")
    
    def test_exists(self, populated_registry):
        """Test exists method."""
        logger.info("Testing exists method")
        assert populated_registry.exists("Object")
        assert populated_registry.exists("ArriveEvent")
        assert populated_registry.exists("Nat")  # built-in
        assert not populated_registry.exists("Unknown")
        logger.debug("exists correctly identifies registered domains")


class TestTypeRegistryAncestors:
    """Tests for TypeRegistry.get_ancestors()."""
    
    def test_get_ancestors_empty(self, empty_registry):
        """Top-level domain has no ancestors."""
        logger.info("Testing ancestors of top-level domain")
        empty_registry.register(Domain("Object"))
        assert empty_registry.get_ancestors("Object") == []
        logger.debug("Top-level domain has empty ancestors")
    
    def test_get_ancestors_single(self, empty_registry):
        """Domain with one parent."""
        logger.info("Testing single ancestor")
        empty_registry.register(Domain("Object"))
        empty_registry.register(Domain("Load", "Object"))
        assert empty_registry.get_ancestors("Load") == ["Object"]
        logger.debug("Single ancestor returned correctly")
    
    def test_get_ancestors_chain(self, populated_registry):
        """Domain with ancestor chain."""
        logger.info("Testing ancestor chain")
        ancestors = populated_registry.get_ancestors("ArriveEvent")
        assert ancestors == ["Event", "Object"]
        logger.debug(f"Ancestor chain: {ancestors}")
    
    def test_get_ancestors_builtin(self, empty_registry):
        """Built-in types have no ancestors."""
        logger.info("Testing built-in ancestors")
        assert empty_registry.get_ancestors("Nat") == []
        assert empty_registry.get_ancestors("Real") == []
        logger.debug("Built-in types have no ancestors")
    
    def test_get_ancestors_extended_builtin(self, empty_registry):
        """Extended built-in has built-in as ancestor."""
        logger.info("Testing extended built-in ancestors")
        empty_registry.register(Domain("PositiveReal", "Real"))
        assert empty_registry.get_ancestors("PositiveReal") == ["Real"]
        logger.debug("Extended built-in has correct ancestor")
    
    def test_get_ancestors_unknown(self, empty_registry):
        """Unknown domain returns empty list."""
        logger.info("Testing unknown domain ancestors")
        assert empty_registry.get_ancestors("Unknown") == []
        logger.debug("Unknown domain returns empty ancestors")


class TestTypeRegistryCollections:
    """Tests for all_domains() and user_domains()."""
    
    def test_all_domains_includes_builtins(self, empty_registry):
        """All domains includes built-ins."""
        logger.info("Testing all_domains includes built-ins")
        all_doms = empty_registry.all_domains()
        for builtin in BUILTIN_TYPES:
            assert builtin in all_doms
        logger.debug(f"all_domains includes all {len(BUILTIN_TYPES)} built-ins")
    
    def test_all_domains_includes_user(self, populated_registry):
        """All domains includes user domains."""
        logger.info("Testing all_domains includes user domains")
        all_doms = populated_registry.all_domains()
        assert "Object" in all_doms
        assert "ArriveEvent" in all_doms
        assert "Nat" in all_doms  # built-in
        logger.debug(f"all_domains has {len(all_doms)} domains")
    
    def test_user_domains_excludes_builtins(self, empty_registry):
        """User domains excludes built-ins."""
        logger.info("Testing user_domains excludes built-ins")
        user_doms = empty_registry.user_domains()
        for builtin in BUILTIN_TYPES:
            assert builtin not in user_doms
        logger.debug("user_domains excludes all built-ins")
    
    def test_user_domains_includes_user(self, populated_registry):
        """User domains includes only user-defined domains."""
        logger.info("Testing user_domains content")
        user_doms = populated_registry.user_domains()
        assert "Object" in user_doms
        assert "ArriveEvent" in user_doms
        assert "Load" in user_doms
        assert "Nat" not in user_doms
        logger.debug(f"user_domains has {len(user_doms)} domains")
