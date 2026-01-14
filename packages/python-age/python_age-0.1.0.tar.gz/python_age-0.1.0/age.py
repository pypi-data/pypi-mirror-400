#!/usr/bin/env python3
"""
Minimal Python implementation of age-encryption.org/v1.

Supported recipients:
- X25519 ("age1...") public keys
- scrypt passphrases ("-p")

Requires the "cryptography" package for X25519 and ChaCha20-Poly1305.
"""

import argparse
import base64
import binascii
import getpass
import hashlib
import hmac
import io
import os
import sys
from typing import BinaryIO, Iterable, Optional, Tuple

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.asymmetric.x25519 import (
        X25519PrivateKey,
        X25519PublicKey,
    )
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PublicFormat,
        PrivateFormat,
        NoEncryption,
    )
except ImportError:  # pragma: no cover - handled at runtime
    InvalidTag = None
    X25519PrivateKey = None
    X25519PublicKey = None
    ChaCha20Poly1305 = None
    Encoding = None
    PublicFormat = None
    PrivateFormat = None
    NoEncryption = None


INTRO = b"age-encryption.org/v1\n"
COLUMNS_PER_LINE = 64
BYTES_PER_LINE = COLUMNS_PER_LINE // 4 * 3
FILE_KEY_SIZE = 16
STREAM_NONCE_SIZE = 16
CHUNK_SIZE = 64 * 1024
ENC_CHUNK_SIZE = CHUNK_SIZE + 16
LAST_CHUNK_FLAG = 0x01
SCRYPT_R = 8
SCRYPT_P = 1

X25519_LABEL = b"age-encryption.org/v1/X25519"
SCRYPT_LABEL = b"age-encryption.org/v1/scrypt"

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
GENERATOR = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]

__all__ = [
    "IncorrectIdentity",
    "NoIdentityMatchError",
    "Stanza",
    "Header",
    "X25519Recipient",
    "X25519Identity",
    "ScryptRecipient",
    "ScryptIdentity",
    "parse_recipient",
    "parse_identity",
    "load_recipients",
    "load_identities",
    "encrypt_file",
    "decrypt_file",
    "encrypt_bytes",
    "decrypt_bytes",
    "generate_keypair",
]


class IncorrectIdentity(Exception):
    pass


class NoIdentityMatchError(Exception):
    def __init__(self, errors):
        super().__init__("no identity matched any of the recipients")
        self.errors = errors


class Stanza:
    def __init__(self, stanza_type: str, args: list[str], body: bytes):
        self.stanza_type = stanza_type
        self.args = args
        self.body = body


class Header:
    def __init__(self, recipients: list[Stanza], mac: Optional[bytes] = None):
        self.recipients = recipients
        self.mac = mac


def _require_crypto():
    if ChaCha20Poly1305 is None:
        raise SystemExit(
            "cryptography is required. Install with: pip install cryptography"
        )


def b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii").rstrip("=")


def b64_decode(text: str) -> bytes:
    if "\n" in text or "\r" in text:
        raise ValueError("unexpected newline character")
    pad = (-len(text)) % 4
    try:
        return base64.b64decode(text + ("=" * pad), validate=True)
    except binascii.Error as exc:
        raise ValueError(str(exc)) from exc


def encode_wrapped_base64(data: bytes) -> bytes:
    if not data:
        return b""
    raw = b64_encode(data)
    lines = [raw[i : i + COLUMNS_PER_LINE] for i in range(0, len(raw), COLUMNS_PER_LINE)]
    body = "\n".join(lines)
    if len(raw) % COLUMNS_PER_LINE == 0:
        body += "\n"
    return body.encode("ascii")


def _split_args(line: bytes) -> tuple[str, list[str]]:
    parts = line.rstrip(b"\n").split(b" ")
    prefix = parts[0].decode("ascii", errors="strict")
    args = [p.decode("ascii", errors="strict") for p in parts[1:]]
    return prefix, args


