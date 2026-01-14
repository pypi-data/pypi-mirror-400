import os
import inspect
import subprocess
from unittest.mock import patch
from contextlib import contextmanager
from typing import ContextManager, Callable, Optional, List, ClassVar, Type
from psycopg2.extensions import AsIs
from psycopg2.extensions import cursor as _psycopg2_cursor
from psycopg2.extensions import connection as _psycopg2_connection
from psycopg2 import connect as _unmockable_psycopg2_connect

CursorType = Type[_psycopg2_cursor]
ConnectionType = Type[_psycopg2_connection]


def _in_autotest_env() -> bool:
    """
    Return true iff this script is being run by the autotester.

    This function can be used to check whether the AUTOTESTENV environment
    variable has been set to 'true'.
    """
    return os.environ.get("AUTOTESTENV") == "true"


def connection(*args, **kwargs):
    """
    Return a psycopg2 connection object

    If this function is called while being run by the autotester,
    any arguments passed to this function will be ignored and a connection will
    be made to the correct database in the autotester's run environment.

    If this function is called elsewhere, the arguments passed to this function
    will be used to call psycopg2.connect in order to connect to a database.
    """
    if _in_autotest_env():
        return _unmockable_psycopg2_connect(os.environ["DATABASE_URL"])
    return _unmockable_psycopg2_connect(*args, **kwargs)


@contextmanager
def patch_connection(target: str = "psycopg2.connect") -> ContextManager:
    """
    Context manager that patches any call to the function decribed in the
    <target> string with the connection function (in this module).

    See the documentation for unittest.mock.patch for a description of the
    format of the <target> string. By default, the function that will be
    mocked is the function called as psycopg2.connect. This function can
    also be used as a function decorator.

    >>> import psycopg2
    >>> with patch_connection():
    >>>     conn = psycopg2.connect()

    >>> from psycopg2 import connect
    >>> with patch_connection('__main__.connect'):
    >>>     conn = connect() # calls __main__._connection instead

    >>> import psycopg2
    >>> @patch_connection()
    >>> def f():
    >>>     conn = psycopg2.connect() # calls __main__._connection instead
    """
    with patch(target, side_effect=connection):
        yield
