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
    |    ...

    2) Error type 2:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {message}
    |    {filename}:{line}
    |    ...

    3.1) Error type 3.1 -- lib files first in trace:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {message}
    |    (libname) {other_filename}:{line}
    |    ...
    |    {filename}:{line}
    |    ...

    3.2) Error type 3.2 -- function names first in trace:
    |== Compilation error on file {filename} ==
    |** ({error_name}) {message}
    |    {function_name}()
    |    ...
    |    {filename}:{line}
    |    ...

    4) Error type 5:
    |** ({error_name}) {filename}:{line}: {message}
    |...<trace lines>...

    Warning formats:

    1) Warning type 1:
    |{filename}:{line}: warning: {message}


    In order to cover all cases we need a complex regex.
    Since a single regex does *not* allow to have several
    groups with the same name, we introduce custom group
    names.
    The group names are then transformed back to the ones
    expected by the Linter. This is done by overriding
    the split_match method.


    Examples (mix project of a Phoenix app):
    1)
    |== Compilation error on file web/router.ex ==
    |** (CompileError) web/router.ex:19: undefined function get/2
    |    ...

    2) #todo

    3) insert a "resources :users, UserController" line in router.ex
    |== Compilation error on file web/router.ex ==
    |** (FunctionClauseError) no function clause matching in Phoenix.Router.Resource.build/3
    |    (phoenix) lib/phoenix/router/resource.ex:30: Phoenix.Router.Resource.build(:users, UserController, [])
    |    web/router.ex:20: (module)
    |    ...

    4) Modify line 2 to "use MyApp.Web, :dasdsadasda"
    |== Compilation error on file web/controllers/page_controller.ex ==
    |** (UndefinedFunctionError) undefined function: MyApp.Web.controllers/0
    |    MyApp.Web.controllers()
    |    expanding macro: MyApp.Web.__using__/1
    |    web/controllers/page_controller.ex:2: MyApp.PageController (module)
    |    ...

    """

    syntax = ("elixir")
    tempfile_suffix = "-"

    regex_parts = (
        # Error type 1
        r"== Compilation error on file (?P<e_file1>.+) ==\n"
        r"\*\* \(.+\) (?P=e_file1):(?P<e_line1>\d+): (?P<e_msg1>.+)",

        # Error type 2
        r"== Compilation error on file (?P<e_file2>.+) ==\n"
        r"\*\* \(.+\) (?P<e_msg2>.+)\n"
        r"    (?P=e_file2):(?P<e_line2>\d+)",

        # Error type 3
        # Do not backreference e_file3 -- we want the _first_
        # meaningful trace line to be captured, skipping an
        # arbitary number of irrelevant lines before that.
        r"== Compilation error on file .+ ==\n"
        r"\*\* \(.+\) (?P<e_msg3>.+)\n"
        r"(.+\n)*?"
        r"    (?P<e_file3>[^(].+):(?P<e_line3>\d+)",

        # Error type 4
        r"\*\* \(.+\) (?P<e_file4>.+):(?P<e_line4>\d+): (?P<e_msg4>.+)",

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
        # TODO: this does not work for .exs files
        #       (e.g. ExUnit test files) -- i haven't found
        #       out how to lint them with mix
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
          * etc..

        """
        dummy_match = None

        if match:
            captures = match.groupdict()
            dummy_string = self.build_dummy_string(captures)
            dummy_match = re.match(self.dummy_regex, dummy_string)

        if dummy_match:
            filename = os.path.join(self.chdir, dummy_match.group('filename'))

            persist.debug("Linted file: %s" % self.filename)
            persist.debug("Error source: %s" % filename)

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
            persist.debug('Error type 1')
            dummy_str = '%s:%s:%s:%s' % (
                captures['e_file1'],
                captures['e_line1'],
                'error',
                captures['e_msg1']
            )
        elif captures['e_file2'] is not None:
            persist.debug('Error type 2')
            dummy_str = "%s:%s:%s:%s" % (
                captures['e_file2'],
                captures['e_line2'],
                'error',
                captures['e_msg2']
            )
        elif captures['e_file3'] is not None:
            persist.debug('Error type 3')
            dummy_str = "%s:%s:%s:%s" % (
                captures['e_file3'],
                captures['e_line3'],
                'error',
                captures['e_msg3']
            )

        elif captures['e_file4'] is not None:
            persist.debug('Error type 4')
            dummy_str = "%s:%s:%s:%s" % (
                captures['e_file4'],
                captures['e_line4'],
                'error',
                captures['e_msg4']
            )
        elif captures['w_file1'] is not None:
            persist.debug('Warning type 1')
            dummy_str = "%s:%s:%s:%s" % (
                captures['w_file1'],
                captures['w_line1'],
                'warning',
                captures['w_msg1']
            )
        else:
            persist.debug('No match')
            dummy_str = ""

        persist.debug("Dummy string: %s" % dummy_str)
        return dummy_str

