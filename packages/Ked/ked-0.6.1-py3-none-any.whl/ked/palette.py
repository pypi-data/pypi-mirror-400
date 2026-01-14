"""Discovery for the command palette"""

from textual.system_commands import SystemCommandsProvider
from textual.command         import DiscoveryHit
from textual.command         import Hits


class UnsortedCommandsProvider(SystemCommandsProvider):
    """
    Provider for the command palette leaving command in insert order

    The `discover()` method of Textual's built-in `SystemCommandsProvider`
    sorts commands by name. But we want them to appear in the very order in
    which we populate the palette with commands in `app.get_system_commands()`.
    """

    async def discover(self) -> Hits:
        """Yields commands that appear in the command palette."""
        commands = self.app.get_system_commands(self.screen)
        for (name, help_text, callback, discover) in commands:
            if discover:
                yield DiscoveryHit(name, callback, help=help_text)
