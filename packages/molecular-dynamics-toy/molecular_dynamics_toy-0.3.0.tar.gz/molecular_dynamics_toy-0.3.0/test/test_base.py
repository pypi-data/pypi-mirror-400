"""Tests for widgets.base."""

import pytest
import pygame
from molecular_dynamics_toy.widgets.base import Button, ToggleButton, TextButton


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_button_initialization(pygame_init):
    """Test that Button initializes correctly."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect)

    assert button.rect == rect
    assert button.hovered is False
    assert button.enabled is True
    assert button.callback is None


def test_button_with_callback(pygame_init):
    """Test that Button can be initialized with callback."""
    rect = pygame.Rect(10, 10, 60, 60)
    callback_called = []

    def callback():
        callback_called.append(True)

    button = Button(rect, callback=callback)

    assert button.callback is not None


def test_button_disabled_initialization(pygame_init):
    """Test that Button can be initialized as disabled."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect, enabled=False)

    assert button.enabled is False


def test_button_click(pygame_init):
    """Test that clicking button returns True."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect)

    clicked = button.handle_click((30, 30))

    assert clicked is True


def test_button_click_outside(pygame_init):
    """Test that clicking outside button returns False."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect)

    clicked = button.handle_click((100, 100))

    assert clicked is False


def test_button_calls_callback(pygame_init):
    """Test that clicking button calls callback."""
    rect = pygame.Rect(10, 10, 60, 60)
    callback_called = []

    def callback():
        callback_called.append(True)

    button = Button(rect, callback=callback)
    button.handle_click((30, 30))

    assert len(callback_called) == 1


def test_button_disabled_no_click(pygame_init):
    """Test that disabled button doesn't respond to clicks."""
    rect = pygame.Rect(10, 10, 60, 60)
    callback_called = []

    def callback():
        callback_called.append(True)

    button = Button(rect, callback=callback, enabled=False)
    clicked = button.handle_click((30, 30))

    assert clicked is False
    assert len(callback_called) == 0


def test_button_hover(pygame_init):
    """Test that hovering over button updates hover state."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect)

    # Hover inside
    button.handle_hover((30, 30))
    assert button.hovered is True

    # Hover outside
    button.handle_hover((100, 100))
    assert button.hovered is False


def test_button_disabled_no_hover(pygame_init):
    """Test that disabled button doesn't register hover."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect, enabled=False)

    button.handle_hover((30, 30))

    assert button.hovered is False


def test_button_render(pygame_init):
    """Test that button renders without crashing."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = Button(rect)

    surface = pygame.Surface((100, 100))
    button.render(surface)  # Should not raise


def test_button_on_click_override(pygame_init):
    """Test that on_click can be overridden."""
    rect = pygame.Rect(10, 10, 60, 60)
    on_click_called = []

    class TestButton(Button):
        def on_click(self):
            on_click_called.append(True)

    button = TestButton(rect)
    button.handle_click((30, 30))

    assert len(on_click_called) == 1


def test_toggle_button_initialization(pygame_init):
    """Test that ToggleButton initializes correctly."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect)

    assert button.rect == rect
    assert button.selected is False
    assert button.hovered is False
    assert button.enabled is True


def test_toggle_button_custom_initial_state(pygame_init):
    """Test that ToggleButton can be initialized as selected."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect, selected=True)

    assert button.selected is True


def test_toggle_button_click_toggles(pygame_init):
    """Test that clicking toggles the selected state."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect)

    # First click: select
    button.handle_click((30, 30))
    assert button.selected is True

    # Second click: deselect
    button.handle_click((30, 30))
    assert button.selected is False


def test_toggle_button_click_returns_true(pygame_init):
    """Test that clicking toggle button returns True."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect)

    clicked = button.handle_click((30, 30))

    assert clicked is True


def test_toggle_button_with_callback(pygame_init):
    """Test that toggle button calls callback when clicked."""
    rect = pygame.Rect(10, 10, 60, 60)
    callback_called = []

    def callback():
        callback_called.append(True)

    button = ToggleButton(rect, callback=callback)
    button.handle_click((30, 30))

    assert len(callback_called) == 1
    assert button.selected is True


def test_toggle_button_disabled_no_toggle(pygame_init):
    """Test that disabled toggle button doesn't toggle."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect, enabled=False)

    button.handle_click((30, 30))

    assert button.selected is False


def test_toggle_button_render_unselected(pygame_init):
    """Test that unselected toggle button renders without crashing."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect)

    surface = pygame.Surface((100, 100))
    button.render(surface)  # Should not raise


def test_toggle_button_render_selected(pygame_init):
    """Test that selected toggle button renders without crashing."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect, selected=True)

    surface = pygame.Surface((100, 100))
    button.render(surface)  # Should not raise


def test_toggle_button_render_disabled(pygame_init):
    """Test that disabled toggle button renders without crashing."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect, enabled=False)

    surface = pygame.Surface((100, 100))
    button.render(surface)  # Should not raise


def test_toggle_button_hover_selected(pygame_init):
    """Test that selected toggle button can be hovered."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ToggleButton(rect, selected=True)

    button.handle_hover((30, 30))

    assert button.hovered is True
    assert button.selected is True


def test_toggle_button_on_click_override(pygame_init):
    """Test that on_click can be overridden in ToggleButton."""
    rect = pygame.Rect(10, 10, 60, 60)
    on_click_called = []

    class TestToggleButton(ToggleButton):
        def on_click(self):
            on_click_called.append(True)
            super().on_click()  # Call parent to maintain toggle behavior

    button = TestToggleButton(rect)
    button.handle_click((30, 30))

    assert len(on_click_called) == 1
    assert button.selected is True


def test_text_button_initialization(pygame_init):
    """Test that TextButton initializes correctly."""
    rect = pygame.Rect(10, 10, 60, 30)
    button = TextButton(rect, "Test")

    assert button.rect == rect
    assert button.text == "Test"
    assert button.enabled is True
    assert button.hovered is False


def test_text_button_custom_font_size(pygame_init):
    """Test that TextButton can use custom font size."""
    rect = pygame.Rect(10, 10, 60, 30)
    button = TextButton(rect, "Test", font_size=24)

    assert button.font.get_height() > 0  # Font was created


def test_text_button_click(pygame_init):
    """Test that clicking text button works."""
    rect = pygame.Rect(10, 10, 60, 30)
    button = TextButton(rect, "Test")

    clicked = button.handle_click((30, 20))

    assert clicked is True


def test_text_button_with_callback(pygame_init):
    """Test that text button calls callback when clicked."""
    rect = pygame.Rect(10, 10, 60, 30)
    callback_called = []

    def callback():
        callback_called.append(True)

    button = TextButton(rect, "Test", callback=callback)
    button.handle_click((30, 20))

    assert len(callback_called) == 1


def test_text_button_disabled(pygame_init):
    """Test that disabled text button doesn't respond to clicks."""
    rect = pygame.Rect(10, 10, 60, 30)
    callback_called = []

    def callback():
        callback_called.append(True)

    button = TextButton(rect, "Test", callback=callback, enabled=False)
    clicked = button.handle_click((30, 20))

    assert clicked is False
    assert len(callback_called) == 0


def test_text_button_render(pygame_init):
    """Test that text button renders without crashing."""
    rect = pygame.Rect(10, 10, 60, 30)
    button = TextButton(rect, "Test")

    surface = pygame.Surface((100, 100))
    button.render(surface)  # Should not raise
