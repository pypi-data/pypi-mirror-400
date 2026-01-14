"""Preset atomic configurations for loading into simulations."""

import logging
from typing import Dict, Callable, List
import importlib.resources

import numpy as np
from ase import Atoms
import ase.io
from ase.build import molecule, bulk, graphene_nanoribbon


logger = logging.getLogger(__name__)


def _load_from_file(filename: str) -> Callable[[], Atoms]:
    """Create a loader function for a structure file.

    Args:
        filename: Name of file in data/structures/ directory.

    Returns:
        Function that loads and returns the Atoms object.
    """
    def loader() -> Atoms:
        """Load structure from file."""
        structures_path = importlib.resources.files(
            'molecular_dynamics_toy.data') / 'structures' / filename
        try:
            atoms = ase.io.read(structures_path, format='vasp')
        except IOError as e:
            logger.error(f"Failed to load structure from {filename}: {e}")
            raise

        # Ensure cubic cell for compatibility
        cell = atoms.get_cell()
        if not (abs(cell[0, 0] - cell[1, 1]) < 1e-6 and
                abs(cell[1, 1] - cell[2, 2]) < 1e-6 and
                abs(cell[0, 1]) < 1e-6 and abs(cell[0, 2]) < 1e-6 and
                abs(cell[1, 0]) < 1e-6 and abs(cell[1, 2]) < 1e-6 and
                abs(cell[2, 0]) < 1e-6 and abs(cell[2, 1]) < 1e-6):
            logger.warning(
                f"Structure {filename} does not have cubic cell, may not work correctly")

        atoms.pbc = True
        logger.info(f"Loaded structure from {filename}")
        return atoms

    return loader


def _molecule_in_box(molecule_name: str, vacuum: float = 5.0) -> Atoms:
    """Create a molecule centered in a cubic box with vacuum.

    Args:
        molecule_name: Name of molecule (ASE molecule database).
        vacuum: Vacuum space on each side in Angstroms.

    Returns:
        Atoms object with molecule in cubic cell.
    """
    atoms = molecule(molecule_name)

    # Get bounding box
    positions = atoms.get_positions()
    min_pos = positions.min(axis=0)
    max_pos = positions.max(axis=0)
    size = max_pos - min_pos

    # Create cubic cell with appropriate vacuum
    cell_size = max(size) + 2 * vacuum
    atoms.set_cell([cell_size, cell_size, cell_size])
    atoms.center()
    atoms.pbc = True

    return atoms


def create_water_molecule() -> Atoms:
    """Create a water molecule.

    Returns:
        Atoms object containing H2O in a cubic cell.
    """
    atoms = _molecule_in_box('H2O', vacuum=5.0)
    atoms.rotate(90, 'y', center='COU')
    logger.info("Created water molecule preset")
    return atoms


def create_ethanol_molecule() -> Atoms:
    """Create an ethanol molecule.

    Returns:
        Atoms object containing C2H5OH in a cubic cell.
    """
    atoms = _molecule_in_box('CH3CH2OH', vacuum=5.0)
    logger.info("Created ethanol molecule preset")
    return atoms


def create_methane_molecule() -> Atoms:
    """Create a methane molecule.

    Returns:
        Atoms object containing CH4 in a cubic cell.
    """
    atoms = _molecule_in_box('CH4', vacuum=5.0)
    logger.info("Created methane molecule preset")
    return atoms


def create_benzene_molecule() -> Atoms:
    """Create a benzene molecule.

    Returns:
        Atoms object containing C6H6 in a cubic cell.
    """
    atoms = _molecule_in_box('C6H6', vacuum=5.0)
    logger.info("Created benzene molecule preset")
    return atoms


def create_co2_molecule() -> Atoms:
    """Create a carbon dioxide molecule.

    Returns:
        Atoms object containing CO2 in a cubic cell.
    """
    atoms = _molecule_in_box('CO2', vacuum=5.0)
    atoms.rotate(90, 'y', center='COU')
    logger.info("Created CO2 molecule preset")
    return atoms


