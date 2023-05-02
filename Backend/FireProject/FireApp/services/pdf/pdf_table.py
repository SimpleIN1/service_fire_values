from numbers import Number

from fpdf.fonts import FontFace
from fpdf.table import Table
from fpdf.enums import Align, TableCellFillMode


class TableOverride(Table):
    def _get_col_width(self, i, j, colspan=1):
        if not self._col_widths or i == 0:
            cols_count = self.rows[i].cols_count
            return colspan * (self._width / cols_count)
        if isinstance(self._col_widths, Number):
            return colspan * self._col_widths
        if j >= len(self._col_widths):
            raise ValueError(
                f"Invalid .col_widths specified: missing width for table() column {j + 1} on row {i + 1}"
            )
        # pylint: disable=unsubscriptable-object
        col_width = 0
        for k in range(j, j + colspan):
            col_ratio = self._col_widths[k] / sum(self._col_widths)
            col_width += col_ratio * self._width
        return col_width

    def _render_table_row(self, i, fill=False, **kwargs):
        row = self.rows[i]
        lines_heights_per_cell = self._get_lines_heights_per_cell(i)
        row_height = max(sum(lines_heights) for lines_heights in lines_heights_per_cell)
        j = 0
        while j < len(row.cells):

            if i == 1:
                row_height = 20
            else:
                row_height = row_height

            if i == 1 and j == 4:
                cell_line_height = 5
            else:
                cell_line_height = row_height / len(lines_heights_per_cell[j])

            self._render_table_cell(
                i,
                j,
                cell_line_height=cell_line_height,
                row_height=row_height,
                fill=fill,
                **kwargs,
            )
            j += row.cells[j].colspan
        self._fpdf.ln(row_height)

    def render(self): #override
        "This is an internal method called by `fpdf.FPDF.table()` once the table is finished"
        if self._width > self._fpdf.epw:
            raise ValueError(
                f"Invalid value provided .width={self._width}: effective page width is {self._fpdf.epw}"
            )
        table_align = Align.coerce(self._align)
        if table_align == Align.J:
            raise ValueError("JUSTIFY is an invalid value for table .align")
        prev_l_margin = self._fpdf.l_margin
        if table_align == Align.C:
            self._fpdf.l_margin = (self._fpdf.w - self._width) / 2
            self._fpdf.x = self._fpdf.l_margin
        elif table_align == Align.R:
            self._fpdf.l_margin = self._fpdf.w - self._width
            self._fpdf.x = self._fpdf.l_margin
        elif self._fpdf.x != self._fpdf.l_margin:
            self._fpdf.l_margin = self._fpdf.x
        for i in range(len(self.rows)):
            with self._fpdf.offset_rendering() as test:
                self._render_table_row(i)
            if test.page_break_triggered:
                # pylint: disable=protected-access
                self._fpdf._perform_page_break()
                if self._first_row_as_headings:  # repeat headings on top:
                    self._render_table_row(0)
                    self._render_table_row(1)
            self._render_table_row(i)
        self._fpdf.l_margin = prev_l_margin
        self._fpdf.x = self._fpdf.l_margin

    def _render_table_cell(
        self,
        i,
        j,
        cell_line_height,
        row_height,
        fill=False,
        lines_heights_only=False,
        **kwargs,
    ):
        """
        If `lines_heights_only` is True, returns a list of lines (subcells) heights.
        """
        row = self.rows[i]
        cell = row.cells[j]
        col_width = self._get_col_width(i, j, cell.colspan)
        lines_heights = []
        if cell.img:
            if lines_heights_only:
                info = self._fpdf.preload_image(cell.img)[2]
                img_ratio = info.width / info.height
                if cell.img_fill_width or row_height * img_ratio > col_width:
                    img_height = col_width / img_ratio
                else:
                    img_height = row_height
                lines_heights += [img_height]
            else:
                x, y = self._fpdf.x, self._fpdf.y
                self._fpdf.image(
                    cell.img,
                    w=col_width,
                    h=0 if cell.img_fill_width else row_height,
                    keep_aspect_ratio=True,
                )
                self._fpdf.set_xy(x, y)
        text_align = cell.align or self._text_align
        if not isinstance(text_align, (Align, str)):
            text_align = text_align[j]
        if i == 0 and self._first_row_as_headings:
            style = self._headings_style
        else:
            style = cell.style or row.style
        if lines_heights_only and style:
            # Avoid to generate font-switching instructions: BT /F... Tf ET
            style = style.replace(emphasis=None)
        if style and style.fill_color:
            fill = True
        elif (
            not fill
            and self._cell_fill_color
            and self._cell_fill_mode != TableCellFillMode.NONE
        ):
            if self._cell_fill_mode == TableCellFillMode.ALL:
                fill = True
            elif self._cell_fill_mode == TableCellFillMode.ROWS:
                fill = bool(i % 2)
            elif self._cell_fill_mode == TableCellFillMode.COLUMNS:
                fill = bool(j % 2)
        if fill and self._cell_fill_color and not (style and style.fill_color):
            style = (
                style.replace(fill_color=self._cell_fill_color)
                if style
                else FontFace(fill_color=self._cell_fill_color)
            )

        with self._fpdf.use_font_face(style):
            lines = self._fpdf.multi_cell(
                w=col_width,
                h=row_height,
                txt=cell.text,
                max_line_height=cell_line_height,
                border=self.get_cell_border(i, j),
                align=text_align,
                new_x="RIGHT",
                new_y="TOP",
                fill=fill,
                split_only=lines_heights_only,
                markdown=self._markdown,
                **kwargs,
            )
        if lines_heights_only and not cell.img:
            lines_heights += (len(lines) or 1) * [self._line_height]

        if lines_heights_only:
            return lines_heights