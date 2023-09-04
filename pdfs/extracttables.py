"""
Return a Python list of lists from the words found in a fitz.Page page
-------------------------------------------------------------------------------
License: GNU GPL V3
(c) 2018 Jorj X. McKie

Notes
-----
(1) Works correctly for simple, non-nested tables only.

(2) Line recognition depends on the coordinates of the detected words in the
    rectangle. These will be round to integer (pixel) values. However, use of
    different fonts, scan inaccuracies, and so on, may lead to artefacts line
    differences, which must be handled by the caller.

Dependencies
-------------
PyMuPDF v1.12.0 or later
"""

from tabula import read_pdf
from operator import itemgetter
from itertools import groupby
import fitz


def parse_table(page: fitz.Page, bbox: list, columns=None) -> list[str]:
    """
    Returns the parsed table of a page in a PDF/XPS/EPUB document.
    Parameters:
        page: fitz.Page object
        bbox: containing rectangle, list of numbers [xmin, ymin, xmax, ymax]
        columns: optional list of column coordinates. If None, columns are generated
        Returns the parsed table as a list of lists of strings.
        The number of rows is determined automatically
        from parsing the specified rectangle.
    """

    table_rect = fitz.Rect(bbox).irect
    xmin, ymin, xmax, ymax = tuple(table_rect)

    if table_rect.is_empty or table_rect.is_infinite:
        print("Warning: incorrect rectangle coordinates")
        return []

    if (not columns) or (columns == []):
        all_columns = [table_rect.x0, table_rect.x1]
    else:
        all_columns = sorted(columns)
    # add the table's x-coords
    if xmin < min(all_columns):
        all_columns.insert(0, xmin)
    #
    if xmax > all_columns[-1]:
        all_columns.append(xmax)

    words = page.get_text("words")

    if words == []:
        print("Warning: page contains no text")
        return []

    alltxt = []

    # get words contained in table rectangle and distribute them into columns
    for word in words:
        # construct a rect from word coords
        word_rect = fitz.Rect(word[:4]).irect  # word rectangle
        # word rect in main table
        if word_rect in table_rect:
            col_index = 0  # column index
            for i in range(1, len(all_columns)):  # loop over column coordinates
                if word_rect.x0 < all_columns[i]:  # word start left of column border
                    col_index = i - 1
                    break
            # store coords of word and the word itself
            alltxt.append([word_rect.x0, word_rect.y0, word_rect.x1, col_index, word[4]])

    if alltxt == []:
        print("Warning: no text found in rectangle")
        return []

    alltxt.sort(key=itemgetter(1))  # sort words vertically

    # create the table / matrix
    spantab = []  # the output matrix

    for key, group in groupby(alltxt, itemgetter(1)):  # groupby x0
        schema = [""] * (len(all_columns) - 1)
        #
        for col_key, words in groupby(group, itemgetter(3)):  # groupby column
            entry = " ".join([w[4] for w in words])
            schema[col_key] = entry

        spantab.append(schema)

    return spantab


def tabula_tables(filename: str, **kwargs):
    """ yield dataframes of tables in filename PDF """

    dfs = read_pdf(filename, **kwargs)
    for df in dfs:
        yield df


if __name__ == '__main__':
    file = "C:\\Users\\Windows 10 Pro\\Downloads\\annual report-gb-en-180173.pdf"
    for index, table in enumerate(tabula_tables(file, pages=23)):
        print(table)