def create_diamond_lattice() -> Atoms:
    """Create a diamond lattice structure.

    Returns:
        Atoms object containing diamond structure.
    """
    atoms = bulk('C', 'diamond', a=3.567, cubic=True)
    # Make it 2x2x2 supercell for better visualization
    # atoms = atoms.repeat((2, 2, 2))
    logger.info("Created diamond lattice preset")
    return atoms


def create_fcc_gold() -> Atoms:
    """Create an FCC gold structure.

    Returns:
        Atoms object containing FCC Au structure.
    """
    atoms = bulk('Au', 'fcc', a=4.08, cubic=True)
    # Make it 2x2x2 supercell
    atoms = atoms.repeat((2, 2, 2))
    logger.info("Created FCC gold preset")
    return atoms


def create_graphene_sheet() -> Atoms:
    """Create a graphene sheet.

    Returns:
        Atoms object containing graphene in a cubic cell.
    """
    # Create small graphene nanoribbon (in x-z plane)
    atoms = graphene_nanoribbon(3, 4, type='zigzag', saturated=False)

    # Rotate 90 degrees around x-axis to move from x-z to x-y plane
    atoms.rotate(90, 'x', rotate_cell=True)

    # Get bounding box in each dimension
    positions = atoms.get_positions()
    min_pos = positions.min(axis=0)
    max_pos = positions.max(axis=0)
    size = max_pos - min_pos

    # Create cubic cell with appropriate vacuum
    xy_size = max(size[0], size[1])
    # More vacuum perpendicular to sheet
    cell_size = max(xy_size + 6.0, size[2] + 10.0)

    atoms.set_cell([cell_size, cell_size, cell_size])
    atoms.center()

    atoms.pbc = True

    logger.info("Created graphene sheet preset")
    return atoms


def create_nacl_crystal() -> Atoms:
    """Create a NaCl (rock salt) crystal structure.

    Returns:
        Atoms object containing NaCl structure.
    """
    atoms = bulk('NaCl', 'rocksalt', a=5.64, cubic=True)
    logger.info("Created NaCl crystal preset")
    return atoms


def create_copper_fcc() -> Atoms:
    """Create an FCC copper structure.

    Returns:
        Atoms object containing FCC Cu structure.
    """
    atoms = bulk('Cu', 'fcc', a=3.61, cubic=True)
    # Make it 2x2x2 supercell
    atoms = atoms.repeat((2, 2, 2))
    logger.info("Created FCC copper preset")
    return atoms


