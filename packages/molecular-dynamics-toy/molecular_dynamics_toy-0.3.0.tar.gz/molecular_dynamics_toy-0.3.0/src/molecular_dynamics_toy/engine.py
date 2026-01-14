"""Molecular dynamics engine for interactive atomic simulation."""

import logging
import numpy as np
from ase import Atom, Atoms, units
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.langevin import Langevin
from typing import Optional

logger = logging.getLogger(__name__)


class MDEngine:
    """Manages molecular dynamics simulation state and execution.

    This class wraps ASE's MD functionality to provide a simple interface
    for running MD simulations step-by-step with dynamic parameter updates.
    Uses periodic boundary conditions and the VelocityVerlet integrator.

    Attributes:
        atoms: ASE Atoms object containing the simulation state.
        timestep: MD timestep in femtoseconds.
        temperature: Target temperature in Kelvin.
    """

    def __init__(
        self,
        atoms: Optional[Atoms] = None,
        calculator=None,
        timestep: float = 1.0,
        temperature: float = 300.0,
        cell_size: float = 20.0
    ):
        """Initialize the MD engine.

        Args:
            atoms: Initial Atoms object. If None, creates empty cell.
            calculator: ASE Calculator for force/energy calculations.
            timestep: Time step for MD integration in femtoseconds.
            temperature: Initial temperature in Kelvin.
            cell_size: Size of cubic simulation cell in Angstroms.
        """
        if atoms is None:
            # Create empty periodic cell
            atoms = Atoms(cell=[cell_size, cell_size, cell_size], pbc=True)

        self._atoms = atoms
        self._timestep = timestep
        self._temperature = temperature
        self._calculator = calculator

        # Attach calculator if provided
        if calculator is not None:
            self._atoms.calc = calculator

        # Initialize MD integrator (will be recreated when needed)
        self._integrator = None

    @property
    def atoms(self) -> Atoms:
        """Get the current Atoms object."""
        return self._atoms

    @atoms.setter
    def atoms(self, atoms: Atoms):
        """Set the Atoms object.

        Args:
            atoms: New Atoms object to use for simulation.
        """
        self._atoms = atoms
        if self._calculator is not None:
            self._atoms.calc = self._calculator
        # Reset integrator when atoms change
        self._integrator = None

    @property
    def calculator(self):
        """Get the current calculator."""
        return self._calculator

    @calculator.setter
    def calculator(self, calc):
        """Set the calculator.

        Args:
            calc: ASE Calculator object.
        """
        self._calculator = calc
        if self._atoms is not None:
            self._atoms.calc = calc

    @property
    def timestep(self) -> float:
        """Get timestep in femtoseconds."""
        return self._timestep

    @timestep.setter
    def timestep(self, value: float):
        """Set timestep in femtoseconds.

        Args:
            value: New timestep value.
        """
        self._timestep = value
        # Reset integrator to use new timestep
        self._integrator = None

    @property
    def temperature(self) -> float:
        """Get target temperature in Kelvin."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        """Set target temperature in Kelvin.

        Updates the thermostat to use the new temperature.

        Args:
            value: New temperature in Kelvin.
        """
        # Only update if temperature actually changed
        if abs(self._temperature - value) < 1e-6:
            return

        self._temperature = value

        # Update integrator's temperature if it exists
        if self._integrator is not None:
            self._integrator.set_temperature(temperature_K=value)
            logger.debug(f"Updated thermostat temperature to {value} K")

        # If no integrator yet but we have atoms, initialize velocities
        elif len(self._atoms) > 0:
            MaxwellBoltzmannDistribution(self._atoms, temperature_K=value)

    def _ensure_integrator(self):
        """Create or recreate the MD integrator if needed."""
        if self._integrator is None and len(self._atoms) > 0:

            self._integrator = Langevin(
                self._atoms,
                timestep=self._timestep * units.fs,
                temperature_K=self._temperature,
                friction=0.01 / units.fs  # Friction coefficient
            )
            logger.debug(
                f"Created Langevin integrator with dt={self._timestep} fs, T={self._temperature} K")

    def run(self, steps: int = 1):
        """Run MD simulation for specified number of steps.

        Updates the atoms object in-place by integrating Newton's equations
        of motion using the VelocityVerlet algorithm.

        Args:
            steps: Number of MD timesteps to perform.
        """
        if len(self._atoms) == 0:
            logger.debug("No atoms to simulate")
            return

        if self._calculator is None:
            logger.warning("No calculator attached, cannot run MD")
            return

        self._ensure_integrator()

        try:
            self._integrator.run(steps)
            # Wrap positions to ensure atoms are in home unit cell
            self._atoms.wrap()
            logger.debug(f"Completed {steps} MD steps")
        except Exception as e:
            logger.error(f"MD step failed: {e}")
            raise

    def add_atom(self, symbol: str, position: np.ndarray, initialize_velocity: bool = True):
        """Add a new atom to the simulation.

        Args:
            symbol: Chemical symbol of the atom to add.
            position: 3D position in Angstroms.
            initialize_velocity: If True, initialize velocity from Maxwell-Boltzmann
                distribution at current temperature.
        """

        new_atom = Atom(symbol, position=position)
        self._atoms.append(new_atom)

        if initialize_velocity and self._temperature > 0:
            # Sample velocity from Maxwell-Boltzmann distribution
            mass = new_atom.mass
            sigma = np.sqrt(units.kB * self._temperature / mass)
            velocity = np.random.normal(0, sigma, 3)

            # Set momentum for the new atom (last atom in list)
            momenta = self._atoms.get_momenta()
            momenta[-1] = mass * velocity
            self._atoms.set_momenta(momenta)

        # Reset integrator when atoms are added
        self._integrator = None
        logger.info(f"Added {symbol} atom at {position}")
