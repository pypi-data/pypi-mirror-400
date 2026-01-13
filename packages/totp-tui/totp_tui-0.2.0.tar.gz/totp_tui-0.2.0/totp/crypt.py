import base64
import json
import os
import sqlite3
import time
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from dataclasses import dataclass
from typing import Iterable, Dict

from totp import utils
from totp.config import HASH_FILE, SITES_TABLE

logger = utils.get_logger(__name__)

# WARN: handle user input only for valid chars when encoding b64encode
# FIX: handle possible incorrect type in HASH_FILE and SITES_TABLE
# TODO: properly handle and raise exceptions
# TODO: logs

# NOTE: Crypt init() Fernet is used for getting the main encryption key
# NOTE: crypt(), decrypt() for 2FA (TOTP) secret encryption
# NOTE: derive(), verify() for main password hashing

"""
password = load_hash()["password"]
salt = load_hash()["salt"]
input = ... userinput
if check_hash(input,password,salt)

return read_table()
"""

table_create_query = """
    CREATE TABLE IF NOT EXISTS SITES (
        secret VARCHAR(255) NOT NULL,
        site VARCHAR(255) NOT NULL,
        nick VARCHAR(255),
        PRIMARY KEY (site, nick)
    );
"""


class CryptTokenError(Exception):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "Hash file has incorrect formatting or is missing a key."


class InvalidSecretKey(Exception):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "TOTP secret key is invalid"


@dataclass
class EntrySite:
    secret: str
    nick: str
    site: str
    nick_hidden: bool = False
    site_hidden: bool = False

    # NOTE: as per RFC 6238
    def get_totp_token(self) -> str:
        key = base64.b32decode(self.secret.encode())
        try:
            totp = TOTP(
                key=key,
                length=6,
                algorithm=hashes.SHA1(),
                time_step=30,
                enforce_key_length=False,
            )
            totp_token = totp.generate(time.time())
            return totp_token.decode()
        except ValueError:
            raise InvalidSecretKey()


def load_hash() -> Dict:
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            try:
                data_dump = json.load(f)
                password = base64.urlsafe_b64decode(data_dump["password"])
                salt = base64.urlsafe_b64decode(data_dump["salt"])
                return {"password": password, "salt": salt}
            except json.JSONDecodeError:
                logger.error("Error decoding JSON from HASH_FILE.")
                return None
            except KeyError:
                logger.error("Missing expected keys in HASH_FILE.")
                return None
    else:
        # TODO: create file
        logger.warning("HASH_FILE not found.")
        return None


def save_hash(hash: bytes, salt: bytes = os.urandom(16)) -> None:
    if os.path.exists(HASH_FILE):
        logger.debug("HASH_FILE already exists.")
    else:
        logger.debug("Attempting to open HASH_FILE.")
        with open(HASH_FILE, "w") as f:
            data = {
                "password": base64.urlsafe_b64encode(hash).decode("utf-8"),
                "salt": base64.urlsafe_b64encode(salt).decode("utf-8"),
            }
            json.dump(obj=data, fp=f, indent=4)
            logger.debug("Writing to HASH_FILE finished.")


def read_table(password: bytes, salt: bytes) -> Iterable[EntrySite]:
    with sqlite3.connect(SITES_TABLE) as conn:
        cur = conn.cursor()

        cur.execute(table_create_query)

        cr = Crypt(password=password, salt=salt)
        res = cur.execute("SELECT secret, site, nick FROM SITES ORDER BY site; ")

        for row in res:
            try:
                encrypted, site, nick = row
                secret = cr.decrypt(data=encrypted).decode()
                yield EntrySite(
                    secret=secret,
                    nick=nick,
                    nick_hidden=False,
                    site=site,
                    site_hidden=False,
                )
            except CryptTokenError:
                logger.warning("Invalid entry found in table.")
                pass


def get_entry(password: bytes, salt: bytes, site: str, nick: str) -> EntrySite:
    with sqlite3.connect(SITES_TABLE) as conn:
        cur = conn.cursor()

        cr = Crypt(password=password, salt=salt)
        row = cur.execute(
            "SELECT secret, site, nick FROM SITES WHERE site = ? AND nick = ?; ",
            (site, nick)
        ).fetchone()

        if row:
            try:
                encrypted, site, nick = row
                secret = cr.decrypt(data=encrypted).decode()
                return EntrySite(
                    secret=secret,
                    nick=nick,
                    nick_hidden=False,
                    site=site,
                    site_hidden=False,
                )
            except CryptTokenError:
                logger.warning("Invalid entry found in table.")
                pass
        else:
            logger.warning("No matching entry found.")
            return None


def add_site(site: EntrySite, password: bytes, salt: bytes) -> None:
    with sqlite3.connect(SITES_TABLE) as conn:
        cur = conn.cursor()

        cur.execute(table_create_query)

        cr = Crypt(password=password, salt=salt)
        encrypted = cr.encrypt(site.secret)
        try:
            cur.execute(
                "INSERT INTO SITES (secret, site, nick) VALUES (?, ?, ?); ",
                (encrypted, site.site, site.nick),
            )
        except sqlite3.IntegrityError:
            logger.error("Site already present.")

        conn.commit()
        logger.debug(f'Added entry "{site.site}" to table.')


def derive(
    password: bytes, salt: bytes = os.urandom(16)
) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_200_000)
    return kdf.derive(key_material=password)


def verify(password: bytes, salt: bytes, hash: bytes) -> bool:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_200_000
    )
    try:
        kdf.verify(key_material=password, expected_key=hash)
        return True
    except InvalidKey:
        return False


class Crypt:
    def __init__(self, password: bytes, salt: bytes) -> None:
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_200_000
        )
        key = base64.urlsafe_b64encode(self.kdf.derive(password))
        self.f = Fernet(key)

    def decrypt(self, data: bytes) -> bytes:
        try:
            token = self.f.decrypt(data)
            return token
        except InvalidToken:
            logger.warning("Invalid token cannot be decrypted.")
            raise CryptTokenError()

    def encrypt(self, data: bytes) -> bytes:
        return self.f.encrypt(data)