def create_ice_crystal() -> Atoms:
    """Create an ice crystal structure (ice Ih, slightly distorted to cubic).

    Returns:
        Atoms object containing ice Ih structure in cubic cell.
    """
    # Ice Ih has a hexagonal structure with specific hydrogen bonding
    # We'll create a small ice Ih structure and then fit it to a cubic cell

    # Ice Ih parameters
    a = 4.52  # Hexagonal a parameter (Angstrom)
    c = 7.37  # Hexagonal c parameter (Angstrom)

    # Ratio c/a ≈ 1.63
    # To get close to cubic, we want dimensions that are similar
    # A 2x2x1 supercell gives: 2a × 2a × c ≈ 9.04 × 9.04 × 7.37
    # This is reasonably close to cubic

    # Oxygen positions in hexagonal ice unit cell (fractional)
    o_frac = np.array([
        [0.0, 0.0, 0.0625],
        [0.0, 0.0, 0.5625],
        [1/3, 2/3, 0.0625],
        [2/3, 1/3, 0.5625],
    ])

    # Hexagonal cell vectors
    cell_hex = np.array([
        [a, 0, 0],
        [-a/2, a*np.sqrt(3)/2, 0],
        [0, 0, c]
    ])

    # Convert to Cartesian
    o_cart = np.dot(o_frac, cell_hex)

    # Create atoms object with hexagonal cell
    atoms = Atoms('O4', positions=o_cart, cell=cell_hex, pbc=True)

    # Add hydrogens with ice Ih geometry (simplified)
    # O-H bond length ~0.96 Å, tetrahedral angle ~109.5°
    h_positions = []
    bond_length = 0.96

    # Approximate hydrogen positions based on ice rules
    # (2 close H per O in tetrahedral arrangement)
    for i, pos in enumerate(o_cart):
        if i == 0:
            h_positions.append(pos + np.array([bond_length, 0, 0]))
            h_positions.append(
                pos + np.array([-bond_length/2, bond_length*np.sqrt(3)/2, 0]))
        elif i == 1:
            h_positions.append(pos + np.array([0, bond_length, 0]))
            h_positions.append(
                pos + np.array([0, -bond_length/2, bond_length*np.sqrt(3)/2]))
        elif i == 2:
            h_positions.append(pos + np.array([bond_length, 0, 0]))
            h_positions.append(pos + np.array([0, 0, bond_length]))
        else:
            h_positions.append(pos + np.array([0, bond_length, 0]))
            h_positions.append(pos + np.array([bond_length, 0, 0]))

    h_atoms = Atoms('H8', positions=h_positions)
    atoms += h_atoms

    # Make 2x2x1 supercell for better cubic approximation
    atoms = atoms.repeat((2, 2, 1))

    # Now convert to cubic cell
    # Average the dimensions
    current_cell = atoms.get_cell()
    dims = [np.linalg.norm(current_cell[i]) for i in range(3)]
    avg_dim = np.mean(dims)

    # Set to cubic cell with average dimension
    atoms.set_cell([avg_dim, avg_dim, avg_dim], scale_atoms=True)

    logger.info("Created ice Ih crystal preset (2x2x1 supercell, cubic)")
    return atoms


# Registry of all available presets
# Format: name -> (description, creation_function)
PRESETS: Dict[str, tuple[str, Callable[[], Atoms]]] = {
    "water": ("Water molecule", create_water_molecule),
    # "ice": ("Ice crystal", create_ice_crystal),
    "ethanol": ("Ethanol molecule", create_ethanol_molecule),
    "methane": ("Methane molecule", create_methane_molecule),
    "benzene": ("Benzene molecule", create_benzene_molecule),
    "co2": ("Carbon dioxide", create_co2_molecule),
    "diamond": ("Diamond lattice", create_diamond_lattice),
    "gold": ("FCC gold", create_fcc_gold),
    "graphene": ("Graphene sheet", create_graphene_sheet),
    "nacl": ("NaCl crystal", create_nacl_crystal),
    "copper": ("FCC copper", create_copper_fcc),
    "pbse_dw": ("PbSe domain wall", _load_from_file("PbSe_domain_wall.vasp")),
    "dca": ("DCA molecule", _load_from_file("DCA.vasp")),
    "hat": ("HAT molecule", _load_from_file("HAT.vasp")),
    "eu526": ("Eu5Sn2As6", _load_from_file("Eu5Sn2As6.vasp")),
    "cbamnbr4": ("(18-crown-6)BaMnBr4", _load_from_file("CBaMnBr4.vasp")),
}


def get_preset_names() -> List[str]:
    """Get list of all preset names.

    Returns:
        List of preset identifiers.
    """
    return list(PRESETS.keys())


def get_preset_display_name(preset_id: str) -> str:
    """Get display name for a preset.

    Args:
        preset_id: Preset identifier.

    Returns:
        Human-readable name for the preset.
    """
    if preset_id in PRESETS:
        return PRESETS[preset_id][0]
    return preset_id


def create_preset(preset_id: str) -> Atoms:
    """Create atoms for a given preset.

    Args:
        preset_id: Preset identifier.

    Returns:
        Atoms object for the preset.

    Raises:
        ValueError: If preset_id is not recognized.
    """
    if preset_id not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_id}")

    _, creator_func = PRESETS[preset_id]
    return creator_func()
