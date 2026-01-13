Generate, view and store TOTP codes from the command line.
Data is encrypted with a password.

## Install
You can install via `pip`:
```
pip install totp-tui
```

## Usage
### Terminal User Interface
Opens ncurses TUI in current terminal
```
totp tui
```
or just
```
totp
```

> [!WARNING]
> Prompts for password if run for the first time, and fails if no entries have been added

### Manage entries
Add a new entry with
```
totp add --site <site> --nick <nick> --secret <secret>
```

List all entries with
```
totp ls
```

Most commands can receive an optional `--password` for easier scripting

## Config
Most settings and interface can be changed via `totp/config.py`
