"""Tests for preset configurations."""

import pytest
import numpy as np
from ase import Atoms
from molecular_dynamics_toy.data.presets import (
    PRESETS,
    get_preset_names,
    get_preset_display_name,
    create_preset,
)


def test_get_preset_names():
    """Test that get_preset_names returns all preset IDs."""
    names = get_preset_names()

    assert isinstance(names, list)
    assert len(names) > 0
    assert "water" in names
    assert "diamond" in names


def test_get_preset_display_name():
    """Test that get_preset_display_name returns correct names."""
    assert get_preset_display_name("water") == "Water molecule"
    assert get_preset_display_name("diamond") == "Diamond lattice"

    # Unknown preset returns the ID itself
    assert get_preset_display_name("unknown_preset") == "unknown_preset"


def test_create_preset_unknown():
    """Test that creating unknown preset raises ValueError."""
    with pytest.raises(ValueError, match="Unknown preset"):
        create_preset("nonexistent_preset")


@pytest.mark.parametrize("preset_id", [
    "water",
    "ethanol",
    "methane",
    "benzene",
    "co2",
    "diamond",
    "gold",
    "graphene",
    "nacl",
    "copper",
    "pbse_dw",
    "dca",
    "hat",
    "eu526",
    "cbamnbr4",
])
def test_preset_creates_atoms(preset_id):
    """Test that each preset creates a non-empty Atoms object."""
    atoms = create_preset(preset_id)

    # Check that we got an Atoms object
    assert isinstance(atoms, Atoms)

    # Check that it's not empty
    assert len(atoms) > 0


@pytest.mark.parametrize("preset_id", [
    "water",
    "ethanol",
    "methane",
    "benzene",
    "co2",
    "diamond",
    "gold",
    "graphene",
    "nacl",
    "copper",
    "pbse_dw",
    "dca",
    "hat",
    "eu526",
    "cbamnbr4",
])
def test_preset_has_cubic_cell(preset_id):
    """Test that each preset has a cubic unit cell."""
    atoms = create_preset(preset_id)

    cell = atoms.get_cell()

    # Check that diagonal elements are equal (cubic)
    a = cell[0, 0]
    b = cell[1, 1]
    c = cell[2, 2]

    assert abs(a - b) < 1e-6, f"{preset_id}: cell[0,0] != cell[1,1]"
    assert abs(b - c) < 1e-6, f"{preset_id}: cell[1,1] != cell[2,2]"

    # Check that off-diagonal elements are zero
    assert abs(cell[0, 1]) < 1e-6, f"{preset_id}: cell[0,1] != 0"
    assert abs(cell[0, 2]) < 1e-6, f"{preset_id}: cell[0,2] != 0"
    assert abs(cell[1, 0]) < 1e-6, f"{preset_id}: cell[1,0] != 0"
    assert abs(cell[1, 2]) < 1e-6, f"{preset_id}: cell[1,2] != 0"
    assert abs(cell[2, 0]) < 1e-6, f"{preset_id}: cell[2,0] != 0"
    assert abs(cell[2, 1]) < 1e-6, f"{preset_id}: cell[2,1] != 0"


@pytest.mark.parametrize("preset_id", [
    "water",
    "ethanol",
    "methane",
    "benzene",
    "co2",
    "diamond",
    "gold",
    "graphene",
    "nacl",
    "copper",
    "pbse_dw",
    "dca",
    "hat",
    "eu526",
    "cbamnbr4",
])
def test_preset_has_pbc(preset_id):
    """Test that each preset has periodic boundary conditions set."""
    atoms = create_preset(preset_id)

    # Check that PBC is enabled
    assert atoms.pbc.all(), f"{preset_id}: PBC not set to True"


@pytest.mark.parametrize("preset_id", [
    "water",
    "ethanol",
    "methane",
    "benzene",
    "co2",
    "diamond",
    "gold",
    "graphene",
    "nacl",
    "copper",
    "pbse_dw",
    "dca",
    "hat",
    "eu526",
    "cbamnbr4",
])
def test_preset_positions_within_cell(preset_id):
    """Test that atom positions are within the unit cell."""
    atoms = create_preset(preset_id)

    positions = atoms.get_positions()
    cell_size = atoms.get_cell()[0, 0]

    # All positions should be within [0, cell_size) range (approximately)
    # Allow some tolerance for atoms near boundaries
    assert np.all(
        positions >= -1e-6), f"{preset_id}: Some positions are negative"
    assert np.all(positions <= cell_size +
                  1e-6), f"{preset_id}: Some positions exceed cell size"


def test_presets_registry_format():
    """Test that PRESETS registry has correct format."""
    assert isinstance(PRESETS, dict)

    for preset_id, (description, creator_func) in PRESETS.items():
        assert isinstance(preset_id, str)
        assert isinstance(description, str)
        assert callable(creator_func)
