#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import stat
import tempfile
from urllib.request import urlopen


RELEASES_URL = 'https://github.com/evilmartians/lefthook/releases/download'
REQUEST_TIMEOUT_SECONDS = 15
ASSET_SUFFIXES = {
    ('linux', 'x86_64'): 'Linux_x86_64',
    ('linux', 'aarch64'): 'Linux_aarch64',
    ('darwin', 'x86_64'): 'MacOS_x86_64',
    ('darwin', 'aarch64'): 'MacOS_arm64',
}


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def cached_checksum(path: Path) -> str | None:
    try:
        checksum = path.read_text(encoding='ascii').strip()
    except FileNotFoundError:
        return None
    if len(checksum) == 64 and all(character in '0123456789abcdef' for character in checksum):
        return checksum
    return None


def release_checksum(release_url: str, asset: str) -> str:
    with urlopen(
        release_url + '/lefthook_checksums.txt', timeout=REQUEST_TIMEOUT_SECONDS
    ) as response:
        for line in response.read().decode('utf-8').splitlines():
            checksum, filename = line.split(maxsplit=1)
            if filename == asset:
                return checksum
    raise RuntimeError(f'Lefthook checksum manifest does not contain {asset}.')


def download_lefthook(
    output_path: Path, version: str, system: str, cpu_family: str
) -> None:
    checksum_path = output_path.with_name(output_path.name + '.sha256.' + version)

    try:
        asset_suffix = ASSET_SUFFIXES[(system, cpu_family)]
    except KeyError as error:
        raise RuntimeError(
            f'No Lefthook executable is configured for {system} {cpu_family}.'
        ) from error

    release_url = f'{RELEASES_URL}/v{version}'
    asset = f'lefthook_{version}_{asset_suffix}'
    expected_hash = cached_checksum(checksum_path)
    if output_path.is_file() and expected_hash is not None and sha256sum(output_path) == expected_hash:
        output_path.chmod(output_path.stat().st_mode | stat.S_IXUSR)
        return

    expected_hash = release_checksum(release_url, asset)
    if output_path.is_file() and sha256sum(output_path) == expected_hash:
        output_path.chmod(output_path.stat().st_mode | stat.S_IXUSR)
        checksum_path.write_text(expected_hash + '\n', encoding='ascii')
        return

    asset_url = release_url + '/' + asset

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent,
            prefix=output_path.name + '.tmp.',
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            with urlopen(asset_url, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    temporary_file.write(chunk)

        if sha256sum(temporary_path) != expected_hash:
            raise RuntimeError('Downloaded Lefthook executable has an unexpected SHA-256 hash.')

        temporary_path.chmod(temporary_path.stat().st_mode | stat.S_IXUSR)
        os.replace(temporary_path, output_path)
        checksum_path.write_text(expected_hash + '\n', encoding='ascii')
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Download and verify a Lefthook executable.'
    )
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--system', required=True)
    parser.add_argument('--cpu-family', required=True)
    arguments = parser.parse_args()
    download_lefthook(
        arguments.output,
        arguments.version,
        arguments.system,
        arguments.cpu_family,
    )


if __name__ == '__main__':
    main()
