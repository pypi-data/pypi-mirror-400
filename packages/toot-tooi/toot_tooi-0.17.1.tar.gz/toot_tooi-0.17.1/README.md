tooi
====

<!-- https://commons.wikimedia.org/wiki/File:Britannica_Horn_Modern_Horn.png -->
![Horn logo](horn.jpg)

tooi is a text-based user interface for Mastodon, Pleroma and friends. The name
is a portmanteau of [toot](https://toot.bezdomni.net/) and
[TUI](https://en.wikipedia.org/wiki/Text-based_user_interface).

tooi is a re-implementation of the TUI included with
[toot](https://toot.bezdomni.net/) using the modern and more powerful
[Textual](https://textual.textualize.io/) framework.

* Source code: https://codeberg.org/ihabunek/tooi
* Python package: https://pypi.org/project/toot-tooi/ \*
* IRC chat: #toot channel on libera.chat

\* Could not get `tooi` as Python project name, if someone knows python people
ask them kindly to approve
[this request](https://github.com/pypi/support/issues/3097).

This project proudly uses [Pride Versioning 🏳️‍🌈](https://pridever.org/).

## Project status

**This project is in its early days and things _will_ change without notice.**

While we aim to keep the project usable at all times, expect that things may
break before we hit version 1.0.

## Installation

The recommended method of installation is using [uv](https://docs.astral.sh/uv/)
which installs python projects into their own virtual environments.

1. Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
   to set it up.

2. Install tooi by running:
   ```
   uv tool install toot-tooi
   ```

Alternatively, if you know what you're doing, install both projects from pypi
using your favourite method.

## Usage

Launch the program by running `tooi`.

Run `tooi --help` to see the available commandline options.

On first login tooi will offer an account selection screen where you can log
into your instance.

## Key bindings

Note that you can see available bindings depending on current context in the
status bar. To get a list of all available bindings, open the command palette
(ctrl+p) and select "Keys".

Generic bindings:

* Arrow keys or `h`/`j`/`k`/`l` - move up/down/left/right
* `Tab` and `Shift+Tab` - move between focusable components
* `Space` or `Enter` - activate buttons and menu items
* `Ctrl+p` - open the command palette

Managing tabs:

* `.` - refresh timeline
* `/` - open search tab
* `1` - `9` - switch between open tabs
* `Ctrl+d, Ctrl+w` - close current tab
* `g` - open new tab ("goto")

Status bindings:

* `a` - show account
* `b` - boost status
* `d` - delete status
* `e` - edit status
* `f` - favourite status
* `m` - show media
* `r` - reply to status
* `s` - reveal sensitive
* `t` - show thread
* `u` - show toot source
* `v` - open toot in browser

## Setting up a dev environment

Usage of [uv](https://docs.astral.sh/uv/) for development is recommended.

Check out tooi and install the dependencies:

```
git clone https://codeberg.org/ihabunek/tooi.git
cd tooi
uv sync
```

Run the app by invoking:

```
uv run tooi
```

## Using the console

To use the
[Textual console](https://textual.textualize.io/guide/devtools/#console), run
it in a separate terminal window:

```
uv run textual console
```

Then run tooi in dev mode so it connects to the console:

```
uv run textual run --dev tooi.cli:main
```

## Code style and linting

Rule of thumb: look at existing code, try to keep it similar in style.

This project uses `ruff` to format code. Please run it on any modified files
before submitting changes: `ruff format <path>`

## Type checking

This project is configured to use
[pyright](https://github.com/microsoft/pyright) for type checking, and I
recommend that you install the pyright language server if it's available for
your editor. Currently it returns errors in some places, some of which are
caused by the way textual is implemented. So it's not required to have zero
errors before submitting patches, but it will indicate problems in new code.
