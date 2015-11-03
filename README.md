SublimeLinter-contrib-elixirc
==========================

[![Build Status](https://travis-ci.org/smanolloff/SublimeLinter-contrib-elixirc.svg?branch=master)](https://travis-ci.org/smanolloff/SublimeLinter-contrib-elixirc)

This linter plugin for [SublimeLinter][docs] provides an interface to check [elixir](http://elixir-lang.org) syntax using **elixirc**. It will be used with files that have the “elixir” syntax.

## Installation
SublimeLinter 3 must be installed in order to use this plugin. If SublimeLinter 3 is not installed, please follow the instructions [here][installation].

### Linter installation
Before installing this plugin, you must ensure that `elixir` (>= 1.0) is installed on your system. For instructions on how to install elixir, please refer to the [elixir-lang docs](http://elixir-lang.org/install.html).

### Linter configuration
In order for `elixir` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. Before going any further, please read and follow the steps in [“Finding a linter executable”](http://sublimelinter.readthedocs.org/en/latest/troubleshooting.html#finding-a-linter-executable) through “Validating your PATH” in the documentation.

Once `elixir` is installed and configured, you can proceed to install the SublimeLinter-contrib-elixirc plugin if it is not yet installed.

### Plugin installation
Please use [Package Control][pc] to install the linter plugin. This will ensure that the plugin will be updated when new versions are available. If you want to install from source so you can modify the source code, you probably know what you are doing so we won’t cover that here.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette][cmd] and type `install`. Among the commands you should see `Package Control: Install Package`. If that command is not highlighted, use the keyboard or mouse to select it. There will be a pause of a few seconds while Package Control fetches the list of available plugins.

1. When the plugin list appears, type `elixirc`. Among the entries you should see `SublimeLinter-contrib-elixirc`. If that entry is not highlighted, use the keyboard or mouse to select it.

## Settings
For general information on how SublimeLinter works with settings, please see [Settings][settings]. For information on generic linter settings, please see [Linter Settings][linter-settings].

In addition to the standard SublimeLinter settings, SublimeLinter-contrib-elixirc provides its own settings.

|Setting     |Description                    |
|:-----------|:------------------------------|
|pa          |_(list)_ dirs for `-pa` option |
|require     |_(list)_ dirs/files to require |
|mix_project |_(bool)_ use mix for linting   |

### In a mix project:
* set `chdir` to your mix project's root directory.
* set `mix_project` to `true`

#### Example:
In your _.sublime-project_ file:
```JSON
   "SublimeLinter": {
      "linters": {
         "elixirc": {
            "mix_project": true,
            "chdir": "PROJECT_ROOT"
         }
      }
   }
```

Where:
* `PROJECT_ROOT` is the path to the root your project (use `${project}` if your sublime project is saved there)

Note: Currently, `exs` files within a mix project (e.g. ExUnit tests) are not linted. This is a known issue and will be resolved in a future version.

### Outside a mix project:
* if a file uses macros, the beam output paths must be added to code path through `pa`
* files (or directories) to require prior to linting must be added through `require`. They are required in the given order. Directories, if given, are traversed recursively and alphabetically.

#### Example
In your _.sublime-project_ file:
```JSON
   "SublimeLinter": {
      "linters": {
         "elixirc": {
            "pa": ["PROJECT_ROOT/_build/dev/lib/PROJECT_WITH_MACROS/ebin"],
            "require": ["PROJECT_ROOT/deps/DEP1"]
         }
      }
   }
```

Where:
* `PROJECT_ROOT` is the path to the root of your project (use `${project}` if your sublime project is saved there)
* `PROJECT_WITH_MACROS` is the project name which contains the macros. List all projects in `pa`
* `DEP1` is a directory with files to require. If needed, list specific files first.


## Contributing
If you would like to contribute enhancements or fixes, please do the following:

1. Fork the plugin repository.
1. Hack on a separate topic branch created from the latest `master`.
1. Commit and push the topic branch.
1. Make a pull request.
1. Be patient.  ;-)

Please note that modifications should follow these coding guidelines:

- Indent is 4 spaces.
- Code should pass flake8 and pep257 linters.
- Vertical whitespace helps readability, don’t be afraid to use it.
- Please use descriptive variable names, no abbreviations unless they are very well known.

Thank you for helping out!

[docs]: http://sublimelinter.readthedocs.org
[installation]: http://sublimelinter.readthedocs.org/en/latest/installation.html
[locating-executables]: http://sublimelinter.readthedocs.org/en/latest/usage.html#how-linter-executables-are-located
[pc]: https://sublime.wbond.net/installation
[cmd]: http://docs.sublimetext.info/en/sublime-text-3/extensibility/command_palette.html
[settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html
[linter-settings]: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html
[inline-settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html#inline-settings
