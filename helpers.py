"""
module defining help functions for flask-based db search
"""
import re
import urllib.parse

def build_html(columns, data, term):
    """
    Function to build HTML
    :param columns: DB columns
    :param data: Data retrieved from DB
    :param term: Search term used to search DB
    :return: A string containing HTML with the search results
    """
    html_string = \
        f"<p>No of records found: {len(data)}</p>"

    if not data:
        return html_string

    column_str = ''.join(["<th style=\"text-align:left\">Play Song</th>"]+
                         [f'<th style="text-align:left">{col}</th>' for col in columns])
    html_string += f"<table id=\"table\"><tr>{column_str}</tr>"

    for row in data:
        seek_path = row[5]+'/'+row[15]
        seek_path = urllib.parse.quote(seek_path)
        html_string += f"""<tr>
                        <td><input type = "button" value="Play track" onclick="setPlayer('{seek_path}')"/></td>"""

        for entry in row:
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
    re_term = fr'({term})'
    s = re.split(re_term, in_string)
    s = [a for a in s if a]

    for count, item in enumerate(s):
        if item != term:
            continue

        s[count] = f"<mark>{item}</mark>"

    return ''.join(s)


if __name__ == '__main__':
    # print(get_span('Bach J.S. C.P. Bach J.SBach','Bach'))
    print(replace_matches('Bach', 'Bach J.S. C.P. Bach J.SBach'))
