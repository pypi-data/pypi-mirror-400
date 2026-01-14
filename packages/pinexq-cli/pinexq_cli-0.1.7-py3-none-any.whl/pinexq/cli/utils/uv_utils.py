import subprocess


def is_uv_lockfile_up_to_date() -> bool:
    result = subprocess.run(
        ['uv', 'lock', '--check'],
        cwd='.',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.returncode == 0


