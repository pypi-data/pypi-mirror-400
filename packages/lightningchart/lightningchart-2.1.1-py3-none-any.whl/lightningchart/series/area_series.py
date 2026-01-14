from __future__ import annotations
from typing import Optional

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DLines,
    SeriesWithAddEventListener,
    SeriesWithXYAxes,
    SeriesWithDataCleaning,
    PointLineAreaSeries,
    SeriesWithClear,
    SeriesWithDrawOrder,
)
from lightningchart.utils import convert_color_to_hex
from lightningchart.utils.utils import ColorInput, LegendOptions, build_series_legend_options, normalize_schema


class AreaSeries(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DLines,
    SeriesWithDataCleaning,
    PointLineAreaSeries,
    SeriesWithClear,
    SeriesWithDrawOrder,
    SeriesWithAddEventListener,
    SeriesWithXYAxes,
):
    """Series for visualizing 2D areas."""

    def __init__(
        self,
        chart: Chart,
        colors: bool = None,
        lookup_values: bool = None,
        ids: bool = None,
        sizes: bool = None,
        rotations: bool = None,
        schema: dict = None,
        strict_mode: bool = None,
        auto_detect_patterns: bool = False,
        allow_data_grouping: bool = None,
        allow_input_modification: bool = None,
        auto_sorting_enabled: bool = None,
        automatic_color_index: int = None,
        includes_nan: bool = None,
        warnings: bool = None,
        axis_x: Axis = None,
        axis_y: Axis = None,
        legend: Optional[LegendOptions] = None,
    ):
        super().__init__(chart, axis_x, axis_y)
        if schema:
            schema = normalize_schema(schema)

        legend_options = build_series_legend_options(legend)
        if schema is None:
            schema = {'x': {'pattern': 'progressive'}, 'y': {}}


        self.instance.send(
            self.id,
            'areaSeries',
            {
                'chart': self.chart.id,
                'colors': colors,
                'lookup_values': lookup_values,
                'ids': ids,
                'sizes': sizes,
                'rotations': rotations,
                'schema': schema,
                'strictMode': strict_mode,
                'autoDetectPatterns': auto_detect_patterns,
                'allowDataGrouping': allow_data_grouping,
                'allowInputModification': allow_input_modification,
                'autoSortingEnabled': auto_sorting_enabled,
                'automaticColorIndex': automatic_color_index,
                'includesNaN': includes_nan,
                'warnings': warnings,
                'axisX': axis_x,
                'axisY': axis_y,
                'legend': legend_options if legend_options else None,
            },
        )

    def set_fill_color(self, color: ColorInput | None):
        """Set a fill color of the area.

        Args:
            color (Color): Color of the area. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setAreaFillStyle', {'color': color})
        return self

    def set_palette_area_coloring(
        self,
        steps: list[dict[str, any]],
        look_up_property: str = 'value',
        interpolate: bool = True,
        percentage_values: bool = False,
        formatter_precision: int | None = None,
        formatter_unit: str = '',
        formatter_scale: float = 1.0,
        formatter_type: str = 'standard',
        formatter_operation: str = 'none'
    ):
        """Define a palette for dynamically looked up fill coloring in the series.

        Args:
            steps (list[dict]): List of {"value": number, "color": Color, 'label': 'Label'} dictionaries.
            interpolate (bool): Enables automatic linear interpolation between color steps.
            look_up_property (str): "value" | "x" | "y" | "z"
            percentage_values (bool): Whether values represent percentages or explicit values.
            formatter_precision: Decimal places for legend display.
            formatter_unit: Unit suffix (e.g., "mag", "ms").
            formatter_scale: Multiply values by this factor.
            formatter_type: 'standard', 'compact', 'engineering', 'scientific'.
            formatter_operation: 'none', 'round', 'ceil', 'floor'.

        Returns:
            The instance of the class for fluent interface.
        """
        for i in steps:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(
            self.id,
            'setPalettedAreaFillStyle',
            {
                'steps': steps,
                'lookUpProperty': look_up_property,
                'interpolate': interpolate,
                'percentageValues': percentage_values,
                'formatter_precision': formatter_precision,
                'formatter_unit': formatter_unit,
                'formatter_scale': formatter_scale,
                'formatter_type': formatter_type,
                'formatter_operation': formatter_operation
            },
        )
        return self 
      