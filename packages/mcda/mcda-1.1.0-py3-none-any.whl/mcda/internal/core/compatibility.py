"""This module contains wrappers to use instead of externally imported ones
for compatibility reasons.

They enable a broader compatibility of our package with its dependencies.
"""
from pandas import DataFrame

from .utils import package_version

if package_version("pandas") >= (2, 1, 0):  # pragma: nocover

    def dataframe_map(df: DataFrame, *args, **kwargs) -> DataFrame:
        """Wraps :meth:`DataFrame.map`.

        :param df:
        :param args: args passed to :meth:`DataFrame.map`
        :param kwargs: kwargs passed to :meth:`DataFrame.map`
        :return: result

        .. note::
            Only used internally to account for possible different versions of
            `pandas` installed (in this case, `pandas>=2.1.0`).
        .. seealso::
            `Method DataFrame.map <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.map.html>`_
                Documentation of wrapped method :meth:`DataFrame.map`.
        """  # noqa: E501
        return df.map(*args, **kwargs)

else:  # pragma: nocover

    def dataframe_map(df: DataFrame, *args, **kwargs) -> DataFrame:
        """Wraps :meth:`DataFrame.applymap`.

        :param df:
        :param args: args passed to :meth:`DataFrame.applymap`
        :param kwargs: kwargs passed to :meth:`DataFrame.applymap`
        :return: result

        .. note::
            Only used internally to account for possible different versions of
            `pandas` installed (in this case, `pandas<2.1.0`).
        .. seealso::
            `Method DataFrame.applymap <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.applymap.html>`_
                Documentation of wrapped method :meth:`DataFrame.applymap`.
        """  # noqa: E501
        return df.applymap(*args, **kwargs)  # type: ignore
