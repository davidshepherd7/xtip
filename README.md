# Xtip

A semi-clone of tanin47's [tip](https://github.com/tanin47/tip) but for X11 (i.e. Linux).

Alpha stage, anything may change at any time.

Customised in python (but it's very easy to run shell commands from python if
you prefer another language).


## Installation and setup

* Install the core dependencies: `zenity`, `dmenu`, `xclip`
  * e.g. on Debian-based OS: `sudo apt install zenity xclip suckless-tools`
* Save x-tip.py into a directory on your `$PATH` and `chmod +x x-tip.py`
* Bind a hotkey to it using your preferred method. 
  * I use [sxhkd](https://github.com/baskerville/sxhkd), but I think most
  desktop environments have a hotkey binding system.
* Optionally install dependencies for any individual commands that you want to use:
  * GoogleTranslate requires the python googtrans library
  * Emacsclient requires emacs (obviously)


## Writing your own commands


For most customisation of commands you should probably just write your own
(because it only takes a few lines of python).

To do so: write a new class derived from `Command` and decorate it with `@command`.

TODO: better docs?


## TODO

* Write some tests
* Set up typechecking properly
* Add support for config files to specify commands
* Add support for installing using `pip` (and break up into multiple files)
* Try to display useful outputs in dmenu completion (e.g. converted datetimes)
* Something better than dmenu? Better mouse support, popup at cursor.
* Figure out how to construct an absolute path from 
