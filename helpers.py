"""
module defining help functions for flask-based db search
"""
import urllib.parse
from collections import OrderedDict
from pathlib import Path
from string import Template

from settings import display_columns, play_cfg


def columns_to_show(requested: list[str]) -> list[str]:
    """
    Verify the columns useer wants to see values from
    :param requested: The names of the columns provided by the user
    :return: A list of column names
    """
    return [col for col in requested if col in display_columns] if requested else display_columns


def build_html(user_columns: list[str], db_columns: list[str], data: list[tuple], term: str) -> str:
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
        return {'records': len(data), 'html': html_string,'player_data': []}

    use_cols = columns_to_show(user_columns)

    th_row_tmpl = Template("<table id=\"table\"><tr>$col_str</tr>")
    tr_input_tmpl = \
        Template('<tr><td><input type = "button" value="Play track" onclick="window.myPlayer.updateSrc(this,$row)"/></td>')
    tr_td_tmpl = Template('<td style="text-align:left"><div class="cell-content">$cells</div></td>')

    html_string += th_row_tmpl.substitute(
        col_str=''.join(['<th style="text-align:left">Play Song</th>']+
                         [f'<th style="text-align:left">{col}</th>' for col in use_cols]))
    player_data = []

    for row_num, row in enumerate(data):
        row_data_dict = dict(zip(db_columns,list(row)))
        use_dict = OrderedDict({col: row_data_dict[col] for col in use_cols})

        html_string += tr_input_tmpl.substitute(row=row_num) + \
            ''.join((mark_matches(term, tr_td_tmpl.substitute(cells=entry)) for entry in use_dict.values())) + \
            '</tr>'

        player_data.append([urllib.parse.quote(row_data_dict.get(play_cfg.get('file_path', ''), '')),
                            urllib.parse.quote(row_data_dict.get(play_cfg.get('file_name', ''), ''))])

    return {'records': len(data), 'html': html_string + '</table>','player_data': player_data}


def mark_matches(term: str, in_string: str) -> str:
    """
    Mark (highlight) the received term in the HTML string.
    :param term: term to mark
    :param in_string: string in which to mark occurrences of term
    :return: marked-up HTML string on success or unchanged in_string if no matches are found
    """
    return in_string.replace(term, f"<mark>{term}</mark>")


def find_music_file(filename: str, audio_dir: str)-> Path|None:
    """
    Find the audio file and get its current path.
    :param filename: filename to find
    :param audio_dir: directory to search in
    :return correct filepath if file is found, else None
    """
    if not audio_dir or not filename:
        return None

    filepath = Path(audio_dir) / filename

    if filepath.is_file():
        return filepath

    # In case the DB is out of date and audio files have been converted
    # to a different format, try different extensions ...

    extensions = ['.flac','.mp3','.ogg','.cue']

    for ext in filter(lambda e: e != filepath.suffix, extensions):
        if (new_path := filepath.with_suffix(ext)).is_file():
            return new_path

    return None


if __name__ == '__main__':
    # print(get_span('Bach J.S. C.P. Bach J.SBach','Bach'))
    # print(replace_matches('Bach', 'Bach J.S. C.P. Bach J.SBach'))
    out = find_music_file("09_Serenade No 10, Gran Partita - 3rd mvt, Adagio.flac",
                    "/home/adam/lanmount/music/Various_-_Classic_CD_Magazine_32")

    print(out)
