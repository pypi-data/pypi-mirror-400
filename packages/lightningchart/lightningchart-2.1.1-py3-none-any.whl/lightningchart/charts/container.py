from __future__ import annotations
from typing import Optional, Dict
import uuid
from lightningchart.instance import Instance
from lightningchart import conf

from lightningchart.charts.bar_chart import BarChartContainer
from lightningchart.charts.chart_3d import Chart3DContainer
from lightningchart.charts.funnel_chart import FunnelChartContainer
from lightningchart.charts.gauge_chart import GaugeChartContainer
from lightningchart.charts.map_chart import MapChartContainer
from lightningchart.charts.parallel_coordinate_chart import ParallelCoordinateChartContainer
from lightningchart.charts.pie_chart import PieChartContainer
from lightningchart.charts.polar_chart import PolarChartContainer
from lightningchart.charts.pyramid_chart import PyramidChartContainer
from lightningchart.charts.spider_chart import SpiderChartContainer
from lightningchart.charts.treemap_chart import TreeMapChartContainer
from lightningchart.charts.zoom_band_chart import ZoomBandChartContainer
from lightningchart.charts.data_grid import DataGridContainer
from lightningchart.charts import Chart, ChartsWithCoordinateTransforms, GeneralMethods
from lightningchart.themes import Themes
from lightningchart.ui.legend import LegendPanelContainer
from lightningchart.utils.utils import LegendOptions
from lightningchart.charts.chart_xy import ChartXY, ChartXYContainer

class DOMContainer():
    """
    Mixin for charts that need Container control.

    Notes:
        - Charts can be constructed with a 'container' (DOM id) or attached later
          with set_container().
        - When you change container styles (width/height/position), the engine resizes automatically.
    """

    def _create_container(
        self,
        container_id: str,
        parent_id: Optional[str] = None,
        style: Optional[Dict[str, str]] = None,
    ) -> "DOMContainer":
        """
        Create a <div> container in the browser and register it.

        Args:
            container_id: DOM id to assign to the div.
            parent_id: Optional parent DOM id (defaults to <body>).
            style: Optional inline CSS as dict, e.g. {'width':'100%', 'height':'100%'}.
        """
        self.instance.send(self.id, 'createContainer', {
            'containerId': container_id,
            'parentId': parent_id,
            'style': style or {}
        })
        return self

    def set_container(self, container_id: str) -> "DOMContainer":
        """
        Attach this chart's engine to an existing container div.

        Args:
            container_id: DOM id of an existing div.
        """
        self.instance.send(self.id, 'setContainer', {'containerId': container_id})
        return self


