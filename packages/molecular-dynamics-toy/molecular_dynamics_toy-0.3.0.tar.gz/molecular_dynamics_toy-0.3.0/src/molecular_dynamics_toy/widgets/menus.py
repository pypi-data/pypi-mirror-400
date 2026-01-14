"""Specialized menu widgets."""

import logging
import sys
import os.path
from typing import Optional, Callable
import webbrowser
import importlib.metadata

import pygame

from molecular_dynamics_toy.widgets.base import Menu, TextBox, TextButton
from molecular_dynamics_toy.data import presets
import molecular_dynamics_toy.data.colors as colors

from molecular_dynamics_toy.widgets.controls import ControlsWidget
from molecular_dynamics_toy.widgets.picker import PeriodicTableWidget
from molecular_dynamics_toy.widgets.simulation import SimulationWidget

logger = logging.getLogger(__name__)


class PresetsMenu(Menu):
    """Menu for loading preset atomic configurations.

    Automatically populates with presets from data.presets module.
    """

    def __init__(self, rect: pygame.Rect, load_callback: Optional[Callable[[str], None]] = None):
        """Initialize the presets menu.

        Args:
            rect: Rectangle defining menu position and size.
            load_callback: Function to call when preset is selected.
                           Takes preset_id as argument.
        """
        super().__init__(rect, title="Load Preset", auto_close_on_select=True)

        self.load_callback = load_callback

        # Populate with presets
        for preset_id in presets.get_preset_names():
            display_name = presets.get_preset_display_name(preset_id)
            self.add_item(
                display_name, lambda pid=preset_id: self._load_preset(pid))

    def _load_preset(self, preset_id: str):
        """Load a preset configuration.

        Args:
            preset_id: Preset identifier.
        """
        logger.info(f"Loading preset: {preset_id}")

        if self.load_callback:
            self.load_callback(preset_id)


try:
    _VERSION = importlib.metadata.version("molecular_dynamics_toy")
except importlib.metadata.PackageNotFoundError:
    _VERSION = "dev"

ABOUT_TEXT = f"""Molecular Dynamics Toy

A simple molecular dynamics simulation demo built with Python, Pygame, and ASE.

Features:
- Interactive atom placement
- Real-time MD simulation using MatterSim
- Multiple preset structures
- Adjustable simulation parameters

Version: {_VERSION}
Author: Bernard Field

Check for updates and see the source code on the website:
github.com/bfield1/molecular-dynamics-toy
"""

COPYRIGHT_TEXT = """molecular_dynamics_toy
Copyright (C) 2025  Bernard Field

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>."""


class MainMenu(Menu):
    """Main application menu.

    Provides access to application-level functions like About, Info, and Exit.
    """

    def __init__(self, rect: pygame.Rect, exit_callback: Optional[Callable[[], None]] = None,
                 force_show_third_party: Optional[bool] = False):
        """Initialize the main menu.

        Args:
            rect: Rectangle defining menu position and size.
            exit_callback: Function to call when Exit is selected.
            force_show_third_party: Shows the "Third Party Information" button,
                even in a package or development build.
                Note that it will likely not work if used in a package build,
                and may check outside the intended directory.
        """
        super().__init__(rect, title="Menu", auto_close_on_select=False)

        self.exit_callback = exit_callback

        about_rect = pygame.Rect(0, 0, 500, 500)
        self.about_textbox = TextBox(
            about_rect, title="About", text=ABOUT_TEXT)
        about_rect = pygame.Rect(0, 0, 500, 500)
        self.copyright_textbox = TextBox(
            about_rect, title="Copyright", text=COPYRIGHT_TEXT)

        # Add menu items
        self.add_item("About", self._show_about)
        self.add_item("Website", self._open_website)
        self.add_item("Copyright", self._show_copyright)
        if getattr(sys, "frozen", False) or force_show_third_party:
            # Only link to 3rd party info if using the bundled version of the app.
            self.add_item("Third Party Information",
                          self._show_third_party_info)
        self.add_item("Exit", self._exit_application)

    def _show_about(self):
        """Show about dialog."""
        logger.info("Showing About dialog")
        self.about_textbox.open()

    def _show_copyright(self):
        """Show copyright dialog."""
        logger.info("Showing Copyright dialog")
        self.copyright_textbox.open()

    def _open_website(self):
        """Open GitHub home-page"""
        URL = r"https://github.com/bfield1/molecular-dynamics-toy"
        logger.info(f"Opening {URL}")
        webbrowser.open(URL)

    def _show_third_party_info(self):
        """Show third party information in default web browser."""
        try:
            # Get the path to ThirdPartyNotices.html
            # When bundled with PyInstaller, files are in sys._MEIPASS
            if hasattr(sys, '_MEIPASS'):
                html_path = os.path.join(
                    sys._MEIPASS, 'ThirdPartyNotices.html')
            else:
                # Development mode - look in project root or similar
                html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                         'ThirdPartyNotices.html')

            if os.path.exists(html_path):
                # Open in default web browser
                webbrowser.open('file://' + os.path.abspath(html_path))
                logger.info(f"Opened third party notices: {html_path}")
            else:
                logger.error(
                    f"Third party notices file not found: {html_path}")

        except Exception as e:
            logger.error(f"Failed to open third party notices: {e}")

    def _exit_application(self):
        """Exit the application."""
        logger.info("Exit requested from menu")
        if self.exit_callback:
            self.exit_callback()


