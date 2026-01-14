# gimu

A minimal toolkit and python library for modelling at Geothermal Institute, University of Auckland.

-----

## Table of Contents

- [Installation](#installation)
- [Commands](#Commands)
- [Related Packages](#related-packages)
- [License](#license)
- [Developer](#Developer)

## Installation

```console
pip install -U gimu
```

If you use conda, use the supplied `environment.yml` to create `py311-gimu`.  This installs packages using conda as much as possible before installing packages from PyPI.

```console
conda env create -f environment.yml
```

## Commands

### Convert SAVE file to INCON file

```console
save2incon a.save b.incon
```

NOTE this command is used during the scenario run.

## License

`gimu` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Developer

### Build and Publish

To bump version, create a tag, eg. `v0.1.0`

PyPI token is expected in `~/.pypirc`

If upload for the first time, create a PyPI account token, then add the token into `~/.pypirc`. Build and publish as normal, the PyPI project will be created on first upload.  Then revoke the account token.  Create a project token for later publishes.

Publish to PyPI:

```console
hatch build
hatch publish
```

### TODO