class OverlayContainer(GeneralMethods, ChartsWithCoordinateTransforms, Chart, DOMContainer):
    """Container for creating grid-based chart overlays."""
    
    def __init__(
        self, 
        columns: int, 
        rows: int, 
        theme: Themes,
        theme_scale: float = 1.0,
        width: int | float | str = '100vw', 
        height: int | float | str = '100vh',
        scrollable: bool = True,
        license: str = None,                   
        license_information: str = None,
    ):
        """Create an overlay container with CSS Grid positioning for chart overlays."""
        
        self._theme = theme
        self._theme_scale = theme_scale

        self.instance = Instance()
        self.id = f'container_{id(self)}'
        self.columns = columns
        self.rows = rows
        self.charts = []
        self._cell_counter = 0
        self._shared_cells: dict[str, str] = {}
        self.container_name = f'{self.id}_scroll'
        self.grid_id = f'{self.id}_grid'

        width_str  = f'{width}px'  if isinstance(width, (int, float)) else width
        height_str = f'{height}px' if isinstance(height, (int, float)) else height

        scroll_host_style = {
            'position': 'fixed',
            'inset': '0',
            'overflow': 'auto' if scrollable else 'hidden',
            'boxSizing': 'border-box',
            'z-index': '1',
        }

        grid_style = {
            'position': 'relative',
            'height': height_str,
            'width': width_str,
            'display': 'grid',
            'grid-template-columns': f'repeat({columns}, 1fr)',
            'grid-template-rows': f'repeat({rows}, minmax(0, 1fr))',
            'gap': '6px',
        }

        self._cell_frame_style = {
            'position': 'relative',
            'width': '100%',
            'height': '100%',
            'borderRadius': '8px',
        }

        self._create_container(self.container_name, style=scroll_host_style)
        self._create_container(self.grid_id, parent_id=self.container_name, style=grid_style)

        self.instance.send(
            self.id,
            'createContainerDashboard',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'columns': columns,
                'rows': rows,
                'containerId': self.grid_id,
                'pageScroll': False,           
                
            },
        )  


    def _create_chart_cell(self, column_index, row_index, column_span, row_span):
        key = f"{column_index}_{row_index}_{column_span}_{row_span}"
        if key in self._shared_cells:
            return self._shared_cells[key]

        cell_id = f'cell_{self._cell_counter}'
        self._cell_counter += 1
        cell_style = {
            'grid-area': f'{row_index + 1} / {column_index + 1} / span {row_span} / span {column_span}',
            'position': 'relative',
        }
        self._create_container(cell_id, self.grid_id, cell_style)

        frame_id = f'{cell_id}_frame'
        self._create_container(frame_id, parent_id=cell_id, style=self._cell_frame_style)

        self._shared_cells[key] = frame_id
        return frame_id


    def _setup_chart_in_cell(self, chart, cell_or_frame_id: str):
        wrapper_id = f'{chart.id}_wrapper'
        self._create_container(wrapper_id, parent_id=cell_or_frame_id, style={
            'position': 'absolute',
            'inset': '0',
        })
        if hasattr(chart, 'set_container'):
            chart.set_container(wrapper_id)

        self.charts.append(chart)
        return chart  


    def MapChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        map_type: str = 'World', 
        legend: Optional[LegendOptions] = None,
    ) -> MapChartContainer:
        """Create a Map Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> # World map in top-left cell
            >>> world = sc_db.MapChart(0, 0, title="World map")
        
        Returns:
            Reference to the Map Chart
        """
        chart = MapChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            map_type=map_type,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    
    def ChartXY(
        self, 
        column_index: int, 
        row_index: int, 
        column_span: int = 1, 
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,
        ) -> ChartXYContainer:
        """Create an XY Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.ChartXY(0, 0, title="ChartXY")
        
        Returns:
            Reference to the ChartXY        
        """    
        chart = ChartXYContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            legend=legend,
        )
        self.charts.append(chart)
        return chart

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
    ) -> BarChartContainer:
        """Create a Bar Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.BarChart(0, 0, title="Bar Chart")
        
        Returns:
            Reference to the Bar Chart 
        """
        chart = BarChartContainer(
            instance=self.instance,
            container=self,
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
        self.charts.append(chart)
        return chart

    def Chart3D(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,
    ) -> Chart3DContainer:
        """Create a 3D Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.Chart3D(0, 0, title="Chart3D")
        
        Returns:
            Reference to the Chart3D 
        """  
        chart = Chart3DContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            legend=legend,
            
        )    
        self.charts.append(chart)
        return chart
    
    def PieChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        labels_inside_slices: bool = False, 
        legend: Optional[LegendOptions] = None,       
    ) -> PieChartContainer:
        """Create a Pie Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.PieChart(0, 0, title="Pie Chart")
        
        Returns:
            Reference to the Pie Chart 
        """    
        chart = PieChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            labels_inside_slices=labels_inside_slices,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    

    def PolarChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,       
    ) -> PolarChartContainer:
        """Create a Polar Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.PolarChart(0, 0, title="Polar Chart")
        
        Returns:
            Reference to the Polar Chart 
        """            
        chart = PolarChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    
    def ParallelCoordinateChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,       
    ) -> ParallelCoordinateChartContainer:
        """Create a ParallelCoordinate Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.ParallelCoordinateChart(0, 0, title="ParallelCoordinate Chart")
        
        Returns:
            Reference to the ParallelCoordinate Chart 
        """   
        chart = ParallelCoordinateChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    
    def TreeMapChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,       
    ) -> TreeMapChartContainer:
        """Create a TreeMap Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.TreeMapChart(0, 0, title="TreeMap Chart")
        
        Returns:
            Reference to the TreeMap Chart
        """    
        cell_id = self._create_chart_cell(column_index, row_index, column_span, row_span)
        chart = TreeMapChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            legend=legend,
            theme=self._theme,
        )
        return self._setup_chart_in_cell(chart, cell_id)
    
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
    ) -> FunnelChartContainer:
        """Create a Funnel Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.FunnelChart(0, 0, title="Funnel Chart")
        
        Returns:
            Reference to the Funnel Chart
        """   
        chart = FunnelChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title, 
            slice_mode=slice_mode,
            labels_inside=labels_inside,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    
    def GaugeChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,   
    ) -> GaugeChartContainer:
        """Create a Gauge Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.GaugeChart(0, 0, title="Gauge Chart")
        
        Returns:
            Reference to the Gauge Chart
        """           
        chart = GaugeChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
        )
        self.charts.append(chart)
        return chart
    
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
    ) -> PyramidChartContainer:
        """Create a Pyramid Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.PyramidChart(0, 0, title="Pyramid Chart")
        
        Returns:
            Reference to the Pyramid Chart
        """   
        chart = PyramidChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            slice_mode=slice_mode,
            labels_inside=labels_inside,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    
    def SpiderChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
        legend: Optional[LegendOptions] = None,       
    ) -> SpiderChartContainer:
        """Create a Spider Chart positioned in the overlay grid.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> world = sc_db.SpiderChart(0, 0, title="Spider Chart")
        
        Returns:
            Reference to the Spider Chart
        """
        chart = SpiderChartContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,            
            title=title,
            legend=legend,
        )
        self.charts.append(chart)
        return chart
    
    def ZoomBandChart(
        self,
        chart: ChartXY,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str | None = None,
        orientation: str = 'x',
        use_shared_value_axis: bool = False,
        axis_type: str = 'linear',
    )-> ZoomBandChartContainer:
        """Create a Zoom Band Chart positioned in the overlay grid.

        Args:
            chart (ChartXY): Reference to XY Chart which the Zoom Band Chart will use.
            column_index (int): Column index of the container grid where the chart will be placed.
            row_index (int): Row index of the container grid where the chart will be placed.
            column_span (int): How many columns the chart occupies (width in grid cells). Default: 1.
            row_span (int): How many rows the chart occupies (height in grid cells). Default: 1.
            title (str | None): Chart title text.
            orientation (str): Select orientation of ZoomBandChart.
                'x' = primary axis is X axis (commonly used when X = Time axis).
                'y' = opposite mode, for example when Time axis is Y and chart is rotated 90 degrees.
            use_shared_value_axis (bool): ZoomBandChart can display series belonging to several different axes. 
                By default, every unique value axis will have its own scale in the zoom band chart. 
                By setting this flag to true, the zoom band chart will display all its series with 1 shared scale.
            axis_type (str): Creation-time axis options for the zoom band’s
                internal default axis ("linear" | "linear-highPrecision" | "logarithmic").

        Example:
            >>> sc_db = lc.Container(columns=2, rows=2, theme=lc.Themes.Dark)
            >>> main = sc_db.ChartXY(0, 0, 2, 1, title="Main view")
            >>> s = main.add_line_series().add([1, 2, 3, 4], [10, 15, 8, 20])
            >>> # Zoom band underneath controlling X axis of the main chart
            >>> zbc = sc_db.ZoomBandChart(chart=main, column_index=0, row_index=1, orientation='x',
            ...                               use_shared_value_axis=True, title="Overview")
            >>> zbc.add_series(s)

        Returns:
            Reference to the created Zoom Band Chart.
        """
        zbc = ZoomBandChartContainer(
            instance=self.instance,
            container=self,
            chart_id=chart.id if chart else None,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,   
            title=title,
            orientation=orientation,
            use_shared_value_axis=use_shared_value_axis,
            axis_type=axis_type,
        )
        self.charts.append(zbc)
        return zbc
    
    def LegendPanel(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        legend: Optional[LegendOptions] = None,
    ) -> LegendPanelContainer:
        """Create a legend panel on the container.
        
        Args:
            column_index (int): Column index of the container where the chart will be located.
            row_index (int): Row index of the container where the chart will be located.
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
        panel = LegendPanelContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,  
            legend=legend,
        )
        self.charts.append(panel)
        return panel
    
    def add_event_listener(
        self,
        event: str,
        handler: callable | None = None,
        throttle_ms: int = 0,
        once: bool = False,
        target: str = 'chart',
    ) -> str:
        """Add event listener to the container.

        Args:
            event: Event name. Supported events:
                - 'resize': Fires when dragging splitters between charts in the grid
            handler: Python callback receiving event data
            throttle_ms: Minimum delay between callbacks in milliseconds
            once: If True, listener removes itself after first trigger
            target: 'chart' for container-level events

        Examples:
            Listen for container resize (triggered by dragging chart splitters):
            >>> def on_resize(event):
            ...     size = event.get('size', {})
            ...     print(f"Resized: {size.get('width')} x {size.get('height')}")
            >>> container.add_event_listener('resize', handler=on_resize, target='chart')

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

    def DataGrid(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str | None = None,
    )-> DataGridContainer:
        """Create a Data Grid.

        Args:
            column_index (int): Column index of the container grid where the chart will be placed.
            row_index (int): Row index of the container grid where the chart will be placed.
            column_span (int): How many columns the chart occupies (width in grid cells). Default: 1.
            row_span (int): How many rows the chart occupies (height in grid cells). Default: 1.            
            title (str | None): Chart title text.

        Example:
            >>> sc_db = lc.Container(columns=1, rows=1, theme=lc.Themes.Dark)
            >>> DataGrid = sc_db.DataGrid(0, 0, title="Data Grid")

        Returns:
            Reference to the created DataGrid.
        """
        grid = DataGridContainer(
            instance=self.instance,
            container=self,
            column=column_index,
            row=row_index,
            colspan=column_span,
            title=title,
            rowspan=row_span,  
        )
        self.charts.append(grid)
        return grid

