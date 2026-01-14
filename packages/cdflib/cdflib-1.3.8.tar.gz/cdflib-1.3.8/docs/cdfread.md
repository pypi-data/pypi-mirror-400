# cdfread

::: cdflib.cdfread

Sample Usage
------------

To begin accessing the data within a CDF file, first create a new CDF class.
This can be done with the following commands

```python
>>> import cdflib
>>> cdf_file = cdflib.CDF('/path/to/cdf_file.cdf')
```

Then, you can call various functions on the variable.

For example

```python
>>> x = cdf_file.varget("NameOfVariable", startrec = 0, endrec = 150)
```

This command will return all data inside of the variable ``Variable1``, from records 0 to 150.
