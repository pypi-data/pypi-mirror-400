"""Custom widgets of this application"""

from textual.widgets    import Label
from textual.widgets    import RadioButton
from textual.reactive   import reactive
from textual.containers import VerticalScroll
from textual.binding    import Binding
from textual.message    import Message
from textual.events     import Key
from textual.events     import Click
from textual.events     import MouseDown
from textual.events     import Blur
from textual.app        import ComposeResult

from typing import Any


class KeyInput(Label, can_focus=True):
    """Input widget for a key combination"""

    key: reactive[str] = reactive('', layout=True)
    """key (combination) represented by the widget"""

    capture: reactive[bool] = reactive(False, layout=True)
    """flag indicating if waiting for key press to capture"""

    class Changed(Message):
        """Message posted when user assigned new key"""
        def __init__(self, id: str, key: str, old: str):
            self.id  = id
            """id of (this) sender widget"""
            self.key = key
            """new key selected by the user"""
            self.old = old
            """old key stored previously"""
            super().__init__()

    DEFAULT_CSS = """
        KeyInput {
            border:        round $border;
            background:    $surface;
            content-align: center middle;
            &:focus {
                background-tint: $foreground 5%;
            }
        }
    """

    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key

    def render(self) -> str:
        """Renders the key input."""
        if self.capture:
            self.tooltip = 'Press key or key combination. Press Del to unset.'
            return 'Press key…'
        else:
            self.tooltip  = 'Click to change.'
            dummy_binding = Binding(self.key, '', '')
            key_display   = self.app.get_key_display(dummy_binding)
            return key_display

    async def on_key(self, event: Key) -> None:
        """Captures key presses."""
        if not self.capture:
            if event.key == 'enter':
                self.capture = True
                event.stop()
            # Bubble up any other key.
        else:
            match event.key:
                case 'tab' | 'shift+tab':
                    # Bubble up.
                    return
                case 'enter' | 'escape':
                    # Stop capture.
                    pass
                case 'backspace' | 'delete':
                    # Deactivate key binding.
                    old_key  = self.key
                    self.key = ''
                    self.post_message(self.Changed(self.id, self.key, old_key))
                case _:
                    # Assign new key.
                    old_key  = self.key
                    self.key = event.key
                    self.post_message(self.Changed(self.id, self.key, old_key))
            self.capture = False
            event.stop()

    def on_blur(self, _event: Blur):
        """Stops key capture when losing focus."""
        self.capture = False

    async def on_mouse_up(self, _event: MouseDown):
        """Starts key capture when user clicks the widget."""
        if self.has_focus:
            self.capture = True


class Options(VerticalScroll, can_focus=True, can_focus_children=False):
    """
    Widget where user can pick one of several options

    Similar to Textual's `RadioSet`, but changes the selected option when
    the users presses Up or Down (not just when pressing Space on the focused
    radio button).
    """

    class Changed(Message):
        """Message posted when the selected option changed"""
        def __init__(self, option: str):
            self.option  = option
            """newly selected option"""
            super().__init__()

    DEFAULT_CSS = """
        Options {
            border:     round $border;
            background: $surface;
            height:     auto;
            width:      1fr;
            padding:    0;
            &:focus {
                background-tint: $foreground 5%;
            }
            .option {
                border:     none;
                background: transparent;
                margin:     1 0;
            }
            .option .toggle--button {
                background: transparent;
            }
            .option.-on {
                .toggle--button {
                    color: $primary;
                }
                .toggle--label {
                    text-style: bold;
                }
            }
        }
    """

    BINDINGS = (
        ('down', 'select_next'),
        ('up',   'select_previous'),
    )

    def __init__(self,
        options:  list[str],
        initial:  str,
        tooltips: list[str] = None,
        **kwargs: Any,
    ) -> None:
        self.options  = options
        if initial not in options:
            raise ValueError(
                'The "selected" option must be one of the "options".'
            )
        self.selected = initial
        if tooltips is None:
            self.tooltips = [''] * len(options)
        else:
            if len(tooltips) != len(options):
                raise ValueError(
                    'Pass as many "tooltips" as there are "options".'
                )
            self.tooltips = tooltips
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Composes the list of options."""
        for (option, tooltip) in zip(self.options, self.tooltips, strict=True):
            yield RadioButton(option, tooltip=tooltip, classes='option')

    def on_mount(self):
        """Selects the initial option when widget is created."""
        self.select(self.selected)

    def select(self, option: str):
        """Selects one `option`, deselects all others."""
        with self.prevent(RadioButton.Changed):
            for button in self.query(RadioButton):
                button.value = (button.label == option)
        self.selected = option
        self.post_message(self.Changed(option))

    def on_click(self, _event: Click):
        """Focuses the widget when clicked."""
        self.focus()

    def on_radio_button_changed(self, event: RadioButton.Changed):
        """Responds to one of the radio buttons being clicked."""
        self.select(event.radio_button.label)

    def action_select_next(self):
        """Selects the next option."""
        index = (self.options.index(self.selected) + 1) % len(self.options)
        self.select(self.options[index])

    def action_select_previous(self):
        """Selects the previous option."""
        index = (self.options.index(self.selected) - 1) % len(self.options)
        self.select(self.options[index])


class Spacer(Label):
    """Blank widget that stretches to fill space"""

    DEFAULT_CSS = """
        Spacer {
            width: 1fr;
        }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, expand=True)
