"""Controls widget for simulation parameters."""

import logging
import pygame
from typing import Tuple

from molecular_dynamics_toy.data import colors
from molecular_dynamics_toy.widgets.base import Button, TextButton, Menu, Slider

logger = logging.getLogger(__name__)


class PlayPauseButton(Button):
    """A button that toggles between play and pause states.

    Attributes:
        playing: True if in play state, False if paused.
    """

    # Colors (use Button defaults)
    ICON_COLOR = colors.CONTROL_ICON_COLOR

    def __init__(self, rect: pygame.Rect):
        """Initialize the play/pause button.

        Args:
            rect: Rectangle defining position and size.
        """
        super().__init__(rect)
        self.playing = False

    def on_click(self):
        """Toggle play/pause state and log the change."""
        super().on_click()
        self.playing = not self.playing
        logger.info(f"Simulation {'playing' if self.playing else 'paused'}")

    def render_content(self, surface: pygame.Surface):
        """Render the play or pause icon.

        Args:
            surface: Surface to render onto.
        """
        icon_rect = self.rect.inflate(-20, -20)  # Padding

        if self.playing:
            # Draw pause icon (two vertical bars)
            bar_width = icon_rect.width // 3
            bar_height = icon_rect.height
            left_bar = pygame.Rect(
                icon_rect.left,
                icon_rect.top,
                bar_width,
                bar_height
            )
            right_bar = pygame.Rect(
                icon_rect.right - bar_width,
                icon_rect.top,
                bar_width,
                bar_height
            )
            pygame.draw.rect(surface, self.ICON_COLOR, left_bar)
            pygame.draw.rect(surface, self.ICON_COLOR, right_bar)
        else:
            # Draw play icon (triangle pointing right)
            triangle_points = [
                (icon_rect.left, icon_rect.top),
                (icon_rect.left, icon_rect.bottom),
                (icon_rect.right, icon_rect.centery)
            ]
            pygame.draw.polygon(surface, self.ICON_COLOR, triangle_points)


class ResetButton(Button):
    """A button that resets the simulation."""

    # Colors
    ICON_COLOR = colors.ICON_RESET_COLOR  # Reddish for reset

    def __init__(self, rect: pygame.Rect):
        """Initialize the reset button.

        Args:
            rect: Rectangle defining position and size.
        """
        super().__init__(rect)

    def on_click(self):
        """Log reset button click."""
        logger.info("Reset button clicked")

    def render_content(self, surface: pygame.Surface):
        """Render the X icon.

        Args:
            surface: Surface to render onto.
        """
        # Draw X icon (two diagonal lines)
        icon_rect = self.rect.inflate(-20, -20)  # Padding

        # Top-left to bottom-right
        pygame.draw.line(
            surface,
            self.ICON_COLOR,
            (icon_rect.left, icon_rect.top),
            (icon_rect.right, icon_rect.bottom),
            3
        )

        # Top-right to bottom-left
        pygame.draw.line(
            surface,
            self.ICON_COLOR,
            (icon_rect.right, icon_rect.top),
            (icon_rect.left, icon_rect.bottom),
            3
        )


class SpeedControlButton(Button):
    """A button for incrementing or decrementing a value.

    Attributes:
        direction: 'increase' or 'decrease'.
    """

    ICON_COLOR = colors.CONTROL_ICON_COLOR

    def __init__(self, rect: pygame.Rect, direction: str):
        """Initialize the speed control button.

        Args:
            rect: Rectangle defining position and size.
            direction: 'increase' or 'decrease'.
        """
        if direction != "increase" and direction != "decrease":
            raise ValueError(
                f"direction should be 'increase' or 'decrease', not '{direction}'")
        super().__init__(rect)
        self.direction = direction

    def render_content(self, surface: pygame.Surface):
        """Render double triangle icon.

        Args:
            surface: Surface to render onto.
        """
        icon_rect = self.rect.inflate(-12, -12)
        mid_x = icon_rect.centerx

        if self.direction == 'decrease':
            # Draw double left triangles (rewind symbol: <<)
            left_triangle = [
                (mid_x - 6, icon_rect.top),
                (mid_x - 6, icon_rect.bottom),
                (icon_rect.left, icon_rect.centery)
            ]
            right_triangle = [
                (mid_x + 2, icon_rect.top),
                (mid_x + 2, icon_rect.bottom),
                (mid_x - 4, icon_rect.centery)
            ]
        else:  # 'increase'
            # Draw double right triangles (fast forward symbol: >>)
            left_triangle = [
                (mid_x - 2, icon_rect.top),
                (mid_x - 2, icon_rect.bottom),
                (mid_x + 4, icon_rect.centery)
            ]
            right_triangle = [
                (mid_x + 6, icon_rect.top),
                (mid_x + 6, icon_rect.bottom),
                (icon_rect.right, icon_rect.centery)
            ]

        pygame.draw.polygon(surface, self.ICON_COLOR, left_triangle)
        pygame.draw.polygon(surface, self.ICON_COLOR, right_triangle)


