"""This module exports the elixirc plugin class."""

import tempfile
import os
from SublimeLinter.lint import Linter


class Elixirc(Linter):

    """Provides an interface to elixirc."""

    syntax = ("elixir")

    executable = "elixirc"
    tempfile_suffix = "ex"

    # Must skip lines in the stack trace such as
    #
    #     |    (stdlib) lists.erl:1336: :lists.foreach/2
    #
    # because the line number leads to array index out of bound exception.
    #
    # Since they all start with 4 spaces, just ignore all lines starting with a space.
    regex = (
        r"^[^ ].+:(?P<line>\d+):"
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
            command.extend(["-I", d])

        return command
