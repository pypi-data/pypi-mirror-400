from __future__ import annotations
from typing import Optional

from lightningchart.charts import Chart
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithAddEventListener,
    SeriesWithWireframe,
    SeriesWithInvalidateHeight,
    SeriesWithIntensityInterpolation,
    SeriesWithCull,
    SeriesWith3DShading,
    SeriesWithClear,
    SeriesWithXYZAxes,
)
from lightningchart.utils.utils import LegendOptions, build_series_legend_options, convert_color_to_hex, convert_to_matrix


class SurfaceGridSeries(
    ComponentWithPaletteColoring,
    SeriesWithWireframe,
    SeriesWithInvalidateHeight,
    SeriesWithIntensityInterpolation,
    SeriesWithCull,
    SeriesWith3DShading,
    SeriesWithClear,
    SeriesWithAddEventListener,
    SeriesWithXYZAxes,
):
    """Series for visualizing 3D surface data in a grid."""

    def __init__(
        self,
        chart: Chart,
        columns: int,
        rows: int,
        data_order: str = 'columns',
        automatic_color_index: int = None,
        legend: Optional[LegendOptions] = None,  
    ):
        super().__init__(chart)
        legend_options = build_series_legend_options(legend)
            
        self.columns = columns
        self.rows = rows
        self.instance.send(
            self.id,
            'surfaceGridSeries',
            {
                'chart': self.chart.id,
                'automaticColorIndex': automatic_color_index,
                'columns': columns,
                'rows': rows,
                'dataOrder': data_order,
                'legend': legend_options if legend_options else None
            },
        )

    def set_start(self, x: int | float, z: int | float):
        """Set start coordinate of surface on its X and Z axis where the first surface sample will be positioned

        Args:
            x: x-coordinate.
            z: z-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStartXZ', {'x': x, 'z': z})
        return self

    def set_end(self, x: int | float, z: int | float):
        """Set end coordinate of surface on its X and Z axis where the last surface sample will be positioned.

        Args:
            x: x-coordinate.
            z: z-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setEndXZ', {'x': x, 'z': z})
        return self

    def set_step(self, x: int | float, z: int | float):
        """Set Step between each consecutive surface value on the X and Z Axes.

        Args:
            x: x-coordinate.
            z: z-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStepXZ', {'x': x, 'z': z})
        return self
    

    def invalidate_intensity_values(
        self,
        data: list[list[int | float]],
        column_index: int = None,
        row_index: int = None,
        sample_index: int = None,
    ):
        """Invalidate range of surface intensity values starting from first column and row.

        Args:
            data (list[list[int | float]]): a number matrix.
            column_index (int): Index of first invalidated column.
            row_index (int): Index of first invalidated row.
            sample_index (int): The location along scrolling dimension is identified by a sample index.
                Sample index 0 would reference the first sample in the heatmap, whereas 1 the second sample.

        Returns:
            The instance of the class for fluent interface.
        """
        data = convert_to_matrix(data)

        self.instance.send(
            self.id,
            'invalidateIntensityValues',
            {
                'data': data,
                'column': column_index,
                'row': row_index,
                'iSample': sample_index,
            },
        )
        return self
    

    def set_contours(
        self,
        value_source: str = 'y',
        levels: list[dict] = None,
    ):
        """Set contour lines for 3D surface. Note: labels are not supported.
        
        Args:
            value_source: Data source for contours ('y' for height, 'intensity' for color values)
            levels: List of contour level dicts with:
                - value (float, required): Contour threshold
                - stroke_style (dict, optional): Line style with 'thickness' and 'color'
        """
        if levels is None:
            self.instance.send(self.id, 'setContours', {'config': None})
            return self
        
        processed_levels = []
        for level in levels:
            processed_level = {'value': level['value']}
            
            if 'stroke_style' in level and level['stroke_style'] is not None:
                stroke = level['stroke_style']
                processed_stroke = {}
                if 'thickness' in stroke:
                    processed_stroke['thickness'] = stroke['thickness']
                if 'color' in stroke:
                    processed_stroke['color'] = convert_color_to_hex(stroke['color'])
                processed_level['strokeStyle'] = processed_stroke
                
            processed_levels.append(processed_level)
        
        config = {
            'valueSource': value_source,
            'levels': processed_levels
        }
        
        self.instance.send(self.id, 'set3DSurfaceContours', {'config': config})
        return self