def Container(
    columns: int, 
    rows: int, 
    theme: Themes = Themes.Light, 
    theme_scale: float = 1.0,
    width: int | float | str = '100vw',
    height: int | float | str = '100vh',
    scrollable: bool = True,
    license: str = None,                 
    license_information: str = None,     
) -> OverlayContainer:
    """Create an overlay container for grid-based chart positioning.

    Args:
        columns (int): Number of grid columns in the container.
        rows (int): Number of grid rows in the container.
        theme (Themes): Default theme applied to all charts in the container (default: Themes.Light).
        theme_scale (float): Scale factor for fonts, ticks, padding (default: 1.0).
        width (int | float | str): container width - number for pixels or CSS string (default: '100vw').
        height (int | float | str): container height - number for pixels or CSS string (default: '100vh').
        scrollable (bool): Enable vertical scrolling for tall containers (default: True).

    Returns:
        OverlayContainer: Container instance for creating positioned and layered charts.

    Examples:
        With pixel dimensions:
        >>> sc_db = lc.Container(columns=2, rows=2, width=1920, height=1080)

        With CSS units:
        >>> sc_db = lc.Container(columns=1, rows=4, width='100vw', height='200vh', scrollable=True)
    """
    return OverlayContainer(columns, rows, theme, theme_scale, width, height, scrollable, license, license_information)