class SpeedControl:
    """A control for adjusting simulation speed (steps per frame).

    Attributes:
        rect: Rectangle defining control position and size.
        value: Current value.
        label: Label text to display.
        increment: Amount to increment/decrement by.
        min_value: Minimum allowed value.
    """

    # Colors
    TEXT_COLOR = colors.TEXT_COLOR
    BORDER_COLOR = colors.CONTROL_BORDER_COLOR

    def __init__(self, rect: pygame.Rect, label: str = "Speed",
                 initial_value: float = 1, increment: float = 1, min_value: float = 1):
        """Initialize the speed control.

        Args:
            rect: Rectangle defining position and size.
            label: Label text to display above control.
            initial_value: Initial value.
            increment: Amount to increment/decrement by.
            min_value: Minimum allowed value.
        """
        self.rect = rect
        self.label = label
        self.value = max(min_value, initial_value)
        self.increment = increment
        self.min_value = min_value

        # Calculate sub-component rects
        self.label_height = 20
        button_height = rect.height - self.label_height
        button_width = button_height  # Square buttons
        text_width = rect.width - 2 * button_width

        control_top = rect.top + self.label_height

        decrease_rect = pygame.Rect(
            rect.left, control_top, button_width, button_height
        )
        self.text_rect = pygame.Rect(
            rect.left + button_width, control_top, text_width, button_height
        )
        increase_rect = pygame.Rect(
            rect.right - button_width, control_top, button_width, button_height
        )

        # Create button objects
        self.decrease_button = SpeedControlButton(decrease_rect, 'decrease')
        self.increase_button = SpeedControlButton(increase_rect, 'increase')

        self.font = pygame.font.Font(None, 24)
        self.label_font = pygame.font.Font(None, 18)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Check if position is inside control and handle click.

        Args:
            pos: Mouse position (x, y).

        Returns:
            True if control was clicked.
        """
        if self.decrease_button.handle_click(pos):
            self.value = max(self.min_value, self.value - self.increment)
            logger.info(f"{self.label} decreased to {self.value}")
            return True
        elif self.increase_button.handle_click(pos):
            self.value += self.increment
            logger.info(f"{self.label} increased to {self.value}")
            return True
        return False

    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover state based on mouse position.

        Args:
            pos: Mouse position (x, y).
        """
        self.decrease_button.handle_hover(pos)
        self.increase_button.handle_hover(pos)

    def render(self, surface: pygame.Surface):
        """Render the control.

        Args:
            surface: Surface to render onto.
        """
        # Draw label
        label_surface = self.label_font.render(
            self.label, True, self.TEXT_COLOR)
        label_rect = label_surface.get_rect(
            centerx=self.rect.centerx, top=self.rect.top + 2)
        surface.blit(label_surface, label_rect)

        # Render buttons
        self.decrease_button.render(surface)
        self.increase_button.render(surface)

        # Draw text box with value
        pygame.draw.rect(surface, colors.WIDGET_BG_COLOR, self.text_rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.text_rect, 2)

        # Format value appropriately (show decimals if needed)
        if isinstance(self.value, float) and self.value % 1 != 0:
            value_str = f"{self.value:.1f}"
        else:
            value_str = str(int(self.value))

        text_surface = self.font.render(value_str, True, self.TEXT_COLOR)
        text_pos = text_surface.get_rect(center=self.text_rect.center)
        surface.blit(text_surface, text_pos)


