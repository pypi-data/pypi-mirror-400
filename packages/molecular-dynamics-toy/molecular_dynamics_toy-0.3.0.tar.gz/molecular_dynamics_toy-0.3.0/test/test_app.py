"""Tests for the GUI application and widgets."""

import pytest
import pygame
from unittest.mock import patch
from molecular_dynamics_toy.app import MDApplication


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_application_initialization(pygame_init):
    """Test that MDApplication initializes without crashing."""
    app = MDApplication(fps=30, calculator="mock")

    assert app.screen is not None
    assert app.clock is not None
    assert app.fps == 30
    assert app.running is False  # Not started yet


def test_application_has_correct_dimensions(pygame_init):
    """Test that application window has expected dimensions."""
    app = MDApplication(calculator="mock")

    assert app.WINDOW_WIDTH == 1400
    assert app.WINDOW_HEIGHT == 800
    assert app.screen.get_width() == 1400
    assert app.screen.get_height() == 800


def test_mdapplication_initialization_custom_fps(pygame_init):
    """Test MDApplication with custom FPS."""
    app = MDApplication(fps=60, calculator='mock')
    
    assert app.fps == 60


def test_mdapplication_update_layout(pygame_init):
    """Test that _update_layout recalculates widget positions."""
    app = MDApplication(calculator='mock')
    
    # Change window size
    app.WINDOW_WIDTH = 1024
    app.WINDOW_HEIGHT = 768
    app._update_layout()
    
    # Widgets should have updated positions
    assert app.simulation_widget.rect is not None
    assert app.periodic_table_widget.rect is not None
    assert app.controls_widget.rect is not None


def test_mdapplication_update(pygame_init):
    """Test that update() runs without error."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Should run without raising
    app.update()


def test_mdapplication_update_with_reset_request(pygame_init):
    """Test that update() handles reset requests."""
    from ase import Atoms
    
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Add some atoms
    atoms = Atoms('H2', positions=[[0, 0, 0], [1, 0, 0]])
    atoms.set_cell([10, 10, 10])
    atoms.pbc = True
    app.simulation_widget.engine.atoms = atoms
    
    assert len(app.simulation_widget.engine.atoms) == 2
    
    # Request reset
    app.controls_widget.reset_requested = True
    app.update()
    
    # Atoms should be cleared
    assert len(app.simulation_widget.engine.atoms) == 0
    assert app.controls_widget.reset_requested is False


def test_mdapplication_update_with_preset_menu_request(pygame_init):
    """Test that update() opens preset menu when requested."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    assert app.preset_menu.visible is False
    
    # Request preset menu
    app.controls_widget.open_preset_menu_requested = True
    app.update()
    
    # Menu should be open
    assert app.preset_menu.visible is True
    assert app.controls_widget.open_preset_menu_requested is False


def test_mdapplication_update_with_main_menu_request(pygame_init):
    """Test that update() opens main menu when requested."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    assert app.main_menu.visible is False
    
    # Request main menu
    app.controls_widget.open_main_menu_requested = True
    app.update()
    
    # Menu should be open
    assert app.main_menu.visible is True
    assert app.controls_widget.open_main_menu_requested is False


def test_mdapplication_render(pygame_init):
    """Test that render() draws without error."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Should render without raising
    app.render()


def test_mdapplication_render_with_fps(pygame_init):
    """Test that render() draws FPS counter when enabled."""
    app = MDApplication(calculator='mock', show_fps=True)
    
    # Should render without raising
    app.render()


def test_mdapplication_handle_quit_event(pygame_init):
    """Test that QUIT event stops the application."""
    app = MDApplication(calculator='mock', show_fps=False)
    app.running = True
    
    # Post QUIT event
    quit_event = pygame.event.Event(pygame.QUIT)
    pygame.event.post(quit_event)
    
    app.handle_events()
    
    assert app.running is False


