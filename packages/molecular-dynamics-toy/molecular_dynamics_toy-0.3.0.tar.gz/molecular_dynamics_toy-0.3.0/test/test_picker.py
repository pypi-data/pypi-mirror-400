"""Tests for the GUI application and widgets."""

import pytest
import pygame
from molecular_dynamics_toy.widgets.picker import PeriodicTableWidget, ElementButton


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_periodic_table_widget_initialization(pygame_init):
    """Test that PeriodicTableWidget initializes correctly."""
    rect = pygame.Rect(0, 0, 500, 400)
    widget = PeriodicTableWidget(rect)

    assert widget.rect == rect
    assert widget.selected_element is None
    assert len(widget.buttons) > 0  # Should have element buttons


def test_periodic_table_has_all_elements(pygame_init):
    """Test that periodic table contains all expected elements up to Pu."""
    rect = pygame.Rect(0, 0, 500, 400)
    widget = PeriodicTableWidget(rect)

    symbols = {button.symbol for button in widget.buttons}

    # Check some key elements
    assert 'H' in symbols
    assert 'He' in symbols
    assert 'C' in symbols
    assert 'Fe' in symbols
    assert 'Au' in symbols
    assert 'Pu' in symbols

    # Should have 94 elements (H to Pu minus gaps)
    assert len(symbols) == len(widget.ELEMENT_POSITIONS)


def test_element_button_click(pygame_init):
    """Test that clicking an element button selects it."""
    rect = pygame.Rect(10, 10, 50, 50)
    button = ElementButton('H', rect)

    assert button.selected is False

    # Click inside button
    clicked = button.handle_click((30, 30))

    assert clicked is True
    assert button.selected is True


def test_element_button_toggle(pygame_init):
    """Test that clicking a selected button deselects it."""
    rect = pygame.Rect(10, 10, 50, 50)
    button = ElementButton('H', rect)

    # First click: select
    button.handle_click((30, 30))
    assert button.selected is True

    # Second click: deselect
    button.handle_click((30, 30))
    assert button.selected is False


def test_element_button_click_outside(pygame_init):
    """Test that clicking outside button doesn't select it."""
    rect = pygame.Rect(10, 10, 50, 50)
    button = ElementButton('H', rect)

    clicked = button.handle_click((100, 100))

    assert clicked is False
    assert button.selected is False


def test_periodic_table_single_selection(pygame_init):
    """Test that only one element can be selected at a time."""
    rect = pygame.Rect(0, 0, 1000, 600)
    widget = PeriodicTableWidget(rect)

    # Find H and C buttons
    h_button = next(b for b in widget.buttons if b.symbol == 'H')
    c_button = next(b for b in widget.buttons if b.symbol == 'C')

    # Click H
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                               'button': 1, 'pos': h_button.rect.center})
    widget.handle_event(event)

    assert widget.selected_element == 'H'
    assert h_button.selected is True

    # Click C
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                               'button': 1, 'pos': c_button.rect.center})
    widget.handle_event(event)

    assert widget.selected_element == 'C'
    assert c_button.selected is True
    assert h_button.selected is False  # H should be deselected


def test_periodic_table_deselection(pygame_init):
    """Test that clicking a selected element deselects it."""
    rect = pygame.Rect(0, 0, 1000, 600)
    widget = PeriodicTableWidget(rect)

    h_button = next(b for b in widget.buttons if b.symbol == 'H')

    # Click H to select
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                               'button': 1, 'pos': h_button.rect.center})
    widget.handle_event(event)
    assert widget.selected_element == 'H'

    # Click H again to deselect
    widget.handle_event(event)
    assert widget.selected_element is None
    assert h_button.selected is False


def test_periodic_table_resize(pygame_init):
    """Test that periodic table can be resized."""
    rect1 = pygame.Rect(0, 0, 500, 400)
    widget = PeriodicTableWidget(rect1)

    initial_button_count = len(widget.buttons)

    # Resize
    rect2 = pygame.Rect(0, 0, 800, 600)
    widget.set_rect(rect2)

    assert widget.rect == rect2
    # Same number of buttons
    assert len(widget.buttons) == initial_button_count


def test_periodic_table_resize_preserves_selection(pygame_init):
    """Test that resizing preserves the selected element."""
    rect1 = pygame.Rect(0, 0, 1000, 600)
    widget = PeriodicTableWidget(rect1)

    # Select an element
    h_button = next(b for b in widget.buttons if b.symbol == 'H')
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                               'button': 1, 'pos': h_button.rect.center})
    widget.handle_event(event)

    assert widget.selected_element == 'H'

    # Resize
    rect2 = pygame.Rect(0, 0, 800, 500)
    widget.set_rect(rect2)

    # Selection should be preserved
    assert widget.selected_element == 'H'
    h_button_new = next(b for b in widget.buttons if b.symbol == 'H')
    assert h_button_new.selected is True


def test_element_button_hover(pygame_init):
    """Test that hovering over element button updates hover state."""
    rect = pygame.Rect(10, 10, 50, 50)
    button = ElementButton('H', rect)

    # Hover inside
    button.handle_hover((30, 30))
    assert button.hovered is True

    # Hover outside
    button.handle_hover((100, 100))
    assert button.hovered is False


def test_element_button_hover_and_select(pygame_init):
    """Test that button can be both hovered and selected."""
    rect = pygame.Rect(10, 10, 50, 50)
    button = ElementButton('H', rect)

    # Select the button
    button.handle_click((30, 30))
    assert button.selected is True

    # Hover over selected button
    button.handle_hover((30, 30))
    assert button.hovered is True
    assert button.selected is True

    # Move away
    button.handle_hover((100, 100))
    assert button.hovered is False
    assert button.selected is True  # Still selected


def test_periodic_table_hover_event(pygame_init):
    """Test that periodic table widget handles hover events."""
    rect = pygame.Rect(0, 0, 1000, 600)
    widget = PeriodicTableWidget(rect)

    h_button = next(b for b in widget.buttons if b.symbol == 'H')

    # Send mouse motion event over H button
    event = pygame.event.Event(
        pygame.MOUSEMOTION,
        {'pos': h_button.rect.center}
    )
    widget.handle_event(event)

    assert h_button.hovered is True
