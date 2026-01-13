![Dragonfly](https://www.ladybug.tools/assets/img/dragonfly.png) ![DesignBuilder](https://avatars.githubusercontent.com/u/17565908?s=200&v=4)

[![Build Status](https://github.com/ladybug-tools/dragonfly-designbuilder/actions/workflows/ci.yaml/badge.svg)](https://github.com/ladybug-tools/dragonfly-designbuilder/actions)

[![Python 3.10](https://img.shields.io/badge/python-3.10-orange.svg)](https://www.python.org/downloads/release/python-3100/)

Dragonfly extension for translation to/from DesignBuilder.

Translation is accomplished using XML files following the
[DesignBuilder DsbXML Schema](https://github.com/DesignBuilderSoftware/db-dsbxml-schema).
Files can be imported to DesignBuilder using the [DsbXML Importer](https://designbuilder.co.uk/helpv2025.1/#ImportDesignBuilderXML.htm?TocPath=Get%2520Started%257CMenu%257CFile%2520Menu%257C_____2)

## Installation

`pip install -U dragonfly-designbuilder`

To check if the command line interface is installed correctly
use `dragonfly-designbuilder --help`.

## QuickStart

```console
import dragonfly_designbuilder
```

## [API Documentation](http://ladybug-tools.github.io/dragonfly-designbuilder/docs)

## Local Development

1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/dragonfly-designbuilder

# or

git clone https://github.com/ladybug-tools/dragonfly-designbuilder
```
2. Install dependencies:
```
cd dragonfly-designbuilder
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./dragonfly_designbuilder
sphinx-build -b html ./docs ./docs/_build/docs
```
