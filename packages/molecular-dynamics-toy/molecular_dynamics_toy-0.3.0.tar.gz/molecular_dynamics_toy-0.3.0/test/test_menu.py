"""Tests for menu classes."""

import pytest
import pygame
from molecular_dynamics_toy.widgets.base import Menu, MenuItem, CloseButton


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_menu_initialization(pygame_init):
    """Test that Menu initializes correctly."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, title="Test Menu")

    assert menu.rect == rect
    assert menu.title == "Test Menu"
    assert menu.visible is False
    assert menu.show_close_button is True
    assert menu.close_on_outside_click is True
    assert menu.auto_close_on_select is True
    assert len(menu.items) == 0


def test_menu_custom_options(pygame_init):
    """Test that Menu can be initialized with custom options."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, title="Custom",
                show_close_button=False,
                close_on_outside_click=False,
                auto_close_on_select=False)

    assert menu.show_close_button is False
    assert menu.close_button is None
    assert menu.close_on_outside_click is False
    assert menu.auto_close_on_select is False


def test_menu_open_close(pygame_init):
    """Test opening and closing menu."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    assert menu.visible is False

    menu.open()
    assert menu.visible is True

    menu.close()
    assert menu.visible is False


def test_menu_toggle(pygame_init):
    """Test toggling menu visibility."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    menu.toggle()
    assert menu.visible is True

    menu.toggle()
    assert menu.visible is False


def test_menu_add_item(pygame_init):
    """Test adding items to menu."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    menu.add_item("Item 1")
    menu.add_item("Item 2")

    assert len(menu.items) == 2
    assert menu.items[0].text == "Item 1"
    assert menu.items[1].text == "Item 2"


def test_menu_item_callback(pygame_init):
    """Test that menu item callback is called."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    callback_called = []
    menu.add_item("Test", lambda: callback_called.append(True))

    menu.open()

    # Click on the item
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': menu.items[0].rect.center}
    )
    menu.handle_event(event)

    assert len(callback_called) == 1


def test_menu_auto_close_on_select(pygame_init):
    """Test that menu closes after item selection when auto_close_on_select is True."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, auto_close_on_select=True)

    menu.add_item("Test", lambda: None)
    menu.open()

    # Click on the item
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': menu.items[0].rect.center}
    )
    menu.handle_event(event)

    assert menu.visible is False


def test_menu_no_auto_close_on_select(pygame_init):
    """Test that menu stays open after item selection when auto_close_on_select is False."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, auto_close_on_select=False)

    menu.add_item("Test", lambda: None)
    menu.open()

    # Click on the item
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': menu.items[0].rect.center}
    )
    menu.handle_event(event)

    assert menu.visible is True


def test_menu_close_button(pygame_init):
    """Test that close button closes the menu."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, show_close_button=True)

    menu.open()

    # Click close button
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': menu.close_button.rect.center}
    )
    handled = menu.handle_event(event)

    assert handled is True
    assert menu.visible is False


def test_menu_close_on_outside_click(pygame_init):
    """Test that clicking outside closes menu when close_on_outside_click is True."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, close_on_outside_click=True)

    menu.open()

    # Click outside menu
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': (50, 50)}  # Outside menu rect
    )
    handled = menu.handle_event(event)

    assert handled is True
    assert menu.visible is False


def test_menu_no_close_on_outside_click(pygame_init):
    """Test that clicking outside doesn't close menu when close_on_outside_click is False."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect, close_on_outside_click=False)

    menu.open()

    # Click outside menu
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': (50, 50)}
    )
    menu.handle_event(event)

    assert menu.visible is True


def test_menu_consumes_events_when_visible(pygame_init):
    """Test that menu consumes all events when visible."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    menu.open()

    # Mouse motion event
    event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (500, 500)})
    handled = menu.handle_event(event)

    assert handled is True


