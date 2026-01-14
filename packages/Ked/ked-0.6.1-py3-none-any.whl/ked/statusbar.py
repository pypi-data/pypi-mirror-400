"""Custom footer showing key bindings and editor status"""

from textual.widgets         import Footer
from textual.widgets._footer import FooterKey
from textual.widgets         import Label
from textual.containers      import Horizontal
from textual.reactive        import reactive
from textual.message         import Message
from textual.app             import ComposeResult

from pathlib import Path


class Statusbar(Footer):
    """Footer showing key bindings and status of edited file"""

    file: reactive[Path | None] = reactive(None)
    """file currently being edited"""

    encoding: reactive[str] = reactive('')
    """text encoding of the file"""

    newline: reactive[str] = reactive('')
    """line endings of the file"""

    cursor: reactive[tuple[int, int]] = reactive((1, 1))
    """current cursor position in the editor"""

    DEFAULT_CSS = """
        $footer-key-foreground: $primary;
        #key-bindings {
            align-horizontal: left;
            FooterKey {
                border-right:  solid $surface;
                padding-left:  1;
                padding-right: 1;
            }
            FooterKey:last-child {
                border-right: none;
            }
        }
        #edit-status {
            align-horizontal: right;
            Label {
                border-right:  solid $surface;
                padding-left:  1;
                padding-right: 1;
            }
            Label:last-child {
                border-right:  none;
            }
        }
    """

    def compose(self) -> ComposeResult:
        """Composes the status bar."""

        with Horizontal(id='key-bindings'):
            active_bindings = self.screen.active_bindings
            app_bindings    = {}
            other_bindings  = {}
            for (key, (node, binding, enabled, _)) in active_bindings.items():
                if not binding.show:
                    continue
                if node is self.app:
                    app_bindings[key] = (binding, enabled)
                else:
                    other_bindings[key] = (binding, enabled)
            sorted_bindings = app_bindings | other_bindings
            for (key, (binding, enabled)) in sorted_bindings.items():
                yield FooterKey(
                    key,
                    self.app.get_key_display(binding),
                    binding.description,
                    binding.action,
                    disabled=not enabled,
                    tooltip=binding.tooltip,
                )

        with Horizontal(id='edit-status'):
            yield CursorPosition(id='cursor-position').data_bind(
                Statusbar.cursor
            )
            yield LineEndings(id='line-endings').data_bind(Statusbar.newline)
            yield TextEncoding(id='text-encoding').data_bind(
                Statusbar.encoding
            )
            yield FileName(id='file-name').data_bind(Statusbar.file)


class FileName(Label):
    """Displays the file name."""

    file: reactive[Path | None] = reactive(None, layout=True)
    """file currently being edited"""

    class Clicked(Message):
        """Message posted when the widget was clicked"""

    def render(self) -> str:
        """Renders the status display of the file name."""
        if self.file is None:
            self.tooltip = ''
            return ''
        self.tooltip = str(self.file)
        return self.file.name

    def on_click(self):
        """Posts message when clicked so ancestor widgets can react."""
        self.post_message(self.Clicked())


class TextEncoding(Label):
    """Displays the text encoding of the file."""

    encoding: reactive[str] = reactive('', layout=True)
    """text encoding of the file"""

    class Clicked(Message):
        """Message posted when the widget was clicked"""

    def render(self) -> str:
        """Renders the status display of the text encoding."""
        match self.encoding:
            case 'utf-8':
                display = 'UTF-8'
                tooltip = 'Text encoding is UTF-8 Unicode.'
            case 'utf-8-sig':
                display = 'UTF-8-BOM'
                tooltip = 'Text encoding is UTF-8 with a byte-order mark.'
            case _:
                display = self.encoding
                tooltip = ''
        if tooltip:
            tooltip += '\n\n'
        tooltip += '(Click to change.)'
        self.tooltip = tooltip
        return display

    def on_click(self):
        """Posts message when clicked so ancestor widgets can react."""
        # For reasons I don't fully understand, calling
        # `self.app.editor.action_change_encoding()` doesn't really work here.
        # Nor does awaiting `run_action()` of either this widget, the app, or
        # editor widget. They do bring up the dialog, but then the callback
        # function `editor.change_encoding()` never gets called. It may be
        # because we should follow "attributes down, messages up", but not
        # sure. See: https://textual.textualize.io/guide/widgets/#data-flow
        self.post_message(self.Clicked())


class LineEndings(Label):
    """Displays the line endings of the file."""

    newline: reactive[str] = reactive('', layout=True)
    """line endings of the file"""

    class Clicked(Message):
        """Message posted when the widget was clicked"""

    def render(self) -> str:
        """Renders the status display of the line endings."""
        match self.newline:
            case '\r\n':
                display = 'CRLF'
                tooltip = (
                    'Windows-like line endings:\n'
                    'carriage-return plus line-feed'
                )
            case '\n':
                display = 'LF'
                tooltip = (
                    'Unix-like line endings:\n'
                    'a single line-feed character'
                )
            case _:
                display = self.newline.replace('\r', 'CR').replace('\n', 'LF')
                tooltip = 'Unrecognized line endings.'
        if tooltip:
            tooltip += '\n\n'
        tooltip += '(Click to change.)'
        self.tooltip = tooltip
        return display

    def on_click(self):
        """Posts message when clicked so ancestor widgets can react."""
        self.post_message(self.Clicked())


class CursorPosition(Label):
    """Displays the current cursor position in the file."""

    cursor: reactive[tuple[int, int]] = reactive((1, 1), layout=True)
    """current cursor position in the editor"""

    def render(self) -> str:
        """Renders the status display of the cursor position."""
        (line, column) = self.cursor
        line += 1
        column += 1
        self.tooltip = f'The cursor is on line {line} in column {column}.'
        return f'{line},{column}'
