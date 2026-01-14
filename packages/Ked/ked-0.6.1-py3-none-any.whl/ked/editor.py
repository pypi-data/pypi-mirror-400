"""Editor widget central to the application"""

from . import config
from . import bindings
from . import dialogs

from textual.widgets           import TextArea
from textual.widgets.text_area import Edit
from textual.reactive          import reactive
from textual.message           import Message
from textual.events            import Key
from textual.events            import MouseDown

import os
import tokenize
from functools import partial
from pathlib   import Path


class Editor(TextArea, inherit_bindings=False):
    """Widget for editing a file"""

    file: reactive[Path | None] = reactive(None)
    """file currently being edited"""

    encoding: str = ''
    """detected text encoding of the file"""

    newline: str = ''
    """character sequence marking line endings in the file"""

    saved_as: list[list[Edit]] = None
    """undo stack when file was last saved, empty when loaded"""

    class FileLoaded(Message):
        """Message posted when a file was loaded"""

    class EncodingDetected(Message):
        """Message posted when text encoding was detected"""

    class NewlineDetected(Message):
        """Message posted when line endings were detected"""

    class CursorMoved(Message):
        """Message posted when cursor was moved"""

    BINDINGS = bindings.editor

    DEFAULT_CSS = """
        Editor {
            border:  round $border;
            padding: 0;
        }
    """

    def __init__(self, id: str = 'editor'):
        super().__init__(
            id                = id,
            soft_wrap         = False,
            tab_behavior      = 'indent',
            show_line_numbers = False,
            max_checkpoints   = 1000,
            theme             = 'css',
        )

    def on_mount(self):
        """Called when widget is ready to process messages."""
        self.theme = config.query(('theme', 'syntax'))

    def watch_file(self, file: Path | None):
        """Loads file whenever the reactive `file` attribute changes."""

        if file is None:
            return

        language = infer_language(file)
        if language in self.available_languages:
            self.language = language
        else:
            self.language = None

        encoding = detect_encoding(file)
        self.encoding = encoding
        self.post_message(self.EncodingDetected())

        with file.open(encoding=self.encoding) as stream:
            self.load_text(stream.read())
            newlines = stream.newlines

        mixed_newlines = False
        if newlines is None:
            newlines = os.linesep
        elif isinstance(newlines, str):
            pass
        elif isinstance(newlines, tuple):
            mixed_newlines = True
            newlines = os.linesep
        else:
            raise TypeError(f'Unexpected type for "newlines": {newlines}')
        self.newline = newlines
        self.post_message(self.NewlineDetected())

        self.file = file
        self.post_message(self.FileLoaded())
        self.saved_as = self.history.undo_stack.copy()
        self.post_message(self.CursorMoved())

        if mixed_newlines:
            dialog = dialogs.MessageBox(
                'This file contains mixed line endings. The default line '
                'endings for this operating system will be used once you '
                'change and save the file. Or click on the line endings '
                'indicator in the status bar below to change them.',
                title='Warning',
            )
            self.app.push_screen(dialog)

    def on_key(self, _event: Key):
        """Posts message that cursor moved on every key press."""
        self.post_message(self.CursorMoved())

    def on_mouse_up(self, _event: MouseDown):
        """Posts message that cursor moved when a mouse button was released."""
        self.post_message(self.CursorMoved())

    def on_text_area_changed(self):
        """Makes sure the "Save" action is correctly grayed out or not."""
        self.refresh_bindings()

    def action_save(self):
        """Saves the file to disk."""
        if not self.file:
            return
        self.file.write_text(
            self.text, encoding=self.encoding, newline=self.newline
        )
        self.saved_as = self.history.undo_stack.copy()
        self.refresh_bindings()

    def action_save_as(self):
        """Asks the user for a new name to save the file as."""
        if not self.file:
            return
        dialog = dialogs.TextInput('Save file as:', self.file.name)
        self.app.push_screen(dialog, self.save_as_entered)

    def save_as_entered(self, answer: str):
        """Called when the user entered a new file name to save as."""
        if not answer:
            return
        path = Path(answer)
        if path.is_absolute():
            file = path
        else:
            file = self.file.parent / path
        if file.exists() and file != self.file:
            if file.is_dir():
                self.app.push_screen(
                    dialogs.MessageBox(
                        'Cannot save file under that name as a folder with '
                        'the same name exists.',
                        title='Error',
                    )
                )
            else:
                dialog = dialogs.ClickResponse(
                    'A file with that name already exists. Overwrite it?'
                )
                callback = partial(self.save_as_overwrite, file)
                self.app.push_screen(dialog, callback)
        else:
            self.save_as_execute(file)

    def save_as_overwrite(self, file: Path, answer: str):
        """Called when the user answered whether to overwrite existing file."""
        if answer == 'Yes':
            self.save_as_execute(file)

    def save_as_execute(self, file: Path):
        """Saves the currently edited file as the new `file`."""
        self.set_reactive(Editor.file, file)
        self.post_message(self.FileLoaded())
        self.action_save()

    def action_trim_whitespace(self):
        """Trims trailing white-space characters."""
        changed = False

        trims = 0
        for n in range(self.document.line_count):
            line = self.document.get_line(n)
            trimmed = line.rstrip(' \t')
            if trimmed != line:
                self.delete(start=(n, len(trimmed)), end=(n, len(line)))
                trims += 1
        if trims > 0:
            noun = 'line' if trims == 1 else 'lines'
            self.notify(f'Trimmed trailing white-space on {trims} {noun}.')
            changed = True

        n = self.document.line_count - 1
        last_line = self.document.get_line(n)
        if last_line != '':
            self.insert('\n', location=(n, len(last_line)))
            self.notify('Appended a blank line.')
            changed = True

        n = self.document.line_count - 2
        m = n
        while self.document.get_line(m) == '' and m >= 0:
            m -= 1
        if (m != n):
            self.delete(start=(m+1, 0), end=(n+1, 0))
            noun = 'line' if n - m == 1 else 'lines'
            self.notify(f'Deleted {n - m} trailing blank {noun}.')
            changed = True

        if not changed:
            self.notify('No trailing white-space to trim.')
        else:
            self.move_cursor(self.cursor_location)
            self.post_message(self.CursorMoved())
            self.refresh_bindings()

    def action_toggle_wrapping(self):
        """Toggles soft-wrapping of lines."""
        self.soft_wrap = not self.soft_wrap

    def action_change_encoding(self):
        """Lets the user change the text encoding of the file."""
        options  = ('UTF-8', 'UTF-8-BOM')
        tooltips = (
            'UTF-8 Unicode encoding',
            'UTF-8 encoding with byte-order mark',
        )
        match self.encoding:
            case 'utf-8':
                initial = options[0]
            case 'utf-8-sig':
                initial = options[1]
            case _:
                raise ValueError(f'Unexpected encoding: {self.encoding}')
        dialog = dialogs.SelectOption(
            options, initial, tooltips,
            accept_text    = 'Save',
            accept_tooltip = 'Save file to disk with new encoding.',
            accept_initial = False,
        )
        self.app.push_screen(dialog, self.change_encoding)

    def change_encoding(self, encoding: str):
        """Changes the text encoding of the file."""
        match encoding:
            case 'UTF-8':
                new_encoding = 'utf-8'
            case 'UTF-8-BOM':
                new_encoding = 'utf-8-sig'
            case None:
                return
            case _:
                raise ValueError(f'Unexpected encoding: {encoding}')
        self.encoding = new_encoding
        self.post_message(self.EncodingDetected())
        self.action_save()
        self.notify(f'Saved file with text encoding {encoding}.')

    def action_change_newline(self):
        """Lets the user change the line endings of the file."""
        options  = ('LF', 'CRLF')
        tooltips = (
            'Unix-like line endings (Linux/macOS)',
            'Windows-like line endings',
        )
        match self.newline:
            case '\n':
                initial = options[0]
            case '\r\n':
                initial = options[1]
            case _:
                raise ValueError(f'Unexpected line endings: {self.newline}')
        dialog = dialogs.SelectOption(
            options, initial, tooltips,
            accept_text    = 'Save',
            accept_tooltip = 'Save file to disk with new line endings.',
            accept_initial = False,
        )
        self.app.push_screen(dialog, self.change_newline)

    def change_newline(self, newline: str):
        """Changes the line endings of the file."""
        match newline:
            case 'LF':
                new_newline = '\n'
            case 'CRLF':
                new_newline = '\r\n'
            case None:
                return
            case _:
                raise ValueError(f'Unexpected line endings: {newline}')
        self.newline = new_newline
        self.post_message(self.NewlineDetected())
        self.action_save()
        self.notify(f'Saved file with line endings {newline}.')

    def action_cursor_file_start(self):
        """Moves cursor to start of file."""
        self.move_cursor((0, 0))
        self.post_message(self.CursorMoved())

    def action_cursor_file_end(self):
        """Moves cursor to end of file."""
        y = self.document.line_count - 1
        x = len(self.document.get_line(y))
        self.move_cursor((y, x))
        self.post_message(self.CursorMoved())

    def check_action(self, action: str, _: tuple[object, ...]) -> bool | None:
        """Marks actions as currently available or not."""
        if action == 'save' and self.file and not self.modified:
            return None
        return True

    @property
    def modified(self):
        """Indicates whether the file has been modified since it was saved."""
        return (self.history.undo_stack != self.saved_as)