class TemperatureSlider(Slider):
    """A slider control for adjusting simulation temperature.

    Attributes:
        temperature: Temperature in Kelvin.
        min_temp: Minimum temperature.
        max_temp: Maximum temperature.
    """

    # Colors (inherit from Slider)
    TEXT_COLOR = colors.TEXT_COLOR

    def __init__(self, rect: pygame.Rect, initial_temp: float = 300.0,
                 min_temp: float = 0.0, max_temp: float = 1000.0):
        """Initialize the temperature slider.

        Args:
            rect: Rectangle defining position and size.
            initial_temp: Initial temperature in Kelvin.
            min_temp: Minimum temperature in Kelvin.
            max_temp: Maximum temperature in Kelvin.
        """
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.temperature = initial_temp

        # Calculate initial normalized value
        initial_value = (initial_temp - min_temp) / (max_temp - min_temp)

        super().__init__(rect, initial_value, orientation='horizontal')

        # Layout
        self.label_height = 25
        self.slider_height = 20

        # Override handle dimensions for temperature slider
        self.handle_width = 15
        self.handle_height = self.slider_height

        self.font = pygame.font.Font(None, 22)

    def _get_track_rect(self) -> pygame.Rect:
        """Get the rectangle for the slider track."""
        margin = 10
        return pygame.Rect(
            self.rect.left + margin,
            self.rect.top + self.label_height + 10,
            self.rect.width - 2 * margin,
            self.slider_height
        )

    def on_value_changed(self):
        """Update temperature when slider value changes."""
        old_temp = self.temperature
        self.temperature = self.min_temp + \
            self.value * (self.max_temp - self.min_temp)

        if abs(self.temperature - old_temp) > 0.5:  # Log only significant changes
            logger.debug(f"Temperature set to {self.temperature:.1f} K")

    def render(self, surface: pygame.Surface):
        """Render the temperature slider.

        Args:
            surface: Surface to render onto.
        """
        # Draw label
        label_text = f"Temperature: {self.temperature:.0f} K"
        label_surface = self.font.render(label_text, True, self.TEXT_COLOR)
        label_rect = label_surface.get_rect(
            left=self.rect.left + 10,
            top=self.rect.top + 5
        )
        surface.blit(label_surface, label_rect)

        # Draw slider (track and handle)
        super().render(surface)


