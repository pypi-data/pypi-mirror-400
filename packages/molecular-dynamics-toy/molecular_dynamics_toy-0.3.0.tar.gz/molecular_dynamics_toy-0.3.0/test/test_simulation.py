"""Tests for the simulation widget."""

import pytest
import pygame
import numpy as np
from molecular_dynamics_toy.widgets.simulation import SimulationWidget
from molecular_dynamics_toy.calculators import get_calculator


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_simulation_widget_initialization(pygame_init):
    """Test that SimulationWidget initializes correctly."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    assert widget.rect == rect
    assert widget.engine is not None
    assert widget.calculator is calc
    assert widget.radius_type == "covalent"


def test_simulation_widget_update_when_paused(pygame_init):
    """Test that simulation doesn't advance when paused."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    initial_positions = widget.engine.atoms.get_positions().copy()

    # Update with playing=False
    widget.update(playing=False)

    final_positions = widget.engine.atoms.get_positions()
    np.testing.assert_array_equal(initial_positions, final_positions)


def test_simulation_widget_update_when_playing(pygame_init):
    """Test that simulation advances when playing."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    # Add an atom
    widget.engine.add_atom("H", [2, 2, 2])
    widget.engine.add_atom("H", [2, 3, 2])
    initial_positions = widget.engine.atoms.get_positions().copy()

    # Update with playing=True
    widget.update(playing=True)

    final_positions = widget.engine.atoms.get_positions()

    # Positions should have changed (atoms have velocities from temperature)
    assert not np.array_equal(initial_positions, final_positions)


def test_simulation_widget_covalent_radii(pygame_init):
    """Test that widget can use covalent radii."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc, radius_type="covalent")

    assert widget.radius_type == "covalent"

    # Check that covalent radii are generally smaller
    from molecular_dynamics_toy.data.atom_properties import ATOM_VDW_RADII, ATOM_COVALENT_RADII
    assert ATOM_COVALENT_RADII['H'] < ATOM_VDW_RADII['H']
    assert widget.atom_radii['H'] == ATOM_COVALENT_RADII['H']


def test_simulation_widget_vdw_radii_default(pygame_init):
    """Test that widget defaults to van der Waals radii."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc, radius_type="vdw")

    from molecular_dynamics_toy.data.atom_properties import ATOM_VDW_RADII
    assert widget.atom_radii['H'] == ATOM_VDW_RADII['H']


def test_simulation_widget_resize(pygame_init):
    """Test that simulation widget can be resized."""
    rect1 = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect1, calculator=calc)

    rect2 = pygame.Rect(0, 0, 800, 800)
    widget.set_rect(rect2)

    assert widget.rect == rect2


def test_simulation_widget_get_cell_rect(pygame_init):
    """Test that cell rect is calculated correctly."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    cell_rect = widget._get_cell_rect()

    # Cell should be square and centered with margin
    assert cell_rect.width == cell_rect.height
    assert cell_rect.width <= rect.width - 40  # 2*margin
    assert cell_rect.centerx == rect.centerx
    assert cell_rect.centery == rect.centery


def test_simulation_widget_render_doesnt_crash(pygame_init):
    """Test that rendering doesn't crash."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    surface = pygame.Surface((700, 700))

    # Should not raise
    widget.render(surface)


def test_simulation_widget_handle_event(pygame_init):
    """Test that widget handles events without crashing."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    # Create a dummy event
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                               'button': 1, 'pos': (100, 100)})

    # Should not raise
    widget.handle_event(event)


def test_simulation_widget_screen_to_sim_conversion(pygame_init):
    """Test conversion from screen coordinates to simulation coordinates."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    cell_rect = widget._get_cell_rect()

    # Click in center of cell should give center coordinates
    center_screen = (cell_rect.centerx, cell_rect.centery)
    sim_pos = widget._screen_to_sim(center_screen, cell_rect)

    assert sim_pos is not None
    cell_size = widget.engine.atoms.cell[0, 0]

    # Should be near center (within reasonable tolerance)
    assert abs(sim_pos[0] - cell_size / 2) < 0.5
    assert abs(sim_pos[1] - cell_size / 2) < 0.5


def test_simulation_widget_screen_to_sim_out_of_bounds(pygame_init):
    """Test that clicks outside cell return None."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    cell_rect = widget._get_cell_rect()

    # Click outside cell boundary
    outside_pos = (cell_rect.right + 10, cell_rect.top + 10)
    sim_pos = widget._screen_to_sim(outside_pos, cell_rect)

    assert sim_pos is None


def test_simulation_widget_add_atom_on_click(pygame_init):
    """Test that clicking adds an atom when element is selected."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    # Remove test atoms
    widget.engine.atoms = widget.engine.atoms[[]]  # Empty atoms object
    widget.engine.atoms.cell = [10.0, 10.0, 10.0]
    widget.engine.atoms.pbc = True

    initial_count = len(widget.engine.atoms)

    # Select an element
    widget.selected_element = 'C'

    # Click in center of cell
    cell_rect = widget._get_cell_rect()
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': cell_rect.center}
    )
    widget.handle_event(click_event)

    # Should have added one atom
    assert len(widget.engine.atoms) == initial_count + 1
    assert widget.engine.atoms[-1].symbol == 'C'


def test_simulation_widget_no_add_without_selection(pygame_init):
    """Test that clicking without element selected doesn't add atom."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    initial_count = len(widget.engine.atoms)

    # No element selected
    widget.selected_element = None

    # Click in cell
    cell_rect = widget._get_cell_rect()
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': cell_rect.center}
    )
    widget.handle_event(click_event)

    # Should not have added atom
    assert len(widget.engine.atoms) == initial_count


