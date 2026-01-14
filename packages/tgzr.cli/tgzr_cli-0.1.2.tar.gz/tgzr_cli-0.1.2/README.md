# tgzr.cli
tgzr command line

# Installation

## Standalone Executable

Download the executable corresponding to your platform on https://github.com/open-tgzr/tgzr.cli/releases

## uvx

To run `tgzr` without installation, you can use `uvx`. 
The default command is `install`, so you can install `tgzr` with:

`uvx --from tgzr.cli tgzr`\
or\
`uvx --from tgzr.cli tgzr --home /path/to/your/TGZR --studio MyStudioName`

You can also run `tgzr` with plugins loaded from other pacakages.
The default command becomes `app manager` when you install `tgzr.shell_apps.manager_panel`, so 
you can run the manager with:

`uvx --from tgzr.cli --with tgzr.shell_apps.manager_panel tgzr`

## Python Package

Create a virtual environment, activate it, and `pip install -U tgzr.cli`

# Usage

## Home

### Lookup

`tgzr` looks for a config file named `.tgzr` in the current directory. If the config file is not found there
if looks for it in the parent directory and all parent's sub-directories, and goes on up until reaching the
root directory or finding a Config file.

To start the config lookup in another directory, you can use the `-H` or `--home` option:
- `tgzr --home ~/TGZR ...`

Once the config is found, we refer to its folder as **"home"**.

### Manage

- You can see the session config with:
    - `tgzr session show`
- You can save a config with:
    - `tgzr session save` 
    - This will bake the options into the config, so if you do:
        - `tgzr --verbose session save`
        - Next usage of `tgzr` will behave as if the `--verbose` option was specified.

## Sub Commands

`tgzr` provides different sub-commands depending from where you run it.

A bare `tgzr` will only have `help` and `install` sub-commands.
When installed (for example, using `tgzr install`), some plugins will then
provide additionnal sub-commands.

In order to activate a specific list of plugins, you need to run `tgzr` from an installed "Studio" . \
All Studios contain a `tgzr` alias in their root directory (`tgzr.bat` for windows).\
This is the command you want to run in order to use the plugins installed in that Studio.

### Command short name

Commands and Groups can be specified using their first letter(s) only, as long as
their is no ambiguity on the command name you are aiming at.

For example, let's say available commands are:
- search
- save
- load

Then, if entering `tgzr l` resolve to `tgzr load`.
But entering `tgzr s` could resolve to `tgzr search` or `tgzr load`, so 
you will receive an error. You should use at lease `tgzr se` or `tgzr sa`.

### Getting Help

- Use `-h` or `--help` after the sub-command name to get usage details:
    - `tgzr <subcommand> --help`
- Use the commands in the `help` group to get detailed information / tips:
    - `tgzr help <topic>`




## Env Vars

You can config the session using environement variables.

Use the `tgzr help env` command to list the name of all usable env vars.

The env var name is the config field prepended with the appropriate prefix:
- SessionConfig: `tgzr_<field_name>`
- WorkspacesConfig: `tgzr_ws_<field_name>`
- WorkspaceConfig: `tgzr_ws_default_<field_name>`

You can open the config files saved in the session and workspaces to find 
examples of the env var names.

For example:
- `tgzr_verbose=True tgzr config show` == `tgzr -v config show`
- `tgzr_verbose=False tgzr config show` == `tgzr --quite config show`
- `tgzr_ws_default_workspace_name=MyStudio tgzr ws show` == `tgzr ws --name MyStudio show`

# Plugins

`tgzr` command line is plugin based: all plugin installed in the current virtual env will
be accessible in the command line.

## Implement a Plugin

To implement a plugin you need:
- to declare entry point(s) in a `tgzr.cli.plugin` group.
- to have the entry point(s) lead to a callable accepting one argument: the root click group

__Example__: 
> in `my_package/cli_plugin.py`:
> ```python
> import click
>
> @click.group()
> def my_group():
>     '''My Awesome commands'''
>  
> def install_plugin(group::click.Group):
>     group.add_command(my_group)
> ```
>
> in `pyproject.toml`:
> 
> ```
> [project.entry-points."tgzr.cli.plugin"]
> my_package = "my_package.cli_plugin:install_plugin"
> ```

# Installer

Generate the installer with: `uv run pyinstaller pyinstaller_specs/tgzr-<platform>.spec`
The `tgzr-<platform>` executable will be generated in the `dist/` folder