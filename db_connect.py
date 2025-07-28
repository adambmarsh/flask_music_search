"""
module: db_connector
"""
import re
# import socket
from collections import OrderedDict
import psycopg2
from settings import DATABASES


album_columns = [
    'title',
    'artist',
    'date',
    'label',
    'comment',
    'path'
]


song_columns = [
    'title',
    'track_id',
    'artist',
    'composer',
    'performer',
    'album_id',  # use to get album title
    'genre',
    'date',
    'comment',
    'file'
]


db_tables = OrderedDict({
    'album': album_columns,
    'song': song_columns
})


class DBConnection:
    """
    Class handling the database connection and retrieval of data.
    """
    def __init__(self):
        self._current_schema = None
        db_info = DATABASES.get('default', {})
        self.conn = psycopg2.connect(database=db_info.get("NAME"),
                                     user=db_info.get("USER"),
                                     password=db_info.get("PASSWORD"),
                                     host=db_info.get("HOST"),
                                     port=db_info.get("PORT"))
        self.cur = self.conn.cursor()
        self.current_schema = []

    @property
    def current_schema(self):  # pylint: disable=missing-function-docstring
        return self._current_schema

    @current_schema.setter
    def current_schema(self, in_schema):
        self._current_schema = in_schema

    def close(self):
        """
        Close db
        :return: Result of the close op
        """
        self.conn.close()

    def get_schema(self, table):
        """
        Get the schema (columns from the given table).
        :param table: Name of the table
        :return: A list of column names
        """
        if self.current_schema:
            return self.current_schema

        self.cur.execute(
            f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")

        query_results = self.cur.fetchall()
        return [x[0] for x in query_results]

    @staticmethod
    def resolve_tables(in_str=None):   # pylint: disable=missing-function-docstring
        if not in_str or in_str == '*':
            return list(db_tables.keys())

        return [tbl for tbl in list(db_tables.keys()) if tbl in re.split(r', *', in_str)]

    def resolve_tables_and_columns(self, table_names, columns=None):
        """
        Get strings with the names of the tables and columns to search.
        :param table_names: Names of the DB tables or '*' or None for all
        :param columns: Name(s) of column(s); if not supplied (None), use all column names
        :return: Strings, one with resolved table names, one with column names
        """
        self.current_schema = self.get_schema(table_names)
        tables = self.resolve_tables(table_names)

        where_columns = []
        for tbl in tables:
            if columns == '*':
                where_columns += [f"{tbl}.{col}" for col in db_tables.get(tbl, [])]
            else:
                where_columns += [f"{tbl}.{col}" for col in db_tables.get(tbl, []) if col in columns]

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

    def search(self, user_query, table, columns='*'):
        """
        Run a db search.
        :param user_query: Text containing the search terms
        :param table: The name of the DB table
        :param columns: The name of the column to search, if None, use all columns (retrieve from schema)
        :return: Results of the search
        """
        where_operand = 'LIKE'
        pc_sign = '%'

        if user_query and self.is_re_pattern(user_query):
            where_operand = '~'
            pc_sign = ''

        where_tables, where_cols = self.resolve_tables_and_columns(table, columns or '*')
        where_col_str = '::TEXT||'.join(where_cols) + '::TEXT'

        if len(where_tables) == 1:
            use_table = next(iter(where_tables), '')
            self.current_schema = list(db_tables.get(use_table))
            select_col_str = ", ".join(self.current_schema)
            query_str = \
                f"SELECT {select_col_str} FROM {use_table} WHERE {where_col_str}" + \
                f"{where_operand} \'{pc_sign}{user_query}{pc_sign}\';"
        else:
            # Construct a PSQL JOIN like this:
            #  "SELECT album.title, album.artist, album.date, song.title, song.track_id,
            #  song.genre, album.path FROM album JOIN song on song.album_id = album.id
            #  ORDER BY album.path, song.track_id;"
            self.current_schema = where_cols
            select_col_str = ", ".join(self.current_schema)
            query_str = (f"SELECT {select_col_str} FROM {where_tables[0]} JOIN {where_tables[1]} on " +
                         f"{where_tables[1]}.album_id = {where_tables[0]}.id WHERE " +
                         f"{where_col_str} {where_operand} \'{pc_sign}{user_query}{pc_sign}\';")

        self.cur.execute(query_str)

        return self.cur.fetchall()


if __name__ == '__main__':
    db = DBConnection()
    db.get_schema('song')
    out = db.search(user_query='Bach', table='song')
    db.close()
