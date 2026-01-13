#!/usr/bin/env python3

import argparse
import base64
import curses
import logging
import getpass
import os
import sys
import time
from curses import window, wrapper
from functools import partial
from typing import Dict

from totp import _version, utils, tui, crypt
from totp.config import CONFIG_DIR

logger = utils.get_logger(__name__)

# TODO: document code and functions
# TODO: clean and ordered imports

# WARN: drop exceptions, instead check cases and use logger
# TODO: command-line utils, expand parse_args -> parse.py,
#   - [x] totp (tui) -> tui
#       - [x] get colors to work!
#       - [_] navigation, user input and yank
#       - [_] longer lists than window size
#   - [x] totp add
#   - [x] totp ls
#   - [x] totp get
#   - [_] totp del
#   - [_] totp --delete-all
#   - [_] totp dump


_initialized: bool = False
password: bytes
salt: bytes


def initialize_parsers() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="totp",
        description="totp authentication in the terminal",
        add_help=True,
        # allow_abbrev=True,
        usage="totp command [command options]",
    )
    parser.add_argument("-v", "--version", action="version", version=_version())
    parser.set_defaults(func=tui_func)

    subparsers = parser.add_subparsers(title="commands")

    tui_parser = subparsers.add_parser("tui", prog="totp tui", help="show codes in tui")
    tui_auth = tui_parser.add_argument_group("authentication")
    tui_auth.add_argument(
        "-p", "--password", type=str, help="pass the password as a parameter"
    )
    tui_parser.set_defaults(func=tui_func)

    add_parser = subparsers.add_parser("add", prog="totp add", help="add an entry")
    add_required = add_parser.add_argument_group("required arguments")
    add_required.add_argument("--site", type=str, required=True)
    add_required.add_argument("--nick", type=str, required=True)
    add_required.add_argument("--secret", type=str, required=True)
    add_auth = add_parser.add_argument_group("authentication")
    add_auth.add_argument(
        "-p", "--password", type=str, help="pass the password as a parameter"
    )
    add_parser.set_defaults(func=add_func)

    ls_parser = subparsers.add_parser("ls", prog="totp ls", help="list all entries")
    ls_auth = ls_parser.add_argument_group("authentication")
    ls_auth.add_argument(
        "-p", "--password", type=str, help="pass the password as a parameter"
    )
    ls_parser.set_defaults(func=ls_func)

    get_parser = subparsers.add_parser("get", prog="totp get", help="get the TOTP code for an entry")
    get_required = get_parser.add_argument_group("required arguments")
    get_required.add_argument("--site", type=str, required=True)
    get_required.add_argument("--nick", type=str, required=True)
    get_auth = get_parser.add_argument_group("authentication")
    get_auth.add_argument(
        "-p", "--password", type=str, help="pass the password as a parameter"
    )
    get_parser.set_defaults(func=get_func)

    return parser


def tui_func(args) -> None:
    param_password = args["password"] if "password" in args.keys() else None
    if _initialized or login(param_password):
        if not _initialized:
            logger.error("Password and salt not properly initialized.")
            return

        hashes = crypt.load_hash()
        password, salt = hashes["password"], hashes["salt"]

        sites = list(crypt.read_table(password, salt))

        if not any(sites):
            logger.error("Empty sites list.")
            return

        wrapper(partial(run, sites))
    else:
        print("Incorrect password.")


def add_func(args) -> None:
    param_password = args["password"] if "password" in args.keys() else None
    if _initialized or login(param_password):
        if not _initialized:
            logger.error("Password and salt not properly initialized.")
            return

        new_site = crypt.EntrySite(
            secret=args["secret"].encode(),
            site=args["site"],
            nick=args["nick"],
        )
        crypt.add_site(site=new_site, password=password, salt=salt)
    else:
        pass


def ls_func(args) -> None:
    param_password = args["password"] if "password" in args.keys() else None
    if _initialized or login(param_password):
        if not _initialized:
            logger.error("Password and salt not properly initialized.")
            return

        hashes = crypt.load_hash()
        password, salt = hashes["password"], hashes["salt"]

        sites = list(crypt.read_table(password, salt))

        for entry in sites:
            print(f"{entry.nick}, {entry.site}")
    else:
        print("Incorrect password.")


def get_func(args) -> None:
    param_password = args["password"] if "password" in args.keys() else None
    if _initialized or login(param_password):
        if not _initialized:
            logger.error("Password and salt not properly initialized.")
            return

        hashes = crypt.load_hash()
        password, salt = hashes["password"], hashes["salt"]

        entry = crypt.get_entry(password, salt, args["site"], args["nick"])
        code = entry.get_totp_token()
        print(code)
    else:
        print("Incorrect password.")



def _ask_for_password() -> str:
    return getpass.getpass(prompt="Password: ").strip()


def _login(hash_dump: Dict, input: bytes) -> bool:
    global _initialized
    global password
    global salt

    if _initialized:
        logger.warning("Tried to override password and salt.")
        return

    if "password" not in hash_dump.keys() or type(hash_dump["password"]) is not bytes:
        raise crypt.CryptTokenError()
    password = hash_dump["password"]

    if "salt" not in hash_dump.keys() or type(hash_dump["salt"]) is not bytes:
        raise crypt.CryptTokenError()
    salt = hash_dump["salt"]

    res = crypt.verify(password=input, hash=password, salt=salt)
    if res:
        # valid password
        # logger.info("Correct password.")
        pass
    else:
        # invalid password
        # logger.info("Incorrect password.")
        pass

    _initialized = True
    return res


def login(input_password: str) -> bool:
    hash_dump = crypt.load_hash()
    match hash_dump:
        case None:
            # create new hash
            os.makedirs(CONFIG_DIR, exist_ok=True)
            random_salt = os.urandom(16)  # sets salt randomly
            input = _ask_for_password() if input_password is None else input_password
            hash = crypt.derive(password=input.encode(), salt=random_salt)
            crypt.save_hash(hash=hash, salt=random_salt)
            saved_hash = crypt.load_hash()
            return _login(saved_hash, input.encode())

        case _:
            # check hash
            input = _ask_for_password() if input_password is None else input_password
            return _login(hash_dump, input.encode())


def run(sites, stdsrc: window) -> None:
    # logger.info("App started.")

    stdsrc.nodelay(True)
    curses.start_color()
    curses.curs_set(0)

    src = tui.AuthWindow(stdsrc)

    for entry in sites:
        src.add_site(entry)

    while True:
        try:
            src.draw()
        except RuntimeError as ex:
            logger.error(f'curses exception: "{ex}".')
            raise ex

        c = stdsrc.getch()
        if c == ord("q"):
            break
        elif c != -1:  # getch returns -1 if no key is pressed
            pass


def main() -> None:
    # call arg parser and check
    parser = initialize_parsers()
    args = parser.parse_args()

    try:
        args.func(vars(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logger.error(f'Program ended due to exception: "{ex}".')
        raise ex

