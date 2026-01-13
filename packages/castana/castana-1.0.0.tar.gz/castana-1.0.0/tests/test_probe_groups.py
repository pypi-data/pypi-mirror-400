"""Tests for probe groups (K8s liveness/readiness support)."""

import pytest

from castana import HealthCheck, BaseProbe


class SimpleProbe(BaseProbe):
    def check(self):
        return "ok"


class TestProbeGroups:
    """Tests for add_probe with groups and get_probes filtering."""

    def test_add_probe_without_groups_assigns_all_group(self):
        """Probes without explicit groups get the __all__ group."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="p1"))
        
        assert "p1" in health.probe_groups
        assert health.probe_groups["p1"] == {"__all__"}

    def test_add_probe_with_groups(self):
        """Probes with explicit groups get those groups."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="p1"), groups=["liveness", "readiness"])
        
        assert health.probe_groups["p1"] == {"liveness", "readiness"}

    def test_add_probes_with_groups(self):
        """add_probes assigns same groups to all probes."""
        health = HealthCheck()
        health.add_probes(
            [SimpleProbe(name="p1"), SimpleProbe(name="p2")],
            groups=["readiness"],
        )
        
        assert health.probe_groups["p1"] == {"readiness"}
        assert health.probe_groups["p2"] == {"readiness"}

    def test_get_probes_without_filter_returns_all(self):
        """get_probes() without args returns all probes."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="p1"))
        health.add_probe(SimpleProbe(name="p2"), groups=["readiness"])
        
        probes = health.get_probes()
        names = {p.name for p in probes}
        
        assert names == {"p1", "p2"}

    def test_get_probes_with_matching_group(self):
        """get_probes() returns probes matching the specified group."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="liveness_only"), groups=["liveness"])
        health.add_probe(SimpleProbe(name="readiness_only"), groups=["readiness"])
        health.add_probe(SimpleProbe(name="both"), groups=["liveness", "readiness"])
        
        liveness_probes = health.get_probes(groups=["liveness"])
        names = {p.name for p in liveness_probes}
        
        assert "liveness_only" in names
        assert "both" in names
        assert "readiness_only" not in names

    def test_get_probes_includes_all_group(self):
        """Probes in __all__ group are included in every filter."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="always"))  # No groups = __all__
        health.add_probe(SimpleProbe(name="readiness_only"), groups=["readiness"])
        
        # Filter for liveness - should include "always" but not "readiness_only"
        liveness_probes = health.get_probes(groups=["liveness"])
        names = {p.name for p in liveness_probes}
        
        assert "always" in names
        assert "readiness_only" not in names

    def test_get_probes_with_nonexistent_group(self):
        """Filtering by a group with no probes returns only __all__ probes."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="always"))  # __all__
        health.add_probe(SimpleProbe(name="readiness_only"), groups=["readiness"])
        
        unknown_probes = health.get_probes(groups=["unknown"])
        names = {p.name for p in unknown_probes}
        
        assert names == {"always"}

    def test_empty_groups_list_returns_only_all_probes(self):
        """Empty groups list filters to only __all__ probes."""
        health = HealthCheck()
        health.add_probe(SimpleProbe(name="always"))
        health.add_probe(SimpleProbe(name="specific"), groups=["readiness"])
        
        probes = health.get_probes(groups=[])
        names = {p.name for p in probes}
        
        assert names == {"always"}
