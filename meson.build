project('lefthook', meson_version: '>=1.1.0')

lefthook_version = get_option('lefthook_version')
lefthook_path = meson.current_build_dir() / 'lefthook'
run_command(
  find_program('python3', native: true),
  meson.current_source_dir() / 'download-lefthook.py',
  '--output',
  lefthook_path,
  '--version',
  lefthook_version,
  '--system',
  build_machine.system(),
  '--cpu-family',
  build_machine.cpu_family(),
  check: true,
)
lefthook = find_program(lefthook_path)
meson.override_find_program('lefthook', lefthook)

shell = find_program('sh', native: true)
lefthook_command = [
  shell,
  '-c',
  'cd "$1" && shift && exec "$@"',
  'sh',
  meson.global_source_root(),
  lefthook,
]

if get_option('install_git_hooks_by_default')
  run_command(lefthook_command + ['install'], check: true)
endif

run_target(
  'lefthook-install',
  command: lefthook_command + ['install'],
)