def test_simulation_widget_no_add_outside_cell(pygame_init):
    """Test that clicking outside cell doesn't add atom."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    initial_count = len(widget.engine.atoms)

    # Select an element
    widget.selected_element = 'C'

    # Click outside cell
    cell_rect = widget._get_cell_rect()
    outside_pos = (cell_rect.right + 50, cell_rect.top + 50)
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': outside_pos}
    )
    widget.handle_event(click_event)

    # Should not have added atom
    assert len(widget.engine.atoms) == initial_count


def test_simulation_widget_z_coordinate_with_atoms(pygame_init):
    """Test that new atoms get z-coordinate from center of mass."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    # Add some atoms
    widget.engine.add_atom('H', [3, 3, 0.5])
    widget.engine.add_atom('H', [4, 7, 1.7])

    # Get z center of mass from existing atoms
    initial_positions = widget.engine.atoms.get_positions()
    expected_z = np.mean(initial_positions[:, 2])

    widget.selected_element = 'C'

    cell_rect = widget._get_cell_rect()
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': cell_rect.center}
    )
    widget.handle_event(click_event)

    # Check that new atom has z near center of mass
    new_atom_z = widget.engine.atoms.get_positions()[-1, 2]
    assert abs(new_atom_z - expected_z) < 0.1


def test_simulation_widget_z_coordinate_empty_cell(pygame_init):
    """Test that new atoms get z-coordinate at cell center when no atoms exist."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    cell_size = widget.engine.atoms.cell[0, 0]

    widget.selected_element = 'C'

    cell_rect = widget._get_cell_rect()
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': cell_rect.center}
    )
    widget.handle_event(click_event)

    # Check that new atom has z at cell center
    new_atom_z = widget.engine.atoms.get_positions()[0, 2]
    assert abs(new_atom_z - cell_size / 2) < 0.1

def test_simulation_widget_double_click(pygame_init):
    """Test that attempting to place two atoms in the same place applies a z-offset (to avoid divide-by-zero)."""
    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    widget.selected_element = 'H'

    cell_rect = widget._get_cell_rect()
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': cell_rect.center}
    )
    # Click twice in the same place.
    widget.handle_event(click_event)
    widget.handle_event(click_event)

    # Check that new atom has z at cell center
    positions = widget.engine.atoms.get_positions()
    assert positions[0, 0] == positions[1, 0], "x-positions incorrectly offset on double click."
    assert positions[0, 1] == positions[1, 1], "y-positions incorrectly offset on double click."
    assert positions[0, 2] != positions[1, 2], "z-positions should be offset on double click."

def test_simulation_widget_update_with_speed(pygame_init):
    """Test that simulation widget respects speed parameter."""
    from molecular_dynamics_toy.calculators import get_calculator

    rect = pygame.Rect(0, 0, 700, 700)
    calc = get_calculator("mock")
    widget = SimulationWidget(rect, calculator=calc)

    # Add some atoms for testing
    widget.engine.add_atom('H', [5, 5, 5])
    widget.engine.add_atom('H', [5.74, 5, 5])

    initial_positions = widget.engine.atoms.get_positions().copy()

    # Update with speed=5
    widget.update(playing=True, speed=5)

    # Positions should have changed
    final_positions = widget.engine.atoms.get_positions()
    assert not np.array_equal(initial_positions, final_positions)

def test_simulation_widget_render_with_atoms(pygame_init):
    """Test that SimulationWidget renders atoms correctly."""
    from molecular_dynamics_toy.calculators import MockCalculator
    from ase import Atoms
    
    rect = pygame.Rect(0, 0, 400, 400)
    calculator = MockCalculator()
    widget = SimulationWidget(rect, calculator=calculator)
    
    # Add some atoms to the engine
    atoms = Atoms('H2O', positions=[[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    atoms.set_cell([10, 10, 10])
    atoms.pbc = True
    widget.engine.atoms = atoms
    
    # Create surface and render
    surface = pygame.Surface((800, 600))
    widget.render(surface)  # Should not raise
    
    # Test rendering with different atom types
    atoms = Atoms('CNO', positions=[[2, 2, 2], [3, 3, 3], [4, 4, 4]])
    atoms.set_cell([10, 10, 10])
    atoms.pbc = True
    widget.engine.atoms = atoms
    
    widget.render(surface)  # Should not raise


def test_simulation_widget_reset(pygame_init):
    """Test that SimulationWidget.reset() clears atoms."""
    from molecular_dynamics_toy.calculators import MockCalculator
    from ase import Atoms
    
    rect = pygame.Rect(0, 0, 400, 400)
    calculator = MockCalculator()
    widget = SimulationWidget(rect, calculator=calculator)
    
    # Add some atoms
    atoms = Atoms('H2O', positions=[[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    atoms.set_cell([10, 10, 10])
    atoms.pbc = True
    widget.engine.atoms = atoms
    
    assert len(widget.engine.atoms) == 3
    
    # Reset should clear atoms
    widget.reset()
    
    assert len(widget.engine.atoms) == 0


def test_simulation_widget_reset_multiple_times(pygame_init):
    """Test that reset can be called multiple times safely."""
    from molecular_dynamics_toy.calculators import MockCalculator
    from ase import Atoms
    
    rect = pygame.Rect(0, 0, 400, 400)
    calculator = MockCalculator()
    widget = SimulationWidget(rect, calculator=calculator)
    
    # Add atoms
    atoms = Atoms('H', positions=[[5, 5, 5]])
    atoms.set_cell([10, 10, 10])
    atoms.pbc = True
    widget.engine.atoms = atoms
    
    # Reset multiple times
    widget.reset()
    widget.reset()
    widget.reset()
    
    assert len(widget.engine.atoms) == 0