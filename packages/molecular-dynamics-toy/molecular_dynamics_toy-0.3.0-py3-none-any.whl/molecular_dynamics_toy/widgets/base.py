"""Base widget classes for common UI elements."""

import logging
import pygame
from typing import Tuple, Callable, Optional, List
from molecular_dynamics_toy.data import colors

logger = logging.getLogger(__name__)


class Button:
    """A base class for clickable buttons with hover effects.

    Provides common functionality for rectangular buttons with background,
    border, and hover states. Subclasses can override rendering methods
    to customize appearance.

    Attributes:
        rect: Rectangle defining button position and size.
        hovered: Whether mouse is currently over the button.
        enabled: Whether button can be clicked.
        callback: Optional function to call when button is clicked.
    """

    # Default colors (can be overridden by subclasses)
    BG_COLOR = colors.CONTROL_BG_COLOR
    BG_HOVER_COLOR = colors.CONTROL_BG_HOVER_COLOR
    BG_DISABLED_COLOR = colors.BUTTON_BG_DISABLED_COLOR
    BORDER_COLOR = colors.CONTROL_BORDER_COLOR
    BORDER_DISABLED_COLOR = colors.BUTTON_BORDER_DISABLED_COLOR

    def __init__(self, rect: pygame.Rect, callback: Optional[Callable[[], None]] = None,
                 enabled: bool = True):
        """Initialize the button.

        Args:
            rect: Rectangle defining position and size.
            callback: Optional function to call when clicked.
            enabled: Whether button starts enabled.
        """
        self.rect = rect
        self.hovered = False
        self.enabled = enabled
        self.callback = callback

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Generic event handling for buttons, for stand-alone buttons.
        
        Returns True if the button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_hover(event.pos)
        return False

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Check if position is inside button and handle click.

        Args:
            pos: Mouse position (x, y).

        Returns:
            True if button was clicked.
        """
        if not self.enabled:
            return False

        if self.rect.collidepoint(pos):
            self.on_click()
            if self.callback:
                self.callback()
            return True
        return False

    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover state based on mouse position.

        Args:
            pos: Mouse position (x, y).
        """
        self.hovered = self.rect.collidepoint(pos) and self.enabled

    def on_click(self):
        """Handle click event. Override in subclasses for custom behavior."""
        pass

    def render(self, surface: pygame.Surface):
        """Render the button.

        Args:
            surface: Surface to render onto.
        """
        # Determine colors based on state
        if not self.enabled:
            bg_color = self.BG_DISABLED_COLOR
            border_color = self.BORDER_DISABLED_COLOR
        elif self.hovered:
            bg_color = self.BG_HOVER_COLOR
            border_color = self.BORDER_COLOR
        else:
            bg_color = self.BG_COLOR
            border_color = self.BORDER_COLOR

        # Draw background
        pygame.draw.rect(surface, bg_color, self.rect)

        # Draw border
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw content (override in subclasses)
        self.render_content(surface)

    def render_content(self, surface: pygame.Surface):
        """Render button content (icon, text, etc.). Override in subclasses.

        Args:
            surface: Surface to render onto.
        """
        pass


class ToggleButton(Button):
    """A button that toggles between two states when clicked.

    Automatically swaps colors based on toggle state. Subclasses can define
    separate colors for selected/unselected states.

    Attributes:
        selected: Whether button is currently selected/toggled on.
    """

    # Colors for unselected state (inherited from Button)
    BG_COLOR = colors.CONTROL_BG_COLOR
    BG_HOVER_COLOR = colors.CONTROL_BG_HOVER_COLOR
    BORDER_COLOR = colors.CONTROL_BORDER_COLOR

    # Colors for selected state
    BG_SELECTED_COLOR = colors.ELEMENT_BG_SELECTED_COLOR
    BG_SELECTED_HOVER_COLOR = colors.ELEMENT_BG_SELECTED_HOVER_COLOR
    BORDER_SELECTED_COLOR = colors.ELEMENT_BORDER_SELECTED_COLOR

    def __init__(self, rect: pygame.Rect, callback: Optional[Callable[[], None]] = None,
                 enabled: bool = True, selected: bool = False):
        """Initialize the toggle button.

        Args:
            rect: Rectangle defining position and size.
            callback: Optional function to call when clicked.
            enabled: Whether button starts enabled.
            selected: Whether button starts selected.
        """
        super().__init__(rect, callback, enabled)
        self.selected = selected

    def on_click(self):
        """Toggle selected state when clicked."""
        self.selected = not self.selected

    def render(self, surface: pygame.Surface):
        """Render the button with state-dependent colors.

        Args:
            surface: Surface to render onto.
        """
        # Determine colors based on state
        if not self.enabled:
            bg_color = self.BG_DISABLED_COLOR
            border_color = self.BORDER_DISABLED_COLOR
        elif self.selected and self.hovered:
            bg_color = self.BG_SELECTED_HOVER_COLOR
            border_color = self.BORDER_SELECTED_COLOR
        elif self.selected:
            bg_color = self.BG_SELECTED_COLOR
            border_color = self.BORDER_SELECTED_COLOR
        elif self.hovered:
            bg_color = self.BG_HOVER_COLOR
            border_color = self.BORDER_COLOR
        else:
            bg_color = self.BG_COLOR
            border_color = self.BORDER_COLOR

        # Draw background
        pygame.draw.rect(surface, bg_color, self.rect)

        # Draw border
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw content (override in subclasses)
        self.render_content(surface)


