"""Cantrips - basic magic to bootstrap the nicer stuff"""

import sys, os, errno, autopep8, argparse, typing
from IPython.core.magic import Magics, magics_class, cell_magic, line_magic

def path_parents(path):
    """Iterate over the parent directories of path."""
    head, tail = os.path.split(path)
    while tail:
        yield head
        head, tail = os.path.split(head)



def project_root(*libnames):
    """Find a root directory with 'name' for the current working directory."""

    def is_root(head):
        python_match = set(path_parents(os.path.abspath(sys.executable)))
        p = os.path.join(head, *libnames)
        return p if (p in python_match
            or os.path.isdir(os.path.join(head, '.git'))
            or os.path.isdir(os.path.join(head, '.venv'))
            or os.path.exists(os.path.join(head, 'pyproject.toml'))) else None

    cwd = os.path.abspath(os.getcwd())
    p = is_root(cwd)
    if p:
        return p

    head, tail = os.path.split(cwd)
    p = None

    while len(tail) > 0:
        p = is_root(head) 
        if p:
            if os.path.isdir(p):
                return p
            break

        head, tail = os.path.split(head)

    raise FileNotFoundError(
        errno.ENOENT, 
        os.strerror(errno.ENOENT), 
        p
    )


class CantripsMagicWriter(typing.NamedTuple):
    write: typing.Callable


def create_exportfile_argparser():

    parser  = argparse.ArgumentParser(prog='cantrips', description='Cantrips - set_exportfile: prepare to export to a file speciifed by libfolder and python module-path', epilog='See [Custom IPython Magic](https://ipython.readthedocs.io/en/stable/config/custommagics.html) documentation')

    parser.add_argument('libfolder', help='the root folder for the code', default='')
    parser.add_argument('modulepath', help='the module path')
    parser.add_argument('-f', '--format', help='Format code using autopep8', action='store_true')
    parser.add_argument('-w', '--write', help='Write to a new file (default appends)', action='store_true')

    return parser

def extract_filepath(libfolder, modulepath):

    module_parts = modulepath.split('.')
    if libfolder and libfolder == module_parts[0]:
        module_parts.pop(0)

    return  os.path.join(
        project_root(libfolder), 
        os.path.join(*module_parts) 
    ) + '.py'

def create_writer(line_args):
    parser = create_exportfile_argparser()
    if isinstance(line_args, str):
        args = line_args.split(' ')
    else:
        args = line_args.copy()

    parsed_args = parser.parse_args(filter(lambda x: bool(x), args))

    filepath =  extract_filepath(parsed_args.libfolder, parsed_args.modulepath)

    reformat = lambda cell: autopep8.fix_code(cell) if parsed_args.format else cell  # noqa: E731

    if parsed_args.write:
        with open(filepath, 'w') as f:
            f.write("# This file is generated - do not edit\n")

    def write(cell_code):
        with open(filepath, 'a') as f:
            f.write(reformat(cell_code))

    return CantripsMagicWriter(write)


@magics_class
class CantripsMagic(Magics):

    @line_magic
    def set_exportfile(self, line):
        """Magic to export code from ipython notebook cells to python .py files"""
        self.writer = create_writer(line)

    @cell_magic
    def export(self, line, cell):
        self.shell.run_cell(cell)
        self.writer.write(cell)

def load_ipython_extension(ipython):
    ipython.register_magics(CantripsMagic)

__all__ = ['load_ipython_extension', 'CantripsMagic']

