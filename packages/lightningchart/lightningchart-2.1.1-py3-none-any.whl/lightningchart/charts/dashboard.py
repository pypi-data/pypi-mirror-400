from __future__ import annotations
from typing import Optional
import uuid

from lightningchart import conf, Themes
from lightningchart.charts import ChartsWithCoordinateTransforms, GeneralMethods, Chart
from lightningchart.charts.bar_chart import BarChartDashboard
from lightningchart.charts.chart_3d import Chart3DDashboard
from lightningchart.charts.chart_xy import ChartXY, ChartXYDashboard
from lightningchart.charts.funnel_chart import FunnelChartDashboard
from lightningchart.charts.gauge_chart import GaugeChartDashboard
from lightningchart.charts.map_chart import MapChartDashboard
from lightningchart.charts.parallel_coordinate_chart import (
    ParallelCoordinateChartDashboard,
)
from lightningchart.charts.pie_chart import PieChartDashboard
from lightningchart.charts.polar_chart import PolarChartDashboard
from lightningchart.charts.pyramid_chart import PyramidChartDashboard
from lightningchart.charts.spider_chart import SpiderChartDashboard
from lightningchart.charts.zoom_band_chart import ZoomBandChart
from lightningchart.charts.data_grid import DataGridDashboard
from lightningchart.instance import Instance
from lightningchart.ui.legend import LegendPanelDashboard
from lightningchart.utils.utils import LegendOptions, build_legend_config


