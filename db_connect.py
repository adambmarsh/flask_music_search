"""
module: db_connector
"""
import re
from collections import OrderedDict
import psycopg2
from settings import DATABASES


class DBConnection:
    """
    Class handling the database connection and retrieval of data.
    """
    def __init__(self):
        self._db_tables = {}
        self._current_schema = None
        db_info = DATABASES.get('default', {})
        self.conn = psycopg2.connect(database=db_info.get("NAME"),
                                     user=db_info.get("USER"),
                                     password=db_info.get("PASSWORD"),
                                     host=db_info.get("HOST"),
                                     port=db_info.get("PORT"))
        self.cur = self.conn.cursor()
        self.db_tables = OrderedDict({t: self._get_table_schema(t) for t in self._get_db_tables()}
)
        self.current_schema = []

    @property
    def current_schema(self):  # pylint: disable=missing-function-docstring
        return self._current_schema

    @current_schema.setter
    def current_schema(self, in_schema):
        self._current_schema = in_schema

    @property
    def db_tables(self):  # pylint: disable=missing-function-docstring
        return self._db_tables

    @db_tables.setter
    def db_tables(self, in_tables):
        self._db_tables = in_tables

    def _get_db_tables(self, schema_id='public'):
        """
        Query the database to get a list of tables for the specified schema
        :param schema_id: Identifier of the db schema for which to retrieve table names
        :return: a list of table names
        """
        self.cur.execute(
            f"SELECT table_schema,table_name FROM information_schema.tables WHERE tables.table_schema='{schema_id}'")

        query_results = self.cur.fetchall()

        return list(filter(lambda x: x not in ['django_migrations', 'combiview'], [x[1] for x in query_results]))

    def _get_table_schema(self, table):
        """
        Get the schema (columns from the given table).
        :param table: Name of the table
        :return: A list of column names
        """
        self.cur.execute(
            f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")

        query_results = self.cur.fetchall()
        return [x[0] for x in query_results if x[0] != 'id']

    def close(self):
        """
        Close db
        :return: Result of the close op
        """
        self.conn.close()

    def resolve_tables(self, in_tables=None):
        """
        Get table names from supplied string and verify then against the db
        :param in_tables: A string containing comma-separated table names to use or empty string
        :return: A list of verified table names
        """
        if not in_tables or in_tables == '*':
            return list(self.db_tables.keys())

        return [tbl for tbl in list(self.db_tables.keys()) if tbl in re.split(r', *', in_tables)]

    def resolve_columns(self, tables, in_columns=None):
        """
        Get column names for named table and verify them against the db
        :param tables: A list naming tables for which to verify columns
        :param in_columns: A string containing comma-separated table column names or '*'/None for all
        :return: A list of verified column names
        """
        out_columns = []
        for tbl in tables:
            if not in_columns or in_columns == '*':
                out_columns += [f"{tbl}.{col}" for col in self.db_tables.get(tbl, [])]
            else:
                out_columns += [f"{tbl}.{col}" for col in self.db_tables.get(tbl, []) if col in in_columns]

        return out_columns

    def resolve_tables_and_columns(self, table_names='*', columns='*'):
        """
        Get strings with the names of the tables and columns to search.
        :param table_names: Names of the DB tables or '*' or None for all
        :param columns: Name(s) of column(s); if not supplied (None), use all column names
        :return: Strings, one with resolved table names, one with column names
        """
        tables = self.resolve_tables(table_names)
        where_columns = self.resolve_columns(tables, columns)

        return tables, where_columns

    @staticmethod
    def is_re_pattern(in_str):
        """
        Check if the received string is a valid regex pattern and not just piece of ordinary text.
        :param in_str: String to test
        :return: True if the string is a regex pattern, otherwise False
        """
        if re.fullmatch(r'[\w ]+', in_str):
            return False

        try:
            re.compile(in_str)
            return True
        except re.error:
            return False

    def search(self, user_query, tables='*', columns='*'):
        """
        Run a db search.
        :param user_query: Text containing the search terms
        :param tables: Names of DB tables to search, a comma-separated string, if None or '*', search all
        :param columns: DB columns to search, if None, use all columns, if None or '*' search all
        :return: Results of the search
        """
        where_operand = 'LIKE'
        pc_sign = '%'

        if user_query and self.is_re_pattern(user_query):
            where_operand = '~'
            pc_sign = ''

        where_tables, where_cols = self.resolve_tables_and_columns(tables, columns)
        where_col_str = '::TEXT||'.join(where_cols) + '::TEXT'

        if len(where_tables) == 1:
            use_table = next(iter(where_tables), '')
            self.current_schema = list(self.db_tables.get(use_table))
            select_col_str = ", ".join(self.current_schema)
            query_str = \
                f"SELECT {select_col_str} FROM {use_table} WHERE {where_col_str}" + \
                f" {where_operand} \'{pc_sign}{user_query}{pc_sign}\';"
        else:
            # Construct a PSQL JOIN like this:
            #  "SELECT album.title, album.artist, album.date, song.title, song.track_id,
            #  song.genre, album.path FROM album JOIN song on song.album_id = album.id
            #  ORDER BY album.path, song.track_id;"
            self.current_schema = where_cols
            select_col_str = ", ".join(self.current_schema)
            query_str = (f"SELECT {select_col_str} FROM {where_tables[0]} JOIN {where_tables[1]} on " +
                         f"{where_tables[1]}.album_id = {where_tables[0]}.id WHERE " +
                         f"{where_col_str} {where_operand} \'{pc_sign}{user_query}{pc_sign}\'"+
                         "ORDER BY album.title DESC, song.track_id;")

        self.cur.execute(query_str)

        return self.cur.fetchall()


if __name__ == '__main__':
    db = DBConnection()
    out = db.search(user_query='Bach', tables='song')
    db.close()