def detect_encoding(file: Path) -> str:
    """
    Detects the text encoding of the given file.

    Uses the `tokenize` module from the Python standard library under the hood,
    and is thus limited to the same few encodings.
    """
    with file.open('rb') as stream:
        (encoding, _line) = tokenize.detect_encoding(stream.readline)
    return encoding


def infer_language(file: Path) -> str:
    """Infers the syntax-highlighting language from the file extension."""
    match file.stem:
        case '.profile':
            return 'bash'
        case '.bashrc' | '.bash_logout':
            return 'bash'
        case '.zshrc':
            return 'bash'
    match file.suffix:
        case '.md':
            return 'markdown'
        case '.json':
            return 'json'
        case '.yaml' | '.yml':
            return 'yaml'
        case '.toml':
            return 'toml'
        case '.xml':
            return 'xml'
        case '.html' | '.htm':
            return 'html'
        case '.css':
            return 'css'
        case '.js':
            return 'javascript'
        case '.sh' | '.bash' | '.zsh' | '.fish':
            return 'bash'
        case '.py' | '.pyw':
            return 'python'
        case '.rs':
            return 'rust'
        case '.sql':
            return 'sql'
        case '.go':
            return 'go'
        case '.java':
            return 'java'
        case '.kt' | '.kts':
            return 'kotlin'
    return ''
