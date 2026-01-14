# Developing cdflib

## Developer Environment

Typically, development for cdflib is done right on github, using Github Codespaces. Codespaces is ultimately just a slightly fancier devcontainers, so you can also use your local system if you have devcontainers set up. However, CU has weird licensing agreements about Docker Desktop, so I try to avoid it altogether by using Codespaces.  As CU employees, we get 60 free hours of codespace use every month.

The setup that Codespaces uses is located in the .devcontainer folder. The devcontainer installs all requirements for cdflib, sets up precommit, and also starts up a virtual desktop. The reason we start a virtual desktop in the devcontainer is in case we want to perform any plotting with matplotlib. The plots will show up within the browser.

A new codespace should be created for every PR you are working on. Once the PR is merged, you should delete the codespace (in addition to the branch).

## Tests

Unit testing is simply done through pytest. All unit tests are located in the `/tests` folder.

### Remote Data

Some of the unit tests run using sample CDF files that need to be downloaded from the MAVEN Science Data Center website. To run these tests in particular, you can use the command:

```
pytest -m remote_data
```

However be warned, the test will take approximately 15 minutes to run with the ~20 or so CDF files that have caused issues at various points in development.

## Working on a Ticket

The recommended workflow when you want to work on a ticket:

1) Create a new branch (there should be a button to do so on the Github Issue page itself)
2) Start a new Codespace on the branch (again, there should be a button to do so after you create a branch)
3) Make your changes
4) If your changes have made significant alterations to the way CDF files are read/written, run `pytest -m remote_data` to perform unit tests on CDF files stored on the MAVEN SDC server.
5) Ensure your code passes the pre-commit checks (don't worry, it will tell you if you don't)
6) Create a new PR in the repository, and assign Bryan Harter as a reviewer.
7) Once I have approved changes, perform a "Squash and Merge", delete your branch, and delete your Codespace. (All of these should be a button in the page for your specific Pull Request)

## Documentation
Documentation is made using "mkdocs" whenever there is a new release of the library. See `.github/workflows/docs.yaml`.

The above script will update the branch `gh-pages` to build documentation from the markdown files in the "docs" folder. The configuration for mkdocs is located in the file `mkdocks.yaml` in the root directory of the project.

To build the documentation you will need to install the documentation requirements using

```
pip install .[docs]
```

If you have made changes to the documentation that you would like to check prior to merging, you can serve the documentation to yourself using

```
mkdocs serve
```

Note that this will work even on Codespaces. A pop-up will tell you that there is a new port that is open, and you can connect to it.

## Pre-commit

This repository is set up to run checks on the code prior to go being committed to git. The setup for pre-commit it in `pre-commit-config.yaml` in the root of the project. In particular, the key processes that run before a commit are

1) `Autoflake` to remove unused imports and variables. Configuration for autoflake is in the `.flake8` file in the root directory.
2) `isort` to keep imports in alphabetical order.
3) `Black` to restyle the code automatically.
4) `mypy` to use our static typing to check the code and ensure all types match the functions they are put in to. Configuration for mypy is in the `mypy.ini` file in the root directory.

## PyPI Release

New versions of cdflib are released onto PyPI at [https://pypi.org/project/cdflib/](https://pypi.org/project/cdflib/).

This project lives under LASP's PyPI organization, so all members and admins from that organization can make modifications to the PyPI project. The LASP PyPI organization is run by LASP's Data Systems division.

New versions are released to PyPI when a Github release occurs, see the workflow in `.github/workflows/pypi-build.yaml`. There are no secret keys required; PyPI has been configured to trust deployments from `https://github.com/lasp/cdflib/.github/workflows/pypi-build.yaml`.

### Versioning
The package version is automatically determined using [setuptools_scm](https://github.com/pypa/setuptools_scm), so does not need to be manually incremented when doing a new release.
