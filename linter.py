"""This module exports the elixirc plugin class."""

import tempfile
import os
import re
from SublimeLinter.lint import Linter, persist


class Elixirc(Linter):

    """
    Provides an interface to elixirc.

    Error formats:

    1) Error type 1:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {filename}:{line}: {message}
    |...<trace lines>...

    2) Error type 2:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {message}
    |    {filename}:{line}              # optional
    |...<trace lines>...

    3) Error type 3:
    |** ({error_name}) {filename}:{line}: {message}
    |...<trace lines>...

    4) Warning type 1:
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

    regex_parts = (
        # Error type 1
        r"== Compilation error on file (?P<e_file1>.+) ==\n"
        r"\*\* \(.+\) .+:(?P<e_line1>\d+): (?P<e_msg1>.+)",

        # Error type 2
        r"== Compilation error on file (?P<e_file2>.+) ==\n"
        r"\*\* \(.+\) (?P<e_msg2>.+)\n"
        r"(?:    (?:.+):(?P<e_line2>\d+))?",

        # Error type 3
        r"\*\* \(.+\) (?P<e_file3>.+):(?P<e_line3>\d+): (?P<e_msg3>.+)",

        # Warning type 1
        r"(?P<w_file1>.+):(?P<w_line1>\d+): warning: (?P<w_msg1>.+)"
    )

    regex = "|".join([r"^(?:%s)" % x for x in regex_parts])

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
        if captures['e_file1'] is not None:
            # Error type 1
            dummy_str = '%s:%s:%s:%s' % (
                captures['e_file1'],
                captures['e_line1'],
                'error',
                captures['e_msg1']
            )
        elif captures['e_file2'] is not None:
            # Error type 2
            dummy_str = "%s:%s:%s:%s" % (
                captures['e_file2'],
                captures['e_line2'] or '1',
                'error',
                captures['e_msg2']
            )
        elif captures['e_file3'] is not None:
            # Error type 3
            dummy_str = "%s:%s:%s:%s" % (
                captures['e_file3'],
                captures['e_line3'],
                'error',
                captures['e_msg3']
            )
        elif captures['w_file1'] is not None:
            # Warning type 1
            dummy_str = "%s:%s:%s:%s" % (
                captures['w_file1'],
                captures['w_line1'],
                'warning',
                captures['w_msg1']
            )
        else:
            dummy_str = ""

        persist.debug("Dummy string: %s" % dummy_str)
        return dummy_str

