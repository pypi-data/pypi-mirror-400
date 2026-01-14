# cdflib

A python package to read CDF files without needing to install the CDF NASA library.

**Source**: [github](https://github.com/lasp/cdflib) | **Archive**: [zenodo](https://zenodo.org/record/4746617#.Y5NfWXbMKF4).

## Installing
cdflib requires python 3 and numpy. To install run

```bash
python3 -m pip install cdflib
```

## What is cdflib?

cdflib is an effort to replicate the CDF libraries using a pure python implementation.
This means users do not need to install the [CDF NASA libraries](https://cdf.gsfc.nasa.gov/).

The only module you need to install is `numpy`, but there are a few things you can do with `astropy` and `xarray`.

## What can cdflib do?

- Ability to read variables and attributes from CDF files (see [CDF Reading](cdfread.md))
- Writes CDF version 3 files (see [CDF Writing](cdfwrite.md))
- Can convert between CDF time types (EPOCH/EPOCH16/TT2000) to other common time formats (see [`CDF Time Conversions`](cdfepoch.md))
- Can convert CDF files into XArray Dataset objects and vice versa, attempting to maintain ISTP compliance (see [`Working with XArray`](xarray.md))
