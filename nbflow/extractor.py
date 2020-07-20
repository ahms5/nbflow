from __future__ import print_function
import os
import glob
import json
import sys

from nbformat.v4 import reads
from traitlets.config import Application, Unicode

from ._version import __version__


class DependencyExtractor(Application):

    name = 'nbflow'
    description = 'Extract the hierarchy of dependencies from notebooks in the specified folder.'
    version = __version__

    def parameters_to_dict(self, params):
        globals_dict = {}
        locals_dict = {}
        exec(params, globals_dict, locals_dict)
        return locals_dict

    def extract_parameters_script(self, script):
        with open(script) as file:
            text = ''
            keep = False
            for line in file:
                if ('__depends__' in line) or ('__requires__' in line):
                    keep = True
                elif ('# %%' in line) and (keep == True):
                    break
                if keep:
                    text += line
        return self.parameters_to_dict(text)

    def extract_parameters_notebook(self, filename):
        with open(filename, "r") as fh:
            nb = reads(fh.read())

        # find the first code cell
        defs_cell = None
        for cell in nb.cells:
            if cell.cell_type == 'code':
                defs_cell = cell
                break

        if defs_cell is None:
            return {}

        return self.parameters_to_dict(defs_cell.source)

    def resolve_path(self, source, path):
        dirname = os.path.dirname(source)
        return os.path.abspath(os.path.join(dirname, path))

    def get_dependencies(self, dirnames):
        dependencies = {}

        for dirname in dirnames:
            files_nb = glob.glob("{}/*.ipynb".format(dirname))
            files_py = glob.glob("{}/*.py".format(dirname))

            files = files_nb + files_py

            for filename in files:
                modname, ext = os.path.splitext(os.path.basename(filename))

                if ext == '.py':
                    params = self.extract_parameters_script(filename)

                elif ext == '.ipynb':
                    params = self.extract_parameters_notebook(filename)
                else:
                    raise(ValueError("Wrong format: {}".format(ext)))

                if '__depends__' not in params:
                        continue
                if '__dest__' not in params:
                    raise ValueError(
                        "__dest__ is not defined in {}".format(filename))

                # get sources that are specified in the file
                sources = [self.resolve_path(filename, x) for x in params['__depends__']]

                targets = params['__dest__']
                if not isinstance(targets, list):
                    if targets is None:
                        targets = []
                    else:
                        targets = [targets]
                targets = [self.resolve_path(filename, x) for x in targets]

                dependencies[filename] = {
                    'targets': targets,
                    'sources': sources
                }

        return json.dumps(dependencies, indent=2)

    def start(self):
        if len(self.extra_args) == 0:
            self.log.error("No directory names specified.")
            sys.exit(1)

        print(self.get_dependencies(self.extra_args))


def main():
    DependencyExtractor.launch_instance()
