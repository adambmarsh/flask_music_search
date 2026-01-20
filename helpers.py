"""
module defining help functions for flask-based db search
"""
import urllib.parse
import re
from collections import OrderedDict
from pathlib import Path
from string import Template

from settings import display_columns, play_cfg
from utils import is_re_pattern

tr_input_tmpl = \
    Template('<tr><td><input type = "button" value=" \u25B6 " '
             'onclick="window.myPlayer.updateSrc(this,$row)"/>'
             '<input type="hidden" name="full-content" value="$content" />'
             '</td>')
tr_td_tmpl = Template('<td style="text-align:left"><div class="cell-content">$cells</div></td>')
tr_td_comment_tmpl = Template(
    '<td style="text-align:left"><div class="tooltip">$cell<span class="tooltiptext"><pre>' +
    '$allcell</pre></span></div></td>'
)


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
    :param user_columns: Columns whose values user wants to see (format: list of
    '<table_name>.<column_name>')
    :param data: Data retrieved from DB
    :param db_columns: A list of column from DB (format: list of
    '<table_name>.<column_name>')
    :param term: A string representing the search term used to search DB
    :return: A string containing HTML with the search results
    """
    html_string = f"<p>No of records found: {len(data)}</p>"

    if not data:
        return {'records': len(data), 'html': html_string,'player_data': []}

    use_cols = columns_to_show(user_columns)

    th_row_tmpl = Template("<table id=\"table\"><thead><tr>$col_str</tr></thead>")

    html_string += th_row_tmpl.substitute(
        col_str=''.join(['<th style="text-align:left">Play</th>']+
                         [f'<th style="text-align:left">{col}</th>' for col in use_cols]))
    player_data = []

    for row_num, row in enumerate(data):
        row_data_dict = dict(zip(db_columns,list(row)))
        use_dict = OrderedDict({col: row_data_dict[col] for col in use_cols})
        full_content = ''.join([str(a) + '||' for a in list(use_dict.values())])
        html_string += tr_input_tmpl.substitute(row=row_num,content=full_content) + \
            ''.join((
                mark_matches(
                    term,
                    tr_td_comment_tmpl.substitute(
                        cell=" ".join([entry[:10], '...'] if entry else ""), allcell=entry
                    )  if key == 'album.comment' else tr_td_tmpl.substitute(cells=entry)
                ) for key, entry in use_dict.items())) + \
            '</tr>'

        player_data.append(
            [urllib.parse.quote(row_data_dict.get(play_cfg.get('file_path', ''), '')),
                urllib.parse.quote(row_data_dict.get(play_cfg.get('file_name', ''), ''))])

    return {'records': len(data), 'html': html_string + '</table>','player_data': player_data}

def mark_matches(term: str, in_str: str) -> str:
    """
    Mark (highlight) the received term in the HTML string.
    :param term: term to mark
    :param in_str: string in which to mark occurrences of term
    :return: marked-up HTML string on success or unchanged in_string if no matches are found
    """
    if not is_re_pattern(term):
        return in_str.replace(term, f"<mark>{term}</mark>")

    for match in re.finditer(term, in_str):
        in_str = in_str.replace(match.group(), f"<mark>{match.group()}</mark>")

    return in_str

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
