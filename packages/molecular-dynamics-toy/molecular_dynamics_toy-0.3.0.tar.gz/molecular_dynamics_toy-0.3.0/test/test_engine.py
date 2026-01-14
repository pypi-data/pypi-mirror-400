"""Tests for the MD engine."""

import pytest
import numpy as np
from ase import Atoms

from molecular_dynamics_toy.engine import MDEngine
from molecular_dynamics_toy.calculators import MockCalculator

# from mattersim.forcefield import MatterSimCalculator

# calculator = MatterSimCalculator(device="cpu")


def test_mdengine_initialization():
    """Test MDEngine initializes with correct defaults."""
    engine = MDEngine(calculator=MockCalculator())

    assert engine.timestep == 1.0
    assert engine.temperature == 300.0
    assert len(engine.atoms) == 0
    assert engine.calculator is not None


def test_add_atom():
    """Test adding atoms to the simulation."""
    engine = MDEngine(calculator=MockCalculator())

    engine.add_atom('H', [-0.4, 0, 0])
    engine.add_atom('H', [0.4, 0, 0])

    assert len(engine.atoms) == 2
    assert engine.atoms[0].symbol == 'H'
    assert engine.atoms[1].symbol == 'H'
    np.testing.assert_array_almost_equal(
        engine.atoms.get_positions()[0], [-0.4, 0, 0]
    )


def test_temperature_setter():
    """Test temperature property setter."""
    engine = MDEngine(calculator=MockCalculator())
    engine.add_atom('H', [0, 0, 0])

    engine.temperature = 100
    assert engine.temperature == 100


def test_h2_molecule_equilibration():
    """Test H2 molecule equilibrates to correct bond length.

    Creates an H2 molecule, runs MD, and checks that the bond length
    is close to the experimental value of 0.74 Å.
    """
    engine = MDEngine(calculator=MockCalculator(), temperature=100)

    # Add H2 molecule slightly displaced from equilibrium
    engine.add_atom('H', [-0.4, 0, 0])
    engine.add_atom('H', [0.4, 0, 0])

    # Run simulation
    engine.run(100)

    bond_length = engine.atoms.get_distance(0, 1, mic=True)
    # Check bond length is in reasonable range
    assert 0.69 < bond_length < 0.79, f"Bond length {bond_length:.3f} Å out of range"


def test_empty_simulation_runs():
    """Test that running with no atoms doesn't crash."""
    engine = MDEngine(calculator=MockCalculator())
    engine.run(10)  # Should not raise
    assert len(engine.atoms) == 0


def test_atoms_setter():
    """Test setting atoms object directly."""
    engine = MDEngine(calculator=MockCalculator())

    new_atoms = Atoms('H2', positions=[[-0.37, 0, 0], [0.37, 0, 0]],
                      cell=[20, 20, 20], pbc=True)
    engine.atoms = new_atoms

    assert len(engine.atoms) == 2
    assert engine.atoms.calc is engine.calculator
