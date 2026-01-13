import pyodbc
import os
import re
from dotenv import load_dotenv


def build_connection(env: str = None, override: bool = False) -> pyodbc.Connection:
    """
    Builds and establishes a connection to the SQL Server database using environment
    variables for configuration. The function can load the environment variables from
    a specified file or directly from the existing environment.

    Parameters:
    :param env: Optional file location of the environment file to load. If not provided,
        variables are read from the current environment.
    :param override: A flag that determines whether environment variables should be
        overwritten if they are already set.

    Returns:
    :return: A `pyodbc.Connection` object representing the connection to the database.
    """
    if env:
        load_dotenv(env, override=override)
    else:
        load_dotenv(override=override)

    SQL_SERVER = os.getenv("SQL_HOST")
    SQL_PORT = int(os.getenv("SQL_PORT"))
    SQL_USER = os.getenv("SQL_USER")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SQL_SERVER},{SQL_PORT};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USER};"
        f"PWD={SQL_PASSWORD};"
        "Encrypt=yes;"
        "HostNameInCertificate=svsql1.database.windows.net;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    return pyodbc.connect(conn_str)

def named_params(sql: str, params: dict) -> tuple[str, list]:
    """
    Translates a SQL query with named parameters into a statement with positional
    parameters and provides the corresponding arguments list.

    Given a SQL query string with named parameters in the format `:param_name`
    and a dictionary of parameters, this function replaces all named parameters
    in the query with `?`, constructs a list of corresponding parameter values,
    and returns both the modified SQL query string and the list of values.

    :param sql: The SQL query containing named parameters in the format `:param_name`.
    :type sql: str
    :param params: A dictionary where keys are the parameter names (matching the named
                   parameters in the query) and values are the corresponding values
                   for substitution.
    :type params: dict
    :return: A tuple containing the modified query string with positional parameters
             and a list of values in the correct order for execution.
    :rtype: tuple[str, list]
    :raises KeyError: If a named parameter in the query does not have a corresponding
                      key in the `params` dictionary.
    """
    _PARAM = re.compile(r":([A-Za-z_]\w*)")
    names = []

    def repl(m: re.Match[str]) -> str:
        names.append(m.group(1))
        return "?"

    repl_sql = _PARAM.sub(repl, sql)
    try:
        args = [params[n] for n in names]
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(f"Missing parameter '{missing}'") from None
    return repl_sql, args

class MyODBC:
    connection: pyodbc.Connection
    cursor: pyodbc.Cursor

    def __init__(self, env: str = None, override: bool = False):
        self.connection = build_connection(env, override)
        self.cursor = self.connection.cursor()

    def translate(self, cursor: pyodbc.Cursor, rows: list[pyodbc.Row]):
        """
        Translate rows fetched from a database query into a list of dictionaries, where the keys
        are the column names and the values are the corresponding column values for each row.
        This function is helpful for transforming raw database query results into a structured
        Python-friendly format for further processing or usage.

        :param cursor: A pyodbc.Cursor object that holds metadata about the columns of the query result.
        :param rows: A list of pyodbc.Row objects, representing the rows fetched from a database query.
        :return: A list of dictionaries, where each dictionary corresponds to a row and contains
            column names as keys and the corresponding column values as values.
        """
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

    # SIMPLE QUERY
    def sq(self, query: str) -> list[dict] | bool:
        """
        Executes the provided SQL query and translates the result into a list of dictionaries.

        The `sq` method performs a database query using the provided query string, retrieves
        the resulting rows, and translates them using the internal `translate` method to
        produce structured results.

        :param query: The SQL query to execute
        :type query: str
        :return: A list of dictionaries representing the translated rows from the query result
        :rtype: list[dict]
        """
        self.cursor.execute(query)
        if self.cursor.description is None:
            try:
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                return False
            return True

        rows = self.cursor.fetchall()
        return self.translate(self.cursor, rows)

    # COMPLEX QUERY
    def cq(self, query: str, params: list | tuple | dict) -> list[dict] | bool:
        """
        Executes a query against the database using parameterized input and fetches all
        matching rows. The query can include named or positional placeholders, and
        parameters are passed as a dictionary, list, or tuple. The function ensures the
        query is executed securely and the results are processed before returning.

        :param query: The SQL query string to be executed.
        :type query: str
        :param params: The parameters to be substituted into the query, provided as
            a dictionary (for named parameters), or a list/tuple (for positional
            parameters).
        :type params: list | tuple | dict
        :return: A list of dictionaries, with each dictionary representing a single row
            retrieved from the database.
        :rtype: list[dict]
        """
        if isinstance(params, dict):
            sql, args = named_params(query, params)
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(query, params)

        if self.cursor.description is None:
            try:
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                return False
            return True
        rows = self.cursor.fetchall()
        return self.translate(self.cursor, rows)
