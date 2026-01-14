"""Calculator factory for MD simulations."""

import logging
from typing import Optional, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

# Cache for calculators to avoid re-initialization
_calculator_cache: Dict[str, Any] = {}


def get_mattersim_calculator(device: str = "cpu", **kwargs) -> Any:
    """Get MatterSim calculator instance.

    Args:
        device: Device to run on ('cpu' or 'cuda').
        **kwargs: Additional arguments for MatterSimCalculator.

    Returns:
        MatterSimCalculator instance.
    """
    cache_key = f"mattersim_{device}"

    if cache_key not in _calculator_cache:
        try:
            from mattersim.forcefield import MatterSimCalculator
            calc = MatterSimCalculator(device=device, **kwargs)
            _calculator_cache[cache_key] = calc
            logger.info(f"Created MatterSimCalculator on {device}")
        except ImportError as e:
            logger.error(f"Failed to import MatterSim: {e}")
            raise ImportError(
                "MatterSim not installed. Install with: pip install mattersim"
            ) from e

    return _calculator_cache[cache_key]


class MockCalculator:
    """Mock calculator with simple harmonic forces for H2-like molecule."""

    def __init__(self):
        self.results = {}

    def get_potential_energy(self, atoms):
        """Return dummy energy."""
        return 0.0

    def get_forces(self, atoms):
        """Return simple harmonic forces for H2-like molecule."""
        if len(atoms) < 2:
            return np.zeros((len(atoms), 3))

        forces = np.zeros((len(atoms), 3))

        # Simple pairwise harmonic potential centered at 0.74 Å
        equilibrium_distance = 0.74
        k = 100.0  # Force constant in eV/Å²

        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                vec = atoms.get_distance(i, j, mic=True, vector=True)
                dist = np.linalg.norm(vec)
                if dist > 0:
                    force_mag = k * (dist - equilibrium_distance)
                    force_vec = force_mag * vec / dist
                    forces[i] += force_vec
                    forces[j] -= force_vec

        return forces


def get_mock_calculator(**kwargs) -> Any:
    """Get mock calculator for testing (harmonic H2 potential).

    Args:
        **kwargs: Additional arguments (unused).

    Returns:
        MockCalculator instance.
    """
    if "mock" not in _calculator_cache:
        _calculator_cache["mock"] = MockCalculator()
        logger.info("Created MockCalculator")

    return _calculator_cache["mock"]


def get_calculator(name: str = "mock", **kwargs) -> Any:
    """Get calculator by name.

    Args:
        name: Calculator name ('mattersim', 'mock').
        **kwargs: Calculator-specific arguments.

    Returns:
        Calculator instance.

    Raises:
        ValueError: If calculator name is unknown.
    """
    calculators = {
        "mattersim": get_mattersim_calculator,
        "mock": get_mock_calculator,
    }

    if name not in calculators:
        raise ValueError(
            f"Unknown calculator: {name}. "
            f"Available: {', '.join(calculators.keys())}"
        )

    return calculators[name](**kwargs)


def clear_calculator_cache():
    """Clear the calculator cache (useful for testing)."""
    global _calculator_cache
    _calculator_cache.clear()
    logger.info("Calculator cache cleared")