class Dashboard(GeneralMethods, ChartsWithCoordinateTransforms):
    """Dashboard is a tool for rendering multiple charts in the same view."""

    def __init__(
        self,
        columns: int,
        rows: int,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        license: str = None,
        license_information: str = None,
    ):
        """Create a dashboard, i.e., a tool for rendering multiple charts in the same view.

        Args:
            columns (int): The amount of columns in the dashboard.
            rows (int): The amount of rows in the dashboard.
            theme (Themes): Theme of the chart.
            theme_scale (float): Scale factor for fonts, ticks, padding (default: 1.0).
            license (str): License key.
        """
        instance = Instance()
        Chart.__init__(self, instance)
        self.charts = []
        self.columns = columns
        self.rows = rows
        instance.send(
            self.id,
            'dashboard',
            {
                'columns': columns,
                'rows': rows,
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
            },
        )

    def ChartXY(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,
    ) -> ChartXYDashboard:
        """Create a XY Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            Reference to the XY Chart.
        """
        return ChartXYDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            legend=legend,
        )

    def Chart3D(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,
    ) -> Chart3DDashboard:
        """Create a 3D chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
        Returns:
            Reference to the 3D Chart.
        """
        return Chart3DDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            legend=legend,
        )

    def ZoomBandChart(
        self,
        chart: ChartXY,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        axis_type: str = 'linear',
        orientation: str = 'x',
        use_shared_value_axis: bool = False,
    ) -> ZoomBandChart:
        """Create a Zoom Band Chart on the dashboard.

        Args:
            chart (ChartXY): Reference to XY Chart which the Zoom Band Chart will use.
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            axis_type (str): Creation-time axis options for the zoom band’s
                internal default axis ("linear" | "linear-highPrecision" | "logarithmic").
            orientation (str): Select orientation of ZoomBandChart.
                'x' = primary axis is X axis (commonly used when X = Time axis).
                'y' = opposite mode, for example when Time axis is Y and chart is rotated 90 degrees.
            use_shared_value_axis (bool): ZoomBandChart can display series belonging to several different axes. 
                By default, every unique value axis will have its own scale in the zoom band chart. 
                By setting this flag to true, the zoom band chart will display all its series with 1 shared scale.

        Returns:
            Reference to the Zoom Band Chart.
        """
        return ZoomBandChart(
            instance=self.instance,
            dashboard_id=self.id,
            chart_id=chart.id,
            column_index=column_index,
            column_span=column_span,
            row_index=row_index,
            row_span=row_span,
            title=title,
            axis_type=axis_type,
            orientation=orientation,
            use_shared_value_axis=use_shared_value_axis,
        )

    def PieChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1, 
            title: str = None,
            labels_inside_slices: bool = False,
            legend: Optional[LegendOptions] = None,
        ) -> PieChartDashboard:
        """Create a Pie Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            labels_inside_slices (bool): If true, the labels are inside pie slices. If false, the labels are on the
                sides of the slices.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
        Returns:
            Reference to the Pie Chart.
        """
        return PieChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            labels_inside_slices=labels_inside_slices,
            legend=legend,
        )

    def GaugeChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1,
            title: str = None,
        ) -> GaugeChartDashboard:
        """Create a Gauge Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.            
            
        Returns:
            Reference to the Gauge Chart.
        """
        return GaugeChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            title=title,
            colspan=column_span,
            rowspan=row_span,
        )

    def FunnelChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1, 
            title: str = None,
            slice_mode: str = 'height',
            labels_inside: bool = False,
            legend: Optional[LegendOptions] = None,
        ) -> FunnelChartDashboard:
        """Create a Funnel Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.            
            title (str): The title of the chart.
            slice_mode: "width" | "height"
            labels_inside: If True, labels are placed inside slices. If False, labels are on sides (default).
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
        Returns:
            Reference to the Funnel Chart.
        """
        return FunnelChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            slice_mode=slice_mode,
            labels_inside=labels_inside,
            legend=legend,
        )

    def PyramidChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1, 
            title: str = None,
            slice_mode: str = 'height',
            labels_inside: bool = False,
            legend: Optional[LegendOptions] = None,
        ) -> PyramidChartDashboard:
        """Create a Pyramid Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            slice_mode: "width" | "height"
            labels_inside: If True, labels are placed inside slices. If False, labels are on sides (default).
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.


        Returns:
            Reference to the Pyramid Chart.
        """
        return PyramidChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            slice_mode=slice_mode,
            labels_inside=labels_inside,
            legend=legend,
        )

    def PolarChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1,
            title: str = None,
            legend: Optional[LegendOptions] = None,
        ) -> PolarChartDashboard:
        """Create a Polar Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.


        Returns:
            Reference to the Polar Chart.
        """
        polar_chart = PolarChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            title=title,
            colspan=column_span,
            rowspan=row_span,
            legend=legend,
        )
        self.charts.append(polar_chart)
        return polar_chart

    def BarChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        vertical: bool = True,
        axis_type: str = 'linear',
        axis_base: int = 10,
        legend: Optional[LegendOptions] = None,
    ) -> BarChartDashboard:
        """Create a Bar Chart on the dashboard.

       Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            vertical (bool): If true, bars are aligned vertically. If false, bars are aligned horizontally.
            axis_type (str): "linear" | "logarithmic"
            axis_base (int): Specification of Logarithmic Base number (e.g. 10, 2, natural log).
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
        Returns:
            Reference to the Bar Chart.
        """
        return BarChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            vertical=vertical,
            axis_type=axis_type,
            axis_base=axis_base,
            legend=legend,
        )

    def SpiderChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1,
            title: str = None,
            legend: Optional[LegendOptions] = None,
        ) -> SpiderChartDashboard:
        """Create a Spider Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
        Returns:
            Reference to the Spider Chart.
        """
        return SpiderChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            legend=legend,
        )

    def MapChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1, 
            title: str = None,
            map_type: str='World',
            legend: Optional[LegendOptions] = None,
        ) -> MapChartDashboard:
        """Create a Map Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            map_type (str): "Africa" | "Asia" | "Australia" | "Canada" | "Europe" | "NorthAmerica" | "SouthAmerica" | "USA" | "World".
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            Reference to the Map Chart
        """
        return MapChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            map_type=map_type,
            legend=legend,
        )

    def ParallelCoordinateChart(
            self, 
            column_index: int, 
            row_index: int, 
            column_span: int = 1, 
            row_span: int = 1,
            title: str = None,
            legend: Optional[LegendOptions] = None,          
            ) -> ParallelCoordinateChartDashboard:
        """Create a Parallel Coordinates Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
        Returns:
            Reference to the Parallel Coordinates Chart
        """
        return ParallelCoordinateChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
            legend=legend,
        )
    
    def LegendPanel(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        legend: Optional[LegendOptions] = None,
    ) -> LegendPanelDashboard:
        """Create a legend panel on the dashboard.
        
        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            legend (dict): Legend configuration dictionary with the following options:
                visible (bool): Show/hide legend.
                position: Position (TopRight, RightCenter, etc.).
                title (str): Legend title text.
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Horizontal or Vertical orientation.
                render_on_top (bool): Render above chart (default: False).
                background_visible (bool): Show legend background.
                background_fill_style (str): Background color ("#ff0000").
                background_stroke_style (dict): Border style {'thickness': 2, 'color': '#000'}.
                padding (int | dict): Padding around legend content.
                margin_inner (int): Space between chart and legend.
                margin_outer (int): Space from legend to chart edge.
                entry_margin (int): Space between legend entries.
                auto_hide_threshold (float): Auto-hide when legend takes >X of chart (0.0-1.0).
                add_entries_automatically (bool): Auto-add series to legend.
                entries (dict): Default styling for all legend entries with options:
                    button_shape (str): 'Arrow', 'Diamond', 'Plus', 'Triangle', 'Circle', 'Square', 'Cross', 'Minus' and 'Star'.
                    button_size (int | dict): Size in pixels or {'x': 20, 'y': 15}.
                    button_fill_style (str): Button color ("#ff0000").
                    button_stroke_style (dict): Button border {'thickness': 1, 'color': '#000'}.
                    button_rotation (float): Button rotation in degrees.
                    text (str): Override default series name.
                    text_font (dict): Font settings {'size': 16, 'family': 'Arial', 'weight': 'bold'}.
                    text_fill_style (str): Text color ("#000000").
                    show (bool): Show/hide this entry.
                    match_style_exactly (bool): Match series style exactly vs simplified.
                    highlight (bool): Whether highlighting on hover is enabled.
                    lut: LUT element for legends (None to disable).
                    lut_length (int): LUT bar length for heatmap legends.
                    lut_thickness (int): LUT bar thickness for heatmap legends.
                    lut_display_proportional_steps (bool): LUT step display mode.
            
        Returns:
            LegendPanel instance
        """
        
        legend_config = build_legend_config(legend) if legend else {}
        
        panel = LegendPanelDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            legend=legend_config
        )
        return panel
    

    def DataGrid(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
    ) -> DataGridDashboard:
        """Create a DataGrid on the dashboard.
        
        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart spans (grid width). Default = 1.
            row_span (int): How many rows the chart spans (grid height). Default = 1.
            title (str): The title of the grid.               
            
        Returns:
            Reference to the DataGrid
        """        
        panel = DataGridDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
        )
        return panel

    def add_event_listener(
        self,
        event: str,
        handler: callable | None = None,
        throttle_ms: int = 0,
        once: bool = False,
        target: str = 'chart',
    ) -> str:
        """Add event listener to the dashboard.
        
        Args:
            event: Event name ('inviewchange', 'resize')
            handler: Python callback receiving event data
            throttle_ms: Minimum delay between callbacks in milliseconds
            once: If True, listener removes itself after first trigger
            target: 'chart' for dashboard-level events

        Examples:
            >>> dashboard.add_event_listener('resize', handler=on_resize, target='chart')            
            
        Returns:
            callback_id for the registered handler
        """
                
        callback_id = str(uuid.uuid4()).split('-')[0] if handler else ''
        if handler is not None:
            self.instance.event_handlers[callback_id] = handler

        self.instance.send(self.id, 'addEventListener', {
            'event': event,
            'callbackId': callback_id or None,
            'xyId': None,
            'throttleMs': int(throttle_ms) if throttle_ms else 0,
            'options': {'once': bool(once)},
            'target': target,
        })
        return callback_id