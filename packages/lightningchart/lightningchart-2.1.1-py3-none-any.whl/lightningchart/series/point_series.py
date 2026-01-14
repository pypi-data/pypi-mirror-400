from __future__ import annotations
from typing import Optional

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DPoints,
    SeriesWithAddEventListener,
    SeriesWithIndividualPoint,
    PointLineAreaSeries,
    PointSeriesStyle,
    SeriesWithClear,
    SeriesWithDrawOrder,
    SeriesWithXYAxes,
)
from lightningchart.utils.utils import LegendOptions, build_series_legend_options, normalize_schema


class PointSeries(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DPoints,
    SeriesWithIndividualPoint,
    PointLineAreaSeries,
    PointSeriesStyle,
    SeriesWithClear,
    SeriesWithDrawOrder,
    SeriesWithAddEventListener,
    SeriesWithXYAxes,
):
    """Series for visualizing 2D datapoints."""

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

        self.instance.send(
            self.id,
            'pointSeries2D',
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
                'legend': legend_options if legend_options else None
            },
        )
