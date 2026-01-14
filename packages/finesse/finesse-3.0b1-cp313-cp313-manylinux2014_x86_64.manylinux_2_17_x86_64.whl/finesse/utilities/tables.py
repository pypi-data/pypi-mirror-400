"""Defines classes for displaying tables.

This code is inspired by the tabulate package which can be found at
https://github.com/astanin/python-tabulate/ and on PyPI
"""

import csv
import re
import unicodedata
from html import escape as htmlescape

import numpy as np
from click import echo

from .misc import opened_file


class Table:
    """Basic class to display tables via pretty printing or html.

    This class is a container object for formatted tables. All entries should either
    be strings or have a `__str__` method with readable output.
    The table can be pretty printed for console and displayed as html. Additionally
    the table can be saved to a csv file using the same syntax as the `csv` package or
    rendered as latex code.

    Parameters
    ----------
    table : array or list
        A two dimensional array or list-of-lists containing strings.
    headerrow : bool, default=True
        Whether the first row is a header.
    headercolumn : bool, default=False
        Whether the first column is a header.
    color : array, optional
        An array with shape `table.shape + (3,)` of type int containing RGB
        color data to control the textcolor. If any value in a RGB triple is
        negative, no color will be applied to the corresponding cell.
    backgroundcolor : array, optional
        An array to set the backgroundcolors of the cells, works like `color`.
    alignment : array, optional
        An array with on of ("left", "center", "right) for each cell.
    compact : boolean, optional
        Skip internal row separators to save space when printing as string.

    Notes
    -----
    Instead of arrays, color, backgroundcolor and alignment can be given only
    one option per row, column or total. This will be expanded for the whole
    table.
    """

    def __init__(
        self,
        table,
        headerrow=True,
        headercolumn=False,
        color=(-1, -1, -1),
        backgroundcolor=(-1, -1, -1),
        alignment="left",
        compact=False,
    ):
        self.table = np.array(table, dtype=object)
        # ensure that the table has at least one cell
        if len(self.table) == 0:
            self.table = np.full((1, 1), "")
        else:
            if len(self.table.shape) == 0:
                self.table = np.full((1, 1), "")
            elif len(self.table.shape) == 1:
                self.table = np.array([self.table])

        self.headerrow = headerrow
        self.headercolumn = headercolumn
        self.color = self._make_option_array(color, option_shape=(3,), dtype=int)
        self.backgroundcolor = self._make_option_array(
            backgroundcolor, option_shape=(3,), dtype=int
        )
        self.alignment = self._make_option_array(alignment)
        self.compact = compact

    def _make_option_array(
        self, option, dtype=object, dimensions=None, option_shape=()
    ):
        """Expand an option to the whole table.

        Fills an array with values from `option`. If `option` can be cast as a numpy
        array and the shape matches `dimensions+option_shape`, this array will be
        returned. If the shape matches the rows or columns of the desired shape, has a
        length 1 in the other axis and `option_shape` in all additional axis, it will
        be expanded along this axis. In all other cases `option` is assumed to be
        information for a single cell and the returned array is filled with `option` in
        every entry.

        Parameters
        ----------
        option :
            Option for either a single cell, all rows, all columns or
            the whole table.
        dtype : data-type, optional, default=object
            The data type of the option. If the option itself is an array
            (e.g. RGB color tuple), the data type of the elements must be given.
        dimensions : tuple, default=None
            The dimension of the array the option will be expanded to.
            Passing `None` (the default) uses the shape of the table.
        option_shape : tuple, default=()
            The shape of the option value, e.g. (3,) for an RGB triple.

        Returns
        -------
        np.array
            A numpy array of the specified `dtype` with shape `dimensions` filled
            with values from `option`
        """
        isarray = False
        if dimensions is None:
            dimensions = self.table.shape
        if isinstance(option, np.ndarray):
            isarray = True
        else:
            try:
                option = np.array(option, dtype=dtype)
            except Exception:
                pass
            else:
                isarray = True
        if isarray:
            if option.shape == dimensions + option_shape:
                return option
            elif option.shape == (1, dimensions[1], option_shape):
                # expand to all rows
                return np.array(
                    [option[0, :] for i in range(dimensions[0])], dtype=dtype
                )
            elif option.shape == (dimensions[0], 1, option_shape):
                # expand to all columns
                return np.array(
                    [[option[i, :]] * dimensions[1] for i in range(dimensions[0])],
                    dtype=dtype,
                )
        return np.full(dimensions + option_shape, option, dtype=dtype)

    def get_visible_length(self, text):
        """Get the visible length of the string.

        Parameters
        ----------
        text : str

        Returns
        -------
        int
            The number of non combining characters after removing
            ANSI escape sequences.

        Notes
        -----
        Using code from `https://stackoverflow.com/questions/14693701/how-can-
        i-remove-the-ansi-escape-sequences-from-a-string-in-python`
        and `https://stackoverflow.com/questions/33351599/how-do-i-get-the-
        visible-length-of-a-combining-unicode-string-in-python`
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        text = ansi_escape.sub("", text)
        return sum(1 for ch in str(text) if unicodedata.combining(ch) == 0)

    def get_max_column_width(self, j):
        """Determine the maximum width of an entry in this column and add 2."""
        width = 0
        for text in self.table[:, j]:
            width = max(width, self.get_visible_length(str(text)))
        return width + 2

    def apply_ansi_colors(self, text, color, backgroundcolor):
        """Add the color codes to the string if necessary.

        Colors should be given as RGB tuples with integer values from [0,255].
        """
        if not np.any(color < 0):
            text = "\033[38;2;{};{};{}m{t}\033[0m".format(*color, t=text)
        if not np.any(backgroundcolor < 0):
            text = "\033[48;2;{};{};{}m{}\033[0m".format(*backgroundcolor, text)
        return text

    def expand_string(self, text, width, align="right"):
        """Expand a string to have a certain length.

        Add blank spaces to the string to get its visible length to `width`.
        `align` controls whether the spaces are added in front, at the end or
        both. `text` will be converted to `str`.

        Parameters
        ----------
        text : str
            Can also be an objection with `__str__` defined.
        width : int
        align : str, optional
            Must be one of "right", "left" or "center". Defaults to "right".

        Raises
        ------
        ValueError
            If the string is shorter than the given length or `align` is not
            one of the given options.
        """
        text = f" {str(text)} "
        diff = width - self.get_visible_length(text)
        if diff < 0:
            raise ValueError(
                "cannot expand text of length {:} to {:}.".format(
                    self.get_visible_length(text), width
                )
            )
        if align == "right":
            return (diff * " ") + text
        if align == "left":
            return text + (diff * " ")
        if align == "center":
            return (
                (int(np.floor(diff / 2)) * " ") + text + (int(np.ceil(diff / 2)) * " ")
            )
        raise ValueError(
            f"invalid alignment: must be 'right', 'left' or 'center', not"
            f"{repr(align)}"
        )

    def generate_row(self, i, start, headerdivision, division, end):
        """Create the \\`i\\`th row with the given elements."""
        row = start
        if self.table.shape[1] > 1:
            width = self.get_max_column_width(0)
            row += self.apply_ansi_colors(
                self.expand_string(str(self.table[i, 0]), width, self.alignment[i, 0]),
                self.color[i, 0],
                self.backgroundcolor[i, 0],
            )
            if self.headercolumn:
                row += headerdivision
            else:
                row += division
        for j in range(1, self.table.shape[1] - 1):
            width = self.get_max_column_width(j)
            row += self.apply_ansi_colors(
                self.expand_string(str(self.table[i, j]), width, self.alignment[i, j]),
                self.color[i, j],
                self.backgroundcolor[i, j],
            )
            row += division
        width = self.get_max_column_width(-1)
        row += self.apply_ansi_colors(
            self.expand_string(str(self.table[i, -1]), width, self.alignment[i, -1]),
            self.color[i, -1],
            self.backgroundcolor[i, -1],
        )
        row += end
        return row

    def generate_seperating_row(
        self, start, line, intersection, headerintersection, end
    ):
        """Generate the string separating two rows."""
        row = start
        if self.table.shape[1] > 1:
            width = self.get_max_column_width(0)
            row += width * line
            if self.headercolumn:
                row += headerintersection
            else:
                row += intersection
        for j in range(1, self.table.shape[1] - 1):
            width = self.get_max_column_width(j)
            row += width * line
            row += intersection
        width = self.get_max_column_width(-1)
        row += width * line
        row += end
        return row

    def generate_grid_table(self):
        """Create the whole table."""
        table = ""
        if self.headercolumn:
            table += self.generate_seperating_row(
                "\u250c", "\u2500", "\u252c", "\u2565", "\u2510\n"
            )
        else:
            table += self.generate_seperating_row(
                "\u250c", "\u2500", "\u252c", "\u253c", "\u2510\n"
            )
        if self.table.shape[0] > 1:
            table += self.generate_row(0, "\u2502", "\u2551", "\u2502", "\u2502\n")
            if self.headerrow:
                table += self.generate_seperating_row(
                    "\u255e", "\u2550", "\u256a", "\u256c", "\u2561\n"
                )
            else:
                if self.headercolumn:
                    table += self.generate_seperating_row(
                        "\u251c", "\u2500", "\u253c", "\u256b", "\u2524\n"
                    )
                else:
                    table += self.generate_seperating_row(
                        "\u251c", "\u2500", "\u253c", "\u256c", "\u2524\n"
                    )
        for i in range(1, self.table.shape[0] - 1):
            table += self.generate_row(i, "\u2502", "\u2551", "\u2502", "\u2502\n")

            if not self.compact:
                table += self.generate_seperating_row(
                    "\u251c", "\u2500", "\u253c", "\u256b", "\u2524\n"
                )
        table += self.generate_row(-1, "\u2502", "\u2551", "\u2502", "\u2502\n")
        table += self.generate_seperating_row(
            "\u2514", "\u2500", "\u2534", "\u2568", "\u2518\n"
        )
        return table

    def __str__(self):
        return self.generate_grid_table()

    def generate_html_cell(self, row, column, style=None):
        """Generate html code for the table cell at position (row, column).

        `style` may contain pairs of style options with their values.
        """
        style = {} if style is None else style
        if (self.headerrow and row == 0) or (self.headercolumn and column == 0):
            c = '<th style="{}">{}</th>'
        else:
            c = '<td style="{}">{}</td>'

        if not np.any(self.color[row, column] < 0):
            style["color"] = "#{:02x}{:02x}{:02x}".format(*self.color[row, column])
        if not np.any(self.backgroundcolor[row, column] < 0):
            style["background-color"] = "#{:02x}{:02x}{:02x}".format(
                *self.backgroundcolor[row, column]
            )
        style["text-align"] = self.alignment[row, column]
        style_str = ""
        for key in style.keys():
            style_str += key + ":" + style[key] + ";"
        return c.format(style_str, htmlescape(str(self.table[row, column])))

    def generate_html_table(self):
        table = "<table><tbody>\n"
        for i in range(self.table.shape[0]):
            table += "<tr>"
            for j in range(self.table.shape[1]):
                table += self.generate_html_cell(i, j)
            table += "</tr>\n"
        table += "</tbody></table>"
        return table

    def _repr_html_(self):
        return self.generate_html_table()

    def write_csv(self, csvfile, dialect="excel", **fmtparams):
        """Write the table data to a csv file using the csv package.

        Parameters
        ----------
        csvfile :
            Any object with a write method. The file the data will be written to.
        dialect : csv.Dialect or str, default="excel"
            The CSV dialect to use. may be an instance of `csv.Dialect` or any subclass
            thereof or any string in `csv.list_dialects()`.
        **fmtparams : dict, optional
            Formatting parameters for `csv.writer`

        Returns
        -------
        The writer object used.
        """
        table = np.full(self.table.shape, "", dtype=object)
        for i in range(self.table.shape[0]):
            for j in range(self.table.shape[1]):
                table[i, j] = str(self.table[i, j])
        with opened_file(csvfile, "w") as fileobj:
            writer = csv.writer(fileobj, dialect, **fmtparams)
            writer.writerows(table)
        return writer

    def escape_latex(self, text):
        """Replace special characters in latex with their latex representation."""
        latex_special = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde",
            "^": r"\textasciicircum",
            "\\": r"\textbackslash",
        }
        return "".join(map(lambda c: latex_special.get(c, c), text))

    def make_latex_str(self, row, column):
        """Create latex code for the cell at position (row, column)."""
        text = self.escape_latex(str(self.table[row, column]))
        if not np.any(self.color[row, column] < 0):
            text = (
                r"\textcolor{colorredgreenblue}{TEXT}".replace(
                    "red", "{:03.0f}".format(self.color[row, column][0])
                )
                .replace("green", "{:03.0f}".format(self.color[row, column][1]))
                .replace("blue", "{:03.0f}".format(self.color[row, column][2]))
                .replace("TEXT", str(text))
            )
        if self.alignment[row, column] != self.alignment[0, column]:
            if self.alignment[row, column] == "left":
                align = r"\multicolumn{1}{|l|}{text}"
            elif self.alignment[row, column] == "right":
                align = r"\multicolumn{1}{|r|}{text}"
            elif self.alignment[row, column] == "center":
                align = r"\multicolumn{1}{|c|}{text}"
            text = align.replace("text", text)
        return text

    def make_latex_colors(self):
        """Define the colors used in the table for latex."""
        colors = np.concatenate((self.color, self.backgroundcolor))
        colors = np.unique(colors.reshape(-1, colors.shape[-1]), axis=0)
        define = "\\definecolor{colorredgreenblue}{RGB}{red, green, blue}\n"
        text = ""
        for color in colors:
            if not np.any(color < 0):
                text += (
                    define.replace("red", "{:03.0f}".format(color[0]))
                    .replace("green", "{:03.0f}".format(color[1]))
                    .replace("blue", "{:03.0f}".format(color[2]))
                )
        return text

    def latex(self):
        """Make latex code that produces the table.

        If the table cells have colored text, the `xcolor` package must be used in the
        latex file, the backgroundcolor is not used.
        """
        latex = "\\begin{table}\n"
        latex += self.make_latex_colors()
        latex += "\\begin{tabular}{"
        for j in range(self.table.shape[1]):
            latex += "|"
            if self.alignment[0, j] == "left":
                latex += "l"
            elif self.alignment[0, j] == "right":
                latex += "r"
            elif self.alignment[0, j] == "center":
                latex += "c"
        latex += "|}\n"
        for i in range(self.table.shape[0]):
            latex += "\\hline\n"
            latex += self.make_latex_str(i, 0)
            for j in range(1, self.table.shape[1]):
                latex += " & "
                latex += self.make_latex_str(i, j)
            latex += "\\\\\n"
        latex += "\\hline\n"
        latex += "\\end{tabular}\n\\end{table}"
        return latex

    def print(self):
        """Show the table.

        Will use html rendering if possible, otherwise pretty prints the table.
        """
        try:
            from IPython.display import display

            display(self)
        except ImportError:
            echo(str(self))


class NumberTable(Table):
    """Create a table of numbers to display via pretty printing or html.

    Parameters
    ----------
    table : array or list-of-lists
        A two dimensional object containing the values of the table.
    colnames : array or list, optional
        An array or list with the same length as the second dimension of `table`.
        These are the column names displayed in the first row.
        If `rownames` are given this may contain an additional element to
        display a name of the rownames.
    rownames : array or list, optional
        An array or list with the same length as the first dimension of `table`.
        These are the row names displayed in the first column.
    colfunc : func, optional
        A function to assign colors to all values displayed. It will get
        called with `table` as argument and must return an array with
        shape `table.shape + (4,)` and type float with color values ranging from
        0 to 1. The returned array will be interpreted as RGBA color data, but
        the the A value will be ignored. If any value in a RGB triple is negative,
        no color will be applied to the corresponding cell.
        Accepts `matplotlib` colormaps.
    bgcolfunc : func, optional
        A function to set the backgroundcolors of the cells, works like
        `colorfunc`.
    norm : func, optional
        This function is applied to the table data before passing it to the
        color functions. This is intended for normalization functions from
        `matplotlib.colors` when using `matplotlib` colormaps, but can be useful
        with other functions like `numpy.gradient`.
    numfmt : str or func or array, optional
        Either a function to format numbers or a formatting string. The
        function must return a string. Can also be an array with one option per
        row, column or cell.
    compact : boolean, optional
        Skip internal row separators to save space when printing as string.
    """

    def __init__(
        self,
        table,
        colnames=None,
        rownames=None,
        colfunc=None,
        bgcolfunc=None,
        norm=None,
        numfmt=None,
        compact=False,
    ):
        table = np.array(table)
        if colnames is not None:
            headerrow = True
        else:
            headerrow = False
            colnames = []
        if rownames is not None:
            headercolumn = True
        else:
            headercolumn = False
            rownames = []

        # ensure that the shape has indices 0 and 1
        if len(table.shape) == 0:
            table = np.zeros((0, 0), dtype=table.dtype)
        elif len(table.shape) == 1:
            table = np.array([table])

        if 0 in table.shape:
            str_table = np.full(
                (max(len(rownames) + headercolumn, 1), max(len(colnames), 1)),
                "",
                dtype=object,
            )
        else:
            str_table = np.full(
                (table.shape[0] + headerrow, table.shape[1] + headercolumn),
                "",
                dtype=object,
            )

        super().__init__(
            str_table, headerrow, headercolumn, alignment="right", compact=compact
        )

        self.color, self.backgroundcolor = self.make_colors(
            table, colfunc, bgcolfunc, norm
        )

        if self.headerrow and len(colnames) != table.shape[1]:
            if (
                len(colnames) == table.shape[1] + 1 or 0 in table.shape
            ) and self.headercolumn:
                self.table[0, 0] = colnames[0]
                colnames = colnames[1:]
            else:
                raise ValueError(
                    f"Number of column names ({len(colnames)}) differs from columns "
                    f"given ({table.shape[1]})."
                )
        if (
            self.headercolumn
            and 0 not in table.shape
            and len(rownames) != table.shape[0]
        ):
            raise ValueError(
                f"Number of row names ({len(rownames)}) differs from rows given"
                f"({table.shape[0]})."
            )

        self.number_format = np.full(self.table.shape, None, dtype=object)
        if 0 not in table.shape:
            self.number_format[self.headerrow :, self.headercolumn :] = (
                self._make_option_array(numfmt, dtype=object, dimensions=table.shape)
            )

        for i in range(table.shape[0]):
            for j in range(table.shape[1]):
                self.table[i + self.headerrow, j + self.headercolumn] = (
                    self.make_string(
                        table[i, j], i + self.headerrow, j + self.headercolumn
                    )
                )
        if colnames:
            for j in range(len(colnames)):
                x = self.make_string(colnames[j], 0, j + self.headercolumn)
                self.table[0, j + self.headercolumn] = x
        if rownames:
            for i in range(len(rownames)):
                self.table[i + self.headerrow, 0] = self.make_string(
                    rownames[i], i + self.headerrow, 0
                )

        if self.headerrow:
            self.alignment[0, :] = "center"
        if self.headercolumn:
            self.alignment[:, 0] = "center"

    def make_colors(self, table, colorfunc, backgroundcolorfunc, norm):
        """Calculate the colors for the table.

        Produces an array with RGB color values in the range [0, 255] for every cell by
        calling `colorfunc(norm(table))` and `backgroundcolorfunc(norm(table))`.

        Parameters
        ----------
        table : array
            The data table without headers. Should contain numbers, but accepts
            arbitrary data as long as the color and norm functions can handle it.
        colorfunc : callable or None
            A function producing RGB color data for every cell. Color values must
            be in [0,1]. If `None` the array is filled with (-1,-1,-1).
        backgroundcolorfunc :  callable or None
            A function producing RGB color data for every cell. Color values must
            be in [0,1]. If `None` the array is filled with (-1,-1,-1).
        norm : callable or None
            A normalization applied before calling the color functions. If `None` it
            is replaced by a function that does nothing.

        Returns
        -------
        color
            The array produced by `colorfunc`
        backgroundcolor
            The array produced by `backgroundcolorfunc`
        """
        if norm is None:
            norm = lambda x: x
        color = np.full(self.table.shape + (3,), -1, dtype=int)
        if colorfunc is not None:
            color[self.headerrow :, self.headercolumn :] = np.round(
                255 * colorfunc(norm(table))[:, :, :3], 0
            )
        backgroundcolor = np.full(self.table.shape + (3,), -1, dtype=int)
        if backgroundcolorfunc is not None:
            backgroundcolor[self.headerrow :, self.headercolumn :] = np.round(
                255 * backgroundcolorfunc(norm(table))[:, :, :3], 0
            )
        return color, backgroundcolor

    def make_string(self, obj, row, col):
        """Convert obj to a string using `self.number_format[row, column]`.

        If the cell is a header or `self.number_format[row, column]` is None, `obj` is
        converted with `str`. If `self.number_format[row, column]` is a function
        `self.number_format[row, column](obj)` is called. If `self.number_format[row,
        column]` is a string `self.number_format[row, col].format(obj)` is called.
        """
        if (self.headerrow and row == 0) or (self.headercolumn and col == 0):
            return str(obj)

        if self.number_format[row, col] is None:
            return str(obj)

        if isinstance(self.number_format[row, col], str):
            return self.number_format[row, col].format(obj)

        return self.number_format[row, col](obj)
