# arffutils
Python library to convert from and to ARFF files

# Installation
Currently the package is under development, so one can install it using the command:  
`pip install https://github.com/thdiaman/arffutils/tarball/master`

# Running
The package contains four functions:
- pandas_dataframe_to_arff: receives as input a pandas dataframe and writes it to disk as an ARFF file.
- arff_to_pandas_dataframe: receives as input the path to an ARFF file and returns a pandas dataframe.
- csv_to_arff: receives as input the path to a CSV file and writes an ARFF file.
- arff_to_csv: receives as input the path to an ARFF file and writes a CSV file.

One can import any of the above functions and run it. For example, to convert an ARFF file to CSV, one can write:
```
from arffutils import arff_to_csv
arff_to_csv("example.arff", "example.csv")
```

Examples can be found in directory tests.
