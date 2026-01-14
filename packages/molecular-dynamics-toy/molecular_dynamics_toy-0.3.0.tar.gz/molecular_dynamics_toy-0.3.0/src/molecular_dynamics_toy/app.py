"""Main GUI application for interactive molecular dynamics."""

import logging
import pygame
from typing import Optional
import sys

from molecular_dynamics_toy.widgets.picker import PeriodicTableWidget
from molecular_dynamics_toy.widgets.controls import ControlsWidget
from molecular_dynamics_toy.widgets.simulation import SimulationWidget
from molecular_dynamics_toy.widgets.menus import PresetsMenu, MainMenu, HelpOverlay
from molecular_dynamics_toy.widgets.base import TextButton
from molecular_dynamics_toy.data.presets import create_preset
from molecular_dynamics_toy.data import colors
from molecular_dynamics_toy.calculators import get_calculator

logger = logging.getLogger(__name__)


class MDApplication:
    """Main application window for interactive molecular dynamics.

    Manages the pygame window, event loop, and coordinates between different
    UI widgets (simulation renderer, periodic table, controls).

    Attributes:
        screen: Pygame display surface.
        clock: Pygame clock for controlling frame rate.
        running: Flag indicating if application is running.
        fps: Target frames per second.
        show_fps: Whether to display FPS counter.
        preset_menu: Menu for loading preset configurations.
    """

    # Window dimensions
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800

    # Widget layout (position and size rectangles)
    SIMULATION_RECT = pygame.Rect(50, 50, 700, 700)
    PERIODIC_TABLE_RECT = pygame.Rect(800, 50, 550, 400)
    CONTROLS_RECT = pygame.Rect(800, 500, 550, 250)
    HELP_BUTTON_RECT = pygame.Rect(1350, 25, 25, 25)

    # Colors
    BG_COLOR = colors.BG_COLOR
    WIDGET_BG_COLOR = colors.WIDGET_BG_COLOR
    BORDER_COLOR = colors.BORDER_COLOR
    TEXT_COLOR = colors.TEXT_COLOR

    def __init__(self, fps: int = 30, calculator: str = "mattersim", show_fps: bool = True):
        """Initialize the application.

        Args:
            fps: Target frames per second.
            calculator: Calculator name ('mattersim', 'mock').
        """
        pygame.init()

        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Molecular Dynamics Toy")

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.running = False
        self.show_fps = show_fps

        # Font for debug/placeholder text
        self.font = pygame.font.Font(None, 24)
        self.fps_font = pygame.font.Font(None, 20)

        # Widgets
        self.simulation_widget = SimulationWidget(
            self.SIMULATION_RECT, calculator=get_calculator(calculator))
        self.periodic_table_widget = PeriodicTableWidget(
            self.PERIODIC_TABLE_RECT)
        self.controls_widget = ControlsWidget(self.CONTROLS_RECT)
        # Create menus
        self.preset_menu = PresetsMenu(pygame.Rect(
            0, 0, 300, 400), load_callback=self._load_preset)
        self.main_menu = MainMenu(pygame.Rect(
            0, 0, 300, 300), exit_callback=self.exit)
        # Help overlay
        self.help_overlay = HelpOverlay(self.controls_widget, self.periodic_table_widget,
                                        self.simulation_widget)
        self.help_button = TextButton(self.HELP_BUTTON_RECT, "?",
                                      callback=self.help_overlay.open, font_size=30)

        self._update_layout()

        logger.info(
            f"MDApplication initialized: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT} @ {fps} FPS")

    def handle_events(self):
        """Process pygame events.

        Distributes events to appropriate widgets and handles global events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                logger.info("Quit event received")

            elif event.type == pygame.VIDEORESIZE:
                self.WINDOW_WIDTH = event.w
                self.WINDOW_HEIGHT = event.h
                self._update_layout()
                logger.debug(f"Window resized to {event.w}x{event.h}")

            # Menus get priority for event handling
            # Check About textbox first (highest priority when open)
            if self.main_menu and self.main_menu.about_textbox.handle_event(event):
                continue
            if self.main_menu and self.main_menu.copyright_textbox.handle_event(event):
                continue
            if self.preset_menu and self.preset_menu.handle_event(event):
                continue  # Event consumed by menu
            if self.main_menu and self.main_menu.handle_event(event):
                continue  # Event consumed by menu
            if self.help_overlay and self.help_overlay.handle_event(event):
                continue

            # Pass events to widgets when they exist
            if self.help_button:
                self.help_button.handle_event(event)
            if self.simulation_widget:
                self.simulation_widget.handle_event(event)
            if self.periodic_table_widget:
                self.periodic_table_widget.handle_event(event)
            if self.controls_widget:
                self.controls_widget.handle_event(event)

    def update(self):
        """Update application state.

        Called once per frame to update all widgets.
        """
        # Pass selected element to simulation widget
        if self.simulation_widget and self.periodic_table_widget:
            self.simulation_widget.selected_element = self.periodic_table_widget.selected_element

        # Handle reset
        if self.controls_widget and self.controls_widget.reset_requested and self.simulation_widget:
            self.simulation_widget.reset()
            self.controls_widget.reset_requested = False  # Clear flag after consuming

        # Update simulation parameters
        if self.simulation_widget and self.controls_widget:
            self.simulation_widget.engine.temperature = self.controls_widget.temperature
            self.simulation_widget.engine.timestep = self.controls_widget.timestep

            # Update cell size (preserving fractional coordinates)
            new_cell_size = self.controls_widget.cell_size
            old_cell = self.simulation_widget.engine.atoms.cell[0, 0]
            if abs(new_cell_size - old_cell) > 1e-6:
                self.simulation_widget.engine.atoms.set_cell(
                    [new_cell_size] * 3, scale_atoms=True)
                logger.debug(f"Cell size updated to {new_cell_size:.2f} Å")

        # Update simulation with play state and speed
        if self.simulation_widget and self.controls_widget:
            self.simulation_widget.update(
                self.controls_widget.playing,
                self.controls_widget.steps_per_frame
            )

        # Handle menu open requests
        if self.controls_widget and self.controls_widget.open_preset_menu_requested:
            self.preset_menu.open()
            self.controls_widget.open_preset_menu_requested = False
        if self.controls_widget and self.controls_widget.open_main_menu_requested:
            self.main_menu.open()
            self.controls_widget.open_main_menu_requested = False

    def render(self):
        """Render the application.

        Draws background and all widgets to the screen.
        """
        # Fill background
        self.screen.fill(self.BG_COLOR)

        # Render widgets when they exist
        if self.simulation_widget:
            self.simulation_widget.render(self.screen)
        if self.periodic_table_widget:
            self.periodic_table_widget.render(self.screen)
        if self.controls_widget:
            self.controls_widget.render(self.screen)
        
        if self.help_button:
            self.help_button.render(self.screen)
        if self.help_overlay:
            self.help_overlay.render(self.screen)

        # Render menus on top
        if self.preset_menu:
            self.preset_menu.render(self.screen)
        if self.main_menu:
            self.main_menu.render(self.screen)
            # Render About textbox on top of menu
            if self.main_menu.about_textbox:
                self.main_menu.about_textbox.render(self.screen)
            if self.main_menu.copyright_textbox:
                self.main_menu.copyright_textbox.render(self.screen)

        # Draw FPS counter
        if self.show_fps:
            self._render_fps()

        pygame.display.flip()

    def _render_fps(self):
        """Render FPS counter in top-left corner."""
        fps_value = self.clock.get_fps()
        fps_text = f"FPS: {fps_value:.1f}"
        fps_surface = self.fps_font.render(fps_text, True, self.TEXT_COLOR)

        # Draw semi-transparent background
        padding = 5
        bg_rect = fps_surface.get_rect(
            topleft=(10, 10)).inflate(padding * 2, padding * 2)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((255, 255, 255))
        self.screen.blit(bg_surface, bg_rect)

        # Draw text
        self.screen.blit(fps_surface, (10 + padding, 10 + padding))

    def _draw_widget_placeholder(self, rect: pygame.Rect, title: str, subtitle: str):
        """Draw a placeholder box for a widget.

        Args:
            rect: Rectangle defining widget position and size.
            title: Widget title text.
            subtitle: Widget description text.
        """
        # Draw background
        pygame.draw.rect(self.screen, self.WIDGET_BG_COLOR, rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, rect, 2)

        # Draw title
        title_surface = self.font.render(title, True, self.TEXT_COLOR)
        title_rect = title_surface.get_rect(
            centerx=rect.centerx, top=rect.top + 20)
        self.screen.blit(title_surface, title_rect)

        # Draw subtitle
        subtitle_font = pygame.font.Font(None, 18)
        subtitle_surface = subtitle_font.render(
            subtitle, True, (120, 120, 120))
        subtitle_rect = subtitle_surface.get_rect(
            centerx=rect.centerx, top=title_rect.bottom + 10)
        self.screen.blit(subtitle_surface, subtitle_rect)

    def run(self):
        """Run the main application loop."""
        self.running = True
        logger.info("Starting main loop")

        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)

        logger.info("Main loop ended")
        self.quit()

    def quit(self):
        """Clean up and quit the application."""
        pygame.quit()
        logger.info("Application quit")

    def _update_layout(self):
        """Recalculate widget positions based on current window size."""
        # Simple responsive layout - adjust as needed
        margin = 50
        spacing = 20
        controls_width = 460
        controls_height = 260
        sim_size = min(self.WINDOW_WIDTH - controls_width -
                       3*margin, self.WINDOW_HEIGHT - 2*margin)
        periodic_table_width = max(
            controls_width, self.WINDOW_WIDTH - sim_size - 3*margin)

        self.SIMULATION_RECT = pygame.Rect(margin, margin, sim_size, sim_size)
        self.PERIODIC_TABLE_RECT = pygame.Rect(
            self.WINDOW_WIDTH - margin - periodic_table_width, margin,
            periodic_table_width, self.WINDOW_HEIGHT - controls_height - 2*margin - spacing
        )
        self.CONTROLS_RECT = pygame.Rect(
            self.WINDOW_WIDTH - margin -
            controls_width, self.WINDOW_HEIGHT - controls_height - margin,
            controls_width, controls_height
        )
        self.HELP_BUTTON_RECT = pygame.Rect(
            self.WINDOW_WIDTH - margin,
            margin / 2,
            margin / 2, margin / 2
        )

        # Update widget rects if they exist
        if self.periodic_table_widget:
            self.periodic_table_widget.set_rect(self.PERIODIC_TABLE_RECT)
        if self.simulation_widget:
            self.simulation_widget.set_rect(self.SIMULATION_RECT)
        if self.controls_widget:
            self.controls_widget.set_rect(self.CONTROLS_RECT)
        if self.help_button:
            self.help_button.rect = self.HELP_BUTTON_RECT
        # Re-center menus after resize
        if self.preset_menu:
            self.preset_menu.center(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        if self.main_menu:
            self.main_menu.center(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            if self.main_menu.about_textbox:
                self.main_menu.about_textbox.center(
                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            if self.main_menu.copyright_textbox:
                self.main_menu.copyright_textbox.center(
                    self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def _load_preset(self, preset_id: str):
        """Load a preset configuration into the simulation.

        Args:
            preset_id: Preset identifier.
        """

        try:
            atoms = create_preset(preset_id)

            # Verify cubic cell
            cell = atoms.get_cell()
            if not (abs(cell[0, 0] - cell[1, 1]) < 1e-6 and
                    abs(cell[1, 1] - cell[2, 2]) < 1e-6 and
                    abs(cell[0, 1]) < 1e-6 and abs(cell[0, 2]) < 1e-6 and
                    abs(cell[1, 0]) < 1e-6 and abs(cell[1, 2]) < 1e-6 and
                    abs(cell[2, 0]) < 1e-6 and abs(cell[2, 1]) < 1e-6):
                logger.error(f"Preset {preset_id} does not have a cubic cell")
                return

            # Get cell size
            cell_size = cell[0, 0]

            # Update simulation
            if self.simulation_widget:
                self.simulation_widget.engine.atoms = atoms
                logger.info(
                    f"Loaded preset {preset_id}: {len(atoms)} atoms, cell size {cell_size:.2f} Å")

            # Update controls to match
            if self.controls_widget:
                self.controls_widget.cell_size_control.cell_size = cell_size

        except Exception as e:
            logger.error(f"Failed to load preset {preset_id}: {e}")

    def exit(self):
        """Exit the application."""
        self.running = False


def main():
    """Entry point for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = MDApplication(fps=30)
    app.run()
    sys.exit()


if __name__ == "__main__":
    main()
