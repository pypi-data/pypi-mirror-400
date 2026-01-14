from __future__ import annotations
from typing import Optional


from lightningchart import conf, Themes
from lightningchart.charts import ChartsWithAddEventListener, GeneralMethods, TitleMethods, Chart
from lightningchart.instance import Instance
from lightningchart.series.polar_area_series import PolarAreaSeries
from lightningchart.series.polar_line_series import PolarLineSeries
from lightningchart.series.polar_point_line_series import PolarPointLineSeries
from lightningchart.series.polar_point_series import PolarPointSeries
from lightningchart.series.polar_heatmap_series import PolarHeatmapSeries
from lightningchart.series.polar_polygon_series import PolarPolygonSeries
from lightningchart.ui.axis import CategoryAxis
from lightningchart.ui.polar_sector import PolarSector
from lightningchart.ui.polar_axis_amplitude import PolarAxisAmplitude
from lightningchart.ui.polar_axis_radial import PolarAxisRadial
from lightningchart.utils.utils import LegendOptions, apply_post_legend_config, build_legend_config


class PolarChart(GeneralMethods, TitleMethods, ChartsWithAddEventListener):
    """Chart for visualizing data in a polar coordinate system."""

    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = True,
        legend: Optional[LegendOptions] = None,
    ):
        """Create a polar chart.

        Args:
            theme (Themes): Chart theme (Themes.Light, Themes.DarkGold, etc.).
            theme_scale (float): Scale factor for fonts, ticks, padding (default: 1.0).
            title (str): Chart title.
            license (str): License key.
            html_text_rendering (bool): Sharper text display with performance cost.
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
            Reference to PolarChart class.

        Examples:
            Basic chart with simple legend
            >>> chart = lc.PolarChart(
            ...     title='My Chart',
            ...     legend={
            ...         'visible': True,
            ...         'position': 'RightCenter',
            ...         'title': "Data Series"
            ...     }
            ... )

            Styled legend with background and custom entries
            >>> chart = lc.PolarChart(
            ...     title='Styled Chart',
            ...     legend={
            ...         'visible': True,
            ...         'position': 'RightCenter',
            ...         'background_visible': True,
            ...         'background_fill_style': "#e01212",
            ...         'background_stroke_style': {'thickness': 3, 'color': '#003300'},
            ...         'entries': {
            ...             'button_shape': 'Circle',
            ...             'button_size': 20,
            ...             'text_font': {'size': 16},
            ...             'text_fill_style': "#000080"
            ...         }
            ...     }
            ... )

            Custom positioned legend
            >>> chart = lc.PolarChart(
            ...     title='Custom Legend',
            ...     legend={
            ...         'position': 'RightCenter',
            ...         'orientation': 'Horizontal',
            ...         'render_on_top': True,
            ...         'padding': 15,
            ...         'margin_inner': 10
            ...     }
            ... )
        """
        instance = Instance()
        super().__init__(instance)
        self._legend = None        
        self.series_list = []

        legend_config = build_legend_config(legend)

        self.instance.send(
            self.id,
            'polarChart',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
                'legendConfig': legend_config,
            },
        )
        if title:
            self.set_title(title)
        self.category_axis = CategoryAxis(self)
        apply_post_legend_config(self, legend)    
    
    def add_area_series(self, automatic_color_index: int = None, legend: Optional[LegendOptions] = None,):
        """Add an Area series to the PolarChart.

        automatic_color_index (int): Optional index to use for automatic coloring of series.
        legend (dict): Legend configuration dictionary with the following options:
            show (bool): Whether to show this series in legend (default: True).
            text (str): Custom text for legend entry.
            button_shape (str): Button shape ('Circle', 'Square', 'Triangle', 'Diamond', 
                'Plus', 'Cross', 'Minus', 'Star', 'Arrow').
            button_size (int | dict): Button size in pixels or {'x': width, 'y': height}.
            button_fill_style (str): Button color ("#ff0000").
            button_stroke_style (dict): Button border {'thickness': 2, 'color': '#000'}.
            button_rotation (float): Button rotation in degrees.
            text_font (dict): Text font settings {'size': 12, 'family': 'Arial', 'weight': 'bold'}.
            text_fill_style (str): Text color ("#000000").
            match_style_exactly (bool): Whether button should match series style exactly.
            highlight (bool): Whether highlighting on hover is enabled.
            lut: LUT element for legends (None to disable).
            lut_length (int): LUT bar length in pixels.
            lut_thickness (int): LUT bar thickness in pixels.
            lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            PolarAreaSeries instance.

        Examples:        
        Hidden from legend
            >>> series2 = chart.add_area_series(legend={'show': False})
        
        Custom legend appearance
            >>> series3 = chart.add_area_series(
            ...     legend=
            ...     {
            ...         'button_shape': 'Triangle',
            ...         'button_size': 20,
            ...         'button_fill_style': '#00FF00',
            ...         'text': 'Series A',
            ...         'text_font': {'size': 20, 'weight': 'bold'},
            ...     }
            ... )       
        
        """
        area_series = PolarAreaSeries(self, automatic_color_index=automatic_color_index, legend=legend,)
        self.series_list.append(area_series)
        return area_series

    def add_point_series(self, automatic_color_index: int = None, legend: Optional[LegendOptions] = None,):
        """Add a Point series to the PolarChart.

        automatic_color_index (int): Optional index to use for automatic coloring of series.
        legend (dict): Legend configuration dictionary with the following options:
            show (bool): Whether to show this series in legend (default: True).
            text (str): Custom text for legend entry.
            button_shape (str): Button shape ('Circle', 'Square', 'Triangle', 'Diamond', 
                'Plus', 'Cross', 'Minus', 'Star', 'Arrow').
            button_size (int | dict): Button size in pixels or {'x': width, 'y': height}.
            button_fill_style (str): Button color ("#ff0000").
            button_stroke_style (dict): Button border {'thickness': 2, 'color': '#000'}.
            button_rotation (float): Button rotation in degrees.
            text_font (dict): Text font settings {'size': 12, 'family': 'Arial', 'weight': 'bold'}.
            text_fill_style (str): Text color ("#000000").
            match_style_exactly (bool): Whether button should match series style exactly.
            highlight (bool): Whether highlighting on hover is enabled.
            lut: LUT element for legends (None to disable).
            lut_length (int): LUT bar length in pixels.
            lut_thickness (int): LUT bar thickness in pixels.
            lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            PolarPointSeries instance.

        Examples:        
        Hidden from legend
            >>> series2 = chart.add_point_series(legend={'show': False})
        
        Custom legend appearance
            >>> series3 = chart.add_point_series(
            ...     legend=
            ...     {
            ...         'button_shape': 'Triangle',
            ...         'button_size': 20,
            ...         'button_fill_style': '#00FF00',
            ...         'text': 'Series A',
            ...         'text_font': {'size': 20, 'weight': 'bold'},
            ...     }
            ... )        
        """
        point_series = PolarPointSeries(self, automatic_color_index=automatic_color_index, legend=legend,)
        self.series_list.append(point_series)
        return point_series

    def add_line_series(self, automatic_color_index: int = None, legend: Optional[LegendOptions] = None,):
        """Add a Line series to the PolarChart.

        automatic_color_index (int): Optional index to use for automatic coloring of series.
        legend (dict): Legend configuration dictionary with the following options:
            show (bool): Whether to show this series in legend (default: True).
            text (str): Custom text for legend entry.
            button_shape (str): Button shape ('Circle', 'Square', 'Triangle', 'Diamond', 
                'Plus', 'Cross', 'Minus', 'Star', 'Arrow').
            button_size (int | dict): Button size in pixels or {'x': width, 'y': height}.
            button_fill_style (str): Button color ("#ff0000").
            button_stroke_style (dict): Button border {'thickness': 2, 'color': '#000'}.
            button_rotation (float): Button rotation in degrees.
            text_font (dict): Text font settings {'size': 12, 'family': 'Arial', 'weight': 'bold'}.
            text_fill_style (str): Text color ("#000000").
            match_style_exactly (bool): Whether button should match series style exactly.
            highlight (bool): Whether highlighting on hover is enabled.
            lut: LUT element for legends (None to disable).
            lut_length (int): LUT bar length in pixels.
            lut_thickness (int): LUT bar thickness in pixels.
            lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            PolarLineSeries instance.

        Examples:        
        Hidden from legend
            >>> series2 = chart.add_line_series(legend={'show': False})
        
        Custom legend appearance
            >>> series3 = chart.add_line_series(
            ...     legend=
            ...     {
            ...         'button_shape': 'Triangle',
            ...         'button_size': 20,
            ...         'button_fill_style': '#00FF00',
            ...         'text': 'Series A',
            ...         'text_font': {'size': 20, 'weight': 'bold'},
            ...     }
            ... )
        """
        line_series = PolarLineSeries(self, automatic_color_index=automatic_color_index, legend=legend,)
        self.series_list.append(line_series)
        return line_series

    def add_point_line_series(self, automatic_color_index: int = None, legend: Optional[LegendOptions] = None,):
        """Add a Point Line series to the PolarChart.

        automatic_color_index (int): Optional index to use for automatic coloring of series.
        legend (dict): Legend configuration dictionary with the following options:
            show (bool): Whether to show this series in legend (default: True).
            text (str): Custom text for legend entry.
            button_shape (str): Button shape ('Circle', 'Square', 'Triangle', 'Diamond', 
                'Plus', 'Cross', 'Minus', 'Star', 'Arrow').
            button_size (int | dict): Button size in pixels or {'x': width, 'y': height}.
            button_fill_style (str): Button color ("#ff0000").
            button_stroke_style (dict): Button border {'thickness': 2, 'color': '#000'}.
            button_rotation (float): Button rotation in degrees.
            text_font (dict): Text font settings {'size': 12, 'family': 'Arial', 'weight': 'bold'}.
            text_fill_style (str): Text color ("#000000").
            match_style_exactly (bool): Whether button should match series style exactly.
            highlight (bool): Whether highlighting on hover is enabled.
            lut: LUT element for legends (None to disable).
            lut_length (int): LUT bar length in pixels.
            lut_thickness (int): LUT bar thickness in pixels.
            lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            PolarPointLineSeries instance.

        Examples:        
        Hidden from legend
            >>> series2 = chart.add_point_line_series(legend={'show': False})
        
        Custom legend appearance
            >>> series3 = chart.add_point_line_series(
            ...     legend=
            ...     {
            ...         'button_shape': 'Triangle',
            ...         'button_size': 20,
            ...         'button_fill_style': '#00FF00',
            ...         'text': 'Series A',
            ...         'text_font': {'size': 20, 'weight': 'bold'},
            ...     }
            ... )
        """
        series = PolarPointLineSeries(self, automatic_color_index=automatic_color_index, legend=legend,)
        self.series_list.append(series)
        return series

    def add_polygon_series(self, automatic_color_index: int = None, legend: Optional[LegendOptions] = None,):
        """Add a Polygon series to the PolarChart.

        automatic_color_index (int): Optional index to use for automatic coloring of series.
        legend (dict): Legend configuration dictionary with the following options:
            show (bool): Whether to show this series in legend (default: True).
            text (str): Custom text for legend entry.
            button_shape (str): Button shape ('Circle', 'Square', 'Triangle', 'Diamond', 
                'Plus', 'Cross', 'Minus', 'Star', 'Arrow').
            button_size (int | dict): Button size in pixels or {'x': width, 'y': height}.
            button_fill_style (str): Button color ("#ff0000").
            button_stroke_style (dict): Button border {'thickness': 2, 'color': '#000'}.
            button_rotation (float): Button rotation in degrees.
            text_font (dict): Text font settings {'size': 12, 'family': 'Arial', 'weight': 'bold'}.
            text_fill_style (str): Text color ("#000000").
            match_style_exactly (bool): Whether button should match series style exactly.
            highlight (bool): Whether highlighting on hover is enabled.
            lut: LUT element for legends (None to disable).
            lut_length (int): LUT bar length in pixels.
            lut_thickness (int): LUT bar thickness in pixels.
            lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            PolarPolygonSeries instance.

        Examples:        
        Hidden from legend
            >>> series2 = chart.add_polygon_series(legend={'show': False})
        
        Custom legend appearance
            >>> series3 = chart.add_polygon_series(
            ...     legend=
            ...     {
            ...         'button_shape': 'Triangle',
            ...         'button_size': 20,
            ...         'button_fill_style': '#00FF00',
            ...         'text': 'Series A',
            ...         'text_font': {'size': 20, 'weight': 'bold'},
            ...     }
            ... )
        """
        polygon_series = PolarPolygonSeries(self, automatic_color_index=automatic_color_index, legend=legend,)
        self.series_list.append(polygon_series)
        return polygon_series

    def add_heatmap_series(
        self,
        sectors: int,
        annuli: int,
        data_order: str = 'annuli',
        amplitude_start: int | float = 0,
        amplitude_end: int | float = 1,
        amplitude_step: int | float = 0,
        legend: Optional[LegendOptions] = None,
    ):
        """Add a Series for visualizing a Polar Heatmap with a static sector and annuli count.

        Args:
            sectors: Amount of unique data samples along Radial Axis.
            annuli: Amount of unique data samples along Amplitude Axis.
            data_order: "annuli" | "sectors" - Select order of data.
            amplitude_start: Amplitude value where Polar Heatmap originates at.
            amplitude_end: Amplitude value where Polar Heatmap ends at.
            amplitude_step: Amplitude step between each ring (annuli) of the Polar Heatmap.

            legend (dict): Legend configuration dictionary with the following options:
                show (bool): Whether to show this series in legend (default: True).
                text (str): Custom text for legend entry.
                button_shape (str): Button shape ('Circle', 'Square', 'Triangle', 'Diamond', 
                    'Plus', 'Cross', 'Minus', 'Star', 'Arrow').
                button_size (int | dict): Button size in pixels or {'x': width, 'y': height}.
                button_fill_style (str): Button color ("#ff0000").
                button_stroke_style (dict): Button border {'thickness': 2, 'color': '#000'}.
                button_rotation (float): Button rotation in degrees.
                text_font (dict): Text font settings {'size': 12, 'family': 'Arial', 'weight': 'bold'}.
                text_fill_style (str): Text color ("#000000").
                match_style_exactly (bool): Whether button should match series style exactly.
                highlight (bool): Whether highlighting on hover is enabled.
                lut: LUT element for legends (None to disable).
                lut_length (int): LUT bar length in pixels.
                lut_thickness (int): LUT bar thickness in pixels.
                lut_display_proportional_steps (bool): LUT step display mode.

        Returns:
            PolarHeatmapSeries instance.

        Examples:        
        Hidden from legend
            >>> series2 = chart.add_heatmap_series(sectors=4, annuli=3, legend={'show': False})
        
        Custom legend appearance
            >>> series3 = chart.add_heatmap_series(
            ...     sectors=4,
            ...     annuli=3,
            ...     legend=
            ...     {
            ...         'button_shape': 'Triangle',
            ...         'button_size': 20,
            ...         'button_fill_style': '#00FF00',
            ...         'text': 'Series A',
            ...         'text_font': {'size': 20, 'weight': 'bold'},
            ...     }
            ... )
        """
        heatmap_series = PolarHeatmapSeries(
            chart=self,
            sectors=sectors,
            annuli=annuli,
            data_order=data_order,
            amplitude_start=amplitude_start,
            amplitude_end=amplitude_end,
            amplitude_step=amplitude_step,
            legend=legend,
        )
        self.series_list.append(heatmap_series)
        return heatmap_series

    def get_amplitude_axis(self):
        """Get PolarAxisAmplitude object that represents the PolarChart's amplitude dimension,
        which is depicted as a distance away from the Chart's center.

        Returns:
            PolarAxisAmplitude instance.
        """
        amplitude_axis = PolarAxisAmplitude(self)
        return amplitude_axis

    def add_sector(self):
        """Add a Sector highlighter to the PolarChart.

        Returns:
            PolarSector instance.
        """
        sector = PolarSector(self)
        return sector

    def get_radial_axis(self):
        """Get PolarAxisRadial object that represents the PolarChart's radial dimension,
        which is depicted as an angle on the Chart's center.

        Returns:
            PolarAxisRadial instance.
        """
        radial_axis = PolarAxisRadial(self)
        return radial_axis

    def translate_coordinate(self, coordinate: dict, target: str, source: str = None):
        """Translate PolarChart coordinates between systems.
        
        Args:
            coordinate: Dict with coordinate keys for source system
                - polar: {'angle': float, 'amplitude': float} (degrees and radius)
                - relative: {'x': float, 'y': float} (pixels from bottom-left)
                - client: {'clientX': float, 'clientY': float} (screen coordinates)
            target: 'polar' | 'relative' | 'client'
            source: 'polar' | 'relative' | 'client' (auto-detected if None)
    
        Returns:
            Dict with translated coordinates
        
        Examples:
            >>> # Polar to relative (source auto-detected)
            >>> loc = chart.translate_coordinate({'angle': 90, 'amplitude': 4}, target='relative')
            >>> print(f"Relative: x={loc['x']}, y={loc['y']}")
            
            >>> # Polar to client (source auto-detected)
            >>> loc = chart.translate_coordinate({'angle': 45, 'amplitude': 3.5}, target='client')
            >>> print(f"Client: x={loc['clientX']}, y={loc['clientY']}")
            
            >>> # Relative to polar
            >>> loc = chart.translate_coordinate({'x': 200, 'y': 300}, target='polar', source='relative')
            >>> print(f"Polar: angle={loc['angle']}, amplitude={loc['amplitude']}")
            
            >>> # Client to polar (source auto-detected)
            >>> loc = chart.translate_coordinate({'clientX': 500, 'clientY': 400}, target='polar')
            >>> print(f"Polar: angle={loc['angle']}, amplitude={loc['amplitude']}")
        """
        if source is None:
            source = 'polar' if 'angle' in coordinate else 'client' if 'clientX' in coordinate else 'relative'
        
        return self.instance.get(self.id, 'translateCoordinatePolar', {
            'coordinate': coordinate,
            'source': source,
            'target': target
        })

class PolarChartDashboard(PolarChart):
    """Class for PolarChart contained in Dashboard."""

    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        title: str = None,
        legend: Optional[LegendOptions] = None,
    ):
        Chart.__init__(self, instance)
        self.series_list = []
        legend_config = build_legend_config(legend)

        self.instance.send(
            self.id,
            'createPolarChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
                'legendConfig': legend_config,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        apply_post_legend_config(self, legend)


class PolarChartContainer(PolarChart):
    def __init__(self, instance, container, column, row, colspan, rowspan, title, 
                legend):
        Chart.__init__(self, instance)
        self.series_list = []
        legend_config = build_legend_config(legend)
        self.instance.send(
            self.id,
            'createPolarChartContainer',
            {
                'containerId': container.id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
                'legendConfig': legend_config,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        apply_post_legend_config(self, legend)