def _valid_string(value: str) -> bool:
    if not value:
        return False
    for c in value:
        if ord(c) < 33 or ord(c) > 126:
            return False
    return True


def _marshal_stanza(stanza: Stanza, out) -> None:
    pieces = ["->", stanza.stanza_type] + stanza.args
    out.write((" ".join(pieces) + "\n").encode("ascii"))
    out.write(encode_wrapped_base64(stanza.body))
    out.write(b"\n")


def marshal_header_without_mac(header: Header) -> bytes:
    buf = io.BytesIO()
    buf.write(INTRO)
    for stanza in header.recipients:
        _marshal_stanza(stanza, buf)
    buf.write(b"---")
    return buf.getvalue()


def marshal_header(header: Header) -> bytes:
    if header.mac is None:
        raise ValueError("header MAC is missing")
    buf = io.BytesIO()
    buf.write(INTRO)
    for stanza in header.recipients:
        _marshal_stanza(stanza, buf)
    buf.write(b"--- ")
    buf.write(b64_encode(header.mac).encode("ascii"))
    buf.write(b"\n")
    return buf.getvalue()


def parse_header(src: io.BufferedReader) -> Tuple[Header, io.BufferedReader]:
    reader = src if isinstance(src, io.BufferedReader) else io.BufferedReader(src)
    intro = reader.readline()
    if intro == b"":
        raise ValueError("file is empty")
    if intro != INTRO:
        raise ValueError(f"unexpected intro: {intro!r}")

    stanzas: list[Stanza] = []
    while True:
        peek = reader.peek(3)
        if not peek:
            raise ValueError("failed to read header")
        if peek.startswith(b"---"):
            line = reader.readline()
            prefix, args = _split_args(line)
            if prefix != "---" or len(args) != 1:
                raise ValueError(f"malformed closing line: {line!r}")
            mac = b64_decode(args[0])
            if len(mac) != 32:
                raise ValueError("malformed closing line: invalid MAC length")
            return Header(stanzas, mac), reader

        line = reader.readline()
        if not line:
            raise ValueError("unexpected EOF in header")
        if not line.startswith(b"->"):
            raise ValueError(f"malformed stanza opening line: {line!r}")
        prefix, args = _split_args(line)
        if prefix != "->" or len(args) < 1:
            raise ValueError(f"malformed stanza: {line!r}")
        for arg in args:
            if not _valid_string(arg):
                raise ValueError(f"malformed stanza: {line!r}")

        stanza_type = args[0]
        stanza_args = args[1:]
        body = bytearray()
        while True:
            body_line = reader.readline()
            if not body_line:
                raise ValueError("failed to read stanza body")
            stripped = body_line.rstrip(b"\n")
            try:
                decoded = b64_decode(stripped.decode("ascii"))
            except ValueError as exc:
                if body_line.startswith(b"---") or body_line.startswith(b"->"):
                    raise ValueError(
                        "stanza ended without a short line"
                    ) from exc
                raise ValueError(f"malformed body line {body_line!r}: {exc}") from exc
            if len(decoded) > BYTES_PER_LINE:
                raise ValueError(f"malformed body line {body_line!r}: too long")
            body.extend(decoded)
            if len(decoded) < BYTES_PER_LINE:
                stanzas.append(Stanza(stanza_type, stanza_args, bytes(body)))
                break


def hkdf_sha256(ikm: bytes, salt: Optional[bytes], info: bytes, length: int) -> bytes:
    if salt is None:
        salt = b"\x00" * hashlib.sha256().digest_size
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    okm = b""
    t = b""
    counter = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        okm += t
        counter += 1
    return okm[:length]


def scrypt_key(password: bytes, salt: bytes, n: int, r: int, p: int) -> bytes:
    maxmem = 128 * r * n + 1024 * 1024
    return hashlib.scrypt(password, salt=salt, n=n, r=r, p=p, maxmem=maxmem, dklen=32)


