"""Tests for the controls widget."""

import pytest
import pygame
from molecular_dynamics_toy.widgets.controls import ControlsWidget, PlayPauseButton, ResetButton, SpeedControl, TemperatureSlider, CellSizeControl


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_play_pause_button_initialization(pygame_init):
    """Test that PlayPauseButton initializes in paused state."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = PlayPauseButton(rect)

    assert button.rect == rect
    assert button.playing is False
    assert button.hovered is False


def test_play_pause_button_click_to_play(pygame_init):
    """Test that clicking paused button starts playing."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = PlayPauseButton(rect)

    clicked = button.handle_click((30, 30))

    assert clicked is True
    assert button.playing is True


def test_play_pause_button_toggle(pygame_init):
    """Test that clicking toggles between play and pause."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = PlayPauseButton(rect)

    # First click: play
    button.handle_click((30, 30))
    assert button.playing is True

    # Second click: pause
    button.handle_click((30, 30))
    assert button.playing is False

    # Third click: play again
    button.handle_click((30, 30))
    assert button.playing is True


def test_play_pause_button_click_outside(pygame_init):
    """Test that clicking outside button doesn't change state."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = PlayPauseButton(rect)

    clicked = button.handle_click((100, 100))

    assert clicked is False
    assert button.playing is False


def test_play_pause_button_hover(pygame_init):
    """Test that hovering over button updates hover state."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = PlayPauseButton(rect)

    # Hover inside
    button.handle_hover((30, 30))
    assert button.hovered is True

    # Hover outside
    button.handle_hover((100, 100))
    assert button.hovered is False


def test_controls_widget_initialization(pygame_init):
    """Test that ControlsWidget initializes correctly."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    assert widget.rect == rect
    assert widget.play_pause_button is not None
    assert widget.playing is False


def test_controls_widget_playing_property(pygame_init):
    """Test that playing property reflects button state."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    assert widget.playing is False

    # Click button
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.play_pause_button.rect.center}
    )
    widget.handle_event(event)

    assert widget.playing is True


def test_controls_widget_event_handling(pygame_init):
    """Test that widget handles mouse events correctly."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    button_center = widget.play_pause_button.rect.center

    # Mouse motion event
    motion_event = pygame.event.Event(
        pygame.MOUSEMOTION,
        {'pos': button_center}
    )
    widget.handle_event(motion_event)
    assert widget.play_pause_button.hovered is True

    # Mouse click event
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': button_center}
    )
    widget.handle_event(click_event)
    assert widget.playing is True


def test_controls_widget_resize(pygame_init):
    """Test that controls widget can be resized."""
    rect1 = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect1)

    # Resize
    rect2 = pygame.Rect(0, 0, 600, 300)
    widget.set_rect(rect2)

    assert widget.rect == rect2
    assert widget.play_pause_button is not None


def test_controls_widget_resize_preserves_state(pygame_init):
    """Test that resizing doesn't change play/pause state."""
    rect1 = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect1)

    # Set to playing
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.play_pause_button.rect.center}
    )
    widget.handle_event(event)
    assert widget.playing is True

    # Resize
    rect2 = pygame.Rect(0, 0, 600, 300)
    widget.set_rect(rect2)

    # State should be preserved
    assert widget.playing is True


def test_reset_button_initialization(pygame_init):
    """Test that ResetButton initializes correctly."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ResetButton(rect)

    assert button.rect == rect
    assert button.hovered is False


def test_reset_button_click(pygame_init):
    """Test that clicking reset button returns True."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ResetButton(rect)

    clicked = button.handle_click((30, 30))

    assert clicked is True


def test_reset_button_click_outside(pygame_init):
    """Test that clicking outside reset button returns False."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ResetButton(rect)

    clicked = button.handle_click((100, 100))

    assert clicked is False


def test_reset_button_hover(pygame_init):
    """Test that hovering over reset button updates hover state."""
    rect = pygame.Rect(10, 10, 60, 60)
    button = ResetButton(rect)

    # Hover inside
    button.handle_hover((30, 30))
    assert button.hovered is True

    # Hover outside
    button.handle_hover((100, 100))
    assert button.hovered is False


def test_controls_widget_has_reset_button(pygame_init):
    """Test that ControlsWidget initializes with reset button."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    assert widget.reset_button is not None
    assert widget.reset_requested is False


