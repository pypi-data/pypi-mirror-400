from __future__ import annotations
from typing import Optional

from lightningchart.charts import Chart
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DLines,
    SeriesWith3DShading,
    ComponentWithLinePaletteColoring,
    SeriesWithAddEventListener,
    SeriesWithClear,
    SeriesWithXYZAxes,
)
from lightningchart.utils.utils import LegendOptions, build_series_legend_options


class LineSeries3D(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DLines,
    SeriesWith3DShading,
    ComponentWithLinePaletteColoring,
    SeriesWithClear,
    SeriesWithAddEventListener,
    SeriesWithXYZAxes,
):
    """Series for visualizing 3D lines."""

    def __init__(
            self, 
            chart: Chart, 
            automatic_color_index: int = None, 
            individual_lookup_values_enabled: bool = False, 
            legend: Optional[LegendOptions] = None,
            ):
        super().__init__(chart) 
        legend_options = build_series_legend_options(legend)
            
        self.instance.send(
            self.id,
            'lineSeries3D',
            {
                'chart': self.chart.id,
                'automaticColorIndex': automatic_color_index,
                'individualLookupValuesEnabled': individual_lookup_values_enabled,
                'legend': legend_options if legend_options else None
            },
        )