def aead_encrypt(key: bytes, plaintext: bytes) -> bytes:
    aead = ChaCha20Poly1305(key)
    nonce = b"\x00" * 12
    return aead.encrypt(nonce, plaintext, None)


def aead_decrypt(key: bytes, size: int, ciphertext: bytes) -> bytes:
    aead = ChaCha20Poly1305(key)
    if len(ciphertext) != size + 16:
        raise ValueError("encrypted value has unexpected length")
    nonce = b"\x00" * 12
    return aead.decrypt(nonce, ciphertext, None)


def header_mac(file_key: bytes, header: Header) -> bytes:
    hmac_key = hkdf_sha256(file_key, None, b"header", 32)
    data = marshal_header_without_mac(header)
    return hmac.new(hmac_key, data, hashlib.sha256).digest()


def stream_key(file_key: bytes, nonce: bytes) -> bytes:
    return hkdf_sha256(file_key, nonce, b"payload", 32)


def inc_nonce(nonce: bytearray) -> None:
    for i in range(len(nonce) - 2, -1, -1):
        nonce[i] = (nonce[i] + 1) & 0xFF
        if nonce[i] != 0:
            return
    raise ValueError("nonce counter wrapped around")


def read_exact(reader: io.BufferedReader, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = reader.read(size - len(data))
        if chunk == b"":
            break
        data.extend(chunk)
    return bytes(data)


def encrypt_stream(src: io.BufferedReader, dst: io.BufferedWriter, key: bytes) -> None:
    aead = ChaCha20Poly1305(key)
    nonce = bytearray(12)

    buf = read_exact(src, CHUNK_SIZE + 1)
    if buf == b"":
        last_nonce = bytes(nonce[:-1] + bytes([LAST_CHUNK_FLAG]))
        dst.write(aead.encrypt(last_nonce, b"", None))
        return

    while True:
        if len(buf) <= CHUNK_SIZE:
            last = True
            chunk = buf
            buf = b""
        else:
            last = False
            chunk = buf[:CHUNK_SIZE]
            buf = buf[CHUNK_SIZE:]

        if last:
            last_nonce = bytes(nonce[:-1] + bytes([LAST_CHUNK_FLAG]))
            dst.write(aead.encrypt(last_nonce, chunk, None))
            return

        dst.write(aead.encrypt(bytes(nonce), chunk, None))
        inc_nonce(nonce)
        buf += read_exact(src, CHUNK_SIZE + 1 - len(buf))


def decrypt_stream(src: io.BufferedReader, dst: io.BufferedWriter, key: bytes) -> None:
    aead = ChaCha20Poly1305(key)
    nonce = bytearray(12)
    first = True
    while True:
        chunk = read_exact(src, ENC_CHUNK_SIZE)
        if chunk == b"":
            raise ValueError("truncated encrypted payload")

        last = len(chunk) < ENC_CHUNK_SIZE
        nonce_to_use = bytes(nonce)
        if last:
            nonce_to_use = bytes(nonce[:-1] + bytes([LAST_CHUNK_FLAG]))
        try:
            plaintext = aead.decrypt(nonce_to_use, chunk, None)
        except InvalidTag:
            if not last:
                nonce_last = bytes(nonce[:-1] + bytes([LAST_CHUNK_FLAG]))
                try:
                    plaintext = aead.decrypt(nonce_last, chunk, None)
                    last = True
                except InvalidTag as exc:
                    raise ValueError(
                        "failed to decrypt and authenticate payload chunk"
                    ) from exc
            else:
                raise ValueError(
                    "failed to decrypt and authenticate payload chunk"
                ) from None

        if not first and last and len(chunk) == 16:
            raise ValueError("last chunk is empty")
        first = False
        dst.write(plaintext)

        if last:
            extra = src.read(1)
            if extra not in (b"", None):
                raise ValueError("trailing data after end of encrypted file")
            return
        inc_nonce(nonce)


def polymod(values: bytes) -> int:
    chk = 1
    for v in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ v
        for i in range(5):
            if (top >> i) & 1:
                chk ^= GENERATOR[i]
    return chk


def hrp_expand(hrp: str) -> bytes:
    lower = hrp.lower()
    ret = []
    for c in lower:
        ret.append(ord(c) >> 5)
    ret.append(0)
    for c in lower:
        ret.append(ord(c) & 31)
    return bytes(ret)


def verify_checksum(hrp: str, data: bytes) -> bool:
    return polymod(hrp_expand(hrp) + data) == 1


def create_checksum(hrp: str, data: bytes) -> bytes:
    values = hrp_expand(hrp) + data + b"\x00\x00\x00\x00\x00\x00"
    mod = polymod(values) ^ 1
    ret = []
    for p in range(6):
        shift = 5 * (5 - p)
        ret.append((mod >> shift) & 31)
    return bytes(ret)


def convert_bits(data: bytes, frombits: int, tobits: int, pad: bool) -> bytes:
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for idx, value in enumerate(data):
        if value >> frombits != 0:
            raise ValueError(
                f"invalid data range: data[{idx}]={value} (frombits={frombits})"
            )
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits > 0:
            ret.append((acc << (tobits - bits)) & maxv)
    else:
        if bits >= frombits:
            raise ValueError("illegal zero padding")
        if (acc << (tobits - bits)) & maxv != 0:
            raise ValueError("non-zero padding")
    return bytes(ret)


def bech32_encode(hrp: str, data: bytes) -> str:
    values = convert_bits(data, 8, 5, True)
    if len(hrp) < 1:
        raise ValueError(f"invalid HRP: {hrp!r}")
    for p, c in enumerate(hrp):
        if ord(c) < 33 or ord(c) > 126:
            raise ValueError(f"invalid HRP character: hrp[{p}]={ord(c)}")
    if hrp.upper() != hrp and hrp.lower() != hrp:
        raise ValueError(f"mixed case HRP: {hrp!r}")
    lower = hrp.lower() == hrp
    hrp = hrp.lower()
    ret = hrp + "1"
    ret += "".join(CHARSET[p] for p in values)
    ret += "".join(CHARSET[p] for p in create_checksum(hrp, values))
    return ret if lower else ret.upper()


def bech32_decode(text: str) -> tuple[str, bytes]:
    if text.lower() != text and text.upper() != text:
        raise ValueError("mixed case")
    pos = text.rfind("1")
    if pos < 1 or pos + 7 > len(text):
        raise ValueError("separator '1' at invalid position")
    hrp = text[:pos]
    for p, c in enumerate(hrp):
        if ord(c) < 33 or ord(c) > 126:
            raise ValueError(
                f"invalid character human-readable part: s[{p}]={ord(c)}"
            )
    lower = text.lower()
    data = []
    for p, c in enumerate(lower[pos + 1 :]):
        d = CHARSET.find(c)
        if d == -1:
            raise ValueError(f"invalid character data part: s[{p}]={c!r}")
        data.append(d)
    data_bytes = bytes(data)
    if not verify_checksum(hrp, data_bytes):
        raise ValueError("invalid checksum")
    decoded = convert_bits(data_bytes[:-6], 5, 8, False)
    return hrp, decoded


class X25519Recipient:
    def __init__(self, public_key: bytes):
        if len(public_key) != 32:
            raise ValueError("invalid X25519 public key")
        self.public_key = public_key

    def wrap(self, file_key: bytes) -> list[Stanza]:
        _require_crypto()
        ephemeral = X25519PrivateKey.generate()
        epk = ephemeral.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        shared = ephemeral.exchange(X25519PublicKey.from_public_bytes(self.public_key))
        salt = epk + self.public_key
        wrapping_key = hkdf_sha256(shared, salt, X25519_LABEL, 32)
        wrapped = aead_encrypt(wrapping_key, file_key)
        return [Stanza("X25519", [b64_encode(epk)], wrapped)]

    def __str__(self) -> str:
        return bech32_encode("age", self.public_key)


class X25519Identity:
    def __init__(self, secret_key: bytes):
        _require_crypto()
        if len(secret_key) != 32:
            raise ValueError("invalid X25519 secret key")
        self._private = X25519PrivateKey.from_private_bytes(secret_key)
        self.public_key = self._private.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )

    def unwrap(self, stanzas: list[Stanza]) -> bytes:
        saw_stanza = False
        last_err = None
        for stanza in stanzas:
            if stanza.stanza_type != "X25519":
                continue
            saw_stanza = True
            try:
                return self._unwrap(stanza)
            except IncorrectIdentity as exc:
                last_err = exc
                continue
        if last_err is not None:
            raise last_err
        if saw_stanza:
            raise IncorrectIdentity("no matching X25519 stanza")
        raise IncorrectIdentity("file does not contain X25519 stanzas")

    def _unwrap(self, stanza: Stanza) -> bytes:
        if len(stanza.args) != 1:
            raise ValueError("invalid X25519 recipient block")
        public_key = b64_decode(stanza.args[0])
        if len(public_key) != 32:
            raise ValueError("invalid X25519 recipient block")
        shared = self._private.exchange(X25519PublicKey.from_public_bytes(public_key))
        salt = public_key + self.public_key
        wrapping_key = hkdf_sha256(shared, salt, X25519_LABEL, 32)
        try:
            return aead_decrypt(wrapping_key, FILE_KEY_SIZE, stanza.body)
        except (InvalidTag, ValueError) as exc:
            raise IncorrectIdentity("incorrect identity for recipient block") from exc

    def recipient(self) -> X25519Recipient:
        return X25519Recipient(self.public_key)

    def __str__(self) -> str:
        encoded = bech32_encode("AGE-SECRET-KEY-", self._private.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption()
        ))
        return encoded.upper()


