"""Periodic table widget for element selection."""

import logging
import pygame
from typing import Optional, Tuple

from molecular_dynamics_toy.data import colors
from molecular_dynamics_toy.widgets.base import ToggleButton

logger = logging.getLogger(__name__)


class ElementButton(ToggleButton):
    """A clickable button representing a chemical element.

    Attributes:
        symbol: Chemical element symbol (e.g., 'H', 'He').
    """

    # Colors (override ToggleButton defaults)
    BG_COLOR = colors.ELEMENT_BG_COLOR
    BG_HOVER_COLOR = colors.ELEMENT_BG_HOVER_COLOR
    BG_SELECTED_COLOR = colors.ELEMENT_BG_SELECTED_COLOR
    BG_SELECTED_HOVER_COLOR = colors.ELEMENT_BG_SELECTED_HOVER_COLOR
    BORDER_COLOR = colors.ELEMENT_BORDER_COLOR
    BORDER_SELECTED_COLOR = colors.ELEMENT_BORDER_SELECTED_COLOR
    TEXT_COLOR = colors.ELEMENT_TEXT_COLOR
    TEXT_SELECTED_COLOR = colors.ELEMENT_TEXT_SELECTED_COLOR

    def __init__(self, symbol: str, rect: pygame.Rect):
        """Initialize an element button.

        Args:
            symbol: Chemical element symbol.
            rect: Rectangle defining position and size.
        """
        super().__init__(rect)
        self.symbol = symbol

        # Scale font size based on button size
        font_size = min(max(12, int(self.rect.height * 0.8)), 24)
        self.font = pygame.font.Font(None, font_size)

    def on_click(self):
        """Toggle selection and log the change."""
        super().on_click()  # Handles the toggle
        logger.debug(
            f"Element {self.symbol} {'selected' if self.selected else 'deselected'}")

    def deselect(self):
        """Deselect this button."""
        self.selected = False

    def render_content(self, surface: pygame.Surface):
        """Render the element symbol text.

        Args:
            surface: Surface to render onto.
        """
        # Draw symbol text
        text_color = self.TEXT_SELECTED_COLOR if self.selected else self.TEXT_COLOR
        text_surface = self.font.render(self.symbol, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class PeriodicTableWidget:
    """Widget for selecting chemical elements from the periodic table.

    Attributes:
        rect: Rectangle defining widget position and size.
        selected_element: Currently selected element symbol, or None.
    """

    BG_COLOR = colors.WIDGET_BG_COLOR

    # Periodic table layout (period, group) for elements 1-94
    # Format: symbol: (row, column)
    ELEMENT_POSITIONS = {
        # Period 1
        'H': (0, 0), 'He': (0, 17),
        # Period 2
        'Li': (1, 0), 'Be': (1, 1),
        'B': (1, 12), 'C': (1, 13), 'N': (1, 14), 'O': (1, 15), 'F': (1, 16), 'Ne': (1, 17),
        # Period 3
        'Na': (2, 0), 'Mg': (2, 1),
        'Al': (2, 12), 'Si': (2, 13), 'P': (2, 14), 'S': (2, 15), 'Cl': (2, 16), 'Ar': (2, 17),
        # Period 4
        'K': (3, 0), 'Ca': (3, 1),
        'Sc': (3, 2), 'Ti': (3, 3), 'V': (3, 4), 'Cr': (3, 5), 'Mn': (3, 6),
        'Fe': (3, 7), 'Co': (3, 8), 'Ni': (3, 9), 'Cu': (3, 10), 'Zn': (3, 11),
        'Ga': (3, 12), 'Ge': (3, 13), 'As': (3, 14), 'Se': (3, 15), 'Br': (3, 16), 'Kr': (3, 17),
        # Period 5
        'Rb': (4, 0), 'Sr': (4, 1),
        'Y': (4, 2), 'Zr': (4, 3), 'Nb': (4, 4), 'Mo': (4, 5), 'Tc': (4, 6),
        'Ru': (4, 7), 'Rh': (4, 8), 'Pd': (4, 9), 'Ag': (4, 10), 'Cd': (4, 11),
        'In': (4, 12), 'Sn': (4, 13), 'Sb': (4, 14), 'Te': (4, 15), 'I': (4, 16), 'Xe': (4, 17),
        # Period 6
        'Cs': (5, 0), 'Ba': (5, 1),
        'Hf': (5, 3), 'Ta': (5, 4), 'W': (5, 5), 'Re': (5, 6),
        'Os': (5, 7), 'Ir': (5, 8), 'Pt': (5, 9), 'Au': (5, 10), 'Hg': (5, 11),
        'Tl': (5, 12), 'Pb': (5, 13), 'Bi': (5, 14), 'Po': (5, 15), 'At': (5, 16), 'Rn': (5, 17),
        # Period 7 (up to Pu)
        'Fr': (6, 0), 'Ra': (6, 1),
        # Lanthanides (row 8, offset from main table)
        'La': (8, 2), 'Ce': (8, 3), 'Pr': (8, 4), 'Nd': (8, 5), 'Pm': (8, 6), 'Sm': (8, 7),
        'Eu': (8, 8), 'Gd': (8, 9), 'Tb': (8, 10), 'Dy': (8, 11), 'Ho': (8, 12),
        'Er': (8, 13), 'Tm': (8, 14), 'Yb': (8, 15), 'Lu': (8, 16),
        # Actinides (row 9, offset from main table)
        'Ac': (9, 2), 'Th': (9, 3), 'Pa': (9, 4), 'U': (9, 5), 'Np': (9, 6), 'Pu': (9, 7),
    }

    def __init__(self, rect: pygame.Rect):
        """Initialize the periodic table widget.

        Args:
            rect: Rectangle defining widget position and size.
        """
        self.rect = rect
        self.buttons = []
        self.selected_element = None

        self._create_elements()
        logger.info("PeriodicTableWidget initialized")

    def _create_elements(self):
        """Create element buttons in grid layout."""
        # Clear existing buttons
        self.buttons = []

        # Periodic table dimensions
        num_rows = 10  # 7 periods + 2 for lanthanides/actinides
        num_cols = 18  # Standard periodic table width

        # Calculate button size to fit within widget
        margin = 20
        available_width = self.rect.width - 2 * margin
        available_height = self.rect.height - 2 * margin

        # Determine button size based on available space
        spacing = 3
        button_size = min(
            (available_width - (num_cols - 1) * spacing) / num_cols,
            (available_height - (num_rows - 1) * spacing) / num_rows
        )
        button_size = max(20, int(button_size))  # Minimum size of 20px

        # Create buttons for all elements
        for symbol, (row, col) in self.ELEMENT_POSITIONS.items():
            x = self.rect.left + margin + col * (button_size + spacing)
            y = self.rect.top + margin + row * (button_size + spacing)
            button_rect = pygame.Rect(x, y, button_size, button_size)
            self.buttons.append(ElementButton(symbol, button_rect))

        logger.debug(
            f"Created {len(self.buttons)} element buttons (size: {button_size}px)")

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events.

        Args:
            event: Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.handle_hover(event.pos)

    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on widget.

        Args:
            pos: Mouse position (x, y).
        """
        for button in self.buttons:
            if button.handle_click(pos):
                # Deselect all other buttons
                for other in self.buttons:
                    if other is not button:
                        other.deselect()

                # Update selected element
                self.selected_element = button.symbol if button.selected else None
                logger.info(f"Selected element: {self.selected_element}")
                break

    def update(self):
        """Update widget state (called each frame)."""
        pass

    def render(self, surface: pygame.Surface):
        """Render the widget.

        Args:
            surface: Surface to render onto.
        """
        # Draw background
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)

        # Draw all element buttons
        for button in self.buttons:
            button.render(surface)

    def set_rect(self, rect: pygame.Rect):
        """Update widget position and size, recalculating element positions.

        Args:
            rect: New rectangle defining widget position and size.
        """
        # Preserve selection
        old_selection = self.selected_element

        self.rect = rect
        self._create_elements()

        # Restore selection
        if old_selection:
            for button in self.buttons:
                if button.symbol == old_selection:
                    button.selected = True
                    self.selected_element = old_selection
                    break

        logger.debug(f"PeriodicTableWidget resized to {rect}")