class TextButton(Button):
    """A button that displays text.

    Attributes:
        text: Text to display on the button.
    """

    TEXT_COLOR = colors.TEXT_COLOR
    TEXT_HOVER_COLOR = colors.TEXT_COLOR
    TEXT_DISABLED_COLOR = colors.TEXT_DISABLED_COLOR

    def __init__(self, rect: pygame.Rect, text: str,
                 callback: Optional[Callable[[], None]] = None,
                 enabled: bool = True, font_size: int = 20):
        """Initialize the text button.

        Args:
            rect: Rectangle defining position and size.
            text: Text to display.
            callback: Optional function to call when clicked.
            enabled: Whether button starts enabled.
            font_size: Font size for the text.
        """
        super().__init__(rect, callback, enabled)
        self.text = text
        self.font = pygame.font.Font(None, font_size)

    def render_content(self, surface: pygame.Surface):
        """Render the text content.

        Args:
            surface: Surface to render onto.
        """
        # Choose text color based on state
        if not self.enabled:
            text_color = self.TEXT_DISABLED_COLOR
        elif self.hovered:
            text_color = self.TEXT_HOVER_COLOR
        else:
            text_color = self.TEXT_COLOR

        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Slider:
    """Base class for slider controls.

    A slider allows selecting a value by dragging a handle along a track.

    Attributes:
        rect: Rectangle defining slider position and size.
        value: Current value (normalized to 0-1 range).
        dragging: Whether slider is currently being dragged.
        hovered: Whether mouse is over the slider handle.
        orientation: 'horizontal' or 'vertical'.
    """

    # Colors
    BG_COLOR = colors.CONTROL_BG_COLOR
    TRACK_COLOR = colors.SLIDER_TRACK_COLOR
    HANDLE_COLOR = colors.SLIDER_HANDLE_COLOR
    HANDLE_HOVER_COLOR = colors.SLIDER_HANDLE_HOVER_COLOR

    def __init__(self, rect: pygame.Rect, initial_value: float = 0.5,
                 orientation: str = 'horizontal'):
        """Initialize the slider.

        Args:
            rect: Rectangle defining position and size.
            initial_value: Initial value (0-1 normalized).
            orientation: 'horizontal' or 'vertical'.
        """
        self.rect = rect
        self.value = max(0.0, min(1.0, initial_value))
        self.orientation = orientation
        self.dragging = False
        self.hovered = False

        # Handle dimensions
        if orientation == 'horizontal':
            self.handle_width = 15
            self.handle_height = rect.height
        else:  # vertical
            self.handle_width = rect.width
            self.handle_height = 15

    def _get_track_rect(self) -> pygame.Rect:
        """Get the rectangle for the slider track.

        Returns:
            Rectangle for the track.
        """
        return self.rect.copy()

    def _get_handle_rect(self) -> pygame.Rect:
        """Get the rectangle for the slider handle.

        Returns:
            Rectangle for the handle based on current value.
        """
        track_rect = self._get_track_rect()

        if self.orientation == 'horizontal':
            handle_x = track_rect.left + self.value * \
                (track_rect.width - self.handle_width)
            handle_y = track_rect.top
            return pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)
        else:  # vertical
            handle_x = track_rect.left
            handle_y = track_rect.top + self.value * \
                (track_rect.height - self.handle_height)
            return pygame.Rect(handle_x, handle_y, self.handle_width, self.handle_height)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Check if position is inside slider and start dragging.

        Args:
            pos: Mouse position (x, y).

        Returns:
            True if slider was clicked.
        """
        handle_rect = self._get_handle_rect()
        if handle_rect.collidepoint(pos):
            self.dragging = True
            return True

        # Also allow clicking on track to jump to position
        track_rect = self._get_track_rect()
        if track_rect.collidepoint(pos):
            self._update_from_position(pos)
            self.dragging = True
            return True

        return False

    def handle_release(self):
        """Handle mouse button release."""
        self.dragging = False

    def handle_drag(self, pos: Tuple[int, int]):
        """Handle mouse drag to update slider position.

        Args:
            pos: Mouse position (x, y).
        """
        if self.dragging:
            self._update_from_position(pos)

    def _update_from_position(self, pos: Tuple[int, int]):
        """Update value based on position.

        Args:
            pos: Mouse position (x, y).
        """
        track_rect = self._get_track_rect()

        if self.orientation == 'horizontal':
            normalized = (pos[0] - track_rect.left) / track_rect.width
        else:  # vertical
            normalized = (pos[1] - track_rect.top) / track_rect.height

        self.value = max(0.0, min(1.0, normalized))
        self.on_value_changed()

    def on_value_changed(self):
        """Called when value changes. Override in subclasses for custom behavior."""
        pass

    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover state based on mouse position.

        Args:
            pos: Mouse position (x, y).
        """
        handle_rect = self._get_handle_rect()
        self.hovered = handle_rect.collidepoint(pos)

    def render(self, surface: pygame.Surface):
        """Render the slider.

        Args:
            surface: Surface to render onto.
        """
        # Draw track
        track_rect = self._get_track_rect()
        pygame.draw.rect(surface, self.TRACK_COLOR, track_rect)
        pygame.draw.rect(surface, colors.BORDER_COLOR, track_rect, 1)

        # Draw handle
        handle_rect = self._get_handle_rect()
        handle_color = self.HANDLE_HOVER_COLOR if (
            self.hovered or self.dragging) else self.HANDLE_COLOR
        pygame.draw.rect(surface, handle_color, handle_rect)
        pygame.draw.rect(surface, colors.BORDER_COLOR, handle_rect, 2)