class CellSizeControl:
    """A control for adjusting simulation cell size.

    Attributes:
        rect: Rectangle defining control position and size.
        cell_size: Current cell size in Angstroms.
        min_size: Minimum allowed cell size.
    """

    # Colors
    TEXT_COLOR = colors.TEXT_COLOR
    BORDER_COLOR = colors.CONTROL_BORDER_COLOR

    def __init__(self, rect: pygame.Rect, initial_size: float = 20.0, min_size: float = 4.0):
        """Initialize the cell size control.

        Args:
            rect: Rectangle defining position and size.
            initial_size: Initial cell size in Angstroms.
            min_size: Minimum allowed cell size in Angstroms.
        """
        self.rect = rect
        self.cell_size = max(min_size, initial_size)
        self.min_size = min_size

        # Layout parameters
        self.label_height = 20
        button_height = 20
        button_width = 50
        spacing = 2

        # Calculate positions
        control_top = rect.top + self.label_height
        control_height = rect.height - self.label_height

        # Text display in center
        text_width = rect.width - 2 * (button_width + 10)
        self.text_rect = pygame.Rect(
            rect.left + button_width + 10,
            control_top + (control_height - button_height *
                           3 - spacing * 2) // 2,
            text_width,
            button_height * 3 + spacing * 2
        )

        # Left column (decrease buttons)
        left_x = rect.left
        buttons_top = self.text_rect.top

        # Right column (increase buttons)
        right_x = rect.right - button_width

        # Create buttons for each increment

        self.decrease_buttons = [
            TextButton(pygame.Rect(left_x, buttons_top, button_width, button_height),
                       "-1", font_size=16),
            TextButton(pygame.Rect(left_x, buttons_top + button_height + spacing, button_width, button_height),
                       "-0.1", font_size=16),
            TextButton(pygame.Rect(left_x, buttons_top + 2 * (button_height + spacing), button_width, button_height),
                       "-0.01", font_size=16),
        ]

        self.increase_buttons = [
            TextButton(pygame.Rect(right_x, buttons_top, button_width, button_height),
                       "+1", font_size=16),
            TextButton(pygame.Rect(right_x, buttons_top + button_height + spacing, button_width, button_height),
                       "+0.1", font_size=16),
            TextButton(pygame.Rect(right_x, buttons_top + 2 * (button_height + spacing), button_width, button_height),
                       "+0.01", font_size=16),
        ]

        self.increments = [1.0, 0.1, 0.01]

        self.font = pygame.font.Font(None, 24)
        self.label_font = pygame.font.Font(None, 18)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Check if position is inside control and handle click.

        Args:
            pos: Mouse position (x, y).

        Returns:
            True if control was clicked.
        """
        # Check decrease buttons
        for i, button in enumerate(self.decrease_buttons):
            if button.handle_click(pos):
                self.cell_size = max(
                    self.min_size, self.cell_size - self.increments[i])
                logger.info(f"Cell size decreased to {self.cell_size:.2f} Å")
                return True

        # Check increase buttons
        for i, button in enumerate(self.increase_buttons):
            if button.handle_click(pos):
                self.cell_size += self.increments[i]
                logger.info(f"Cell size increased to {self.cell_size:.2f} Å")
                return True

        return False

    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover state based on mouse position.

        Args:
            pos: Mouse position (x, y).
        """
        for button in self.decrease_buttons + self.increase_buttons:
            button.handle_hover(pos)

    def render(self, surface: pygame.Surface):
        """Render the control.

        Args:
            surface: Surface to render onto.
        """
        # Draw label
        label_surface = self.label_font.render(
            "Cell Size (Å)", True, self.TEXT_COLOR)
        label_rect = label_surface.get_rect(
            centerx=self.rect.centerx, top=self.rect.top + 2)
        surface.blit(label_surface, label_rect)

        # Render buttons
        for button in self.decrease_buttons + self.increase_buttons:
            button.render(surface)

        # Draw text box with cell size
        pygame.draw.rect(surface, colors.WIDGET_BG_COLOR, self.text_rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.text_rect, 2)

        value_str = f"{self.cell_size:.2f}"
        text_surface = self.font.render(value_str, True, self.TEXT_COLOR)
        text_pos = text_surface.get_rect(center=self.text_rect.center)
        surface.blit(text_surface, text_pos)


class LoadPresetButton(Button):
    """A button to open the load preset menu."""

    ICON_COLOR = colors.CONTROL_ICON_COLOR

    def __init__(self, rect: pygame.Rect):
        """Initialize load preset button.

        Args:
            rect: Rectangle defining position and size.
        """
        super().__init__(rect)

    def render_content(self, surface: pygame.Surface):
        """Render download/import icon (arrow down into rectangle).

        Args:
            surface: Surface to render onto.
        """
        icon_rect = self.rect.inflate(-16, -16)

        # Draw arrow shaft (vertical line)
        arrow_top = icon_rect.top
        arrow_mid_y = icon_rect.centery - 3
        pygame.draw.line(
            surface,
            self.ICON_COLOR,
            (icon_rect.centerx, arrow_top),
            (icon_rect.centerx, arrow_mid_y),
            3
        )

        # Draw arrow head (triangle pointing down)
        arrow_head = [
            (icon_rect.centerx - 6, arrow_mid_y - 6),
            (icon_rect.centerx + 6, arrow_mid_y - 6),
            (icon_rect.centerx, arrow_mid_y + 3)
        ]
        pygame.draw.polygon(surface, self.ICON_COLOR, arrow_head)

        # Draw base rectangle (landscape oriented)
        base_rect = pygame.Rect(
            icon_rect.left,
            icon_rect.bottom - 8,
            icon_rect.width,
            8
        )
        pygame.draw.rect(surface, self.ICON_COLOR, base_rect)
        pygame.draw.rect(surface, self.ICON_COLOR, base_rect, 2)