def test_menu_ignores_events_when_not_visible(pygame_init):
    """Test that menu doesn't handle events when not visible."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    # Menu is closed
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
                               'button': 1, 'pos': (200, 200)})
    handled = menu.handle_event(event)

    assert handled is False


def test_menu_click_inside_but_not_on_item(pygame_init):
    """Test that clicking inside menu but not on item consumes event."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    menu.open()

    # Click inside menu but in empty space
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': (200, 150)}  # Inside menu, not on item
    )
    handled = menu.handle_event(event)

    assert handled is True
    assert menu.visible is True  # Still open


def test_menu_set_position(pygame_init):
    """Test setting menu position."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    menu.add_item("Item 1")

    old_item_pos = menu.items[0].rect.topleft

    menu.set_position(200, 200)

    assert menu.rect.topleft == (200, 200)
    assert menu.items[0].rect.topleft == (
        old_item_pos[0] + 100, old_item_pos[1] + 100)


def test_menu_center(pygame_init):
    """Test centering menu in window."""
    rect = pygame.Rect(0, 0, 300, 400)
    menu = Menu(rect)

    window_width = 800
    window_height = 600

    menu.center(window_width, window_height)

    assert menu.rect.centerx == window_width // 2
    assert menu.rect.centery == window_height // 2


def test_menu_render_when_not_visible(pygame_init):
    """Test that menu doesn't render when not visible."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    surface = pygame.Surface((800, 600))

    # Should not raise, should do nothing
    menu.render(surface)


def test_menu_render_when_visible(pygame_init):
    """Test that menu renders when visible."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    menu.add_item("Item 1")
    menu.open()

    surface = pygame.Surface((800, 600))

    # Should not raise
    menu.render(surface)


def test_menu_item_initialization(pygame_init):
    """Test that MenuItem initializes correctly."""
    rect = pygame.Rect(10, 10, 200, 35)
    item = MenuItem(rect, "Test Item")

    assert item.rect == rect
    assert item.text == "Test Item"


def test_menu_item_with_callback(pygame_init):
    """Test MenuItem with callback."""
    rect = pygame.Rect(10, 10, 200, 35)
    callback_called = []

    item = MenuItem(rect, "Test", lambda: callback_called.append(True))
    item.handle_click(rect.center)

    assert len(callback_called) == 1


def test_close_button_initialization(pygame_init):
    """Test that CloseButton initializes correctly."""
    rect = pygame.Rect(10, 10, 30, 30)
    button = CloseButton(rect)

    assert button.rect == rect


def test_close_button_render(pygame_init):
    """Test that CloseButton renders without crashing."""
    rect = pygame.Rect(10, 10, 30, 30)
    button = CloseButton(rect)

    surface = pygame.Surface((100, 100))
    button.render(surface)  # Should not raise


def test_menu_no_scrollbar_when_few_items(pygame_init):
    """Test that scrollbar doesn't appear when items fit."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    # Add a few items
    menu.add_item("Item 1")
    menu.add_item("Item 2")
    menu.add_item("Item 3")

    assert menu._needs_scrollbar() is False
    assert menu.scrollbar is None


def test_menu_scrollbar_when_many_items(pygame_init):
    """Test that scrollbar appears when items don't fit."""
    rect = pygame.Rect(100, 100, 300, 200)  # Small height
    menu = Menu(rect)

    # Add many items
    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()  # Trigger scrollbar creation

    assert menu._needs_scrollbar() is True
    assert menu.scrollbar is not None


def test_menu_total_content_height(pygame_init):
    """Test calculation of total content height."""
    rect = pygame.Rect(100, 100, 300, 400)
    menu = Menu(rect)

    # Add 5 items
    for i in range(5):
        menu.add_item(f"Item {i}")

    # Total height = 5 * (item_height + spacing) - spacing
    # = 5 * (35 + 5) - 5 = 195
    expected_height = 5 * (menu.item_height +
                           menu.item_spacing) - menu.item_spacing

    assert menu._get_total_content_height() == expected_height


