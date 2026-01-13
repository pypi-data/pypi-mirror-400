# apycalc

[![GitHub main workflow](https://img.shields.io/github/actions/workflow/status/dmotte/apycalc/main.yml?branch=main&logo=github&label=main&style=flat-square)](https://github.com/dmotte/apycalc/actions)
[![PyPI](https://img.shields.io/pypi/v/apycalc?logo=python&style=flat-square)](https://pypi.org/project/apycalc/)

:snake: [**APY**](https://www.investopedia.com/terms/a/apy.asp) (_Annual Percentage Yield_) **trend calculator**, with configurable MA (_Moving Average_).

> **Note**: APY is calculated over a period of **365 days**.

## Installation

This utility is available as a Python package on **PyPI**:

```bash
python3 -mpip install apycalc
```

## Usage

There are some files in the [`example`](example) directory of this repo that can be useful to demonstrate how this tool works, so let's change directory first:

```bash
cd example/
```

We need a Python **virtual environment** ("venv") with some packages to do the demonstration:

```bash
python3 -mvenv venv
venv/bin/python3 -mpip install -r requirements.txt
```

Now we need to **fetch data** related to some asset. To do that, we can use https://github.com/dmotte/misc/blob/main/python-scripts/ohlcv-fetchers/yahoo-finance.py.

> **Note**: in the following commands, replace the local path of the `invoke.sh` script with the correct one.

```bash
bash ~/git/misc/python-scripts/ohlcv-fetchers/invoke.sh yahoo-finance '^GSPC' -i1wk -d2000-01-01T00Z -f'{:.6f}' > ohlcv-SPX500.csv
```

Now that we have the data, we can **compute the APY and MA values**:

```bash
python3 -mapycalc -w104 --fmt-{rate,yield}='{:.6f}' ohlcv-SPX500.csv apy-SPX500.csv
```

And finally display some nice **plots** using the [`plots.py`](example/plots.py) script (which uses the [_Plotly_](https://github.com/plotly/plotly.py) Python library):

```bash
venv/bin/python3 plots.py -ra apy-SPX500.csv
```

For more details on how to use this command, you can also refer to its help message (`--help`).

## Development

If you want to contribute to this project, you can install the package in **editable** mode:

```bash
python3 -mpip install -e . --user
```

This will just link the package to the original location, basically meaning any changes to the original package would reflect directly in your environment ([source](https://stackoverflow.com/a/35064498)).

If you want to run the tests, you'll have to install the `pytest` package and then run:

```bash
python3 -mpytest test
```