class MenuButton(Button):
    """A button that opens the main menu (hamburger icon)."""

    ICON_COLOR = colors.CONTROL_ICON_COLOR

    def __init__(self, rect: pygame.Rect):
        """Initialize menu button.

        Args:
            rect: Rectangle defining position and size.
        """
        super().__init__(rect)

    def render_content(self, surface: pygame.Surface):
        """Render hamburger menu icon (three horizontal lines).

        Args:
            surface: Surface to render onto.
        """
        icon_rect = self.rect.inflate(-16, -16)

        # Draw three horizontal lines
        line_height = 3
        spacing = (icon_rect.height - 3 * line_height) // 2

        for i in range(3):
            y = icon_rect.top + i * (line_height + spacing)
            pygame.draw.rect(
                surface,
                self.ICON_COLOR,
                pygame.Rect(icon_rect.left, y, icon_rect.width, line_height)
            )


class ControlsWidget:
    """Widget for simulation controls (play/pause, speed, temperature).

    Attributes:
        rect: Rectangle defining widget position and size.
        playing: True if simulation is playing, False if paused.
        reset_requested: True if reset button was clicked this frame.
        steps_per_frame: Number of MD steps per frame.
        timestep: MD timestep in femtoseconds.
        temperature: Target temperature in Kelvin.
        cell_size: Simulation cell size in Angstroms.
        open_preset_menu_requested: True if preset menu should be opened.
        open_main_menu_requested: True if main menu should be opened.
    """

    BG_COLOR = colors.WIDGET_BG_COLOR

    def __init__(self, rect: pygame.Rect):
        """Initialize the controls widget.

        Args:
            rect: Rectangle defining widget position and size.
        """
        self.rect = rect
        self.play_pause_button = None
        self.reset_button = None
        self.steps_control = None
        self.timestep_control = None
        self.temperature_slider = None
        self.cell_size_control = None
        self.load_preset_button = None
        self.reset_requested = False
        self.open_preset_menu_requested = False
        self.open_main_menu_requested = False

        self._create_controls()
        logger.info("ControlsWidget initialized")

    def _create_controls(self):
        """Create control elements."""
        # Preserve state if recreating
        old_playing = self.play_pause_button.playing if self.play_pause_button else False
        old_steps = self.steps_control.value if self.steps_control else 1
        old_timestep = self.timestep_control.value if self.timestep_control else 1
        old_temp = self.temperature_slider.temperature if self.temperature_slider else 300.0
        old_cell_size = self.cell_size_control.cell_size if self.cell_size_control else 20.0

        margin = 20
        button_size = 60
        spacing = 10

        # Create play/pause button
        play_button_rect = pygame.Rect(
            self.rect.left + margin,
            self.rect.top + margin,
            button_size,
            button_size
        )
        self.play_pause_button = PlayPauseButton(play_button_rect)
        self.play_pause_button.playing = old_playing

        # Create reset button
        reset_button_rect = pygame.Rect(
            self.rect.left + margin + button_size + spacing,
            self.rect.top + margin,
            button_size,
            button_size
        )
        self.reset_button = ResetButton(reset_button_rect)

        # Create speed controls (steps per frame and timestep)
        speed_control_width = 120
        speed_control_height = button_size

        steps_control_rect = pygame.Rect(
            self.rect.left + margin + 2 * (button_size + spacing),
            self.rect.top + margin,
            speed_control_width,
            speed_control_height
        )
        self.steps_control = SpeedControl(
            steps_control_rect,
            label="Steps/Frame",
            initial_value=old_steps
        )

        timestep_control_rect = pygame.Rect(
            self.rect.left + margin + 2 *
            (button_size + spacing) + speed_control_width + spacing,
            self.rect.top + margin,
            speed_control_width,
            speed_control_height
        )
        self.timestep_control = SpeedControl(
            timestep_control_rect,
            label="Timestep (fs)",
            initial_value=old_timestep,
            increment=0.5,
            min_value=0.5
        )

        # Create temperature slider
        slider_top = self.rect.top + margin + button_size + spacing
        slider_rect = pygame.Rect(
            self.rect.left + margin,
            slider_top,
            self.rect.width - 2 * margin,
            60
        )
        self.temperature_slider = TemperatureSlider(
            slider_rect, initial_temp=old_temp, max_temp=2000)

        # Create cell size control
        cell_size_top = slider_top + 60 + spacing
        cell_size_rect = pygame.Rect(
            self.rect.left + margin,
            cell_size_top,
            200,
            80
        )
        self.cell_size_control = CellSizeControl(
            cell_size_rect, initial_size=old_cell_size)

        # Create load preset button (next to cell size control)
        load_preset_rect = pygame.Rect(
            self.rect.left + margin + 200 + spacing,
            cell_size_top + 80 - button_size,
            button_size,
            button_size
        )
        self.load_preset_button = LoadPresetButton(load_preset_rect)

        # Create menu button
        menu_button_rect = pygame.Rect(
            self.rect.left + margin + 200 + button_size + 3 * spacing,
            cell_size_top + 80 - button_size,
            button_size,
            button_size
        )
        self.menu_button = MenuButton(menu_button_rect)

    @property
    def playing(self) -> bool:
        """Get current play/pause state."""
        return self.play_pause_button.playing if self.play_pause_button else False

    @property
    def steps_per_frame(self) -> int:
        """Get current steps per frame."""
        return self.steps_control.value if self.steps_control else 1

    @property
    def timestep(self) -> float:
        """Get current timestep in femtoseconds."""
        return float(self.timestep_control.value) if self.timestep_control else 1.0

    @property
    def temperature(self) -> float:
        """Get current temperature in Kelvin."""
        return self.temperature_slider.temperature if self.temperature_slider else 300.0

    @property
    def cell_size(self) -> float:
        """Get current cell size in Angstroms."""
        return self.cell_size_control.cell_size if self.cell_size_control else 20.0

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events.

        Args:
            event: Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.play_pause_button:
                    self.play_pause_button.handle_click(event.pos)
                if self.reset_button:
                    if self.reset_button.handle_click(event.pos):
                        self.reset_requested = True
                if self.steps_control:
                    self.steps_control.handle_click(event.pos)
                if self.timestep_control:
                    self.timestep_control.handle_click(event.pos)
                if self.temperature_slider:
                    self.temperature_slider.handle_click(event.pos)
                if self.cell_size_control:
                    self.cell_size_control.handle_click(event.pos)
                if self.load_preset_button:
                    if self.load_preset_button.handle_click(event.pos):
                        self.open_preset_menu_requested = True
                if self.menu_button:
                    if self.menu_button.handle_click(event.pos):
                        self.open_main_menu_requested = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.temperature_slider:
                    self.temperature_slider.handle_release()

        elif event.type == pygame.MOUSEMOTION:
            if self.play_pause_button:
                self.play_pause_button.handle_hover(event.pos)
            if self.reset_button:
                self.reset_button.handle_hover(event.pos)
            if self.steps_control:
                self.steps_control.handle_hover(event.pos)
            if self.timestep_control:
                self.timestep_control.handle_hover(event.pos)
            if self.temperature_slider:
                self.temperature_slider.handle_hover(event.pos)
                self.temperature_slider.handle_drag(event.pos)
            if self.cell_size_control:
                self.cell_size_control.handle_hover(event.pos)
            if self.load_preset_button:
                self.load_preset_button.handle_hover(event.pos)
            if self.menu_button:
                self.menu_button.handle_hover(event.pos)

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

        # Draw controls
        if self.play_pause_button:
            self.play_pause_button.render(surface)
        if self.reset_button:
            self.reset_button.render(surface)
        if self.steps_control:
            self.steps_control.render(surface)
        if self.timestep_control:
            self.timestep_control.render(surface)
        if self.temperature_slider:
            self.temperature_slider.render(surface)
        if self.cell_size_control:
            self.cell_size_control.render(surface)
        if self.load_preset_button:
            self.load_preset_button.render(surface)
        if self.menu_button:
            self.menu_button.render(surface)

    def set_rect(self, rect: pygame.Rect):
        """Update widget position and size, recalculating control positions.

        Args:
            rect: New rectangle defining widget position and size.
        """
        self.rect = rect
        self._create_controls()
        logger.debug(f"ControlsWidget resized to {rect}")