def test_controls_widget_reset_requested(pygame_init):
    """Test that clicking reset button sets reset_requested flag."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    # Click reset button
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.reset_button.rect.center}
    )
    widget.handle_event(event)

    assert widget.reset_requested is True


def test_controls_widget_reset_flag_persists(pygame_init):
    """Test that reset_requested flag persists until cleared externally."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    # Click reset button
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.reset_button.rect.center}
    )
    widget.handle_event(event)

    assert widget.reset_requested is True

    # Flag should persist (not auto-clear)
    widget.update()
    assert widget.reset_requested is True

    # Must be cleared externally
    widget.reset_requested = False
    assert widget.reset_requested is False


def test_speed_control_initialization(pygame_init):
    """Test that SpeedControl initializes correctly."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect)

    assert control.rect == rect
    assert control.value == 1


def test_speed_control_custom_initial_value(pygame_init):
    """Test that SpeedControl can be initialized with custom speed."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect, initial_value=5)

    assert control.value == 5


def test_speed_control_increase(pygame_init):
    """Test that clicking increase button increments speed."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect)

    initial_speed = control.value
    clicked = control.handle_click(control.increase_button.rect.center)

    assert clicked is True
    assert control.value == initial_speed + 1


def test_speed_control_decrease(pygame_init):
    """Test that clicking decrease button decrements speed."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect, initial_value=5)

    initial_speed = control.value
    clicked = control.handle_click(control.decrease_button.rect.center)

    assert clicked is True
    assert control.value == initial_speed - 1


def test_speed_control_minimum_speed(pygame_init):
    """Test that speed cannot go below 1."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect, initial_value=1)

    # Try to decrease below 1
    control.handle_click(control.decrease_button.rect.center)

    assert control.value == 1


def test_speed_control_multiple_increases(pygame_init):
    """Test that speed can be increased multiple times."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect)

    for i in range(5):
        control.handle_click(control.increase_button.rect.center)

    assert control.value == 6


def test_speed_control_hover(pygame_init):
    """Test that hovering updates button hover states."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect)

    # Hover over decrease button
    control.handle_hover(control.decrease_button.rect.center)
    assert control.decrease_button.hovered is True
    assert control.increase_button.hovered is False

    # Hover over increase button
    control.handle_hover(control.increase_button.rect.center)
    assert control.decrease_button.hovered is False
    assert control.increase_button.hovered is True

    # Hover outside
    control.handle_hover((0, 0))
    assert control.decrease_button.hovered is False
    assert control.increase_button.hovered is False


def test_speed_control_click_outside(pygame_init):
    """Test that clicking outside buttons doesn't change speed."""
    rect = pygame.Rect(10, 10, 200, 60)
    control = SpeedControl(rect, initial_value=3)

    # Click in text area (middle)
    clicked = control.handle_click(control.text_rect.center)

    assert clicked is False
    assert control.value == 3


def test_controls_widget_has_speed_control(pygame_init):
    """Test that ControlsWidget initializes with speed control."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    assert widget.steps_control is not None
    assert widget.steps_per_frame == 1


def test_controls_widget_speed_property(pygame_init):
    """Test that speed property reflects speed control state."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    # Increase speed
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.steps_control.increase_button.rect.center}
    )
    widget.handle_event(event)

    assert widget.steps_per_frame == 2


def test_controls_widget_speed_preserved_on_resize(pygame_init):
    """Test that speed is preserved when widget is resized."""
    rect1 = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect1)

    # Set speed to 5
    for _ in range(4):
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'button': 1, 'pos': widget.steps_control.increase_button.rect.center}
        )
        widget.handle_event(event)

    assert widget.steps_per_frame == 5

    # Resize
    rect2 = pygame.Rect(0, 0, 600, 300)
    widget.set_rect(rect2)

    # Speed should be preserved
    assert widget.steps_per_frame == 5


def test_temperature_slider_initialization(pygame_init):
    """Test that TemperatureSlider initializes correctly."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect)

    assert slider.rect == rect
    assert slider.temperature == 300.0
    assert slider.min_temp == 0.0
    assert slider.max_temp == 1000.0
    assert slider.dragging is False
    assert slider.hovered is False


def test_temperature_slider_custom_initial_temp(pygame_init):
    """Test that TemperatureSlider can be initialized with custom temperature."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect, initial_temp=500.0)

    assert slider.temperature == 500.0


def test_temperature_slider_custom_range(pygame_init):
    """Test that TemperatureSlider can have custom min/max."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect, min_temp=100.0, max_temp=2000.0)

    assert slider.min_temp == 100.0
    assert slider.max_temp == 2000.0


def test_temperature_slider_click_starts_drag(pygame_init):
    """Test that clicking slider starts dragging."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect)

    slider_rect = slider._get_handle_rect()
    clicked = slider.handle_click(slider_rect.center)

    assert clicked is True
    assert slider.dragging is True