class MenuItem(TextButton):
    """A menu item button.

    Just a specialized TextButton with menu-appropriate styling.
    """

    # Menu item specific colors
    BG_COLOR = colors.MENU_ITEM_BG_COLOR
    BG_HOVER_COLOR = colors.MENU_ITEM_BG_HOVER_COLOR
    BORDER_COLOR = colors.MENU_ITEM_BORDER_COLOR
    TEXT_COLOR = colors.TEXT_COLOR

    def __init__(self, rect: pygame.Rect, text: str,
                 callback: Optional[Callable[[], None]] = None):
        """Initialize menu item.

        Args:
            rect: Rectangle defining position and size.
            text: Text to display.
            callback: Function to call when clicked.
        """
        super().__init__(rect, text, callback=callback, font_size=22)


class CloseButton(Button):
    """A close button with an X icon."""

    ICON_COLOR = colors.ICON_RESET_COLOR

    def __init__(self, rect: pygame.Rect):
        """Initialize close button.

        Args:
            rect: Rectangle defining position and size.
        """
        super().__init__(rect)

    def render_content(self, surface: pygame.Surface):
        """Render X icon.

        Args:
            surface: Surface to render onto.
        """
        icon_rect = self.rect.inflate(-12, -12)

        # Draw X (two diagonal lines)
        pygame.draw.line(
            surface,
            self.ICON_COLOR,
            (icon_rect.left, icon_rect.top),
            (icon_rect.right, icon_rect.bottom),
            3
        )
        pygame.draw.line(
            surface,
            self.ICON_COLOR,
            (icon_rect.right, icon_rect.top),
            (icon_rect.left, icon_rect.bottom),
            3
        )


