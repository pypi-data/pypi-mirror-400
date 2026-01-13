<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/opensemantic.svg?branch=main)](https://cirrus-ci.com/github/<USER>/opensemantic)
[![ReadTheDocs](https://readthedocs.org/projects/opensemantic/badge/?version=latest)](https://opensemantic.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/opensemantic/main.svg)](https://coveralls.io/r/<USER>/opensemantic)
[![PyPI-Server](https://img.shields.io/pypi/v/opensemantic.svg)](https://pypi.org/project/opensemantic/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/opensemantic.svg)](https://anaconda.org/conda-forge/opensemantic)
[![Monthly Downloads](https://pepy.tech/badge/opensemantic/month)](https://pepy.tech/project/opensemantic)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/opensemantic)
-->

[![PyPI-Server](https://img.shields.io/pypi/v/opensemantic.svg)](https://pypi.org/project/opensemantic/)
[![Coveralls](https://img.shields.io/coveralls/github/OpenSemanticWorld-Packages/opensemantic/main.svg)](https://coveralls.io/r/OpenSemanticWorld-Packages/opensemantic)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# opensemantic

> This is the top-level Python namespace package for libraries with Python models derived from page packages that reside under world.opensemantic

To mimic the hierarchy and naming conventions of the page packages listed under [OpenSemanticWorld-Packages]
(https://github.com/OpenSemanticWorld-Packages), we have created this namespace package. Eventually it will contain
own Python modules that represent dependencies of the subpackages later on.

All the page packages that share the prefix `world.opensemantic` will be placed under this namespace package. This
'plugged-in packages' or 'subpackages' will state this package as a dependency in their `setup.cfg` file.

## A short primer on namespace packages

Namespace packages are a way to split a single Python package across multiple directories (or repositories). In our
case, this is useful because it allows to create a modular library of packages that can be developed and maintained
independently.

A standard Python package with `src` layout, created with the `pyscaffold` command line tool, could look like this:
```
projectname/  <- repository name, usually the same as the package name
├─ src/
│  └─ packagename/
│     ├─ __init__.py
|     ├─ modulename.py
|     ├─ submodulename1/
|     |  ├─ __init__.py
|     |  └─ module_within_submodule1.py
|     └─ submodulename2/
|        ├─ __init__.py
|        └─ module_within_submodule2.py
├─ setup.cfg
├─ setup.py
└─ ...
```

Namespace packages allow to split this up into separate repositories, while still being able to import the
submodules into a shared namespace as before. The `world.opensemantic` namespace package is an example of this.

The namespace package:
```
projectname/  <- repository name, usually the same as the package name
├─ src/
│  └─ packagename/
│     └─ ...  <- no __init__.py file required if no Python modules are contained on this level
├─ setup.cfg
├─ setup.py
└─ ...
```
The 'plugged-in' subpackage1:
```
other_projectname1/
├─ src/
│  └─ packagename/
|     └─ submodulename1/
|        ├─ __init__.py
|        └─ module_within_submodule1.py
├─ setup.cfg
├─ setup.py
└─ ...
```
The 'plugged-in' subpackage2:
```
other_projectname2/
├─ src/
│  └─ packagename/
|     └─ submodulename2/
|        ├─ __init__.py
|        └─ module_within_submodule2.py
├─ setup.cfg
├─ setup.py
└─ ...
```

Note: If an (implicit) namespace package contains own Python modules, those become unavailable on the installation of subpackages into this namespace. To avoid this, the namespace package must deviate from the implicit namespace package approach, described in [PEP 420](https://peps.python.org/pep-0420/), and contain an `__init__.py` file with the following content:
```python
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
```

## Create a new subpackage

To create a new subpackage, you can use the `PyScaffold` command line tool. For example, to create a new subpackage
called `world.opensemantic.example`, you can run the following command:
```bash
putup packagename.submodulename --package submodulename --namespace packagename -i
```
Here is an example of the complete command used to create the `opensemantic.core` package:
```bash
putup opensemantic.core-python --package core --namespace opensemantic --no-skeleton --markdown --pre-commit --github-actions --license AGPL-3.0-only --url https://github.com/OpenSemanticWorld-Packages/opensemantic.core-python --description "Library with Python models derived from the page package world.opensemantic.core" -i
```
Breaking down the command:
- `putup`: calls the `PyScaffold` command line tool
- `opensemantic.core-python`: the name of the package (directory) to be created
- `--package core`: the name of the subpackage to be created
- `--namespace opensemantic`: the namespace package under which the subpackage will be placed
- `--no-skeleton`: do not create a skeleton for the package
- `--markdown`: use Markdown formatting throughout the package
- `--pre-commit`: set up pre-commit hooks
- `--github-actions`: set up GitHub Actions, for automated publishing to PyPI
- `--license AGPL-3.0-only`: set the license to AGPL-3.0-only
- `--url ...`: the URL of the repository
- `--description ...`: a short description of the package, same as the repository description
- `-i`: interactive mode, to confirm the settings in your default text editor. Save and close the editor to continue
  package creation

After package creation we advise to:
- Make adjustments to the `setup.cfg`
  - Add the repository url to the `project_urls` section (update `Documentation = ...`)
  - Set `python_requires = >=3.8`
  - Remove the line `importlib-metadata; python_version<"3.8"` from the `install_requires` list
  - Add `opensemantic` and other requirements to the `install_requires` list
- Change the `__init__.py` accordingly:
  - Remove content required for python 3.7 and below
  - Add the following content, if the subpackage should also act as a namespace package for other sub-subpackages:
    ```python
    from pkgutil import extend_path

    __path__ = extend_path(__path__, __name__)
    ```
- In the terminal, run:
  - `pre-commit autoupdate` to update the pre-commit hooks
  - `pre-commit run --all-files` to run the pre-commit hooks on all files so that the whole repository complies with the updated hooks
  - `git remote add origin <repository git URL>` to add the remote repository URL`
- Now commit and push the changes to the repository
- (Passive) Continuous Integration (CI) is set up with GitHub Actions, so the CI pipeline will run automatically on
  push and publish this package to PyPI if the pipeline is successful.
- If it fails, consult the logs and fix the issues (e.g. PyPI token missing in repo/org secrets, etc.)


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