class ScryptRecipient:
    def __init__(self, password: str, work_factor: int = 18):
        if not password:
            raise ValueError("passphrase can't be empty")
        if work_factor < 1 or work_factor > 30:
            raise ValueError("invalid scrypt work factor")
        self.password = password.encode("utf-8")
        self.work_factor = work_factor

    def wrap(self, file_key: bytes) -> list[Stanza]:
        salt = os.urandom(16)
        log_n = self.work_factor
        args = [b64_encode(salt), str(log_n)]
        full_salt = SCRYPT_LABEL + salt
        key = scrypt_key(self.password, full_salt, 1 << log_n, SCRYPT_R, SCRYPT_P)
        wrapped = aead_encrypt(key, file_key)
        return [Stanza("scrypt", args, wrapped)]


class ScryptIdentity:
    def __init__(self, password: str, max_work_factor: int = 22):
        if not password:
            raise ValueError("passphrase can't be empty")
        if max_work_factor < 1 or max_work_factor > 30:
            raise ValueError("invalid max scrypt work factor")
        self.password = password.encode("utf-8")
        self.max_work_factor = max_work_factor

    def unwrap(self, stanzas: list[Stanza]) -> bytes:
        for stanza in stanzas:
            if stanza.stanza_type == "scrypt" and len(stanzas) != 1:
                raise ValueError("an scrypt recipient must be the only one")
        for stanza in stanzas:
            if stanza.stanza_type == "scrypt":
                return self._unwrap(stanza)
        raise IncorrectIdentity("file is not passphrase-encrypted")

    def _unwrap(self, stanza: Stanza) -> bytes:
        if len(stanza.args) != 2:
            raise ValueError("invalid scrypt recipient block")
        salt = b64_decode(stanza.args[0])
        if len(salt) != 16:
            raise ValueError("invalid scrypt recipient block")
        log_n_str = stanza.args[1]
        if not log_n_str.isdigit() or log_n_str.startswith("0"):
            raise ValueError(f"scrypt work factor encoding invalid: {log_n_str!r}")
        log_n = int(log_n_str)
        if log_n > self.max_work_factor:
            raise ValueError(f"scrypt work factor too large: {log_n}")
        full_salt = SCRYPT_LABEL + salt
        key = scrypt_key(self.password, full_salt, 1 << log_n, SCRYPT_R, SCRYPT_P)
        try:
            return aead_decrypt(key, FILE_KEY_SIZE, stanza.body)
        except (InvalidTag, ValueError) as exc:
            raise IncorrectIdentity("incorrect passphrase") from exc


