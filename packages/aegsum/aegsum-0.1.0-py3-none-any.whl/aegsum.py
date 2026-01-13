import argparse
import base64
import hashlib
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import aeg
import base64url
import tracerite

tracerite.load()

DEFAULT_ALG, CHUNK_SIZE = "AEGIS-128X2", 1 << 20
GREEN, RED, RESET = ("\033[32m", "\033[31m", "\033[0m") if sys.stdout.isatty() else ("", "", "")


def warn(warnings):
    if warnings:
        sys.stderr.write("⚠️  " + "\n   ".join(warnings) + "\n")


def plural(n, word, suffix="s"):
    return f"{n} {word}{suffix if n != 1 else ''}"


def format_grouped(errors, threshold=5):
    return [
        f"{msg}: {', '.join(files) if len(files) <= threshold else f'({len(files)} files)'}"
        for msg, files in errors.items()
    ]


def derive_key(key_string, ciph):
    return hashlib.sha512(key_string.encode()).digest()[: ciph.KEYBYTES]


def compute_mac(f, ciph, use_long, buffer, key=None):
    nonce = ciph.random_nonce() if key else bytes(ciph.NONCEBYTES)
    mac = ciph.Mac(
        key or bytes(ciph.KEYBYTES),
        nonce,
        ciph.MACBYTES_LONG if use_long else ciph.MACBYTES,
    )
    mv, total, gb, next_report, start = memoryview(buffer), 0, 1 << 30, 1 << 30, time.perf_counter()
    while n := f.readinto(buffer):
        mac.update(mv[:n])
        total += n
        if total >= next_report:
            sys.stderr.write(
                f"{total // gb} GB  {total / (time.perf_counter() - start) / 1e9:.2f} GB/s\r"
            )
            next_report += gb
    if total >= gb:
        sys.stderr.write("\n")
    if key:
        return base64url.enc(b"k" + nonce + mac.digest())
    return mac.hexdigest()


def is_keyed_checksum(checksum):
    """Detect if a checksum is in keyed format (base64url with b'k' prefix inside)."""
    try:
        return base64url.dec(checksum).startswith(b"k")
    except Exception:
        return False


def verify_file(fn, expected, ciph, buffer, key):
    """Verify a single file. Returns bool."""
    if is_keyed_checksum(expected):
        decoded = base64.urlsafe_b64decode(expected)[1:]  # Strip b'k' prefix
        nonce, expected_mac = decoded[: ciph.NONCEBYTES], decoded[ciph.NONCEBYTES :]
        with open(fn, "rb", buffering=0) as f:
            mac = ciph.Mac(key, nonce, len(expected_mac))
            mv = memoryview(buffer)
            while n := f.readinto(buffer):
                mac.update(mv[:n])
            return mac.digest() == expected_mac
    use_long = len(expected) == 64
    with open(fn, "rb", buffering=0) as f:
        return compute_mac(f, ciph, use_long, buffer) == expected


class CheckResult:
    OK = "ok"
    FAILED = "Checksum did NOT match"
    BAD_FORMAT = "Checksum did not have the required format (--long)"
    NO_KEY = "Cannot be verified without correct --key"


def check_single_file(fn, expected, ciph, buffer, require_long, key):
    """Check a single file against its expected checksum.
    Returns (result: CheckResult, error_msg: str|None)."""
    is_keyed = is_keyed_checksum(expected)
    if is_keyed and key is None:
        return CheckResult.NO_KEY, None
    if require_long:
        if is_keyed:
            decoded = base64.urlsafe_b64decode(expected)[1:]
            is_short = len(decoded) - ciph.NONCEBYTES == ciph.MACBYTES
        else:
            is_short = len(expected) == 32
        if is_short:
            return CheckResult.BAD_FORMAT, None
    try:
        ok = verify_file(fn, expected, ciph, buffer, key)
    except OSError as e:
        return None, os.strerror(e.errno or 0)
    return CheckResult.OK if ok else CheckResult.FAILED, None


