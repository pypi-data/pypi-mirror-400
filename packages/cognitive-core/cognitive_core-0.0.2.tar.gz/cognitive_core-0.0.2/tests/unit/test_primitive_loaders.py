"""Tests for domain-specific primitive loaders."""

from __future__ import annotations

import pytest

from cognitive_core.core.types import CodeConcept
from cognitive_core.memory.primitives import ARCPrimitiveLoader, SWEPrimitiveLoader
from cognitive_core.memory.strategies import PrimitiveLoader


class TestARCPrimitiveLoader:
    """Tests for ARCPrimitiveLoader."""

    def test_implements_protocol(self) -> None:
        """ARCPrimitiveLoader implements PrimitiveLoader protocol."""
        loader = ARCPrimitiveLoader()
        assert isinstance(loader, PrimitiveLoader)

    def test_load_returns_dict(self) -> None:
        """load() returns a dict mapping IDs to CodeConcepts."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        assert isinstance(primitives, dict)
        assert len(primitives) > 0

    def test_all_values_are_code_concepts(self) -> None:
        """All returned values are CodeConcept instances."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert isinstance(concept, CodeConcept)

    def test_keys_match_concept_ids(self) -> None:
        """Dict keys match the id field of each CodeConcept."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        for key, concept in primitives.items():
            assert key == concept.id

    def test_all_ids_unique(self) -> None:
        """All primitive IDs are unique."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        ids = [c.id for c in primitives.values()]
        assert len(ids) == len(set(ids))

    def test_all_ids_have_arc_prefix(self) -> None:
        """All ARC primitive IDs have 'arc_' prefix."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert concept.id.startswith("arc_")

    def test_all_concepts_have_required_fields(self) -> None:
        """All concepts have required fields populated."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert concept.id
            assert concept.name
            assert concept.description
            assert concept.code
            assert concept.signature

    def test_all_concepts_are_primitives(self) -> None:
        """All concepts have source='primitive'."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert concept.source == "primitive"

    def test_expected_primitives_present(self) -> None:
        """Expected ARC primitives are present."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        expected = [
            "arc_get_objects",
            "arc_flood_fill",
            "arc_rotate_90",
            "arc_rotate_180",
            "arc_rotate_270",
            "arc_mirror_horizontal",
            "arc_mirror_vertical",
            "arc_get_background_color",
            "arc_get_colors",
            "arc_crop_to_content",
            "arc_scale_grid",
            "arc_tile_pattern",
        ]
        for expected_id in expected:
            assert expected_id in primitives

    def test_descriptions_are_meaningful(self) -> None:
        """Descriptions are meaningful (not empty, reasonable length)."""
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert len(concept.description) >= 10
            assert len(concept.description) <= 500

    def test_multiple_loads_return_same_data(self) -> None:
        """Multiple calls to load() return equivalent data."""
        loader = ARCPrimitiveLoader()
        first = loader.load()
        second = loader.load()
        assert first.keys() == second.keys()
        for key in first:
            assert first[key].id == second[key].id
            assert first[key].name == second[key].name


class TestSWEPrimitiveLoader:
    """Tests for SWEPrimitiveLoader."""

    def test_implements_protocol(self) -> None:
        """SWEPrimitiveLoader implements PrimitiveLoader protocol."""
        loader = SWEPrimitiveLoader()
        assert isinstance(loader, PrimitiveLoader)

    def test_load_returns_dict(self) -> None:
        """load() returns a dict mapping IDs to CodeConcepts."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        assert isinstance(primitives, dict)
        assert len(primitives) > 0

    def test_all_values_are_code_concepts(self) -> None:
        """All returned values are CodeConcept instances."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert isinstance(concept, CodeConcept)

    def test_keys_match_concept_ids(self) -> None:
        """Dict keys match the id field of each CodeConcept."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        for key, concept in primitives.items():
            assert key == concept.id

    def test_all_ids_unique(self) -> None:
        """All primitive IDs are unique."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        ids = [c.id for c in primitives.values()]
        assert len(ids) == len(set(ids))

    def test_all_ids_have_swe_prefix(self) -> None:
        """All SWE primitive IDs have 'swe_' prefix."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert concept.id.startswith("swe_")

    def test_all_concepts_have_required_fields(self) -> None:
        """All concepts have required fields populated."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert concept.id
            assert concept.name
            assert concept.description
            assert concept.code
            assert concept.signature

    def test_all_concepts_are_primitives(self) -> None:
        """All concepts have source='primitive'."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert concept.source == "primitive"

    def test_expected_primitives_present(self) -> None:
        """Expected SWE primitives are present."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        expected = [
            "swe_read_file",
            "swe_write_file",
            "swe_search_codebase",
            "swe_find_definition",
            "swe_find_references",
            "swe_run_tests",
            "swe_apply_patch",
            "swe_git_diff",
        ]
        for expected_id in expected:
            assert expected_id in primitives

    def test_descriptions_are_meaningful(self) -> None:
        """Descriptions are meaningful (not empty, reasonable length)."""
        loader = SWEPrimitiveLoader()
        primitives = loader.load()
        for concept in primitives.values():
            assert len(concept.description) >= 10
            assert len(concept.description) <= 500

    def test_multiple_loads_return_same_data(self) -> None:
        """Multiple calls to load() return equivalent data."""
        loader = SWEPrimitiveLoader()
        first = loader.load()
        second = loader.load()
        assert first.keys() == second.keys()
        for key in first:
            assert first[key].id == second[key].id
            assert first[key].name == second[key].name


class TestPrimitiveLoaderCrossCheck:
    """Cross-check tests between loaders."""

    def test_no_id_collision_between_loaders(self) -> None:
        """ARC and SWE loaders have no ID collisions."""
        arc_loader = ARCPrimitiveLoader()
        swe_loader = SWEPrimitiveLoader()

        arc_ids = set(arc_loader.load().keys())
        swe_ids = set(swe_loader.load().keys())

        assert arc_ids.isdisjoint(swe_ids)

    def test_both_loaders_have_primitives(self) -> None:
        """Both loaders provide a reasonable number of primitives."""
        arc_loader = ARCPrimitiveLoader()
        swe_loader = SWEPrimitiveLoader()

        assert len(arc_loader.load()) >= 5
        assert len(swe_loader.load()) >= 5