def parse_recipient(text: str) -> X25519Recipient:
    if not text.startswith("age1"):
        raise ValueError(f"unknown recipient type: {text!r}")
    hrp, data = bech32_decode(text)
    if hrp != "age":
        raise ValueError(f"malformed recipient {text!r}: invalid type {hrp!r}")
    return X25519Recipient(data)


def parse_identity(text: str) -> X25519Identity:
    _require_crypto()
    if not text.startswith("AGE-SECRET-KEY-1"):
        raise ValueError(f"unknown identity type: {text!r}")
    hrp, data = bech32_decode(text)
    if hrp != "AGE-SECRET-KEY-":
        raise ValueError(f"malformed secret key: unknown type {hrp!r}")
    return X25519Identity(data)


def load_recipients(paths: list[str]) -> list[X25519Recipient]:
    recipients: list[X25519Recipient] = []
    for path in paths:
        if path == "-":
            lines = sys.stdin.read().splitlines()
        else:
            with open(path, "r", encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        for line in lines:
            if not line or line.startswith("#"):
                continue
            recipients.append(parse_recipient(line.strip()))
    if not recipients:
        raise ValueError("no recipients found")
    return recipients


def load_identities(paths: list[str]) -> list[X25519Identity]:
    identities: list[X25519Identity] = []
    for path in paths:
        if path == "-":
            lines = sys.stdin.read().splitlines()
        else:
            with open(path, "r", encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        for line in lines:
            if not line or line.startswith("#"):
                continue
            identities.append(parse_identity(line.strip()))
    if not identities:
        raise ValueError("no identities found")
    return identities


def encrypt_file(
    src: BinaryIO, dst: BinaryIO, recipients: Iterable
) -> None:
    _require_crypto()
    file_key = os.urandom(FILE_KEY_SIZE)
    stanzas: list[Stanza] = []
    for recipient in recipients:
        stanzas.extend(recipient.wrap(file_key))
    header = Header(stanzas)
    header.mac = header_mac(file_key, header)
    dst.write(marshal_header(header))
    nonce = os.urandom(STREAM_NONCE_SIZE)
    dst.write(nonce)
    encrypt_stream(src, dst, stream_key(file_key, nonce))


def decrypt_file(
    src: BinaryIO, dst: BinaryIO, identities: Iterable
) -> None:
    _require_crypto()
    header, payload = parse_header(src)
    file_key = None
    errors = []
    for identity in identities:
        try:
            file_key = identity.unwrap(header.recipients)
        except IncorrectIdentity as exc:
            errors.append(exc)
            continue
        break
    if file_key is None:
        raise NoIdentityMatchError(errors)
    expected = header_mac(file_key, header)
    if not hmac.compare_digest(expected, header.mac or b""):
        raise ValueError("bad header MAC")
    nonce = read_exact(payload, STREAM_NONCE_SIZE)
    if len(nonce) != STREAM_NONCE_SIZE:
        raise ValueError("failed to read nonce")
    decrypt_stream(payload, dst, stream_key(file_key, nonce))


def encrypt_bytes(plaintext: bytes, recipients: Iterable) -> bytes:
    buf_in = io.BytesIO(plaintext)
    buf_out = io.BytesIO()
    encrypt_file(buf_in, buf_out, recipients)
    return buf_out.getvalue()


def decrypt_bytes(ciphertext: bytes, identities: Iterable) -> bytes:
    buf_in = io.BytesIO(ciphertext)
    buf_out = io.BytesIO()
    decrypt_file(buf_in, buf_out, identities)
    return buf_out.getvalue()


def read_passphrase(confirm: bool) -> str:
    env = os.environ.get("AGE_PASSPHRASE")
    if env:
        return env
    first = getpass.getpass("Passphrase: ")
    if not first:
        raise ValueError("passphrase can't be empty")
    if confirm:
        second = getpass.getpass("Confirm passphrase: ")
        if first != second:
            raise ValueError("passphrases do not match")
    return first


def generate_keypair() -> tuple[str, str]:
    _require_crypto()
    private = X25519PrivateKey.generate()
    secret = private.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return bech32_encode("AGE-SECRET-KEY-", secret).upper(), bech32_encode(
        "age", public
    )


def open_input(path: Optional[str]) -> Tuple[io.BufferedReader, bool]:
    if path is None or path == "-":
        return sys.stdin.buffer, False
    return open(path, "rb"), True


def open_output(path: Optional[str]) -> Tuple[io.BufferedWriter, bool]:
    if path is None or path == "-":
        return sys.stdout.buffer, False
    return open(path, "wb"), True


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Python implementation of age-encryption.org/v1 (X25519 + scrypt)"
    )
    parser.add_argument("input", nargs="?", help="input file (default: stdin)")
    parser.add_argument("-o", "--output", help="output file (default: stdout)")
    parser.add_argument("-d", "--decrypt", action="store_true", help="decrypt input")
    parser.add_argument("-r", "--recipient", action="append", default=[], help="recipient")
    parser.add_argument(
        "-R", "--recipients-file", action="append", default=[], help="recipients file"
    )
    parser.add_argument(
        "-i", "--identity", action="append", default=[], help="identity file"
    )
    parser.add_argument("-p", "--passphrase", action="store_true", help="use passphrase")
    parser.add_argument(
        "--scrypt-work-factor",
        type=int,
        default=18,
        help="scrypt work factor for encryption",
    )
    parser.add_argument(
        "--scrypt-max-work-factor",
        type=int,
        default=22,
        help="maximum scrypt work factor for decryption",
    )
    parser.add_argument("--keygen", action="store_true", help="generate a keypair")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    _require_crypto()

    if args.keygen:
        secret, recipient = generate_keypair()
        sys.stdout.write(f"{secret}\n")
        sys.stderr.write(f"# public key: {recipient}\n")
        return 0

    encrypt_mode = not args.decrypt
    if encrypt_mode:
        recipients = []
        if args.passphrase:
            if args.recipient or args.recipients_file:
                raise ValueError("passphrase recipients cannot be mixed with others")
            passphrase = read_passphrase(confirm=True)
            recipients = [ScryptRecipient(passphrase, args.scrypt_work_factor)]
        else:
            recipients = [parse_recipient(r) for r in args.recipient]
            if args.recipients_file:
                recipients.extend(load_recipients(args.recipients_file))
            if not recipients:
                raise ValueError("no recipients specified")

        src, close_src = open_input(args.input)
        dst, close_dst = open_output(args.output)
        try:
            encrypt_file(src, dst, recipients)
        finally:
            if close_src:
                src.close()
            if close_dst:
                dst.close()
        return 0

    identities = []
    if args.identity:
        identities.extend(load_identities(args.identity))
    if args.passphrase:
        passphrase = read_passphrase(confirm=False)
        identities.append(ScryptIdentity(passphrase, args.scrypt_max_work_factor))
    if not identities:
        raise ValueError("no identities specified")

    src, close_src = open_input(args.input)
    dst, close_dst = open_output(args.output)
    try:
        decrypt_file(src, dst, identities)
    finally:
        if close_src:
            src.close()
        if close_dst:
            dst.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        sys.stderr.write(f"age.py: {exc}\n")
        raise SystemExit(1)