def test_temperature_slider_release_stops_drag(pygame_init):
    """Test that releasing mouse stops dragging."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect)

    slider_rect = slider._get_handle_rect()
    slider.handle_click(slider_rect.center)
    assert slider.dragging is True

    slider.handle_release()
    assert slider.dragging is False


def test_temperature_slider_click_on_track(pygame_init):
    """Test that clicking on track updates temperature."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect, initial_temp=300.0)

    track_rect = slider._get_track_rect()

    # Click at start of track (should be min_temp)
    slider.handle_click((track_rect.left + 1, track_rect.centery))
    assert slider.temperature < slider.min_temp + 20  # Near minimum

    # Click at end of track (should be max_temp)
    slider.handle_click((track_rect.right - 1, track_rect.centery))
    assert slider.temperature > slider.max_temp - 20  # Near maximum


def test_temperature_slider_drag_updates_temperature(pygame_init):
    """Test that dragging slider updates temperature."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect, initial_temp=300.0)

    slider_rect = slider._get_handle_rect()
    slider.handle_click(slider_rect.center)

    # Drag to different position
    track_rect = slider._get_track_rect()
    slider.handle_drag((track_rect.right - 50, track_rect.centery))

    # Temperature should have increased significantly
    assert slider.temperature > 800


def test_temperature_slider_no_drag_when_not_dragging(pygame_init):
    """Test that handle_drag does nothing when not dragging."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect, initial_temp=500.0)

    track_rect = slider._get_track_rect()
    slider.handle_drag((track_rect.left, track_rect.centery))

    # Temperature should not have changed
    assert slider.temperature == 500.0


def test_temperature_slider_hover(pygame_init):
    """Test that hovering over slider updates hover state."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect)

    slider_rect = slider._get_handle_rect()

    # Hover over slider
    slider.handle_hover(slider_rect.center)
    assert slider.hovered is True

    # Hover outside slider
    slider.handle_hover((0, 0))
    assert slider.hovered is False


def test_temperature_slider_clamps_to_range(pygame_init):
    """Test that temperature is clamped to min/max range."""
    rect = pygame.Rect(10, 10, 400, 60)
    slider = TemperatureSlider(rect)

    track_rect = slider._get_track_rect()

    # Click far left (beyond track)
    slider.handle_click((track_rect.left - 100, track_rect.centery))
    assert slider.temperature >= slider.min_temp

    # Click far right (beyond track)
    slider.handle_click((track_rect.right + 100, track_rect.centery))
    assert slider.temperature <= slider.max_temp


def test_controls_widget_has_temperature_slider(pygame_init):
    """Test that ControlsWidget initializes with temperature slider."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    assert widget.temperature_slider is not None
    assert widget.temperature == 300.0


def test_controls_widget_temperature_property(pygame_init):
    """Test that temperature property reflects slider state."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    # Click on slider track
    track_rect = widget.temperature_slider._get_track_rect()
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': (track_rect.right - 50, track_rect.centery)}
    )
    widget.handle_event(event)

    # Temperature should have changed from default
    assert widget.temperature != 300.0
    assert widget.temperature > 800


def test_controls_widget_temperature_preserved_on_resize(pygame_init):
    """Test that temperature is preserved when widget is resized."""
    rect1 = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect1)

    # Set temperature to 75% of max
    track_rect = widget.temperature_slider._get_track_rect()
    widget.temperature_slider.handle_click(
        (track_rect.left + track_rect.width * 0.75, track_rect.centery))

    temp_before = widget.temperature
    assert 0.7 * widget.temperature_slider.max_temp < temp_before < 0.8 * \
        widget.temperature_slider.max_temp

    # Resize
    rect2 = pygame.Rect(0, 0, 600, 300)
    widget.set_rect(rect2)

    # Temperature should be preserved
    assert abs(widget.temperature - temp_before) < 1.0


def test_controls_widget_temperature_drag(pygame_init):
    """Test that dragging temperature slider works through widget."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    slider_rect = widget.temperature_slider._get_handle_rect()

    # Start drag
    mousedown = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': slider_rect.center}
    )
    widget.handle_event(mousedown)
    assert widget.temperature_slider.dragging is True

    # Drag
    track_rect = widget.temperature_slider._get_track_rect()
    mousemove = pygame.event.Event(
        pygame.MOUSEMOTION,
        {'pos': (track_rect.left + 50, track_rect.centery)}
    )
    widget.handle_event(mousemove)

    # Temperature should have changed
    assert widget.temperature < 0.15 * \
        widget.temperature_slider.max_temp  # Dragged to low position

    # Release
    mouseup = pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1})
    widget.handle_event(mouseup)
    assert widget.temperature_slider.dragging is False


