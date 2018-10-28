""" Miscellaneous tools """

from subprocess import Popen, PIPE

import os
from os.path import join as pjoin, relpath, isdir, exists
import zipfile
import stat
import time


def back_tick(cmd, ret_err=False, as_str=True, raise_err=None):
    """ Run command `cmd`, return stdout, or stdout, stderr if `ret_err`

    Roughly equivalent to ``check_output`` in Python 2.7

    Parameters
    ----------
    cmd : sequence
        command to execute
    ret_err : bool, optional
        If True, return stderr in addition to stdout.  If False, just return
        stdout
    as_str : bool, optional
        Whether to decode outputs to unicode string on exit.
    raise_err : None or bool, optional
        If True, raise RuntimeError for non-zero return code. If None, set to
        True when `ret_err` is False, False if `ret_err` is True

    Returns
    -------
    out : str or tuple
        If `ret_err` is False, return stripped string containing stdout from
        `cmd`.  If `ret_err` is True, return tuple of (stdout, stderr) where
        ``stdout`` is the stripped stdout, and ``stderr`` is the stripped
        stderr.

    Raises
    ------
    Raises RuntimeError if command returns non-zero exit code and `raise_err`
    is True
    """
    if raise_err is None:
        raise_err = False if ret_err else True
    cmd_is_seq = isinstance(cmd, (list, tuple))
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=not cmd_is_seq)
    out, err = proc.communicate()
    retcode = proc.returncode
    cmd_str = " ".join(cmd) if cmd_is_seq else cmd
    if retcode is None:
        proc.terminate()
        raise RuntimeError(cmd_str + " process did not terminate")
    if raise_err and retcode != 0:
        raise RuntimeError(
            "{} returned code {} with error {}".format(
                cmd_str, retcode, err.decode("latin-1")
            )
        )
    out = out.strip()
    if as_str:
        out = out.decode("latin-1")
    if not ret_err:
        return out
    err = err.strip()
    if as_str:
        err = err.decode("latin-1")
    return out, err


def unique_by_index(sequence):
    """ unique elements in `sequence` in the order in which they occur

    Parameters
    ----------
    sequence : iterable

    Returns
    -------
    uniques : list
        unique elements of sequence, ordered by the order in which the element
        occurs in `sequence`
    """
    uniques = []
    for element in sequence:
        if element not in uniques:
            uniques.append(element)
    return uniques


def chmod_perms(fname):
    # Permissions relevant to chmod
    return stat.S_IMODE(os.stat(fname).st_mode)


def ensure_permissions(mode_flags=stat.S_IWUSR):
    """decorator to ensure a filename has given permissions.

    If changed, original permissions are restored after the decorated
    modification.
    """

    def decorator(f):
        def modify(filename, *args, **kwargs):
            m = chmod_perms(filename) if exists(filename) else mode_flags
            if not m & mode_flags:
                os.chmod(filename, m | mode_flags)
            try:
                return f(filename, *args, **kwargs)
            finally:
                # restore original permissions
                if not m & mode_flags:
                    os.chmod(filename, m)

        return modify

    return decorator


# Open filename, checking for read permission
open_readable = ensure_permissions(stat.S_IRUSR)(open)

# Open filename, checking for read / write permission
open_rw = ensure_permissions(stat.S_IRUSR | stat.S_IWUSR)(open)

# For backward compatibility
ensure_writable = ensure_permissions()


def zip2dir(zip_fname, out_dir):
    """ Extract `zip_fname` into output directory `out_dir`

    Parameters
    ----------
    zip_fname : str
        Filename of zip archive to write
    out_dir : str
        Directory path containing files to go in the zip archive
    """
    # Use unzip command rather than zipfile module to preserve permissions
    # http://bugs.python.org/issue15795
    back_tick(["unzip", "-o", "-d", out_dir, zip_fname])


def dir2zip(in_dir, zip_fname):
    """ Make a zip file `zip_fname` with contents of directory `in_dir`

    The recorded filenames are relative to `in_dir`, so doing a standard zip
    unpack of the resulting `zip_fname` in an empty directory will result in
    the original directory contents.

    Parameters
    ----------
    in_dir : str
        Directory path containing files to go in the zip archive
    zip_fname : str
        Filename of zip archive to write
    """
    z = zipfile.ZipFile(zip_fname, "w", compression=zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(in_dir):
        for file in files:
            in_fname = pjoin(root, file)
            in_stat = os.stat(in_fname)
            # Preserve file permissions, but allow copy
            info = zipfile.ZipInfo(in_fname)
            info.filename = relpath(in_fname, in_dir)
            # Set time from modification time
            info.date_time = time.localtime(in_stat.st_mtime)
            # See https://stackoverflow.com/questions/434641/how-do-i-set-permissions-
            # attributes-on-a-file-in-a-zip-file-using-pythons-zip/48435482#48435482
            # Also set regular file permissions
            perms = stat.S_IMODE(in_stat.st_mode) | stat.S_IFREG
            info.external_attr = perms << 16
            with open_readable(in_fname, "rb") as fobj:
                contents = fobj.read()
            z.writestr(info, contents, zipfile.ZIP_DEFLATED)
    z.close()


def find_package_dirs(root_path):
    """ Find python package directories in directory `root_path`

    Parameters
    ----------
    root_path : str
        Directory to search for package subdirectories

    Returns
    -------
    package_sdirs : set
        Set of strings where each is a subdirectory of `root_path`, containing
        an ``__init__.py`` file.  Paths prefixed by `root_path`
    """
    package_sdirs = set()
    for entry in os.listdir(root_path):
        fname = entry if root_path == "." else pjoin(root_path, entry)
        if isdir(fname) and exists(pjoin(fname, "__init__.py")):
            package_sdirs.add(fname)
    return package_sdirs


def cmp_contents(filename1, filename2):
    """ Returns True if contents of the files are the same

    Parameters
    ----------
    filename1 : str
        filename of first file to compare
    filename2 : str
        filename of second file to compare

    Returns
    -------
    tf : bool
        True if binary contents of `filename1` is same as binary contents of
        `filename2`, False otherwise.
    """
    with open_readable(filename1, "rb") as fobj:
        contents1 = fobj.read()
    with open_readable(filename2, "rb") as fobj:
        contents2 = fobj.read()
    return contents1 == contents2
