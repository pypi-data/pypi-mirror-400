"""Text-based user interface of the application"""

from .          import meta
from .          import config
from .          import bindings
from .          import dialogs
from .editor    import Editor
from .statusbar import Statusbar
from .help      import Help
from .about     import About
from .settings  import Settings
from .palette   import UnsortedCommandsProvider

from textual.app      import App
from textual.app      import ComposeResult
from textual.app      import SystemCommand
from textual.binding  import Binding
from textual.reactive import reactive
from textual.screen   import Screen
from textual.events   import Key

from pathlib         import Path
from collections.abc import Iterable


class TUI(App[str], inherit_bindings=False):
    """Text-based user interface of the application"""

    file: reactive[Path | None] = reactive(None)
    """file currently being edited"""

    encoding: reactive[str] = reactive('')
    """text encoding of the file"""

    newline: reactive[str] = reactive('')
    """line endings of the file"""

    cursor: reactive[tuple[int, int]] = reactive((1, 1))
    """current cursor position in the editor"""

    TITLE     = meta.name
    SUB_TITLE = meta.summary
    BINDINGS  = bindings.application
    COMMANDS  = {UnsortedCommandsProvider}
    CSS_PATH  = 'styles.tcss'

    def compose(self) -> ComposeResult:
        """Composes the application's user interface."""
        yield Editor(id='editor').data_bind(file=TUI.file)
        yield Statusbar(id='statusbar').data_bind(
            file     = TUI.file,
            encoding = TUI.encoding,
            newline  = TUI.newline,
            cursor   = TUI.cursor,
        )

    @property
    def editor(self) -> Editor:
        """Queries the (single) editor widget."""
        return self.app.query_exactly_one('#editor', expect_type=Editor)

    def on_mount(self):
        """Sets theme and key bindings according to configuration."""
        self.theme = config.query(('theme', 'app'))
        self.configure_keys()

    async def on_key(self, event: Key):
        """Works around issue that pressing "^⌫" doesn't trigger its action."""
        if event.key == 'backspace' and event.character == '\x08':
            active_bindings = self.app.screen.active_bindings
            for (node, binding, enabled, _) in active_bindings.values():
                if enabled and binding.key == 'ctrl+backspace':
                    event.prevent_default()
                    await node.run_action(binding.action)

    def on_editor_encoding_detected(self):
        """Propagates detected text encoding to status bar."""
        self.encoding = self.editor.encoding

    def on_editor_newline_detected(self):
        """Propagates detected line endings to status bar."""
        self.newline = self.editor.newline

    def on_editor_file_loaded(self):
        """Propagates new file name to status bar."""
        self.file = self.editor.file

    def on_editor_cursor_moved(self):
        """Propagates new cursor position to status bar."""
        self.cursor = self.editor.cursor_location

    def on_file_name_clicked(self):
        """Runs `editor.save_as` action when file name in footer clicked."""
        self.editor.action_save_as()

    def on_text_encoding_clicked(self):
        """Runs `editor.change_encoding` action when status display clicked."""
        self.editor.action_change_encoding()

    def on_line_endings_clicked(self):
        """Runs `editor.change_newline` action when status display clicked."""
        self.editor.action_change_newline()

    def configure_keys(self):
        """Maps keys as specified in configuration files."""
        keymap = {
            binding.id: config.query(('keys', binding.id))
            for binding in (bindings.application + bindings.editor)
        }
        self.set_keymap(keymap)

    def get_key_display(self, binding: Binding) -> str:
        """Formats how key bindings are displayed throughout the app."""
        return bindings.key_display(binding.key)

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Populates the command palette."""
        commands = (
            (
                'About',
                'Show information about the application.',
                'show_about',
                self.action_show_about,
            ),
            (
                'Help',
                'Show help panel with key bindings.',
                'show_help',
                self.action_show_help,
            ),
            (
                'Settings',
                'Open configuration settings.',
                'open_settings',
                self.action_open_settings,
            ),
            (
                'Save as',
                'Save file under different name.',
                'save_as',
                self.editor.action_save_as,
            ),
            (
                'Trim',
                'Trim trailing white-space.',
                'trim_whitespace',
                self.editor.action_trim_whitespace,
            ),
            (
                'Wrap',
                'Toggle soft-wrapping of long lines.',
                'toggle_wrapping',
                self.editor.action_toggle_wrapping,
            ),
            (
                'Screenshot',
                'Save SVG image of screen in current folder.',
                'screenshot',
                lambda: self.set_timer(0.1, self.action_screenshot),
            ),
            (
                'Quit',
                'Quit the application.',
                'quit',
                self.action_quit,
            ),
        )
        actions_to_bindings = {
            binding.action: binding
            for (_, binding, enabled, _) in screen.active_bindings.values()
            if enabled
        }
        for (title, help, action, callback) in commands:
            if binding := actions_to_bindings.get(action):
                key = self.get_key_display(binding)
                title += f' ({key})'
            yield SystemCommand(title=title, help=help, callback=callback)

    def action_show_help(self) -> None:
        """Shows the Help panel."""
        self.app.push_screen(Help(id='help'))

    def action_show_about(self) -> None:
        """Shows the About panel."""
        self.app.push_screen(About(id='about'))

    def action_open_settings(self) -> None:
        """Opens the Settings dialog."""
        self.app.push_screen(Settings(id='settings'))

    def action_screenshot(self, filename: str = None, path: str = None):
        """Saves a screenshot of the app in the current folder."""
        folder = Path(path) if path else Path('.')
        if filename:
            file = folder / filename
        else:
            stem = f'screenshot_{meta.name}'
            if self.editor.file:
                stem += f'_{self.editor.file.name}'
            folder = Path('.')
            counter = 1
            while True:
                if counter == 1:
                    file = folder / f'{stem}.svg'
                else:
                    file = folder / f'{stem}_{counter}.svg'
                if not file.exists():
                    break
                counter += 1
        svg = self.export_screenshot()
        file.write_text(svg, encoding='UTF-8')

    def action_quit(self):
        """Makes sure we don't quit when there are unsaved changes."""
        if not self.editor.modified:
            self.exit()
        dialog = dialogs.ClickResponse(
            'There are unsaved changes to the file. What to do?',
            buttons  = ('Save',    'Quit',    'Cancel'),
            variants = ('primary', 'warning', 'default'),
        )
        self.push_screen(dialog, self.quit_unsaved_changes)

    def quit_unsaved_changes(self, answer: str):
        """Reacts to how the user wants to deal with unsaved changes."""
        match answer:
            case 'Save':
                self.editor.action_save()
                self.exit()
            case 'Quit':
                self.exit()