def test_speed_control_custom_increment(pygame_init):
    """Test that SpeedControl can use custom increment."""
    rect = pygame.Rect(10, 10, 120, 60)
    control = SpeedControl(rect, initial_value=1.0,
                           increment=0.5, min_value=0.5)

    assert control.value == 1.0
    assert control.increment == 0.5
    assert control.min_value == 0.5


def test_speed_control_increment_by_half(pygame_init):
    """Test that control can increment by 0.5."""
    rect = pygame.Rect(10, 10, 120, 60)
    control = SpeedControl(rect, initial_value=1.0,
                           increment=0.5, min_value=0.5)

    # Increase
    control.handle_click(control.increase_button.rect.center)
    assert control.value == 1.5

    # Increase again
    control.handle_click(control.increase_button.rect.center)
    assert control.value == 2.0


def test_speed_control_decrement_by_half(pygame_init):
    """Test that control can decrement by 0.5."""
    rect = pygame.Rect(10, 10, 120, 60)
    control = SpeedControl(rect, initial_value=2.0,
                           increment=0.5, min_value=0.5)

    # Decrease
    control.handle_click(control.decrease_button.rect.center)
    assert control.value == 1.5

    # Decrease again
    control.handle_click(control.decrease_button.rect.center)
    assert control.value == 1.0


def test_speed_control_respects_custom_minimum(pygame_init):
    """Test that control respects custom minimum value."""
    rect = pygame.Rect(10, 10, 120, 60)
    control = SpeedControl(rect, initial_value=0.5,
                           increment=0.5, min_value=0.5)

    # Try to decrease below minimum
    control.handle_click(control.decrease_button.rect.center)

    assert control.value == 0.5


def test_controls_widget_has_timestep_control(pygame_init):
    """Test that ControlsWidget initializes with timestep control."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    assert widget.timestep_control is not None
    assert widget.timestep == 1.0


def test_controls_widget_timestep_property(pygame_init):
    """Test that timestep property reflects timestep control state."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    # Increase timestep
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.timestep_control.increase_button.rect.center}
    )
    widget.handle_event(event)

    assert widget.timestep == 1.5


def test_controls_widget_timestep_decrement(pygame_init):
    """Test that timestep can be decremented to minimum."""
    rect = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect)

    # Decrease timestep
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1, 'pos': widget.timestep_control.decrease_button.rect.center}
    )
    widget.handle_event(event)

    assert widget.timestep == 0.5

    # Try to decrease below minimum
    widget.handle_event(event)
    assert widget.timestep == 0.5


def test_controls_widget_timestep_preserved_on_resize(pygame_init):
    """Test that timestep is preserved when widget is resized."""
    rect1 = pygame.Rect(0, 0, 500, 250)
    widget = ControlsWidget(rect1)

    # Set timestep to 2.5
    for _ in range(3):
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'button': 1, 'pos': widget.timestep_control.increase_button.rect.center}
        )
        widget.handle_event(event)

    assert widget.timestep == 2.5

    # Resize
    rect2 = pygame.Rect(0, 0, 600, 300)
    widget.set_rect(rect2)

    # Timestep should be preserved
    assert widget.timestep == 2.5


def test_speed_control_float_display(pygame_init):
    """Test that float values are displayed with one decimal place."""
    rect = pygame.Rect(10, 10, 120, 60)
    control = SpeedControl(rect, initial_value=1.5,
                           increment=0.5, min_value=0.5)

    # This is a rendering test - we just verify it doesn't crash
    surface = pygame.Surface((200, 100))
    control.render(surface)

    # Value should still be 1.5
    assert control.value == 1.5


def test_cell_size_control_initialization(pygame_init):
    """Test that CellSizeControl initializes correctly."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect)

    assert control.rect == rect
    assert control.cell_size == 20.0
    assert control.min_size == 4.0


def test_cell_size_control_custom_initial_size(pygame_init):
    """Test that CellSizeControl can be initialized with custom size."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=30.0)

    assert control.cell_size == 30.0


def test_cell_size_control_increase_by_one(pygame_init):
    """Test increasing cell size by 1 Angstrom."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=20.0)

    # Click +1 button
    control.handle_click(control.increase_buttons[0].rect.center)

    assert control.cell_size == 21.0


def test_cell_size_control_increase_by_point_one(pygame_init):
    """Test increasing cell size by 0.1 Angstrom."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=20.0)

    # Click +0.1 button
    control.handle_click(control.increase_buttons[1].rect.center)

    assert abs(control.cell_size - 20.1) < 1e-9


