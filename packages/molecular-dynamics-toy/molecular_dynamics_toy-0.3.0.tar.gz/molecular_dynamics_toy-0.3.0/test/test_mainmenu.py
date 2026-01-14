"""Tests for MainMenu widgets."""

import pytest
import pygame
from molecular_dynamics_toy.widgets.base import TextBox
from molecular_dynamics_toy.widgets.menus import MainMenu


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_mainmenu_initialization(pygame_init):
    """Test that MainMenu initializes correctly."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)

    assert menu.rect == rect
    assert menu.title == "Menu"
    assert menu.visible is False
    assert menu.auto_close_on_select is False
    assert len(menu.items) >= 4  # About, Copyright, Website, Exit


def test_mainmenu_has_about_textbox(pygame_init):
    """Test that MainMenu has About textbox."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)

    assert menu.about_textbox is not None
    assert isinstance(menu.about_textbox, TextBox)
    assert menu.about_textbox.title == "About"


def test_mainmenu_about_textbox_has_version(pygame_init):
    """Test that About textbox contains version information."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)

    # Should contain "Version:" in the text
    assert "Version:" in menu.about_textbox.text


def test_mainmenu_open_close(pygame_init):
    """Test that MainMenu can be opened and closed."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)

    menu.open()
    assert menu.visible is True

    menu.close()
    assert menu.visible is False


def test_mainmenu_show_about(pygame_init):
    """Test that clicking About opens the About textbox."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)

    menu.open()

    # Find and click About menu item
    about_item = menu.items[0]  # First item is About
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': about_item.rect.center}
    )
    menu.handle_event(event)

    # About textbox should now be visible
    assert menu.about_textbox.visible is True


def test_mainmenu_exit_callback(pygame_init):
    """Test that Exit menu item calls exit callback."""
    rect = pygame.Rect(100, 100, 300, 300)
    exit_called = []

    def exit_callback():
        exit_called.append(True)

    menu = MainMenu(rect, exit_callback=exit_callback)
    menu.open()

    # Find and click Exit menu item
    exit_item = menu.items[-1]  # Last item is Exit
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': exit_item.rect.center}
    )
    menu.handle_event(event)

    # Exit callback should have been called
    assert len(exit_called) == 1


def test_mainmenu_doesnt_close_on_about_click(pygame_init):
    """Test that MainMenu stays open when About is clicked."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)
    menu.open()

    # Click About
    about_item = menu.items[0]
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': about_item.rect.center}
    )
    menu.handle_event(event)

    # Menu should still be open (auto_close_on_select=False)
    assert menu.visible is True


def test_mainmenu_render(pygame_init):
    """Test that MainMenu renders without crashing."""
    rect = pygame.Rect(100, 100, 300, 300)
    menu = MainMenu(rect)

    menu.open()

    surface = pygame.Surface((800, 600))
    menu.render(surface)  # Should not raise
