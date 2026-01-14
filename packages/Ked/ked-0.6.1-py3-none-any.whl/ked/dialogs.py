"""Pop-up dialogs used throughout the app"""

from .        import bindings
from .widgets import Options
from .widgets import Spacer

from textual.screen     import ModalScreen
from textual.widgets    import Button
from textual.widgets    import Label
from textual.widgets    import Input
from textual.containers import VerticalGroup
from textual.containers import HorizontalGroup
from textual.containers import Center
from textual.app        import ComposeResult

from collections.abc import Sequence
from typing          import Any


class MessageBox(ModalScreen[None]):
    """
    Pop-up message to be acknowledged by the user

    Pass in the `message` to display, a possible `title` for the box (for
    example "Error"), and the text to display on the accept button ("Okay"
    being the default).

    Create the message box by passing an instance of this class to
    `app.push_screen()`. There is no result to process, the user will have to
    dismiss the message box eventually, by either pressing the button or the
    Esc key.
    """

    BINDINGS = bindings.dialog

    DEFAULT_CSS = """
        MessageBox {
            align-horizontal: center;
            align-vertical:   middle;
            background:       black 20%;
            #frame {
                width:      auto;
                max-width:  60;
                border:     round $border;
                background: $background;
                padding:    1 2;
                align:      center middle;
            }
            #message-row {
            }
            #message {
            }
            #button-row {
                margin-top: 2;
            }
            #button {
                min-width: 12;
            }
        }
    """

    def __init__(self,
        message:  str,
        title:    str = '',
        button:   str = 'Okay',
        **kwargs: Any,
    ):
        self.message = message
        self.title_  = title
        self.button  = button
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Composes the message box."""
        with VerticalGroup(id='frame') as frame:
            if self.title_:
                frame.border_title = self.title_
            with Center(id='message-row'):
                yield Label(self.message, id='message', shrink=True)
            with Center(id='button-row'):
                yield Button(self.button, id='button', action='screen.dismiss')


class ClickResponse(ModalScreen[str]):
    """
    Dialog asking user to click a button as a response

    Pass in a `prompt` with a message or question to the user. Define the
    `buttons` via the text to display on them, the default being "Yes"
    and "No". Choose style `variants` for the buttons (like "primary",
    "warning", "error", or "default").

    There can be more than two buttons if you override the defaults. Create the
    dialog by passing the instance of this class to `app.push_screen()` along
    with a callback function. The latter will receive the text of the button
    that the user clicked as a `result` parameter, or `None` if they dismissed
    the dialog by pressing Esc.
    """

    BINDINGS = bindings.dialog

    DEFAULT_CSS = """
        ClickResponse {
            align-horizontal: center;
            align-vertical:   middle;
            background:       black 20%;
            #frame {
                width:      auto;
                min-width:  60;
                border:     round $border;
                padding:    1 2;
                background: $background;
            }
            #prompt-row {
                width: 100%;
            }
            #prompt {
            }
            #button-row {
                width:      100%;
                margin-top: 2;
            }
            .button {
                min-width: 12;
            }
        }
    """

    def __init__(self,
        prompt:   str,
        buttons:  Sequence[str] = ('Yes',     'No'),
        variants: Sequence[str] = ('primary', 'default'),
        **kwargs: Any,
    ):
        self.prompt   = prompt
        self.buttons  = buttons
        self.variants = variants
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Composes the dialog."""
        with VerticalGroup(id='frame'):
            with HorizontalGroup(id='prompt-row'):
                yield Label(self.prompt, id='prompt', shrink=True)
            first = True
            with HorizontalGroup(id='button-row'):
                for (button, variant) in zip(
                    self.buttons, self.variants, strict=True
                ):
                    if first:
                        first = False
                    else:
                        yield Spacer()
                    yield Button(
                        label=button, variant=variant,
                        id=button, classes='button',
                    )

    def on_button_pressed(self, event: Button.Pressed):
        """Reports to the caller which button the user pressed."""
        self.dismiss(event.button.id)


