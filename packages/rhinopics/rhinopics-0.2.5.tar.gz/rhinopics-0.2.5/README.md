# rhinopics
> Rhinopics, let the fat unicorn rename your pics!

<p align="left">
    <a href="https://pypi.org/project/rhinopics/">
        <img src="https://img.shields.io/pypi/v/rhinopics.svg" alt="latest release" /></a>
    <a href="https://travis-ci.com/axelfahy/rhinopics">
        <img src="https://api.travis-ci.com/axelfahy/rhinopics.svg?branch=master" alt="Build Status" /></a>
    <a href="https://pypi.org/project/rhinopics/">
        <img src="https://img.shields.io/badge/python-3.6-blue.svg" alt="Python36" /></a>
</p>

Python CLI application to rename pictures.

The date of the pictures is retrieved from the metadata of the files and concatenate with a given word to create the new name.

Example of output: `word_20190621_001`

A number is added at the end in chronological order, the number of digits depends on the number of pictures having the same date or being in the folder.

## Installation

```sh
pip install rhinopics
```

## Usage example
Examples are available in the docstrings of the functions. Official documentation will soon come out, or not.

## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
git clone https://github.com/axelfahy/rhinopics.git
cd rhinopics
python -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements_dev.txt
pip install -e .
```

## Tests

```sh
python tests/test_rhinopics.py
```

## Meta

Axel Fahy – axel@fahy.net

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/axelfahy](https://github.com/axelfahy)

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Version number

The version of the package is link to the tag pushed.

To set a new version:

```sh
git tag v0.1.1
git push --tags
```