class HelpOverlay():
    """Overlays the help dialogues onto the app."""

    # Add alpha channel to the colour
    TEXT_BACKGROUND_COLOR = colors.MENU_BG_COLOR

    def __init__(self, controls_widget: ControlsWidget = None,
                 periodic_table_widget: PeriodicTableWidget = None,
                 simulation_widget: SimulationWidget = None):
        """
        Arguments are the widgets that need to be annotated with help text.
        """
        self.visible = False
        self.controls_widget = controls_widget
        self.periodic_table_widget = periodic_table_widget
        self.simulation_widget = simulation_widget
        
        # Display settings
        # Use system font with antialiasing
        self.font = pygame.font.SysFont('arial', 20, bold=False)
    
    def open(self):
        """Open the overlay."""
        self.visible = True
        logger.info(f"Help Overlay opened")

    def close(self):
        """Close the overlay."""
        self.visible = False
        logger.info(f"Help Overlay closed")

    def toggle(self):
        """Toggle overlay visibility."""
        if self.visible:
            self.close()
        else:
            self.open()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.

        Args:
            event: Pygame event to process.

        Returns:
            True if event was handled by overlay (prevents propagation).
            (Overlay locks )
        """
        if not self.visible:
            return False

        # Overlay is visible - consume all mouse events to prevent interaction with widgets behind it
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # When we click, we close the overlay.
                self.close()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Also permit closing with ESCAPE key
                self.close()
        return True

    def render(self, surface: pygame.Surface):
        """Render the menu.

        Args:
            surface: Surface to render onto.
        """
        if not self.visible:
            return

        # Draw semi-transparent over the entire window.
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(100)
        overlay.fill(colors.MENU_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        # Go through each widget element we want to annotate and annotate it.
        self._draw_text(surface, 
                        "Select an element to add to the simulation.",
                        *self.periodic_table_widget.rect.center)
        self._draw_text(surface,
                        "Click here to add the selected element to the simulation cell.",
                        *self.simulation_widget.rect.center)
        self._draw_text(surface,
                        "Play/Pause",
                        *self.controls_widget.play_pause_button.rect.center)
        self._draw_text(surface,
                        "Clear",
                        *self.controls_widget.reset_button.rect.center)
        self._draw_text(surface,
                        "Load preset",
                        *self.controls_widget.load_preset_button.rect.center)
        self._draw_text(surface,
                        "Menu",
                        *self.controls_widget.menu_button.rect.center)
    
    def _draw_text(self, surface: pygame.Surface, text: str, x: float, y: float):
        """Draw help overlay text at position x, y"""
        text_surface = self.font.render(
            text, True, colors.TEXT_COLOR)
        text_rect = text_surface.get_rect(
            centerx = x,
            centery = y,
        )
        # Draw the transparent background (font.render doesn't support transparency)
        bg_surf = pygame.Surface(text_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, self.TEXT_BACKGROUND_COLOR, bg_surf.get_rect())
        bg_surf.set_alpha(150)
        surface.blit(bg_surf, text_rect)
        # Add the text.
        surface.blit(text_surface, text_rect)