class TextInput(ModalScreen[str]):
    """
    Dialog asking the user to enter text

    Pass in the `label_text` describing what you ask the user to enter text
    for, and an `initial_value` for that text.

    By default, an "Okay" button will be shown in the "primary" variant that
    the user can press to accept their own input and proceed, as well as a
    "Cancel" button they can press to abort. Pressing the Esc key has the same
    effect.

    Create the input dialog by passing an instance of this class to
    `app.push_screen()` along with a callback function. The latter will be
    called with the value of the text input as its `result` parameter after the
    accept button was pressed.
    """

    BINDINGS = bindings.dialog

    DEFAULT_CSS = """
        TextInput {
            align-horizontal: center;
            align-vertical:   middle;
            background:       black 20%;
            #frame {
                width:      60;
                border:     round $border;
                background: $background;
                padding:    1 2;
            }
            #input-row {
                align-horizontal: left;
            }
            #label {
                height:                 100%;
                content-align-vertical: middle;
            }
            #input {
                width:       1fr;
                margin-left: 1;
                border:      round $border;
            }
            #button-row {
                margin-top: 2;
            }
            .button {
                min-width: 12;
            }
            #accept {
            }
            #cancel {
            }
        }
    """

    def __init__(self,
        label_text:     str,
        initial_value:  str = '',
        accept_text:    str = 'Okay',
        accept_variant: str = 'primary',
        cancel_text:    str = 'Cancel',
        cancel_variant: str = 'default',
        **kwargs:       Any,
    ):
        self.label_text     = label_text
        self.initial_value  = initial_value
        self.accept_text    = accept_text
        self.accept_variant = accept_variant
        self.cancel_text    = cancel_text
        self.cancel_variant = cancel_variant
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Composes the dialog."""
        with VerticalGroup(id='frame'):
            with HorizontalGroup(id='input-row'):
                yield Label(self.label_text, id='label')
                yield Input(
                    self.initial_value, select_on_focus=False, id='input'
                )
            with HorizontalGroup(id='button-row'):
                yield Button(
                    label   = self.accept_text,
                    variant = self.accept_variant,
                    action  = 'screen.accept',
                    classes = 'button',
                    id      = 'accept',
                )
                yield Spacer()
                yield Button(
                    label   = self.cancel_text,
                    variant = self.cancel_variant,
                    action  = 'screen.dismiss',
                    classes = 'button',
                    id      = 'cancel',
                )

    def on_input_submitted(self):
        """Changes focus to first button when user entered a value."""
        self.query('Button').focus()

    def action_accept(self):
        """Reports the value of the input widget to the caller."""
        input = self.query_exactly_one('#input', expect_type=Input)
        self.dismiss(input.value)


class SelectOption(ModalScreen[str]):
    """
    Dialog letting user select one option out of several

    Pass in the `options` as a tuple of strings, the `initial` option selected
    at the start, and optional tooltips to be show when hovering over the
    options with the mouse.

    By default, an "Okay" button will be shown in the "primary" variant that
    the user can press to accept their own choice and proceed, as well as a
    "Cancel" button they can press to abort. Pressing the Esc key has the same
    effect.

    Create the input dialog by passing an instance of this class to
    `app.push_screen()` along with a callback function. The latter will be
    called with the value of the selected option as its `result` parameter
    after the accept button was pressed.
    """

    BINDINGS = bindings.dialog

    DEFAULT_CSS = """
        SelectOption {
            align-horizontal: center;
            align-vertical:   middle;
            background:       black 20%;
            #frame {
                width:   36;
                border:  round $border;
                padding: 1 2;
            }
            #options {
                border: round $border;
            }
            .option {
            }
            #button-row {
                margin-top: 2;
            }
            .button {
                min-width: 12;
            }
            #accept {
            }
            #cancel {
            }
        }
    """

    def __init__(self,
        options:        tuple[str, ...],
        initial:        str,
        tooltips:       tuple[str, ...] = None,
        accept_text:    str             = 'Okay',
        accept_variant: str             = 'primary',
        accept_tooltip: str             = '',
        cancel_text:    str             = 'Cancel',
        cancel_variant: str             = 'default',
        cancel_tooltip: str             = '',
        accept_initial: bool            = True,
        **kwargs:       Any,
    ):
        self.options        = options
        self.initial        = initial
        self.tooltips       = tooltips
        self.accept_text    = accept_text
        self.accept_tooltip = accept_tooltip
        self.accept_variant = accept_variant
        self.cancel_text    = cancel_text
        self.cancel_tooltip = cancel_tooltip
        self.cancel_variant = cancel_variant
        self.accept_initial = accept_initial
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Composes the dialog."""
        with VerticalGroup(id='frame'):
            yield Options(
                options  = self.options,
                initial  = self.initial,
                tooltips = self.tooltips,
                id       = 'options',
            )
            with HorizontalGroup(id='button-row'):
                yield Button(
                    label   = self.accept_text,
                    tooltip = self.accept_tooltip or None,
                    variant = self.accept_variant,
                    action  = 'screen.accept',
                    classes = 'button',
                    id      = 'accept',
                )
                yield Spacer()
                yield Button(
                    label   = self.cancel_text,
                    tooltip = self.cancel_tooltip or None,
                    variant = self.cancel_variant,
                    action  = 'screen.dismiss',
                    classes = 'button',
                    id      = 'cancel',
                )

    def on_options_changed(self, message: Options.Changed):
        """Enables or disables accept button when selected option changed."""
        accept = self.query_exactly_one('#accept', expect_type=Button)
        accept.disabled = (message.option == self.initial)

    def action_accept(self):
        """Reports the selected option to the caller."""
        options = self.query_exactly_one('#options', expect_type=Options)
        self.dismiss(options.selected)
