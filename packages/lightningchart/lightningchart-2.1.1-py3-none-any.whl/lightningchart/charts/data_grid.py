from __future__ import annotations
from typing import List, Dict, Any, Union

from lightningchart import Themes, conf
from lightningchart.charts import Chart, ChartsWithAddEventListener, GeneralMethods, TitleMethods
from lightningchart.instance import Instance
from lightningchart.ui import UserInteractions
from lightningchart.utils.utils import ColorInput, convert_color_to_hex, convert_to_base64, process_spark_chart_cell


class DataGrid(GeneralMethods, TitleMethods, UserInteractions, ChartsWithAddEventListener):
    """Component for visualizing data inside a grid structure."""
    
    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = True,
    ):
        """Create a DataGrid.
        
        Args:
            theme: Visual theme
            theme_scale: Scale factor for fonts, padding (default: 1.0)
            title (str): Chart title.
            license: License key
            license_information: License information for deployment
            html_text_rendering: Enable HTML text rendering
        
        Examples:
            >>> grid = lc.DataGrid(theme=lc.Themes.Light)
            >>> grid.set_table_content([
            ...     ['Name', 'Age', 'City'],
            ...     ['Alice', 30, 'NYC'],
            ...     ['Bob', 25, 'LA']
            ... ])
        """
        instance = Instance()
        Chart.__init__(self, instance)
        
        self.instance.send(
            self.id,
            'createDataGrid',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )
        if title:
            self.set_title(title)
    
    
    def set_cell_content(
        self,
        column: int,
        row: int,
        content: Union[str, int, float, Dict[str, Any]],
    ):
        """Set content of a single cell.
        
        Args:
            column: Column index (0-based)
            row: Row index (0-based)
            content: Text, number, or spark chart config
        
        Examples:
            >>> grid.set_cell_content(0, 0, 'Header')
            >>> grid.set_cell_content(1, 1, 42)
            >>> grid.set_cell_content(2, 2, {
            ...     'type': 'spark-line',
            ...     'data': [1, 5, 3, 8, 2]
            ... })

        Returns:
            The instance of the class for fluent interface.
        """
        processed = process_spark_chart_cell(content)
        self.instance.send(self.id, 'setCellContent', {
            'column': column, 'row': row, 'content': processed
        })
        return self
    
    def set_row_content(self, row: int, content: List[Any]):
        """Set content for an entire row.
        
        Args:
            row: Row index
            content: List of cell contents

        Examples:
            >>> grid.set_row_content(7, ['Headset', 320, 340, {
            ...    'type': 'spark-pie',
            ...    'data': [30, 70]
            ... }, 'Good'])

        Returns:
            The instance of the class for fluent interface.
        """
        processed = [process_spark_chart_cell(c) for c in content]
        self.instance.send(self.id, 'setRowContent', {
            'row': row, 'content': processed
        })
        return self
    
    def set_column_content(self, column: int, content: List[Any]):
        """Set content for an entire column.
        
        Args:
            column: Column index
            content: List of cell contents

        Examples:
            >>> grid.set_column_content(3, [
            ...    'Trend',
            ...    {'type': 'spark-line', 'data': [10, 15, 12, 18], 'strokeStyle': '#FF0000'},
            ...    {'type': 'spark-bar', 'data': [5, 10, 8, 12], 'fillStyle': '#00FF00'},
            ...    {'type': 'spark-win-loss', 'data': [1, -1, 1, 1], 'winFillStyle': 'green', 'lossFillStyle': 'red'},
            ... ])

        Returns:
            The instance of the class for fluent interface.
        """
        processed = [process_spark_chart_cell(c) for c in content]
        self.instance.send(self.id, 'setColumnContent', {
            'column': column, 'content': processed
        })
        return self
    
    def set_table_content(self, content: List[List[Any]]):
        """Set content for the entire grid at once.
    
        Spark Charts support:
            - spark-line: { type, data, strokeStyle?, markers? }
            - spark-area: { type, data, fillStyle?, strokeStyle?, markers? }
            - spark-bar: { type, data, fillStyle?, strokeStyle?, barSize?, gap? }
            - spark-win-loss: { type, data, winFillStyle?, lossFillStyle?, strokeStyle?, threshold?, barSize?, gap? }
            - spark-pie: { type, data, strokeStyle? }
        
        Styles:
            - Simple: 'fillStyle': '#FF0000' or 'fillStyle': 'red'
            - Advanced: 'fillStyle': {'type': 'radial-gradient', 'stops': [...]}
            - Line: 'strokeStyle': {'thickness': 2, 'color': '#000'}
        
        Markers (spark-line/spark-area):
            Three marker types are supported:
            
            1. Point Marker - Highlights a single XY coordinate:
            {
                'type': 'point',
                'value': 'start' | 'end' | 'min' | 'max' | {'x': 5, 'y': 10},
                'fillStyle': '#FF0000',  # optional
                'size': 10,               # optional
                'shape': 'circle',        # optional
                'rotation': 45            # optional (degrees)
            }
            - 'start': First data point
            - 'end': Last data point
            - 'min': Lowest Y value
            - 'max': Highest Y value
            - {'x': 5, 'y': 10}: Exact coordinate
            
            2. Axis Band - Highlights an interval along X or Y axis:
            {
                'type': 'axis-band',
                'axis': 'x' | 'y',
                'start': 0,
                'end': 10,
                'fillStyle': '#FF000033',    # optional (recommended transparent)
                'strokeStyle': {'thickness': 1, 'color': '#FF0000'}  # optional
            }
            
            3. Constant Line - Highlights a location along X or Y axis:
            {
                'type': 'constant-line',
                'axis': 'x' | 'y',
                'value': 5,
                'strokeStyle': {'thickness': 2, 'color': '#FF0000'}  # optional
            }
        
        Examples:
            Basic spark charts:
            >>> grid.set_table_content([
            ...     ['Product', 'Trend', 'Revenue'],
            ...     ['A', {'type': 'spark-line', 'data': [10, 20, 15]}, 
            ...           {'type': 'spark-bar', 'data': [5, 10, 8]}],
            ... ])
            
            With point markers:
            >>> grid.set_table_content([
            ...     ['Stock', 'Price'],
            ...     ['TECH', {'type': 'spark-line', 
            ...               'data': [100, 105, 98, 110, 108],
            ...               'strokeStyle': {'thickness': 2, 'color': '#00FF00'},
            ...               'markers': [
            ...                   {'type': 'point', 'value': 'max', 'fillStyle': 'green', 'size': 8},
            ...                   {'type': 'point', 'value': 'min', 'fillStyle': 'red', 'size': 8}
            ...               ]}]
            ... ])
            
            With axis band (highlight range):
            >>> grid.set_table_content([
            ...     ['Metric', 'Values'],
            ...     ['CPU', {'type': 'spark-area',
            ...              'data': [{'x': 0, 'y': 45}, {'x': 1, 'y': 60}, {'x': 2, 'y': 75}],
            ...              'fillStyle': '#4488FF',
            ...              'markers': [
            ...                  {'type': 'axis-band', 'axis': 'y', 'start': 70, 'end': 100,
            ...                   'fillStyle': '#FF000033'}  # Danger zone
            ...              ]}]
            ... ])
            
            With constant line (threshold):
            >>> grid.set_table_content([
            ...     ['Revenue', 'Quarterly'],
            ...     ['Q1-Q4', {'type': 'spark-line',
            ...                'data': [85, 92, 88, 95],
            ...                'markers': [
            ...                    {'type': 'constant-line', 'axis': 'y', 'value': 90,
            ...                     'strokeStyle': {'thickness': 2, 'color': 'orange'}}
            ...                ]}]
            ... ])
            
            Combined markers:
            >>> grid.set_table_content([
            ...     ['Sales', 'Performance'],
            ...     ['2024', {'type': 'spark-line',
            ...               'data': [50, 65, 55, 80, 75, 90],
            ...               'markers': [
            ...                   {'type': 'point', 'value': 'max', 'fillStyle': 'green'},
            ...                   {'type': 'axis-band', 'axis': 'y', 'start': 60, 'end': 70,
            ...                    'fillStyle': '#FFFF0033'},
            ...                   {'type': 'constant-line', 'axis': 'y', 'value': 75}
            ...               ]}]
            ... ])

        Returns:
            The instance of the class for fluent interface.
        """
        processed = [[process_spark_chart_cell(c) for c in row] for row in content]
        self.instance.send(self.id, 'setTableContent', {'content': processed})
        return self
        
    def set_cell_background_fill_style(
        self,
        column: int,
        row: int,
        color: ColorInput | None,
    ):
        """Set background color of a single cell.
        
        Args:
            column: Column index
            row: Row index
            color: Color string or object. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setCellBackgroundFillStyle', {
            'column': column,
            'row': row,
            'color': color
        })
        return self
    
    def set_cell_text_fill_style(
        self,
        column: int,
        row: int,
        color: ColorInput | None,
    ):
        """Set text color of a single cell.
        
        Args:
            column: Column index
            row: Row index
            color: Color string or object. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setCellTextFillStyle', {
            'column': column,
            'row': row,
            'color': color
        })
        return self
    
    def set_cell_text_font(
        self,
        column: int,
        row: int,
        size: int = None,
        family: str = None,
        weight: str = None,
        style: str = None,
    ):
        """Set font properties for a single cell.
        
        Args:
            column (int): Column index (0-based).
            row (int): Row index (0-based).
            size (int, optional): CSS font size in pixels (e.g., 14, 16).
            family (str, optional): CSS font family (e.g., 'Arial', 'Arial, sans-serif').
            weight (str, optional): CSS font weight ('normal', 'bold', '100'-'900').
            style (str, optional): CSS font style ('normal', 'italic', 'oblique').
        
        Examples:
            Set bold Arial font:
            >>> grid.set_cell_text_font(0, 0, size=16, family='Arial', weight='bold')
            
            Set italic small-caps:
            >>> grid.set_cell_text_font(1, 2, style='italic')
            
            Set only size:
            >>> grid.set_cell_text_font(2, 3, size=18)
        
        Returns:
            The instance of the class for fluent interface.
        """
        font = {}
        if size is not None: 
            font['size'] = size
        if family is not None: 
            font['family'] = family
        if weight is not None: 
            font['weight'] = weight
        if style is not None: 
            font['style'] = style
        
        self.instance.send(self.id, 'setCellTextFont', {
            'column': column,
            'row': row,
            'font': font
        })
        return self
    
    def set_cell_padding(
        self,
        column: int,
        row: int,
        padding: Union[int, Dict[str, int]],
    ):
        """Set padding of a single cell.
        
        Args:
            column (int): Zero-based column index to affect.
            row (int): Row index (0-based).
            padding: Either a single integer (applies to all sides),
                or a dict with any of {'top','right','bottom','left'} integers,
                e.g. {'left': 8, 'right': 8}.

        Returns:
            The instance of the class for fluent interface.

        """
        self.instance.send(self.id, 'setCellPadding', {
            'column': column,
            'row': row,
            'padding': padding
        })
        return self
    
    def set_cell_highlight(
        self,
        column: int,
        row: int,
        highlight: Union[bool, float],
    ):
        """Highlight a cell.
        
        Args:
            column: Column index
            row: Row index
            highlight: True/False or float (0-1)

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCellHighlight', {
            'column': column,
            'row': row,
            'highlight': highlight
        })
        return self    
    
    def set_cells_background_fill_style(self, color: ColorInput):
        """Set default background color for all existing and future cells.
        
        Args:
            color: Color string or object. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setCellsBackgroundFillStyle', {
            'color': color
        })
        return self
    
    def set_cells_text_fill_style(self, color: ColorInput):
        """Set default text color for all existing and future cells.
        
        Args:
            color: Color string or object. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setCellsTextFillStyle', {
            'color': color
        })
        return self
    
    def set_cells_text_font(
        self,
        size: int = None,
        family: str = None,
        weight: str = None,
        style: str = None,
        variant: bool = None,
    ):
        """Set default font for all existing and future cells.

        Args:
            size (int, optional): CSS font size in pixels (e.g., 14, 16).
            family (str, optional): CSS font family (e.g., 'Arial', 'Arial, sans-serif').
            weight (str, optional): CSS font weight ('normal', 'bold', '100'-'900').
            style (str, optional): CSS font style ('normal', 'italic', 'oblique').
            variant (bool, optional): Font variant - True for 'small-caps', False for 'normal'.
        
        Examples:
            >>> grid.set_cells_text_font(size=14, family='Arial', weight='bold')
        
        Returns:
            The instance of the class for fluent interface.
        """
        font = {}
        if size is not None: 
            font['size'] = size
        if family is not None: 
            font['family'] = family
        if weight is not None: 
            font['weight'] = weight
        if style is not None: 
            font['style'] = style
        if variant is not None: 
            font['variant'] = variant
        
        self.instance.send(self.id, 'setCellsTextFont', {'font': font})
        return self
    
    def set_cells_padding(self, padding: Union[int, Dict[str, int]]):
        """Set default padding for all existing and future cells.
        
        Args:
            padding: Either a single integer (applies to all sides),
                or a dict with any of {'top','right','bottom','left'} integers,
                e.g. {'top': 6, 'bottom': 6, 'left': 10, 'right': 10}.
        
        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCellsPaddings', {'padding': padding})
        return self
    
    def set_cells_borders(self, borders: Union[Dict[str, bool], bool, None] = None):
        """Set default border visibility for all cells.
        
        Args:
            borders: Dict with 'top'/'bottom'/'left'/'right' booleans,
                    True for all borders, False/None for no borders
        
        Examples:
            Show all borders:
            >>> grid.set_cells_borders(True)
            
            Show only top and bottom:
            >>> grid.set_cells_borders({'top': True, 'bottom': True})
            
            Hide all borders:
            >>> grid.set_cells_borders(False)
        
        Returns:
            The instance of the class for fluent interface.
        """
        if borders is True:
            borders_obj = {'top': True, 'bottom': True, 'left': True, 'right': True}
        elif borders is False or borders is None:
            borders_obj = None
        else:
            borders_obj = borders
        
        self.instance.send(self.id, 'setCellsBorders', {'borders': borders_obj})
        return self
    
    def set_cells_border_stroke_style(
        self,
        thickness: int = 1,
        color: ColorInput | None = None
    ):
        """
        Set the border stroke style used for all cells in the grid.

        Args:
            thickness (int, optional): Border line thickness in pixels. Defaults to 1.
            color (Any, optional): Border color. Use 'transparent' or None to hide. 

        Examples:
            >>> grid.set_cells_border_stroke_style(thickness=1, color='#E0E0E0')

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setCellsBorderStrokeStyle', {
            'thickness': thickness,
            'color': color
        })
        return self
    
    def set_row_background_fill_style(self, row: int, color: ColorInput | None):
        """
        Set background fill style for all cells along a specific row.

        Args:
            row (int): Zero-based row index.
            color (Any): Fill color for the row. Use 'transparent' or None to hide.

        Examples:
            >>> grid.set_row_background_fill_style(0, '#2196F3')  # header row

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setRowBackgroundFillStyle', {
            'row': row,
            'color': color
        })
        return self
    
    def set_column_background_fill_style(self, column: int, color: ColorInput | None):
        """
        Set background fill style for all cells along a specific column.

        Args:
            column (int): Zero-based column index.
            color (Any): Fill color for the column. Use 'transparent' or None to hide.

        Examples:
            >>> grid.set_column_background_fill_style(4, '#F5F5F5')

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setColumnBackgroundFillStyle', {
            'column': column,
            'color': color
        })
        return self
    
    def set_row_highlight(self, row: int, highlight: Union[bool, float]):
        """
        Highlight all cells in a row (theme-based brightening/darkening).

        Args:
            row (int): Zero-based row index.
            highlight (bool | float): If a bool, enable/disable highlight.
                If a float, intensity in range [0.0, 1.0] (higher = stronger effect).

        Examples:
            >>> grid.set_row_highlight(2, True)      # enable with default intensity
            >>> grid.set_row_highlight(2, 0.35)      # set custom intensity

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRowHighlight', {
            'row': row,
            'highlight': highlight
        })
        return self
    
    def set_column_highlight(self, column: int, highlight: Union[bool, float]):
        """
        Highlight all cells in a column (theme-based brightening/darkening).

        Args:
            column (int): Zero-based column index.
            highlight (bool | float): If a bool, enable/disable highlight.
                If a float, intensity in range [0.0, 1.0] (higher = stronger effect).

        Examples:
            >>> grid.set_column_highlight(2, True)      # enable with default intensity
            >>> grid.set_column_highlight(2, 0.35)      # set custom intensity

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setColumnHighlight', {
            'column': column,
            'highlight': highlight
        })
        return self
    
    def remove_cell(
        self,
        column: int,
        row: int,
    ):
        """Remove the cell at the intersection of the specified column and row.
        
        Args:
            column: Column index (0-based)
            row: Row index (0-based)

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'removeCell', {
            'column': column,
            'row': row,
        })
        return self
    
    def remove_cells(self):
        """Removes all cells.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'removeCells', {})
        return self
    
    def remove_column(
        self,
        column: int
    ):
        """Remove all cells along a specified column. Removing a column shifts the column indexes of all cells to the right of the removed column.
        
        Args:
            column: Column index (0-based)

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'removeColumn', {
            'column': column,
        })
        return self
    
    def remove_row(self, row: int):
        """Remove all cells along the specified row (rows below shift up)."""
        self.instance.send(self.id, 'removeRow', {'row': row})
        return self

    def set_background_effect(self, enabled: bool):
        """Enable/disable theme background effect on the grid."""
        self.instance.send(self.id, 'setBackgroundEffect', {'enabled': enabled})
        return self

    def set_cell_borders(self, column: int, row: int,
                     borders: dict[str, bool] | None = None):
        """
        Set visibility of the borders for a single cell.

        Args:
            column: Zero-based column index of the target cell.
            row: Zero-based row index of the target cell.
            borders: Per-side visibility flags, e.g.
                {'top': True, 'right': False, 'bottom': True, 'left': True}.
                Omitted sides keep their current state.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCellBorders', {
            'column': column, 'row': row, 'borders': borders or {}
        })
        return self


    def set_column_borders(self, column: int,
                        borders: dict[str, bool] | None = None):
        """
        Set visibility of borders for all cells in a column.

        Args:
            column: Zero-based column index to affect.
            borders: Per-side visibility flags applied to each cell in the column,
                e.g. {'left': True, 'right': True}. Omitted sides are unchanged.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setColumnBorders', {
            'column': column, 'borders': borders or {}
        })
        return self


    def set_cell_content_alignment(self, column: int, row: int, alignment: str):
        """
        Set content alignment for a single cell.

        Args:
            column: Zero-based column index of the target cell.
            row: Zero-based row index of the target cell.
            alignment: One of DataGrid's alignment options, e.g.
                'center' | 'right-center' | 'left-center' | 'right-top' | 'left-top' | 'right-bottom' | 'left-bottom' | 'center-top' | 'center-bottom'.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCellContentAlignment', {
            'column': column, 'row': row, 'alignment': alignment
        })
        return self


    def set_cells_content_alignment(self, alignment: str):
        """
        Set the default content alignment for all existing and future cells.

        Args:
            alignment: One of DataGrid's alignment options, e.g.
                'center' | 'right-center' | 'left-center' | 'right-top' | 'left-top' | 'right-bottom' | 'left-bottom' | 'center-top' | 'center-bottom'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCellsContentAlignment', {'alignment': alignment})
        return self


    def set_column_content_alignment(self, column: int, alignment: str):
        """
        Set content alignment for all cells in a specific column.

        Args:
            column: Zero-based column index to affect.
            alignment: One of DataGrid's alignment options, e.g.
                'center' | 'right-center' | 'left-center' | 'right-top' | 'left-top' | 'right-bottom' | 'left-bottom' | 'center-top' | 'center-bottom'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setColumnContentAlignment', {
            'column': column, 'alignment': alignment
        })
        return self

    def set_column_paddings(self, column: int, padding: int | dict[str, int]):
        """
        Set paddings for all cells in a specific column.

        Args:
            column: Zero-based column index to affect.
            padding: Either a single integer (applies to all sides),
                or a dict with any of {'top','right','bottom','left'} integers,
                e.g. {'left': 8, 'right': 8}.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setColumnPaddings', {
            'column': column, 'padding': padding
        })
        return self


    def set_column_text_fill_style(self, column: int, color: ColorInput | None):
        """
        Set the text fill color of all cells along a single column.

        Args:
            column (int): Column index (0-based).
            color (Any): Color value (e.g., '#FF0000', 'red', RGB tuple). Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setColumnTextFillStyle', {
            'column': column,
            'color': color
        })
        return self

    def set_column_text_font(self,
                            column: int,
                            size: int | None = None,
                            family: str | None = None,
                            weight: str | int | None = None,
                            style: str | None = None,
                            variant: bool | None = None):
        """
        Set the text font of all cells along a single column.

        Args:
            column (int): Column index (0-based).
            size (int, optional): Font size in CSS px.
            family (str, optional): CSS font family or list.
            weight (str|int, optional): CSS font weight ('normal'|'bold'|100..900).
            style (str, optional): CSS font style ('normal'|'italic'|'oblique').
            variant (bool, optional): True='small-caps', False='normal'.

        Returns:
            The instance of the class for fluent interface.
        """
        font: dict[str, Any] = {}
        if size is not None: 
            font['size'] = size
        if family is not None: 
            font['family'] = family
        if weight is not None: 
            font['weight'] = weight
        if style is not None: 
            font['style'] = style
        if variant is not None: 
            font['variant'] = variant
        self.instance.send(self.id, 'setColumnTextFont', {
            'column': column,
            'font': font
        })
        return self


    def set_column_width(self, column: int, width: int | dict | None):
        """
        Set width of a column.

        Args:
            column (int): Column index (0-based).
            width (int|dict|None): Pixel width (int), constraints dict like {'min': 80, 'max': 200},
                                or None to fit-to-content.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setColumnWidth', {
            'column': column,
            'width': width
        })
        return self


    def set_grid_background_fill_style(self, color: ColorInput | None):
        """
        Set the grid background fill style.

        Args:
            color (Any): Color value for the grid background. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setGridBackgroundFillStyle', {
            'color': color
        })
        return self


    def set_row_borders(self, row: int, borders: dict[str, bool] | None = None):
        """
        Set border visibility for all cells along a single row.

        Args:
            row (int): Row index (0-based).
            borders (dict[str,bool]|None): Any of {'top', 'right', 'bottom', 'left'} set to True/False.
                                        Omitted sides remain unchanged.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRowBorders', {
            'row': row,
            'borders': borders or {}
        })
        return self


    def set_row_content_alignment(self, row: int, alignment: str):
        """
        Set content alignment for all cells along a single row.

        Args:
            row (int): Row index (0-based).
            alignment (str): Alignment keyword (e.g., 'center' | 'right-center' | 'left-center' | 'right-top' | 'left-top' | 'right-bottom' | 'left-bottom' | 'center-top' | 'center-bottom').

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRowContentAlignment', {
            'row': row,
            'alignment': alignment
        })
        return self


    def set_row_height(self, row: int, height: int | dict | None):
        """
        Set the height of a row.

        Args:
            row (int): Row index (0-based).
            height (int|dict|None): Pixel height (int), constraints dict like {'min': 20, 'max': 40},
                                    or None to fit-to-content.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRowHeight', {
            'row': row,
            'height': height
        })
        return self


    def set_row_paddings(self, row: int, padding: int | dict[str, int]):
        """
        Set paddings for all cells along a single row.

        Args:
            row (int): Row index (0-based).
            padding (int|dict): Single number (applies to all sides) or dict with any of
                                {'top','right','bottom','left'} in pixels.
                                e.g. {'left': 8, 'right': 8}.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRowPaddings', {
            'row': row,
            'padding': padding
        })
        return self


    def set_row_text_fill_style(self, row: int, color: ColorInput | None):
        """
        Set text fill color for all cells along a single row.

        Args:
            row (int): Row index (0-based).
            color (Any): Color value. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRowTextFillStyle', {
            'row': row,
            'color': convert_color_to_hex(color) if color is not None else None
        })
        return self


    def set_row_text_font(self,
                        row: int,
                        size: int | None = None,
                        family: str | None = None,
                        weight: str | int | None = None,
                        style: str | None = None,
                        variant: bool | None = None):
        """
        Set text font for all cells along a single row.

        Args:
            row (int): Row index (0-based).
            size (int, optional): Font size in px.
            family (str, optional): CSS font family or list.
            weight (str|int, optional): 'normal'|'bold'|100..900.
            style (str, optional): 'normal'|'italic'|'oblique'.
            variant (bool, optional): True='small-caps', False='normal'.

        Returns:
            The instance of the class for fluent interface.
        """
        font: dict[str, Any] = {}
        if size is not None: 
            font['size'] = size
        if family is not None: 
            font['family'] = family
        if weight is not None: 
            font['weight'] = weight
        if style is not None: 
            font['style'] = style
        if variant is not None: 
            font['variant'] = variant
        self.instance.send(self.id, 'setRowTextFont', {
            'row': row,
            'font': font
        })
        return self
    
    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options for DataGrid.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Returns:
            The instance of the class for fluent interface.

        Examples:
            # Disable all interactions:
            >>> grid.set_user_interactions(None)

            # Restore default interactions:
            >>> grid.set_user_interactions()
            ... grid.set_user_interactions({})

            # Configure specific interactions:
            >>> grid.set_user_interactions({
            ...    'scroll': {
            ...        'x': False,
            ...        'y': True,
            ...        'wheel': {}  # wheel = enabled
            ...    }
            ...})  

            # Disable all scrolling
            >>> grid.set_user_interactions({ 'scroll': False })      
        """
        return super().set_user_interactions(interactions)
    
    def translate_coordinate(self, coordinate: dict, target: str, source: str = None):
        """Translate DataGrid coordinates between systems.
        
        Args:
            coordinate: Dict with 'x'/'y' (relative) or 'clientX'/'clientY' (client)
            target: 'relative' | 'client'
            source: 'relative' | 'client' (auto-detected if None)
        
        Returns:
            Dict with translated coordinates
        
        Examples:
            >>> # Client to relative
            >>> loc = grid.translate_coordinate({'clientX': 500, 'clientY': 300}, target='relative')
            >>> # Relative to client
            >>> loc = grid.translate_coordinate({'x': 50, 'y': 100}, target='client')
        """
        if source is None:
            source = 'client' if 'clientX' in coordinate else 'relative'
        return self.instance.get(self.id, 'translateCoordinateGeneral', {
            'coordinate': coordinate,
            'source': source,
            'target': target
        })  
    
    def set_cell_image_content(
        self,
        column: int,
        row: int,
        source: str,
        colspan: int = 1,
        rowspan: int = 1,
        height: int = None,
        width: int = None,
    ):
        """Set an image as cell content.
        
        Args:
            column: Column index (0-based)
            row: Row index (0-based)
            source: Image file path or URL
            colspan: Number of columns to span (default: 1)
            rowspan: Number of rows to span (default: 1)
            height: Image height in pixels
            width: Image width in pixels
        
        Examples:
            >>> grid.set_cell_image_content(0, 1, "logo.png", height=32)
            >>> grid.set_cell_image_content(2, 3, "https://example.com/icon.png", width=48)
        
        Returns:
            The instance of the class for fluent interface.
        """
        base64_image = convert_to_base64(source)
        self.instance.send(self.id, 'setCellImageContent', {
            'column': column,
            'row': row,
            'colspan': colspan,
            'rowspan': rowspan,
            'source': base64_image,
            'height': height,
            'width': width,
        })
        return self
    
class DataGridDashboard(DataGrid):
    """Class for DataGrid contained in Dashboard."""

    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        title: str = None,
    ):
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'createDataGridDashboard',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})

class DataGridContainer(DataGrid):
    def __init__(self, 
                 instance, 
                 container, 
                 column, 
                 row, 
                 colspan, 
                 rowspan, 
                 title,
                 ):
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'createDataGridContainer',
            {
                'containerId': container.id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})