# AEGIS Fast Checksums

A high-performance command-line tool for computing and verifying cryptographic checksums using the AEGIS=128X2 MAC primitive.

## Quick start


Install [UV](https://docs.astral.sh/uv/getting-started/installation/) and then install the tool:

```sh
uv tool install aegsum
```

Now you can use the installed `aegsum` tool, e.g. to checksum and verify:

```sh
aegsum * > .aegsum
aegsum --check .aegsum
```

The program processes all files of any directories passed as arguments, and will read from stdin when no files are passed.

### Options

- `-a, --alg ALGORITHM`: Specify the AEGIS algorithm (default: AEGIS-128X2)
- `-l, --long`: Use doubly long MAC tag for extra security (256 bits). When used with `-c`, only accepts long format checksums for verification.
- `-c, --check`: Verify checksums (using checksum file previously created or fed in via stdin)
- `-q, --quiet`: Don't print OK for each successfully verified file
- `-k, --key PASSWORD`: Use keyed MAC with the given password (key derived via SHA-512)
- `-h, --help`: Show help message

## Keyed Mode

The `-k` option enables keyed MAC mode, where checksums are computed using a secret keu:

```sh
aegsum -k mysecret file1.txt file2.txt > .aegsum
```

```sh
aegsum --check -k mysecret .aegsum
```

Each generation produces a different output, even for the same file and key. This is because a random nonce is included in each computation. Checksums can only be verified with the same password used to create them.

Unlike plain checksums which anyone can recompute, keyed checksums provide authentication—proving that someone with knowledge of the secret created or verified the files.

## Performance

AEGIS-128X2 provides exceptional performance, often achieving speeds above 10 GB/s, as opposed to 1-2 GB/s of traditional tools like `sha256sum`. The `aegsum` tool is designed to never be the bottle neck and producing results quickly. Other AEGIS alrogithms can be specified to optimize performance for a particular platform (where X4 may perform better than X2), and