def test_menu_scrollbar_interaction(pygame_init):
    """Test that scrollbar can be interacted with."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    # Add many items
    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    assert menu.scrollbar is not None

    # Click on scrollbar
    scrollbar_center = menu.scrollbar.rect.center
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': scrollbar_center}
    )
    handled = menu.handle_event(event)

    assert handled is True
    assert menu.scrollbar.dragging is True


def test_menu_scroll_updates_item_positions(pygame_init):
    """Test that scrolling updates item positions."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    # Add many items
    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    # Get initial position of first item
    initial_y = menu.items[0].rect.top

    # Scroll down (increase scroll_offset)
    menu.scroll_offset = 0.5
    menu._update_item_positions()

    # First item should move up (negative y direction)
    assert menu.items[0].rect.top < initial_y


def test_menu_scroll_offset_clamped(pygame_init):
    """Test that scroll offset stays in 0-1 range."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    # Scroll offset should start at 0
    assert menu.scroll_offset == 0.0

    # Set to maximum
    menu.scroll_offset = 1.0
    menu._update_item_positions()

    assert menu.scroll_offset == 1.0


def test_menu_content_rect_with_scrollbar(pygame_init):
    """Test that content rect accounts for scrollbar width."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    # Without scrollbar
    for i in range(3):
        menu.add_item(f"Item {i}")
    menu.open()
    content_rect_no_scroll = menu._get_content_rect()

    # With scrollbar
    for i in range(20):
        menu.add_item(f"Item {i}")
    menu.open()
    content_rect_with_scroll = menu._get_content_rect()

    # Content rect should be narrower with scrollbar
    assert content_rect_with_scroll.width < content_rect_no_scroll.width


def test_menu_scrollbar_position_updates_on_reposition(pygame_init):
    """Test that scrollbar moves with menu."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    old_scrollbar_x = menu.scrollbar.rect.left

    # Move menu
    menu.set_position(200, 200)

    # Scrollbar should have moved
    assert menu.scrollbar.rect.left == old_scrollbar_x + 100


def test_menu_items_clipped_to_content_area(pygame_init):
    """Test that only visible items are in content area."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    content_rect = menu._get_content_rect()

    # Some items should be outside content rect when not scrolled
    visible_count = sum(
        1 for item in menu.items if content_rect.colliderect(item.rect))

    assert visible_count < len(menu.items)


def test_menu_scroll_to_bottom_shows_last_items(pygame_init):
    """Test that scrolling to bottom shows last items."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    # Scroll to bottom
    menu.scroll_offset = 1.0
    menu._update_item_positions()

    content_rect = menu._get_content_rect()

    # Last item should be visible
    assert content_rect.colliderect(menu.items[-1].rect)


def test_menu_scrollbar_drag_updates_scroll(pygame_init):
    """Test that dragging scrollbar updates scroll offset."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()

    # Start drag
    menu.scrollbar.handle_click(menu.scrollbar.rect.center)

    # Drag down
    new_pos = (menu.scrollbar.rect.centerx, menu.scrollbar.rect.bottom - 10)
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': new_pos})
    menu.handle_event(motion_event)

    # Scroll offset should have increased
    assert menu.scroll_offset > 0.5


def test_menu_no_scrollbar_after_removing_items(pygame_init):
    """Test that scrollbar disappears if items are removed."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    # Add many items
    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()
    assert menu._needs_scrollbar() is True

    # Remove most items
    menu.items = menu.items[:3]
    menu._update_item_positions()

    assert menu._needs_scrollbar() is False
    assert menu.scrollbar is None


def test_menu_scroll_offset_resets_when_no_scrollbar_needed(pygame_init):
    """Test that scroll offset resets when scrollbar is no longer needed."""
    rect = pygame.Rect(100, 100, 300, 200)
    menu = Menu(rect)

    # Add many items and scroll
    for i in range(20):
        menu.add_item(f"Item {i}")

    menu.open()
    menu.scroll_offset = 0.5
    menu._update_item_positions()

    # Remove most items
    menu.items = menu.items[:3]
    menu._update_item_positions()

    assert menu.scroll_offset == 0.0
