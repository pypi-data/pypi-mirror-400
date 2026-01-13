#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import date

from apycalc import load_data, save_data, get_entry_1yago, compute_stats


def test_load_data() -> None:
    csv = textwrap.dedent('''\
        Date,Open,High,Low,Close,Adj Close,Volume
        2000-01-01,10,15,9,12,12,123
        2000-01-08,12,13.5,10.2,13,13,456
        2000-01-15,13,22.1,13,18.5,18,789
    ''')

    data = list(load_data(io.StringIO(csv)))

    assert data == [
        {'date': date(2000, 1, 1), 'rate': 10},
        {'date': date(2000, 1, 8), 'rate': 12},
        {'date': date(2000, 1, 15), 'rate': 13},
    ]

    data = list(load_data(io.StringIO(csv), krate='Close'))

    assert data == [
        {'date': date(2000, 1, 1), 'rate': 12},
        {'date': date(2000, 1, 8), 'rate': 13},
        {'date': date(2000, 1, 15), 'rate': 18.5},
    ]

    csv = textwrap.dedent('''\
        Date,Open
        2000-01-01,10
        2000-01-08,0
        2000-01-15,13
    ''')

    data = list(load_data(io.StringIO(csv)))

    assert data == [
        {'date': date(2000, 1, 1), 'rate': 10},
        {'date': date(2000, 1, 8), 'rate': 0},
        {'date': date(2000, 1, 15), 'rate': 13},
    ]

    data = list(load_data(io.StringIO(csv), fill_zeros=True))

    assert data == [
        {'date': date(2000, 1, 1), 'rate': 10},
        {'date': date(2000, 1, 8), 'rate': 10},
        {'date': date(2000, 1, 15), 'rate': 13},
    ]


def test_save_data() -> None:
    data = [
        {'date': date(2000, 1, 1), 'rate': 11, 'apy': 0.12, 'apyma': 0.13},
        {'date': date(2000, 1, 2), 'rate': 21, 'apy': 0.22, 'apyma': 0.23},
        {'date': date(2000, 1, 3), 'rate': 31, 'apy': 0.32, 'apyma': 0.33},
    ]

    csv = textwrap.dedent('''\
        Date,Rate,APY,APYMA
        2000-01-01,11,0.12,0.13
        2000-01-02,21,0.22,0.23
        2000-01-03,31,0.32,0.33
    ''')

    buf = io.StringIO()
    save_data(data, buf)
    buf.seek(0)

    assert buf.read() == csv

    csv = textwrap.dedent('''\
        Date,Rate,APY,APYMA
        2000-01-01,11.000,0.12,0.13
        2000-01-02,21.000,0.22,0.23
        2000-01-03,31.000,0.32,0.33
    ''')

    buf = io.StringIO()
    save_data(data, buf, fmt_rate='{:.3f}')
    buf.seek(0)

    assert buf.read() == csv

    csv = textwrap.dedent('''\
        Date,Rate,APY,APYMA
        2000-01-01,11,0.1200,0.1300
        2000-01-02,21,0.2200,0.2300
        2000-01-03,31,0.3200,0.3300
    ''')

    buf = io.StringIO()
    save_data(data, buf, fmt_yield='{:.4f}')
    buf.seek(0)

    assert buf.read() == csv


def test_get_entry_1yago() -> None:
    data = [
        {'date': date(2001, 1, 1), 'rate': 101},
        {'date': date(2001, 5, 5), 'rate': 105},
        {'date': date(2001, 9, 9), 'rate': 109},
        {'date': date(2002, 1, 1), 'rate': 201},
        {'date': date(2002, 4, 4), 'rate': 204},
        {'date': date(2002, 7, 7), 'rate': 207},
        {'date': date(2002, 10, 10), 'rate': 210},
    ]

    assert get_entry_1yago(data, 0) is None
    assert get_entry_1yago(data, 1) is None
    assert get_entry_1yago(data, 2) is None
    assert get_entry_1yago(data, 3) == {'date': date(2001, 1, 1), 'rate': 101}
    assert get_entry_1yago(data, 4) == {'date': date(2001, 1, 1), 'rate': 101}
    assert get_entry_1yago(data, 5) == {'date': date(2001, 5, 5), 'rate': 105}
    assert get_entry_1yago(data, 6) == {'date': date(2001, 9, 9), 'rate': 109}

    with pytest.raises(IndexError) as exc_info:
        get_entry_1yago(data, 7)
    assert exc_info.value.args == ('list index out of range',)


def test_compute_stats() -> None:
    data_in = [
        {'date': date(2001, 1, 1), 'rate': 101},
        {'date': date(2001, 5, 5), 'rate': 105},
        {'date': date(2001, 9, 9), 'rate': 109},
        {'date': date(2002, 1, 1), 'rate': 201},
        {'date': date(2002, 4, 4), 'rate': 204},
        {'date': date(2002, 7, 7), 'rate': 207},
        {'date': date(2002, 10, 10), 'rate': 210},
    ]

    data_in_copy = [x.copy() for x in data_in]
    data_out = list(compute_stats(data_in))
    assert data_in == data_in_copy
    assert data_out == [
        {'date': date(2002, 1, 1), 'rate': 201,
         'apy': 0.9900990099009901, 'apyma': 0.9900990099009901},
        {'date': date(2002, 4, 4), 'rate': 204,
         'apy': 1.0198019801980198, 'apyma': 1.004950495049505},
        {'date': date(2002, 7, 7), 'rate': 207,
         'apy': 0.9714285714285715, 'apyma': 0.9937765205091939},
        {'date': date(2002, 10, 10), 'rate': 210,
         'apy': 0.926605504587156, 'apyma': 0.9769837665286843},
    ]

    data_in_copy = [x.copy() for x in data_in]
    data_out = list(compute_stats(data_in, 2))
    assert data_in == data_in_copy
    assert data_out == [
        {'date': date(2002, 1, 1), 'rate': 201,
         'apy': 0.9900990099009901, 'apyma': 0.9900990099009901},
        {'date': date(2002, 4, 4), 'rate': 204,
         'apy': 1.0198019801980198, 'apyma': 1.004950495049505},
        {'date': date(2002, 7, 7), 'rate': 207,
         'apy': 0.9714285714285715, 'apyma': 0.9956152758132957},
        {'date': date(2002, 10, 10), 'rate': 210,
         'apy': 0.926605504587156, 'apyma': 0.9490170380078637},
    ]
