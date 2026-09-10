<!--
SPDX-License-Identifier: 0BSD
-->

# Meson Lefthook

[Lefthook](https://lefthook.dev) integration for Meson projects. During Meson
configuration, it downloads the selected native Lefthook release and checks its
SHA-256 checksum against the release manifest.

Supported hosts are Linux and macOS on x86_64 and aarch64.

## Add it to a project

Copy [`lefthook.wrap`](lefthook.wrap) to `subprojects/lefthook.wrap` in the
consuming project:

```ini
[wrap-git]
directory = lefthook
url = https://github.com/krxecs/meson-lefthook.git
revision = main
depth = 1

[provide]
program_names = lefthook
```

Meson downloads the repository when `find_program('lefthook')` cannot find a
host-installed executable. Replace `main` with a tag or commit hash when you
need a fixed revision.

Add a `lefthook.yml` file at the root of your project. For example:

```yaml
pre-commit:
  jobs:
    - run: meson test -C build
```

Find Lefthook in the top-level `meson.build` when another target needs it:

```meson
lefthook = find_program('lefthook', native: true)
```

The integration runs `lefthook install` during configuration. After you add
`lefthook.yml`, configure the project:

```sh
meson setup build
```

Disable automatic installation with the subproject option:

```sh
meson setup build -Dlefthook:install_git_hooks_by_default=false
```

The integration also provides `lefthook-install` for a manual reinstallation.
When this repository is configured on its own, run it with
`meson compile -C build lefthook-install`. When it is a subproject and the
build uses Ninja, run `ninja -C build lefthook@@lefthook-install`.

Lefthook reads `lefthook.yml` when it installs the hooks. Run a hook without a
Git commit with:

```sh
build/subprojects/lefthook/lefthook run pre-commit
```

## Select a Lefthook release

The default is Lefthook 2.1.12. Set the subproject option while configuring:

```sh
meson setup build -Dlefthook:lefthook_version=2.1.12
```

The downloader caches a verified executable and checksum in the Meson build
directory. Meson downloads it again when the selected version changes.

## License

Licensed under the BSD Zero Clause License. See [LICENSE.md](LICENSE.md).
