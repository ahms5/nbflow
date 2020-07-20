import subprocess as sp
import sys
import os

from nbconvert.preprocessors import ClearOutputPreprocessor
from nbformat import read, write
from nbformat.v4 import new_notebook, new_code_cell
from copy import deepcopy


def run_command(cmd, retcode=0):
    if sys.platform == 'win32':
        # shell=True required on windows to run scons using subprocess
        shell = True
    else:
        shell = False
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, shell=shell)
    code = p.wait(timeout=120)
    stdout, _ = p.communicate(timeout=120)
    stdout = stdout.replace(b"\x1b[?1034h", b"")
    if code != retcode:
        print(stdout)
        raise RuntimeError("command returned unexpected code: {}".format(code))

    return stdout


def clear_notebooks(root):
    """Clear the outputs of documentation notebooks."""

    preprocessor = ClearOutputPreprocessor()

    for dirpath, dirnames, filenames in os.walk(root):

        for filename in sorted(filenames):
            if os.path.splitext(filename)[1] == '.ipynb':
                # read in the notebook
                pth = os.path.join(dirpath, filename)
                with open(pth, 'r') as fh:
                    orig_nb = read(fh, 4)

                # copy the original notebook
                new_nb = deepcopy(orig_nb)

                # check outputs of all the cells
                new_nb = preprocessor.preprocess(new_nb, {})[0]

                # clear metadata
                new_nb.metadata = {}

                # write the notebook back to disk
                with open(pth, 'w') as fh:
                    write(new_nb, fh, 4)


def create_notebook(name, cells):
    nb = new_notebook()
    for cell in cells:
        nb.cells.append(new_code_cell(source=cell))

    with open(name, "w") as fh:
        write(nb, fh, 4)
