"""This module exports the elixirc plugin class."""

import tempfile
import os
from SublimeLinter.lint import Linter


class Elixirc(Linter):

    """Provides an interface to elixirc."""

    syntax = ("elixir")

    executable = "elixirc"
    tempfile_suffix = "-"

    regex = (
        r"(?:\*+\s\(.+\) )?(?P<filename>.+):(?P<line>\d+):"
        r"(?:(?P<warning>\swarning:\s)|(?P<error>\s))"
        r"(?P<message>.+)"
    )

    defaults = {
        "include_dirs": [],
        "pa": []
    }

    def cmd(self):
        """Override to accept options `include_dirs` and `pa`."""
        tmpdir = os.path.join(tempfile.gettempdir(), 'SublimeLinter3')
        command = [
            self.executable_path,
            '--warnings-as-errors',
            '--ignore-module-conflict',
            '-o', tmpdir
        ]

        settings = self.get_view_settings()
        dirs = settings.get('include_dirs', [])
        paths = settings.get('pa', [])

        for p in paths:
            command.extend(["-pa", p])

        for d in dirs:
            command.extend(["-r", "%s/**/*.ex" % d])

        return command

    def split_match(self, match):
        """
        Return the components of the match.

        We override this because unrelated library files can throw errors,
        and we only want errors from the linted file.

        """
        if match:
            # The linter seems to always change its working
            # dir to that of the linted given file, so the
            # reported error will contain a basename only.
            if match.group('filename') != os.path.basename(self.filename):
                match = None

        return super().split_match(match)