class Menu:
    """Base class for popup menus.

    Provides a popup menu with a list of items and optional close button.
    Handles layout, rendering, and event handling for menu items.
    Supports scrolling when items don't fit.

    Attributes:
        rect: Rectangle defining menu position and size.
        items: List of menu items.
        visible: Whether menu is currently visible.
        close_on_outside_click: Whether to close when clicking outside menu.
        show_close_button: Whether to show the close button.
        auto_close_on_select: Whether to close menu when item is clicked.
        scroll_offset: Current scroll position (0-1).
        scrollbar: Scrollbar widget if needed.
    """

    # Menu styling
    BG_COLOR = colors.MENU_BG_COLOR
    BORDER_COLOR = colors.MENU_BORDER_COLOR
    TITLE_COLOR = colors.TEXT_COLOR

    def __init__(self, rect: pygame.Rect, title: str = "Menu",
                 show_close_button: bool = True,
                 close_on_outside_click: bool = True,
                 auto_close_on_select: bool = True):
        """Initialize the menu.

        Args:
            rect: Rectangle defining menu position and size.
            title: Title text to display at top of menu.
            show_close_button: Whether to show close button.
            close_on_outside_click: Whether clicking outside closes menu.
            auto_close_on_select: Whether clicking menu item closes menu.
        """
        self.rect = rect
        self.title = title
        self.visible = False
        self.show_close_button = show_close_button
        self.close_on_outside_click = close_on_outside_click
        self.auto_close_on_select = auto_close_on_select

        # Layout parameters
        self.title_height = 40
        self.item_height = 35
        self.item_spacing = 5
        self.margin = 15
        self.scrollbar_width = 20

        # Scrolling
        self.scroll_offset = 0.0  # 0-1 normalized
        self.scrollbar = None

        # Close button
        self.close_button = None
        if self.show_close_button:
            close_size = 30
            self.close_button = CloseButton(
                pygame.Rect(
                    rect.right - close_size - 10,
                    rect.top + 10,
                    close_size,
                    close_size
                )
            )

        self.items: List[MenuItem] = []
        self.title_font = pygame.font.Font(None, 28)

    def _get_content_rect(self) -> pygame.Rect:
        """Get the rectangle for scrollable content area.

        Returns:
            Rectangle defining the visible content area.
        """
        content_top = self.rect.top + self.title_height + self.margin
        content_height = self.rect.height - self.title_height - 2 * self.margin

        # Reserve space for scrollbar if needed
        scrollbar_space = self.scrollbar_width + 5 if self._needs_scrollbar() else 0

        return pygame.Rect(
            self.rect.left + self.margin,
            content_top,
            self.rect.width - 2 * self.margin - scrollbar_space,
            content_height
        )

    def _get_total_content_height(self) -> int:
        """Get total height of all items.

        Returns:
            Total height needed for all items.
        """
        if not self.items:
            return 0
        return len(self.items) * (self.item_height + self.item_spacing) - self.item_spacing

    def _needs_scrollbar(self) -> bool:
        """Check if scrollbar is needed.

        Returns:
            True if content exceeds visible area.
        """
        content_height = self.rect.height - self.title_height - 2 * self.margin
        total_height = self._get_total_content_height()
        return total_height > content_height

    def _update_scrollbar(self):
        """Create or update scrollbar if needed."""
        if self._needs_scrollbar():
            if self.scrollbar is None:
                # Create scrollbar
                content_rect = self._get_content_rect()
                scrollbar_rect = pygame.Rect(
                    self.rect.right - self.scrollbar_width - self.margin,
                    content_rect.top,
                    self.scrollbar_width,
                    content_rect.height
                )
                self.scrollbar = Slider(
                    scrollbar_rect, initial_value=0.0, orientation='vertical')
            else:
                # Update scrollbar position
                content_rect = self._get_content_rect()
                self.scrollbar.rect = pygame.Rect(
                    self.rect.right - self.scrollbar_width - self.margin,
                    content_rect.top,
                    self.scrollbar_width,
                    content_rect.height
                )
        else:
            self.scrollbar = None
            self.scroll_offset = 0.0

    def open(self):
        """Open the menu."""
        self.visible = True
        self._update_item_positions()
        logger.info(f"Menu '{self.title}' opened")

    def close(self):
        """Close the menu."""
        self.visible = False
        logger.info(f"Menu '{self.title}' closed")

    def toggle(self):
        """Toggle menu visibility."""
        if self.visible:
            self.close()
        else:
            self.open()

    def add_item(self, text: str, callback: Optional[Callable[[], None]] = None):
        """Add a menu item.

        Args:
            text: Item text.
            callback: Function to call when item is clicked.
        """
        # Create item at placeholder position (will be updated)
        item_rect = pygame.Rect(0, 0, 100, self.item_height)

        # Optionally wrap callback to auto-close menu after action
        if self.auto_close_on_select and callback:
            original_callback = callback

            def wrapped_callback():
                original_callback()
                self.close()
            final_callback = wrapped_callback
        else:
            final_callback = callback

        item = MenuItem(item_rect, text, callback=final_callback)
        self.items.append(item)

        # Update positions and scrollbar
        self._update_item_positions()

    def _update_item_positions(self):
        """Update positions of all menu items based on scroll offset."""
        content_rect = self._get_content_rect()
        total_height = self._get_total_content_height()

        # Calculate scroll offset in pixels
        if self._needs_scrollbar():
            max_scroll = total_height - content_rect.height
            scroll_pixels = self.scroll_offset * max_scroll
        else:
            scroll_pixels = 0

        # Position items
        for i, item in enumerate(self.items):
            item_y = content_rect.top + i * \
                (self.item_height + self.item_spacing) - scroll_pixels

            item.rect = pygame.Rect(
                content_rect.left,
                item_y,
                content_rect.width,
                self.item_height
            )

        # Update scrollbar
        self._update_scrollbar()

    def set_position(self, x: int, y: int):
        """Set menu position and update all sub-components.

        Args:
            x: New x coordinate for top-left corner.
            y: New y coordinate for top-left corner.
        """
        # Calculate offset
        dx = x - self.rect.left
        dy = y - self.rect.top

        # Move main rect
        self.rect.topleft = (x, y)

        # Move close button
        if self.close_button:
            self.close_button.rect.move_ip(dx, dy)

        # Update item positions (recalculate based on new rect)
        self._update_item_positions()

    def center(self, width: int, height: int):
        """Center menu in a window of given dimensions.

        Args:
            width: Window width.
            height: Window height.
        """
        new_x = (width - self.rect.width) // 2
        new_y = (height - self.rect.height) // 2
        self.set_position(new_x, new_y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.

        Args:
            event: Pygame event to process.

        Returns:
            True if event was handled by menu (prevents propagation).
        """
        if not self.visible:
            return False

        # Menu is visible - consume all mouse events to prevent interaction with widgets behind it
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check scrollbar first
                if self.scrollbar and self.scrollbar.handle_click(event.pos):
                    return True

                # Check close button
                if self.close_button and self.close_button.handle_click(event.pos):
                    self.close()
                    return True

                # Check menu items (only if visible in scroll area)
                content_rect = self._get_content_rect()
                for item in self.items:
                    # Check if item is visible in content area
                    if content_rect.colliderect(item.rect):
                        if item.handle_click(event.pos):
                            return True

                # Check if click is inside menu area
                if self.rect.collidepoint(event.pos):
                    # Click inside menu but not on any item - consume event
                    return True
                elif self.close_on_outside_click:
                    # Click outside menu - close it
                    self.close()
                    return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.scrollbar:
                    self.scrollbar.handle_release()

        elif event.type == pygame.MOUSEWHEEL:
            # Handle mouse wheel scrolling
            if self.scrollbar and self.rect.collidepoint(pygame.mouse.get_pos()):
                # event.y is positive for scroll up, negative for scroll down
                scroll_amount = -event.y * 0.05  # Invert and scale
                self.scroll_offset = max(
                    0.0, min(1.0, self.scroll_offset + scroll_amount))
                self.scrollbar.value = self.scroll_offset
                self._update_item_positions()
                return True

        elif event.type == pygame.MOUSEMOTION:
            # Update hover states only for menu elements
            if self.close_button:
                self.close_button.handle_hover(event.pos)

            # Handle scrollbar dragging
            if self.scrollbar:
                self.scrollbar.handle_hover(event.pos)
                self.scrollbar.handle_drag(event.pos)
                # Update scroll offset from scrollbar
                self.scroll_offset = self.scrollbar.value
                self._update_item_positions()

            # Update item hover states (only for visible items)
            content_rect = self._get_content_rect()
            for item in self.items:
                if content_rect.colliderect(item.rect):
                    item.handle_hover(event.pos)

        # Consume all mouse events when menu is visible
        return True

    def render(self, surface: pygame.Surface):
        """Render the menu.

        Args:
            surface: Surface to render onto.
        """
        if not self.visible:
            return

        # Draw semi-transparent overlay behind menu
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(100)
        overlay.fill(colors.MENU_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        # Draw menu background
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 3)

        # Draw title
        title_surface = self.title_font.render(
            self.title, True, self.TITLE_COLOR)
        title_rect = title_surface.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top + 10
        )
        surface.blit(title_surface, title_rect)

        # Draw separator line under title
        separator_y = self.rect.top + self.title_height
        pygame.draw.line(
            surface,
            self.BORDER_COLOR,
            (self.rect.left + 10, separator_y),
            (self.rect.right - 10, separator_y),
            2
        )

        # Draw close button
        if self.close_button:
            self.close_button.render(surface)

        # Set up clipping for scrollable content
        content_rect = self._get_content_rect()
        surface.set_clip(content_rect)

        # Draw menu items (only visible ones)
        for item in self.items:
            if content_rect.colliderect(item.rect):
                item.render(surface)

        # Remove clipping
        surface.set_clip(None)

        # Draw scrollbar
        if self.scrollbar:
            self.scrollbar.render(surface)


class TextBox(Menu):
    """A popup text box that displays scrollable text.

    Reuses Menu's window, scrolling, and close button infrastructure
    but displays text instead of menu items.

    Attributes:
        text: Text content to display.
        font: Font for rendering text.
        line_height: Height of each text line.
        wrapped_lines: Text split into wrapped lines.
    """

    TEXT_COLOR = colors.TEXT_COLOR

    def __init__(self, rect: pygame.Rect, title: str = "Text", text: str = ""):
        """Initialize the text box.

        Args:
            rect: Rectangle defining position and size.
            title: Title text to display at top.
            text: Text content to display.
        """
        # Initialize as Menu but don't auto-close on select (no items to select)
        super().__init__(rect, title=title, show_close_button=True,
                         close_on_outside_click=True, auto_close_on_select=False)

        self.text = text
        # Use system font with antialiasing
        self.font = pygame.font.SysFont('arial', 16, bold=False)
        self.line_height = 25
        self.wrapped_lines = []

        self._wrap_text()

    def _wrap_text(self):
        """Wrap text to fit in content area."""
        content_rect = self._get_content_rect()
        max_width = content_rect.width - 20  # Padding

        self.wrapped_lines = []

        # Split into paragraphs first
        paragraphs = self.text.split('\n')

        for paragraph in paragraphs:
            if not paragraph.strip():
                self.wrapped_lines.append("")  # Empty line for paragraph break
                continue

            words = paragraph.split(' ')
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                test_surface = self.font.render(
                    test_line, True, self.TEXT_COLOR)

                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        self.wrapped_lines.append(current_line.rstrip())
                    current_line = word + " "

            if current_line:
                self.wrapped_lines.append(current_line.rstrip())

    def _get_total_content_height(self) -> int:
        """Get total height of all text lines.

        Returns:
            Total height needed for all lines.
        """
        return len(self.wrapped_lines) * self.line_height

    def render(self, surface: pygame.Surface):
        """Render the text box.

        Args:
            surface: Surface to render onto.
        """
        if not self.visible:
            return

        # Draw semi-transparent overlay behind text box
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(100)
        overlay.fill(colors.MENU_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        # Draw background
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 3)

        # Draw title
        title_surface = self.title_font.render(
            self.title, True, self.TITLE_COLOR)
        title_rect = title_surface.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top + 10
        )
        surface.blit(title_surface, title_rect)

        # Draw separator line under title
        separator_y = self.rect.top + self.title_height
        pygame.draw.line(
            surface,
            self.BORDER_COLOR,
            (self.rect.left + 10, separator_y),
            (self.rect.right - 10, separator_y),
            2
        )

        # Draw close button
        if self.close_button:
            self.close_button.render(surface)

        # Set up clipping for scrollable content
        content_rect = self._get_content_rect()
        surface.set_clip(content_rect)

        # Calculate scroll offset in pixels
        total_height = self._get_total_content_height()
        if self._needs_scrollbar():
            max_scroll = total_height - content_rect.height
            scroll_pixels = self.scroll_offset * max_scroll
        else:
            scroll_pixels = 0

        # Draw text lines
        y_offset = content_rect.top - scroll_pixels
        for line in self.wrapped_lines:
            if y_offset + self.line_height >= content_rect.top and y_offset <= content_rect.bottom:
                text_surface = self.font.render(line, True, self.TEXT_COLOR)
                surface.blit(text_surface, (content_rect.left + 10, y_offset))
            y_offset += self.line_height

        # Remove clipping
        surface.set_clip(None)

        # Draw scrollbar
        if self.scrollbar:
            self.scrollbar.render(surface)
