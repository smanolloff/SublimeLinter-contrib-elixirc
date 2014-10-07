SublimeLinter-contrib-elixirc
==========================

[![Build Status](https://travis-ci.org/doitian/SublimeLinter-contrib-elixirc.svg?branch=master)](https://travis-ci.org/doitian/SublimeLinter-contrib-elixirc)

This linter plugin for [SublimeLinter][docs] provides an interface to check [elixir](http://elixir-lang.org) syntax using **elixirc**. It will be used with files that have the “elixir” syntax.

## Installation
SublimeLinter 3 must be installed in order to use this plugin. If SublimeLinter 3 is not installed, please follow the instructions [here][installation].

### Linter installation
Before using this plugin, you must ensure that `elixir` is installed on your system. For example, it can be installed throw [Homebrew](http://brew.sh) in Mac OS X:

    brew install elixir

**Note:** This plugin requires `elixirc` 1.0 or later.

### Linter configuration
In order for `elixirc` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. Before going any further, please read and follow the steps in [“Finding a linter executable”](http://sublimelinter.readthedocs.org/en/latest/troubleshooting.html#finding-a-linter-executable) through “Validating your PATH” in the documentation.

Once you have installed and configured `elixirc`, you can proceed to install the SublimeLinter-contrib-elixirc plugin if it is not yet installed.

### Plugin installation
Please use [Package Control][pc] to install the linter plugin. This will ensure that the plugin will be updated when new versions are available. If you want to install from source so you can modify the source code, you probably know what you are doing so we won’t cover that here.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette][cmd] and type `install`. Among the commands you should see `Package Control: Install Package`. If that command is not highlighted, use the keyboard or mouse to select it. There will be a pause of a few seconds while Package Control fetches the list of available plugins.

1. When the plugin list appears, type `elixirc`. Among the entries you should see `SublimeLinter-contrib-elixirc`. If that entry is not highlighted, use the keyboard or mouse to select it.

## Settings
For general information on how SublimeLinter works with settings, please see [Settings][settings]. For information on generic linter settings, please see [Linter Settings][linter-settings].

In addition to the standard SublimeLinter settings, SublimeLinter-contrib-elixirc provides its own settings.

|Setting|Description|
|:------|:----------|
|include\_dirs|List of dirs for `-I` option|
|pa|List of dirs for `-pa` option|

In a mix project, if a file uses macros, the beam output paths must be added to code path through `pa`.

You must save the project file in the top directory in the mix project, then edit the project settings to add the `pa` setting such as:

	{
		"folders":
		[
			{
				"follow_symlinks": true,
				"path": ".",
	      		"folder_exclude_patterns": ["_build"],
			}
		],
	    "SublimeLinter": {
	        "linters": {
	            "elixirc": {
	                "pa": ["${project}/_build/dev/lib/PROJECT_WITH_MACROS/ebin"]
	            }
	        }
	    }
	}

`PROJECT_WITH_MACROS` is the project name which contains the macros. List all projects in `pa`. The project file is required to be saved in the top directory, so that `${project}` can be used as the top level directory of the project.


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
