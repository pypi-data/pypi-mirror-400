"""Tests for TextBox widgets."""

import pytest
import pygame
from molecular_dynamics_toy.widgets.base import TextBox


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


# TextBox tests

def test_textbox_initialization(pygame_init):
    """Test that TextBox initializes correctly."""
    rect = pygame.Rect(100, 100, 400, 500)
    text = "This is a test text."
    textbox = TextBox(rect, title="Test", text=text)

    assert textbox.rect == rect
    assert textbox.title == "Test"
    assert textbox.text == text
    assert textbox.visible is False
    assert len(textbox.wrapped_lines) > 0


def test_textbox_text_wrapping(pygame_init):
    """Test that TextBox wraps long text."""
    rect = pygame.Rect(100, 100, 300, 400)
    long_text = "This is a very long line of text that should definitely wrap to multiple lines when displayed in the text box."
    textbox = TextBox(rect, text=long_text)

    # Should have wrapped into multiple lines
    assert len(textbox.wrapped_lines) > 1


def test_textbox_paragraph_breaks(pygame_init):
    """Test that TextBox preserves paragraph breaks."""
    rect = pygame.Rect(100, 100, 400, 500)
    text = "First paragraph.\n\nSecond paragraph."
    textbox = TextBox(rect, text=text)

    # Should have empty line for paragraph break
    assert "" in textbox.wrapped_lines


def test_textbox_open_close(pygame_init):
    """Test that TextBox can be opened and closed."""
    rect = pygame.Rect(100, 100, 400, 500)
    textbox = TextBox(rect, text="Test")

    assert textbox.visible is False

    textbox.open()
    assert textbox.visible is True

    textbox.close()
    assert textbox.visible is False


def test_textbox_has_close_button(pygame_init):
    """Test that TextBox has a close button."""
    rect = pygame.Rect(100, 100, 400, 500)
    textbox = TextBox(rect, text="Test")

    assert textbox.show_close_button is True
    assert textbox.close_button is not None


def test_textbox_close_button_works(pygame_init):
    """Test that clicking close button closes TextBox."""
    rect = pygame.Rect(100, 100, 400, 500)
    textbox = TextBox(rect, text="Test")

    textbox.open()

    # Click close button
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': textbox.close_button.rect.center}
    )
    textbox.handle_event(event)

    assert textbox.visible is False


def test_textbox_scrolling_with_long_text(pygame_init):
    """Test that TextBox creates scrollbar for long text."""
    rect = pygame.Rect(100, 100, 400, 300)  # Small height
    long_text = "\n".join([f"Line {i}" for i in range(100)])
    textbox = TextBox(rect, text=long_text)

    textbox.open()

    # Should need scrollbar
    assert textbox._needs_scrollbar() is True
    assert textbox.scrollbar is not None


def test_textbox_no_scrollbar_for_short_text(pygame_init):
    """Test that TextBox doesn't create scrollbar for short text."""
    rect = pygame.Rect(100, 100, 400, 500)  # Large height
    short_text = "Short text."
    textbox = TextBox(rect, text=short_text)

    textbox.open()

    # Should not need scrollbar
    assert textbox._needs_scrollbar() is False
    assert textbox.scrollbar is None


def test_textbox_render_when_visible(pygame_init):
    """Test that TextBox renders when visible."""
    rect = pygame.Rect(100, 100, 400, 500)
    textbox = TextBox(rect, text="Test")

    textbox.open()

    surface = pygame.Surface((800, 600))
    textbox.render(surface)  # Should not raise


def test_textbox_render_when_not_visible(pygame_init):
    """Test that TextBox doesn't render when not visible."""
    rect = pygame.Rect(100, 100, 400, 500)
    textbox = TextBox(rect, text="Test")

    surface = pygame.Surface((800, 600))
    textbox.render(surface)  # Should not raise, should do nothing


def test_textbox_close_on_outside_click(pygame_init):
    """Test that TextBox closes when clicking outside."""
    rect = pygame.Rect(100, 100, 400, 500)
    textbox = TextBox(rect, text="Test")

    textbox.open()

    # Click outside textbox
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': (50, 50)}
    )
    textbox.handle_event(event)

    assert textbox.visible is False
