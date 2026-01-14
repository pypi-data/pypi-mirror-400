from __future__ import annotations
from typing import Optional

import numpy as np

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithAddEventListener,
    SeriesWithIntensityInterpolation,
    SeriesWithWireframe,
    SeriesWithClear,
    SeriesWithDrawOrder,
    SeriesWithXYAxes,
)
from lightningchart.utils.utils import LegendOptions, build_series_legend_options, convert_color_to_hex, convert_to_list, convert_to_matrix


class HeatmapGridSeries(
    ComponentWithPaletteColoring,
    SeriesWithIntensityInterpolation,
    SeriesWithWireframe,
    SeriesWithClear,
    SeriesWithDrawOrder,
    SeriesWithAddEventListener,
    SeriesWithXYAxes,
):
    """Series for visualizing 2D heatmap data in a grid."""

    def __init__(
        self,
        chart: Chart,
        columns: int,
        rows: int,
        data_order: str = 'columns',
        automatic_color_index: int = None,
        heatmap_data_type: str = 'intensity',
        axis_x: Axis = None,
        axis_y: Axis = None,
        legend: Optional[LegendOptions] = None,
        max_tile_size: int = None,
    ):
        super().__init__(chart, axis_x, axis_y)
        legend_options = build_series_legend_options(legend)

        self.instance.send(
            self.id,
            'heatmapGridSeries',
            {
                'chart': self.chart.id,
                'columns': columns,
                'rows': rows,
                'dataOrder': data_order,
                'automaticColorIndex': automatic_color_index,
                'heatmapDataType': heatmap_data_type,
                'axisX': axis_x,
                'axisY': axis_y,
                'legend': legend_options if legend_options else None,
                'maxTileSize': max_tile_size,
            },
        )

    def set_start(self, x: int | float, y: int | float):
        """Set start coordinate of Heatmap on its X and Y axis where the first heatmap sample will be positioned

        Args:
            x: x-coordinate.
            y: y-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStartXY', {'x': x, 'y': y})
        return self

    def set_end(self, x: int | float, y: int | float):
        """Set end coordinate of Heatmap on its X and Y axis where the last heatmap sample will be positioned.

        Args:
            x: x-coordinate.
            y: y-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setEndXY', {'x': x, 'y': y})
        return self

    def set_step(self, x: int | float, y: int | float):
        """Set Step between each consecutive heatmap value on the X and Y Axes.

        Args:
            x: x-coordinate.
            y: y-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStepXY', {'x': x, 'y': y})
        return self
    
    def set_aggregation(self, mode: str | None):
        """
        Set heatmap intensity aggregation mode.

        Notes:
            - Works when intensity interpolation is disabled.
            (e.g., `set_intensity_interpolation(False)`)

        Args:
            mode: Aggregation mode - 'max', 'min', or None to disable.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAggregation', {'mode': mode})
        return self
    

    def invalidate_intensity_values(
        self,
        data,
        column_index: int = None,
        row_index: int = None,
        sample_index: int = None,
        columns: int = None,
        rows: int = None,
    ):
        """Invalidate range of heatmap intensity values.
        
        Supports both 2D matrix and flat array formats.
        Flat arrays are more efficient for large datasets and TypedArray transfer.

        Args:
            data: Intensity values as either:
                  - 2D matrix: list[list[int | float]] or np.ndarray (2D)
                  - Flat array: list[int | float] or np.ndarray (1D)
            column_index: Index of first invalidated column (for partial updates).
            row_index: Index of first invalidated row (for partial updates).
            sample_index: Sample index for scrolling heatmaps.
            columns: Number of columns (required for flat array partial updates).
            rows: Number of rows (required for flat array partial updates).

        Returns:
            The instance of the class for fluent interface.
            
        Examples:
            Full update with 2D matrix:
            >>> series.invalidate_intensity_values([[1, 2], [3, 4]])
            
            Full update with flat array (efficient):
            >>> series.invalidate_intensity_values([1, 2, 3, 4, 5, 6])
            
            Partial update with flat array:
            >>> series.invalidate_intensity_values(
            ...     data=[1, 2, 3, 4],
            ...     column_index=5, row_index=2,
            ...     columns=2, rows=2
            ... )
        """
        is_flat = False
        
        if isinstance(data, np.ndarray):
            is_flat = data.ndim == 1
            data = convert_to_list(data) if is_flat else convert_to_matrix(data)
        elif isinstance(data, (list, tuple)):
            if len(data) > 0 and isinstance(data[0], (list, tuple, np.ndarray)):
                is_flat = False
                data = convert_to_matrix(data)
            else:
                is_flat = True
                data = convert_to_list(data)
        else:
            data = convert_to_list(data)
            is_flat = True
        if column_index is not None and row_index is not None:
            if is_flat and columns is not None and rows is not None:
                payload = {
                    'iColumn': column_index,
                    'iRow': row_index,
                    'columns': columns,
                    'rows': rows,
                    'values': data,
                }
            else:
                payload = {
                    'iColumn': column_index,
                    'iRow': row_index,
                    'values': data,
                }
            if sample_index is not None:
                payload['iSample'] = sample_index
        else:
            payload = {'data': data}

        self.instance.send(self.id, 'invalidateIntensityValues', payload)
        return self

    def set_contours(
        self,
        levels: list[dict] = None,
        shadows: str = None,
        show_labels: bool = None,
    ):
        """Set contour lines for heatmap visualization.
        
        Args:
            levels: List of contour level configurations. Each level dict can contain:
                - value (float, required): Contour value threshold
                - label (str, optional): Text label for contour
                - label_color (str, optional): Color for label (hex "#FF0000" or name "red")
                - label_font (dict, optional): Font settings with keys:
                    - size (int): Font size in pixels
                    - family (str): Font family (e.g., "Arial, sans-serif")
                    - weight (str): Font weight ("normal", "bold", "bolder", "lighter", or 100-900)
                    - style (str): Font style ("normal", "italic", "oblique")
                - stroke_style (dict, optional): Line style with keys:
                    - thickness (int): Line thickness in pixels
                    - color (str): Line color (hex or name)
            shadows: Shadow color for contours (hex "#000000" or name "black", None to disable)
            show_labels: Whether to show contour labels
            
        Returns:
            The instance of the class for fluent interface.
            
        Examples:
            Simple contours:
            >>> series.set_contours(
            ...     levels=[
            ...         {'value': 10},
            ...         {'value': 50},
            ...         {'value': 90}
            ...     ]
            ... )
            
            Styled contours with labels:
            >>> series.set_contours(
            ...     levels=[
            ...         {
            ...             'value': 25,
            ...             'label': 'Low',
            ...             'label_color': '#0000FF',
            ...             'label_font': {'size': 14, 'weight': 'bold'},
            ...             'stroke_style': {'thickness': 2, 'color': '#0000FF'}
            ...         },
            ...         {
            ...             'value': 75,
            ...             'label': 'High',
            ...             'label_color': '#FF0000',
            ...             'label_font': {'size': 16, 'family': 'Arial'},
            ...             'stroke_style': {'thickness': 3, 'color': '#FF0000'}
            ...         }
            ...     ],
            ...     shadows='#00000040',
            ...     show_labels=True
            ... )
        """
        if levels is None:
            self.instance.send(self.id, 'setContours', {'config': None})
            return self        
        processed_levels = []
        for level in levels:
            processed_level = {'value': level['value']}
            
            if 'label' in level:
                processed_level['label'] = level['label']
                
            if 'label_color' in level and level['label_color'] is not None:
                processed_level['labelColor'] = convert_color_to_hex(level['label_color'])
                
            if 'label_font' in level and level['label_font'] is not None:
                processed_level['labelFont'] = level['label_font']
                
            if 'stroke_style' in level and level['stroke_style'] is not None:
                stroke = level['stroke_style']
                processed_stroke = {}
                if 'thickness' in stroke:
                    processed_stroke['thickness'] = stroke['thickness']
                if 'color' in stroke and stroke['color'] is not None:
                    processed_stroke['color'] = convert_color_to_hex(stroke['color'])
                processed_level['strokeStyle'] = processed_stroke
                
            processed_levels.append(processed_level)
        
        config = {'levels': processed_levels}
        
        if shadows is not None:
            config['shadows'] = convert_color_to_hex(shadows)
            
        if show_labels is not None:
            config['showLabels'] = show_labels
        
        self.instance.send(self.id, 'setContours', {'config': config})
        return self
    

    def set_contours_from_palette(
        self,
        shadows: str = None,
        show_labels: bool = True,
        customize_level: callable = None
    ):
        """Generate contours automatically from the series' palette colors.
        
        Args:
            shadows: Shadow color (hex "#000000")
            show_labels: Show contour labels
            customize_level: Callback to customize each level: (level_dict) -> level_dict
                The level dict contains:
                    - 'value' (float): Contour threshold value from palette step
                    - 'label' (str, optional): Text label (auto-generated from value)
                    - 'label_color' (str, optional): Label color from palette step
                    - stroke_style (dict, optional): Line style with keys:
                        - thickness (int): Line thickness in pixels
                        - color (str): Line color (hex or name)
            
        Example:
            >>> series.set_palette_colors(steps=[...])
            >>> series.set_contours_from_palette(show_labels=True)
            
            With customization:
            >>> def customize(level):
            ...     level['stroke_style'] = {'thickness': 3, 'color': '#FF0000'}
            ...     return level
            >>> series.set_contours_from_palette(customize_level=customize)
        """
        self.instance.send(
            self.id, 
            'setContoursFromPalette',
            {
                'shadows': convert_color_to_hex(shadows) if shadows else None,
                'showLabels': show_labels,
                'hasCustomizer': customize_level is not None
            }
        )
        return self