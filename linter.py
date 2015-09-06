"""This module exports the elixirc plugin class."""

import tempfile
import os
import re
from SublimeLinter.lint import Linter, persist


class Elixirc(Linter):

    """
    Provides an interface to elixirc.

    Error formats:

    1) Default errors:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {filename}:{line}: {message}
    |...<trace lines>...

    2) Macro errors:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {message}
    |...<trace lines>...

    3) Warnings:
    |{filename}:{line}: warning: {message}


    In order to cover all cases we need a complex regex.
    Since a single regex does *not* allow to have several
    groups with the same name, we introduce custom group
    names.
    The group names are then transformed back to the ones
    expected by the Linter. This is done by overriding
    the split_match method.

    """

    syntax = ("elixir")
    tempfile_suffix = "-"

    regex = (
        r"^(?:== Compilation error on file (?P<file1>.+) ==\n"
        r"(?:\*+\s\(.+\))?(?:\s[\S].*:(?P<line1>\d+): )?)(?P<msg1>.+)"
        r"|"
        r"(?:(?P<file2>.+):(?P<line2>\d+): warning: (?P<msg2>.+))"
    )

    dummy_regex = re.compile(
        r"(?P<filename>.+):"
        r"(?P<line>\d+):"
        r"(?:(?P<error>error)|(?P<warning>warning)):"
        r"(?P<message>.+)",
        re.UNICODE
    )

    defaults = {
        "include_dirs": [],
        "pa": [],
        "mix": False
    }

    multiline = True
    executable = "elixir"

    def cmd(self):
        """Convert the linter options to command arguments."""
        settings = self.get_view_settings()
        require = settings.get('require', [])
        paths = settings.get('pa', [])
        mix = settings.get('mix_project', None)
        command = [self.executable_path]

        if mix:
            command.extend(self.mix_args())
        else:
            command.extend(self.regular_args(paths, require))

        return command

    def regular_args(self, paths, require):
        """
        Build the argument list when mix is not configured.

        * set the compiler outpur into a tmpdir
        * from the `require` and `pa` config values, build
          the list of `-pr` and `-pa` command arguments

        """
        args = [
            '+elixirc',
            '-o', os.path.join(tempfile.gettempdir(), 'SublimeLinter3'),
            '--warnings-as-errors',
            '--ignore-module-conflict'
        ]

        for p in paths:
            args.extend(["-pa", p])

        for i in require:
            if os.path.isdir(i):
                args.extend(["-pr", "%s/**/*.ex" % i])
            else:
                args.extend(["-pr", i])

        args.extend([self.filename])

        return args

    def mix_args(self):
        """With mix, we just need to invoke its compile task."""
        args = [
            '-S', 'mix', 'compile',
            '--warnings-as-errors',
            '--ignore-module-conflict'
        ]

        return args

    def split_match(self, match):
        """
        Pre-process the matchObject before passing it upstream.

        Several reasons for this:
          * unrelated library files can throw errors, and
            we only want errors from the linted file.
          * our regex contains more than just the basic
            capture groups (filename, line, message, etc.)
            but we still need to pass a match object that
            contains the above groups upstream.
          * Line is not reported for some macro errors

        """
        dummy_match = None

        if match:
            captures = match.groupdict()
            dummy_string = self.build_dummy_string(captures)
            dummy_match = re.match(self.dummy_regex, dummy_string)

        if dummy_match:
            filename = os.path.join(self.chdir, dummy_match.group('filename'))

            if self.filename != filename:
                persist.debug(
                    "Ignore error from %s (linted file: %s)" %
                    (filename, self.filename)
                )

                dummy_match = None

        return super().split_match(dummy_match)

    def build_dummy_string(self, captures):
        """
        Build a string to be matched against self.dummy_regex.

        It is used to ensure that a matchObject with the
        appropriate group names is passed upstream.

        Returns a string with the following format:
        {filename}:{line}:{error_type}:{message}

        """
        if captures['file1'] is not None:
            dummy_str = '%s:%s:%s:%s' % (
                captures['file1'],
                captures['line1'] or 0,
                'error',
                captures['msg1']
            )
        elif captures['file2'] is not None:
            dummy_str = "%s:%s:%s:%s" % (
                captures['file2'],
                captures['line2'] or 0,
                'warning',
                captures['msg2']
            )
        else:
            dummy_str = ""

        persist.debug("Dummy string: %s" % self.filename)
        return dummy_str