def check_checksums(files, ciph, buffer, require_long, quiet, key=None, zero_terminated=False):
    """Verify checksums from files or stdin. Returns (has_errors, warnings)."""
    errors, warnings, bad_lines = defaultdict(list), [], 0

    for cf in files:
        try:
            data = sys.stdin.buffer.read() if cf is None else Path(cf).read_bytes()
            line_bytes = data.split(b"\0" if b"\0" in data else b"\n")
            lines = [lb.decode() for lb in line_bytes if lb]
        except OSError as e:
            errors[os.strerror(e.errno or 0)].append(cf or "stdin")
            continue
        except UnicodeDecodeError:
            errors["Checksum file isn't valid text"].append(cf or "stdin")
            continue
        for line in lines:
            if not (line := line.strip()) or line.startswith("#"):
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                bad_lines += 1
                continue
            expected, fn = parts[0].strip(), parts[1]
            is_keyed = is_keyed_checksum(expected)
            if not is_keyed and len(expected) not in (32, 64):
                bad_lines += 1
                continue

            result, err_msg = check_single_file(fn, expected, ciph, buffer, require_long, key)

            if result == CheckResult.OK:
                if not quiet:
                    print(f"{fn}: {GREEN}OK{RESET}", end="\0" if zero_terminated else "\n")
            else:
                print(f"{fn}: {RED}FAILED{RESET}", end="\0" if zero_terminated else "\n")
                errors[err_msg or result].append(fn)

    if bad_lines:
        warnings.append(plural(bad_lines, "line") + " improperly formatted")
    warnings.extend(format_grouped(errors, 8))
    return bool(bad_lines or errors), warnings


def compute_checksums(files, ciph, buffer, use_long, key=None, zero_terminated=False):
    """Compute checksums for files or stdin."""
    errors = defaultdict(list)
    for fn in files:
        try:
            with (
                open(sys.stdin.fileno(), "rb", buffering=0, closefd=False)
                if fn is None
                else open(fn, "rb", buffering=0)
            ) as f:
                tag = compute_mac(f, ciph, use_long, buffer, key)
            print(tag if fn is None else f"{tag}  {fn}", end="\0" if zero_terminated else "\n")
        except OSError as e:
            errors[os.strerror(e.errno or 0)].append(fn or "stdin")
    return errors


def parse_args():
    p = argparse.ArgumentParser(description="Compute AEGIS MAC checksum")
    p.add_argument(
        "-a", "--alg", default=DEFAULT_ALG, help=f"Cipher algorithm (default: {DEFAULT_ALG})"
    )
    p.add_argument("-l", "--long", action="store_true", help="Use long MAC format (256 bits)")
    p.add_argument(
        "-c", "--check", action="store_true", help="Read checksums from files and verify them"
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Don't print OK for each successfully verified file",
    )
    p.add_argument(
        "-k",
        "--key",
        type=str,
        default=None,
        help="Use keyed MAC with the given password (key derived via SHA-512)",
    )
    p.add_argument(
        "-z",
        "--zero",
        action="store_true",
        help="Terminate all stdout lines with \\0 rather than \\n",
    )
    p.add_argument("files", nargs="*", help="Input files (default: stdin)")
    return p.parse_intermixed_args()


def main():
    try:
        args = parse_args()
        ciph = aeg.cipher(args.alg)
        buffer = bytearray(CHUNK_SIZE)
        key = derive_key(args.key, ciph) if args.key else None
        files = []
        for f in args.files or [None]:
            if f and Path(f).is_dir():
                files.extend(str(p) for r, _, fs in os.walk(f) for p in (Path(r) / x for x in fs))
            else:
                files.append(f)

        if args.check:
            has_errors, warnings = check_checksums(
                files, ciph, buffer, args.long, args.quiet, key, args.zero
            )
            warn(warnings)
            if has_errors:
                sys.exit(1)
        else:
            errors = compute_checksums(files, ciph, buffer, args.long, key, args.zero)
            if errors:
                warn(format_grouped(errors, 3))
                sys.exit(1)
    except (KeyboardInterrupt, BrokenPipeError):
        sys.exit(1)


if __name__ == "__main__":
    main()
