try:
    # Prefer getting the installed package version when available
    from importlib.metadata import version as _get_version, PackageNotFoundError
except Exception:
    _get_version = None
    PackageNotFoundError = Exception

if _get_version is not None:
    try:
        __version__ = _get_version('arffutils')
    except PackageNotFoundError:
        __version__ = "0.1.0"
else:
    __version__ = "0.1.0"

from .arffutils import pandas_dataframe_to_arff, arff_to_pandas_dataframe, csv_to_arff, arff_to_csv

__all__ = ["pandas_dataframe_to_arff", "arff_to_pandas_dataframe", "csv_to_arff", "arff_to_csv"]