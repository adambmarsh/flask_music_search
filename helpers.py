"""
module defining help functions for flask-based db search
"""
import re
import urllib.parse
from collections import OrderedDict

from settings import display_columns, play_cfg


def columns_to_show(requested: list) -> list:
    """
    Verify the columns useer wants to see values from
    :param requested: The names of the columns provided by the user
    :return: A list of column names
    """
    return [col for col in requested if col in display_columns] if requested else display_columns


def playback_dict(row_data: dict) -> dict:
    """
    Build a dictionary to use in the playback cell of the results table
    :param row_data: A row or results data
    :return: A dictionary with url encoded path and file name of the media file to play
    """
    d = {
        "folder_path": row_data.get(play_cfg.get('file_path', ''), ''),
        "file_name": row_data.get(play_cfg.get('file_name', ''), '')
    }

    return {k: urllib.parse.quote(v) for k, v in d.items()}


def build_html(user_columns, db_columns, data, term):
    """
    Function to build HTML
    :param user_columns: Columns whose values user wants to see (format: list of '<table_name>.<column_name>')
    :param data: Data retrieved from DB
    :param db_columns: A list of column from DB (format: list of '<table_name>.<column_name>')
    :param term: A string representing the search term used to search DB
    :return: A string containing HTML with the search results
    """
    html_string = f"<p>No of records found: {len(data)}</p>"

    if not data:
        return html_string

    use_cols = columns_to_show(user_columns)
    column_str = ''.join(["<th style=\"text-align:left\">Play Song</th>"]+
                         [f'<th style="text-align:left">{col}</th>' for col in use_cols])
    html_string += f"<table id=\"table\"><tr>{column_str}</tr>"

    for row in data:
        row_data_dict = dict(zip(db_columns,list(row)))
        d = playback_dict(row_data_dict)
        html_string += f"""<tr>
                        <td><input type = "button" value="Play track" onclick="window.setPlayer('{d["folder_path"]}',
                        '{d["file_name"]}')"/></td>"""
        # row_data_dict = {k: v for k,v in row_data_dict.items() if k in display_cols}
        # use_dict = {col: val for col, val in row_data_dict.items() if col in use_cols}
        use_dict = OrderedDict({col: row_data_dict[col] for col in use_cols})

        for entry in use_dict.values():
            entry_string = f'<td style="text-align:left"><div class="cell-content">{entry}</div></td>'

            if term in str(entry):
                entry_string = replace_matches(term, entry_string)

            html_string += entry_string

        html_string += '</tr>'

    return html_string + '</table>'


def replace_matches(term, in_string):
    """

    :param term: term to search for
    :param in_string: string to search in
    :return: a string with html tags marking the matches
    """
    s = re.split(fr'({term})', in_string)
    s = [a for a in s if a]

    for count, item in enumerate(s):
        if item != term:
            continue

        s[count] = f"<mark>{item}</mark>"

    return ''.join(s)


if __name__ == '__main__':
    # print(get_span('Bach J.S. C.P. Bach J.SBach','Bach'))
    print(replace_matches('Bach', 'Bach J.S. C.P. Bach J.SBach'))
