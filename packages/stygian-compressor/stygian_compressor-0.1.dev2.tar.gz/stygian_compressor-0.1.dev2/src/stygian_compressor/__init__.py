from dataclasses import dataclass
from functools import cache
import lzma
import os
import subprocess
import sys
from typing import IO, Any


@dataclass(frozen=True, slots=True)
class CompressorArgs:
    args: list[str] | None
    uses_stdout: bool
    popen_extras: dict[str, Any]


@cache
def _find(prog: str, paths: frozenset[str]) -> str | None:
    for path in paths:
        exe_file = os.path.join(path, prog)
        if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
            return exe_file
    return None


@cache
def _find_7zip() -> str | None:
    # see if the included 7zip is available (windows only)
    if sys.platform == "win32":
        is_64bit = sys.maxsize > (2 ** 32)
        if is_64bit:
            d = os.path.join(os.path.dirname(__file__), "7zip_64bit")
        else:
            d = os.path.join(os.path.dirname(__file__), "7zip_32bit")
        result = _find('7za.exe', frozenset([d]))
        if result:
            return result

    paths = os.environ["PATH"].split(os.pathsep)

    if sys.platform == "win32":
        program_files_keys = ['PROGRAMW6432', 'PROGRAMFILES',
                              'PROGRAMFILES(X86)']
        program_files_dirs: list[str] = []
        for key in program_files_keys:
            try:
                path = os.environ[key]
                if path:
                    program_files_dirs.append(path)
            except KeyError:
                pass

        for program_files in program_files_dirs:
            paths.append(os.path.join(program_files, "7-Zip"))

        progs = ['7zr.exe', '7za.exe', '7z.exe']
    else:
        progs = ['7zr', '7za', '7z']

    for prog in progs:
        result = _find(prog, frozenset(paths))
        if result:
            return result
    return None


@cache
def _find_xz() -> str | None:
    paths = frozenset(os.environ["PATH"].split(os.pathsep))
    if sys.platform == "win32":
        return _find("xz.exe", paths)
    else:
        return _find("xz", paths)


@cache
def get_compressor_args(compression_level: int) -> CompressorArgs:
    if sys.platform == "win32":
        # create a new process group so that ctrl+c doesn't get forwarded
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        popen_extras: dict[str, Any] = {
            'startupinfo': startupinfo,
            'creationflags': (subprocess.CREATE_NEW_PROCESS_GROUP |
                              subprocess.BELOW_NORMAL_PRIORITY_CLASS),
        }
    else:
        # stygian has this process in a different process group
        popen_extras: dict[str, Any] = {
            'preexec_fn': lambda: os.nice(10)
        }

    # find 7zip (7za, 7zr, 7z)
    compressor_path = _find_7zip()
    if compressor_path:
        return CompressorArgs(
            args=[
                compressor_path, 'a', '-si', '-txz', '-m0=lzma2',
                '-mx={}'.format(compression_level),
            ],
            # 7zip writes the file directly (and needs file at the end of args)
            uses_stdout=False,
            popen_extras=popen_extras,
        )

    # find xz
    compressor_path = _find_xz()
    if compressor_path:
        return CompressorArgs(
            args=[
                compressor_path, '-z', '-{}'.format(compression_level),
            ],
            # xz writes to stdout
            uses_stdout=True,
            popen_extras=popen_extras,
        )

    # fall back to internal lzma module
    return CompressorArgs(
        args=None,
        uses_stdout=False,
        popen_extras=popen_extras,
    )


def open_compressor(filename: str, compression_level: int) \
        -> tuple[IO[bytes], subprocess.Popen[bytes] | None]:
    compressor_args = get_compressor_args(compression_level)

    compressor_pipe: IO[bytes]

    if compressor_args.args is None:
        # fall back to internal lzma module
        output = lzma.open(filename, 'wb', preset=compression_level)
        process = None
        compressor_pipe = output
    else:
        if compressor_args.uses_stdout:
            with open(filename, "wb") as f:
                process = subprocess.Popen(
                    compressor_args.args, stdin=subprocess.PIPE, stdout=f,
                    stderr=subprocess.DEVNULL, text=False,
                    universal_newlines=False, encoding=None, errors=None,
                    **compressor_args.popen_extras)
        else:
            args = compressor_args.args.copy()
            args.append(filename)
            process = subprocess.Popen(
                args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, text=False,
                universal_newlines=False, encoding=None, errors=None,
                **compressor_args.popen_extras)
        if not process.stdin:
            raise ValueError("Process missing stdin")
        compressor_pipe = process.stdin

    return compressor_pipe, process


__all__ = ["open_compressor"]