def test_cell_size_control_increase_by_point_zero_one(pygame_init):
    """Test increasing cell size by 0.01 Angstrom."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=20.0)

    # Click +0.01 button
    control.handle_click(control.increase_buttons[2].rect.center)

    assert abs(control.cell_size - 20.01) < 1e-9


def test_cell_size_control_decrease_by_one(pygame_init):
    """Test decreasing cell size by 1 Angstrom."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=20.0)

    # Click -1 button
    control.handle_click(control.decrease_buttons[0].rect.center)

    assert control.cell_size == 19.0


def test_cell_size_control_decrease_by_point_one(pygame_init):
    """Test decreasing cell size by 0.1 Angstrom."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=20.0)

    # Click -0.1 button
    control.handle_click(control.decrease_buttons[1].rect.center)

    assert abs(control.cell_size - 19.9) < 1e-9


def test_cell_size_control_respects_minimum(pygame_init):
    """Test that cell size cannot go below minimum."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=5.0, min_size=5.0)

    # Try to decrease below minimum
    control.handle_click(control.decrease_buttons[0].rect.center)

    assert control.cell_size == 5.0


def test_cell_size_control_multiple_increments(pygame_init):
    """Test multiple increments work correctly."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect, initial_size=20.0)

    # +1, +0.1, +0.01
    control.handle_click(control.increase_buttons[0].rect.center)
    control.handle_click(control.increase_buttons[1].rect.center)
    control.handle_click(control.increase_buttons[2].rect.center)

    assert abs(control.cell_size - 21.11) < 1e-9


def test_cell_size_control_hover(pygame_init):
    """Test that hovering updates button states."""
    rect = pygame.Rect(0, 0, 300, 100)
    control = CellSizeControl(rect)

    # Hover over +1 button
    control.handle_hover(control.increase_buttons[0].rect.center)
    assert control.increase_buttons[0].hovered is True

    # Hover outside
    control.handle_hover((0, 0))
    assert control.increase_buttons[0].hovered is False


def test_controls_widget_has_cell_size_control(pygame_init):
    """Test that ControlsWidget initializes with cell size control."""

    rect = pygame.Rect(0, 0, 500, 300)
    widget = ControlsWidget(rect)

    assert widget.cell_size_control is not None
    assert widget.cell_size == 20.0


def test_controls_widget_cell_size_property(pygame_init):
    """Test that cell_size property reflects control state."""

    rect = pygame.Rect(0, 0, 500, 300)
    widget = ControlsWidget(rect)

    # Increase cell size
    event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {'button': 1,
            'pos': widget.cell_size_control.increase_buttons[0].rect.center}
    )
    widget.handle_event(event)

    assert widget.cell_size == 21.0


def test_controls_widget_cell_size_preserved_on_resize(pygame_init):
    """Test that cell size is preserved when widget is resized."""

    rect1 = pygame.Rect(0, 0, 500, 300)
    widget = ControlsWidget(rect1)

    # Set cell size to 25.5
    for _ in range(5):
        widget.cell_size_control.handle_click(
            widget.cell_size_control.increase_buttons[0].rect.center
        )
    for _ in range(5):
        widget.cell_size_control.handle_click(
            widget.cell_size_control.increase_buttons[1].rect.center
        )

    assert abs(widget.cell_size - 25.5) < 1e-9

    # Resize
    rect2 = pygame.Rect(0, 0, 600, 350)
    widget.set_rect(rect2)

    # Cell size should be preserved
    assert abs(widget.cell_size - 25.5) < 1e-9

def test_controls_widget_render(pygame_init):
    """Test that ControlsWidget renders all controls without crashing."""
    rect = pygame.Rect(0, 0, 500, 400)
    widget = ControlsWidget(rect)
    
    surface = pygame.Surface((800, 600))
    
    # Should render without raising
    widget.render(surface)
    
    # Test rendering in different states
    widget.play_pause_button.playing = True
    widget.render(surface)
    
    # Test with hovered states
    if widget.play_pause_button:
        widget.play_pause_button.hovered = True
    if widget.reset_button:
        widget.reset_button.hovered = True
    if widget.steps_control:
        widget.steps_control.decrease_button.hovered = True
    if widget.timestep_control:
        widget.timestep_control.increase_button.hovered = True
    if widget.temperature_slider:
        widget.temperature_slider.hovered = True
    if widget.cell_size_control:
        for button in widget.cell_size_control.decrease_buttons:
            button.hovered = True
    if widget.load_preset_button:
        widget.load_preset_button.hovered = True
    if widget.menu_button:
        widget.menu_button.hovered = True
    
    widget.render(surface)
