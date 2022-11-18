# mivp-agent

This repository contains the Python code required to run mivp-agent agents.

## Local Installation

```
git clone https://github.com/mivp-agent/mivp-agent.git
```

Install in editable mode...

```
pip install -e .
```

Install the testing and linting "extras".

```
pip install -e '.[test]'
pip install -e '.[lint]'
```

## Contributing

Pull requests are very welcome for bug fixes and feature additions. The only requests would be to...

1. If you intended to add a feature, please open a issue on this repository first so a discussion can be had.
2. Run the testing a linting before submitting a PR (they will be run automatically by GitHub too)

## Running tests

```
cd test
./test_all.py
```

## Running the linter

```
flake8 src test
```