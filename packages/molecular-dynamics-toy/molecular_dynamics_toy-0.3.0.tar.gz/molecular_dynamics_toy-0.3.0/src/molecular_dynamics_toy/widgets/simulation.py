"""Simulation widget for rendering and controlling MD simulation."""

import logging
import pygame
import numpy as np
from typing import Optional, Tuple

from ase import Atoms
import ase.geometry

from molecular_dynamics_toy.engine import MDEngine
from molecular_dynamics_toy.data import colors
from molecular_dynamics_toy.data.atom_properties import ATOM_COLORS, ATOM_VDW_RADII, ATOM_COVALENT_RADII

logger = logging.getLogger(__name__)


class SimulationWidget:
    """Widget for displaying and interacting with MD simulation.

    Attributes:
        rect: Rectangle defining widget position and size.
        engine: MD engine instance.
    """

    BG_COLOR = colors.WIDGET_BG_COLOR
    CELL_COLOR = colors.SIMULATION_CELL_COLOR

    def __init__(self, rect: pygame.Rect, calculator=None, radius_type: str = "covalent"):
        """Initialize the simulation widget.

        Args:
            rect: Rectangle defining widget position and size.
            calculator: ASE calculator for MD engine.
            radius_type: Type of atomic radii to use ('vdw' or 'covalent').
        """
        self.rect = rect
        self.engine = None
        self.calculator = calculator
        self.radius_type = radius_type
        self.selected_element = None  # Will be set by parent application

        # Select radii based on type
        self.atom_radii = ATOM_VDW_RADII if radius_type == "vdw" else ATOM_COVALENT_RADII

        # Distance threshold in Angstrom to avoid putting atoms on top of each other.
        self.collision_threshold = 0.1

        self._create_engine()
        logger.info("SimulationWidget initialized")

    def _create_engine(self):
        """Create MD engine with initial test configuration."""
        # Create engine with H2 molecule for testing
        cell_size = 10.0  # Angstroms
        self.engine = MDEngine(
            calculator=self.calculator,
            timestep=1.0,
            temperature=300.0,
            cell_size=cell_size
        )

    def update(self, playing: bool, speed: int = 1):
        """Update simulation state.

        Args:
            playing: Whether simulation should be running.
            speed: Number of MD steps to perform per update.
        """
        if playing and self.engine:
            try:
                self.engine.run(steps=speed)
            except Exception as e:
                logger.error(f"MD step failed: {e}")

    def render(self, surface: pygame.Surface):
        """Render the simulation.

        Args:
            surface: Surface to render onto.
        """
        # Draw background
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)

        # Draw simulation cell boundary
        cell_rect = self._get_cell_rect()
        pygame.draw.rect(surface, self.CELL_COLOR, cell_rect)
        pygame.draw.rect(surface, colors.BORDER_COLOR, cell_rect, 2)

        # Draw atoms
        if self.engine and len(self.engine.atoms) > 0:
            self._render_atoms(surface)

    def _get_cell_rect(self) -> pygame.Rect:
        """Get the rectangle for the simulation cell display.

        Returns:
            Rectangle for cell, centered in widget with some margin.
        """
        margin = 20
        max_size = min(self.rect.width, self.rect.height) - 2 * margin

        return pygame.Rect(
            self.rect.centerx - max_size // 2,
            self.rect.centery - max_size // 2,
            max_size,
            max_size
        )

    def _render_atoms(self, surface: pygame.Surface):
        """Render all atoms in the simulation.

        Args:
            surface: Surface to render onto.
        """
        positions = self.engine.atoms.get_positions()
        symbols = self.engine.atoms.get_chemical_symbols()
        cell_size = self.engine.atoms.cell[0, 0]  # Cubic cell

        cell_rect = self._get_cell_rect()

        # Calculate scale: cell_size (Angstroms) -> cell_rect size (pixels)
        scale = cell_rect.width / cell_size

        # Sort atoms by z-coordinate for proper depth rendering
        z_coords = positions[:, 2]
        draw_order = np.argsort(z_coords)

        for idx in draw_order:
            pos = positions[idx]
            symbol = symbols[idx]

            # Project 3D -> 2D (simple orthogonal projection, xy plane)
            screen_x = cell_rect.left + pos[0] * scale
            screen_y = cell_rect.top + pos[1] * scale

            # Get atom properties
            color = ATOM_COLORS[symbol]
            radius_angstrom = self.atom_radii[symbol]

            # Scale radius based on z-depth for pseudo-3D effect
            z_depth = pos[2] / cell_size  # Normalize to 0-1
            depth_scale = 0.7 + 0.3 * z_depth  # Farther = smaller
            radius_pixels = int(radius_angstrom * scale * depth_scale)

            # Adjust brightness based on depth
            brightness = 0.6 + 0.4 * z_depth
            adjusted_color = tuple(int(c * brightness) for c in color)

            # Draw atom as circle
            if radius_pixels > 0:
                pygame.draw.circle(
                    surface,
                    adjusted_color,
                    (int(screen_x), int(screen_y)),
                    radius_pixels
                )
                # Draw outline
                pygame.draw.circle(
                    surface,
                    tuple(max(0, c - 40) for c in adjusted_color),
                    (int(screen_x), int(screen_y)),
                    radius_pixels,
                    1
                )

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events.

        Args:
            event: Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_click(event.pos)

    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click to add atom.

        Args:
            pos: Mouse position (x, y) in screen coordinates.
        """
        if not self.selected_element:
            logger.debug("No element selected, ignoring click")
            return

        cell_rect = self._get_cell_rect()

        # Check if click is inside simulation cell
        if not cell_rect.collidepoint(pos):
            logger.debug("Click outside simulation cell")
            return

        # Convert screen coordinates to simulation coordinates
        sim_pos = self._screen_to_sim(pos, cell_rect)

        if sim_pos is not None:
            self.engine.add_atom(self.selected_element, sim_pos)

    def _screen_to_sim(self, screen_pos: Tuple[int, int], cell_rect: pygame.Rect) -> Optional[np.ndarray]:
        """Convert screen coordinates to 3D simulation coordinates.

        Uses the center of mass of existing atoms for z-coordinate, or
        center of cell if no atoms exist.
        Also checks for collisions.

        Args:
            screen_pos: Screen position (x, y).
            cell_rect: Rectangle of the simulation cell on screen.

        Returns:
            3D position in simulation coordinates (Angstroms), or None if invalid.
        """
        cell_size = self.engine.atoms.cell[0, 0]  # Cubic cell

        # Calculate scale based on current cell_rect
        scale = cell_rect.width / cell_size

        # Convert screen pixels to Angstroms
        x_angstrom = (screen_pos[0] - cell_rect.left) / scale
        y_angstrom = (screen_pos[1] - cell_rect.top) / scale

        # Determine z coordinate
        if len(self.engine.atoms) > 0:
            # Use center of mass z-coordinate
            positions = self.engine.atoms.get_positions()
            z_angstrom = np.mean(positions[:, 2])
            # Check for collisions.
            if self.collision_threshold > 0:
                found = False
                fallback_z = None
                # Step through increments, increasing the z-coordinate until no collision is found.
                for dz in np.linspace(0, cell_size, int(cell_size/self.collision_threshold)):
                    # Wrap coordinates
                    z_angstrom = (z_angstrom + dz) % cell_size
                    # If all atoms are further away from the point than the collision threshold, we've found our point.
                    _, distances = ase.geometry.get_distances(positions, [[x_angstrom, y_angstrom, z_angstrom]], cell=self.engine.atoms.cell, pbc=True)
                    if np.all(distances > self.collision_threshold):
                        found = True
                        break
                    elif fallback_z is None and np.all(distances > 0):
                        # A fall-back. If no space with the specified collision threshold can be found,
                        # then at least find a space where the distances are non-zero.
                        # The simulation breaks if any distances are zero.
                        fallback_z = z_angstrom
                if not found:
                    if fallback_z is None:
                        logger.error(f"Unable to find anywhere safe to place an atom at ({x_angstrom},{y_angstrom}) (zero distance)! Not placing atom.")
                        return None
                    else:
                        logger.warning(f"Position ({x_angstrom},{y_angstrom}) is rather crowded (no free space of more than {self.collision_threshold} A). \
                                       Atoms might be unhappy.")

        else:
            # Use center of cell
            z_angstrom = cell_size / 2

        # Check bounds
        if 0 <= x_angstrom <= cell_size and 0 <= y_angstrom <= cell_size:
            return np.array([x_angstrom, y_angstrom, z_angstrom])
        else:
            logger.warning(
                f"Click position {screen_pos} (x,y)=({x_angstrom},{y_angstrom}) out of bounds")
            return None

    def set_rect(self, rect: pygame.Rect):
        """Update widget position and size.

        Args:
            rect: New rectangle defining widget position and size.
        """
        self.rect = rect
        logger.debug(f"SimulationWidget resized to {rect}")

    def reset(self):
        """Reset simulation by removing all atoms."""
        if self.engine:
            # Delete all atoms using slice notation
            del self.engine.atoms[:]
            logger.info("Simulation reset - all atoms removed")