def test_mdapplication_handle_videoresize_event(pygame_init):
    """Test that VIDEORESIZE event updates window size."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    old_width = app.WINDOW_WIDTH
    old_height = app.WINDOW_HEIGHT
    
    # Post VIDEORESIZE event
    resize_event = pygame.event.Event(pygame.VIDEORESIZE, {'w': 1024, 'h': 768})
    pygame.event.post(resize_event)
    
    app.handle_events()
    
    assert app.WINDOW_WIDTH == 1024
    assert app.WINDOW_HEIGHT == 768
    assert app.WINDOW_WIDTH != old_width or app.WINDOW_HEIGHT != old_height


def test_mdapplication_load_preset(pygame_init):
    """Test that _load_preset loads a preset into the simulation."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Load water preset
    app._load_preset('water')
    
    # Should have atoms now
    assert len(app.simulation_widget.engine.atoms) > 0


def test_mdapplication_load_preset_updates_cell_size(pygame_init):
    """Test that _load_preset updates cell size control."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Load preset
    app._load_preset('water')
    
    # Cell size control should match loaded structure
    loaded_cell_size = app.simulation_widget.engine.atoms.cell[0, 0]
    control_cell_size = app.controls_widget.cell_size_control.cell_size
    
    assert abs(loaded_cell_size - control_cell_size) < 1e-6


def test_mdapplication_exit_application(pygame_init):
    """Test that _exit_application stops the app."""
    app = MDApplication(calculator='mock', show_fps=False)
    app.running = True
    
    app.exit()
    
    assert app.running is False


def test_mdapplication_run_single_iteration(pygame_init):
    """Test that run() can execute at least one iteration."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Mock the clock to prevent infinite loop
    with patch.object(app, 'handle_events') as mock_events:
        # Set running to False after first iteration
        def stop_after_first():
            app.running = False
        mock_events.side_effect = stop_after_first
        
        app.run()
        
        # Should have called handle_events at least once
        assert mock_events.call_count >= 1


def test_mdapplication_update_simulation_parameters(pygame_init):
    """Test that update() synchronizes simulation parameters."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Change control values
    app.controls_widget.temperature_slider.temperature = 500.0
    app.controls_widget.timestep_control.value = 2.0
    
    # Update should sync to engine
    app.update()
    
    assert app.simulation_widget.engine.temperature == 500.0
    assert app.simulation_widget.engine.timestep == 2.0


def test_mdapplication_selected_element_sync(pygame_init):
    """Test that selected element syncs from periodic table to simulation."""
    app = MDApplication(calculator='mock', show_fps=False)
    
    # Select an element
    h_button = None
    for button in app.periodic_table_widget.buttons:
        if button.symbol == 'H':
            h_button = button
            break
    
    assert h_button is not None
    h_button.selected = True
    app.periodic_table_widget.selected_element = 'H'
    
    # Update should sync
    app.update()
    
    assert app.simulation_widget.selected_element == 'H'


def test_helpoverlay(pygame_init):
    # It's rather hard to test the help overlay without mocking up
    # all the UI elements which it connects to.
    # So I may as well cut out the middle-man and do an integration test
    app = MDApplication(calculator = "mock", show_fps=False)

    assert app.help_overlay.visible == False, "Help overlay didn't start invisible"
    # Click the button to open the overlay
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                         {'button': 1, 'pos': app.help_button.rect.center}))
    app.handle_events()
    assert app.help_overlay.visible == True, \
        "Help overlay didn't become visible when help button was clicked."
    # Check that rendering runs without breaking.
    app.help_overlay.render(app.screen)
    # Another click to close it
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                         {'button': 1, 'pos': (1,1)}))
    app.handle_events()
    assert app.help_overlay.visible == False, \
        "Help overlay didn't close when mouse button was clicked."
    # Escape should also make it go away.
    app.help_overlay.open()
    assert app.help_overlay.visible == True, \
        "HelpOverlay.open() didn't open."
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
    app.handle_events()
    assert app.help_overlay.visible == False, \
        "Help overlay didn't close when ESC was pressed."
