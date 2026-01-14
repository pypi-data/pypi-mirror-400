from typing import Optional, Self
from lightningchart import Themes, conf
from lightningchart.series.parallel_coordinate_series import ParallelCoordinateSeries
from lightningchart.charts import ChartWithSeries, ChartsWithAddEventListener, ChartsWithCoordinateTransforms, ChartsWithCursorMode, TitleMethods, GeneralMethods, Chart
from lightningchart.instance import Instance
from lightningchart.ui.axis import GenericAxis
from lightningchart.ui import UserInteractions
from lightningchart.ui.parallel_coordinate_custom_tick import ParallelCoordinateCustomTick
from lightningchart.utils import convert_color_to_hex
import uuid

from lightningchart.utils.utils import ColorInput, LegendOptions, apply_post_legend_config, build_legend_config


class ParallelCoordinateChart(ChartWithSeries, TitleMethods, GeneralMethods, UserInteractions, ChartsWithCoordinateTransforms, ChartsWithAddEventListener, ChartsWithCursorMode):
    """Chart for visualizing data in a parallel coordinate system."""

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
        """Initialize a Parallel Coordinate Chart with a theme and optional title.

        Args:
            theme (Themes): Theme for the chart. Defaults to `Themes.White`.
            title (str, optional): Title of the chart. Defaults to None.
            license (str): License key.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
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
            Reference to ParallelCoordinateChart class.

        Examples:
            Basic chart with simple legend
            >>> chart = lc.ParallelCoordinateChart(
            ...     title='My Chart',
            ...     legend={
            ...         'visible': True,
            ...         'position': 'RightCenter',
            ...         'title': "Data Series"
            ...     }
            ... )

            Styled legend with background and custom entries
            >>> chart = lc.ParallelCoordinateChart(
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
            >>> chart = lc.ParallelCoordinateChart(
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
        self.theme = theme
        self.axes = []
        self.series_list = []

        legend_config = build_legend_config(legend)
        self.instance.send(
            self.id,
            'parallelCoordinateChart',
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
        apply_post_legend_config(self, legend)        
    
    def set_axes(self, axes: list):
        """Set axes of the parallel coordinate chart as a list of strings.

        Args:
            axes (list): List of axis names or identifiers.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.axes = axes
        self.instance.send(self.id, 'setAxes', {'axes': axes})
        return self

    def get_axis(self, axis_key: str):
        """Retrieve a specific axis by its name or ID.

        Args:
            axis_key (str): The key or name of the axis.

        Returns:
            The corresponding axis object.

        Raises:
            ValueError: If the axis with the given key is not found.
        """

        if axis_key in self.axes:
            axis_name = axis_key
        else:
            raise ValueError(f"Axis with key '{axis_key}' not found.")

        return ParallelCoordinateAxis(self, axis_name)

    def add_series(self, theme: Themes = Themes.Light,  name: str = None):
        """Add a new data series to the chart. 
       
               
        Returns:
            The created series instance.        
        """
        series = ParallelCoordinateSeries(self)
        self.series_list.append(series)
        return series

    def get_series(self) -> list[ParallelCoordinateSeries]:
        """Get all data series in the chart.

        Returns:
            A list of all series in the chart.
        """
        return self.series_list

    def set_lut(
            self, 
            axis_key: str, 
            interpolate: bool, 
            steps: list,
            percentage_values: bool = False,
            formatter_precision: int | None = None,
            formatter_unit: str = '',
            formatter_scale: float = 1.0,
            formatter_type: str = 'standard',
            formatter_operation: str = 'none'
            ):
        """Configure series coloring by a Value-Color Table (LUT) based on a specific axis.

        Args:
            axis_key (str): The key of the axis for which to apply LUT.
            interpolate (bool): Whether to interpolate between LUT steps.
            steps (list): List of LUT steps, each with a value and color.
            percentage_values (bool): Whether values represent percentages or explicit values.
            formatter_precision (int | None): Decimal places for legend display.
            formatter_unit (str): Unit suffix (e.g., "mag", "ms").
            formatter_scale (float): Multiply values by this factor.
            formatter_type (str): 'standard', 'compact', 'engineering', 'scientific'.
            formatter_operation (str): 'none', 'round', 'ceil', 'floor'.

        Returns:
            The instance of the chart for fluent interface.
        """
        for step in steps:
            step['color'] = convert_color_to_hex(step['color'])

        lut_config = {
            'interpolate': interpolate,
            'steps': steps,
            'percentageValues': percentage_values,
            'formatter_precision': formatter_precision,
            'formatter_unit': formatter_unit,
            'formatter_scale': formatter_scale,
            'formatter_type': formatter_type,
            'formatter_operation': formatter_operation,
        }
        self.instance.send(self.id, 'setParallelAxisLUT', {'axisId': axis_key, 'lut': lut_config})
        return self

    def set_spline(self, enabled: bool):
        """Enable or disable spline interpolation for the chart.

        Args:
            enabled (bool): True to enable spline interpolation, False to disable.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.instance.send(self.id, 'setSpline', {'enabled': enabled})
        return self

    def set_series_stroke_thickness(self, thickness: int | float):
        """Set the thickness of series lines.

        Args:
            thickness (int | float): Thickness of the lines in pixels.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.instance.send(self.id, 'setSeriesStrokeThickness', {'thickness': thickness})
        return self

    def set_highlight_on_hover(self, state: bool):
        """Enable or disable highlight on hover for series.

        Args:
            state (bool): True to enable highlight on hover, False to disable.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.instance.send(self.id, 'setSeriesHighlightOnHover', {'state': state})
        return self

    def set_unselected_series_color(self, color: ColorInput | None)-> Self:
        """Set the color for unselected series.

        Args:
            Color: Color to apply to unselected series. Use 'transparent' or None to hide.

        Returns:
            The instance of the chart for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setUnselectedSeriesColor', {'color': color})
        return self

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Examples:
            ## Disable all interactions:
            >>> chart.set_user_interactions(None)

            ## Restore default interactions:
            >>> chart.set_user_interactions()
            ... chart.set_user_interactions({})

            ## Remove select range selector interactions
            >>> chart.set_user_interactions(
            ...     {
            ...         'rangeSelectors': {
            ...             'create': {
            ...                 'doubleClickAxis': True,
            ...             },
            ...             'dispose': {
            ...                 'doubleClick': True,
            ...             },
            ...         },
            ...     }
            ... )
        """
        return super().set_user_interactions(interactions)
    
    def set_all_axes_tick_labels(
        self,
        major_size: int | float | None = None,
        minor_size: int | float | None = None,
        family: str | None = None,
        style: str | None = None,
        weight: str | None = None,
        major_color : ColorInput | None = None,
        minor_color : ColorInput | None = None,
        major_rotation: float | None = None,
        minor_rotation: float | None = None,
        format_type: str = 'standard',
        precision: int | None = None,
        unit: str | None = None,
        scale: float = 1.0,
    ):
        """Style tick labels for ALL parallel coordinate axes at once.
        
        Args:
            major_size: Font size for major tick labels in pixels.
            minor_size: Font size for minor tick labels in pixels.
            family: CSS font family for both major and minor tick labels.
            style: CSS font style ('normal', 'italic').
            weight: CSS font weight ('normal', 'bold').
            major_color: Text color for major tick labels.
                Accepts hex string, named color, RGB/RGBA tuple, or Color object.
            minor_color: Text color for minor tick labels.
                Accepts hex string, named color, RGB/RGBA tuple, or Color object.
            major_rotation: Rotation angle in degrees for major tick labels.
            minor_rotation: Rotation angle in degrees for minor tick labels.
            format_type: Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'thousands': Compact notation (K, M, B, T)
                - 'integer': Rounded integer values
            precision: Number of decimal places (None = auto).
            unit: Unit to append (e.g., "kg", "ms", "items").
            scale: Scale factor to multiply value (default: 1.0).
        
        Returns:
            The instance of the chart for fluent interface.
        
        Examples:
            Style all axes uniformly
            >>> chart.set_all_axes_tick_labels(major_size=14, minor_size=10, weight='bold')
            
            Rotated labels on all axes
            >>> chart.set_all_axes_tick_labels(
            ...     major_size=12,
            ...     major_rotation=45,
            ...     major_color='darkblue'
            ... )
            
            Formatted with units on all axes
            >>> chart.set_all_axes_tick_labels(
            ...     major_size=12,
            ...     precision=2,
            ...     format_type='standard'
            ... )
        """
        from lightningchart.utils import convert_color_to_hex
        
        config = {}
        if family is not None:
            config['family'] = family
        if style is not None:
            config['style'] = style
        if weight is not None:
            config['weight'] = weight
        if major_size is not None:
            config['majorSize'] = major_size
        if minor_size is not None:
            config['minorSize'] = minor_size
        if major_rotation is not None:
            config['majorRotation'] = major_rotation
        if minor_rotation is not None:
            config['minorRotation'] = minor_rotation
        if major_color is not None:
            config['majorColor'] = convert_color_to_hex(major_color)
        if minor_color is not None:
            config['minorColor'] = convert_color_to_hex(minor_color)
        if format_type is not None:
            config['formatType'] = format_type
        if precision is not None:
            config['precision'] = precision
        if unit is not None:
            config['unit'] = unit
        if scale is not None:
            config['scale'] = scale
        
        self.instance.send(
            self.id,
            'setAllParallelAxesTickLabels',
            {'config': config}
        )
        return self

class ParallelCoordinateAxis(GenericAxis):
    def __init__(self, chart, axis_key):
        """Initialize a parallel coordinate axis.

        Args:
            chart (ParallelCoordinateChart): The parent chart.
            axis_key (str): The identifier or name of the axis.
        """
        self.chart = chart
        self.axis_key = axis_key
        self.instance = chart.instance
        self.id = str(uuid.uuid4()).split('-')[0]

        self.instance.send(
            self.chart.id,
            'getParallelAxisReference',
            {'axisKey': axis_key, 'axisID': self.id},
        )

    def add_range_selector(self):
        """Add a range selector to this axis.

        Returns:
            The created range selector object.
        """
        selector_id = str(uuid.uuid4()).split('-')[0]
        self.chart.instance.send(
            self.chart.id,
            'addRangeSelector',
            {'axisId': self.axis_key, 'selectorId': selector_id},
        )
        return ParallelCoordinateAxisRangeSelector(self.chart, self.axis_key, selector_id)

    def set_palette_stroke(self, thickness: int | float, interpolate: bool, steps: list):
        """Set the stroke style of the axis with a palette.

        Args:
            thickness (int | float): Thickness of the stroke in pixels.
            interpolate (bool): Whether to interpolate between palette steps.
            steps (list): List of palette steps, each containing value and color.

        Returns:
            The instance of the axis for fluent interface.
        """
        for step in steps:
            step['color'] = convert_color_to_hex(step['color'])
        self.chart.instance.send(
            self.chart.id,
            'setParallelAxisStrokeStyle',
            {
                'axisId': self.axis_key,
                'thickness': thickness,
                'lut': {'interpolate': interpolate, 'steps': steps},
            },
        )
        return self

    def set_solid_stroke(self, thickness: int | float, color: ColorInput | None = None) -> Self:
        """Set a solid stroke style for the axis.

        Args:
            thickness (int | float): Thickness of the stroke in pixels.
            color: Solid color for the stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the axis for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.chart.instance.send(
            self.chart.id,
            'setSolidStroke',
            {'axisId': self.axis_key, 'thickness': thickness, 'color': color},
        )
        return self

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set the tick strategy for the axis.

        Args:
            strategy (str): Tick strategy ("Empty", "Numeric", "DateTime", "Time").
            time_origin (int | float, optional): Time origin for the strategy. Defaults to None.
            utc (bool, optional): Whether to use UTC for DateTime strategy. Defaults to False.

        Returns:
            The instance of the axis for fluent interface.
        """
        strategies = ('Empty', 'Numeric', 'DateTime', 'Time')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.chart.instance.send(
            self.chart.id,
            'setParallelAxisTickStrategy',
            {
                'strategy': strategy,
                'axisId': self.axis_key,
                'timeOrigin': time_origin,
                'utc': utc,
            },
        )
        return self

    def set_stopped(self, stopped: bool):
        """Stop/resume axis so scroll strategy won't change its interval.

        Args:
            stopped (bool): True to stop, False to resume.

        Returns:
            The instance of the axis for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'setStopped',
            {'axisId': self.axis_key, 'stopped': stopped},
        )
        return self

    def set_units(self, units: str | None, behavior: dict | None = None):
        """Set axis units (e.g., 'Hz', '°C') with optional behavior flags.

        Args:
            units: String (e.g., 'Hz') or None to clear.
            behavior: Optional dict with keys:
                - displayOnAxis (bool)
                - displayInCursor (bool)

        Returns:
            The instance of the axis for fluent interface.
        """
        payload = {'axisId': self.axis_key, 'units': units, 'behavior': behavior or {}}
        self.chart.instance.send(self.chart.id, 'setUnits', payload)
        return self

    def set_animation_scroll(self, enabled: bool | None):
        """Enable/disable scroll animation.

        Args:
            enabled: True/False; None maps to undefined (disables custom setting).

        Returns:
            The instance of the axis for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'setAnimationScroll',
            {'axisId': self.axis_key, 'enabled': enabled},
        )
        return self
    
    def add_custom_tick(self):
        """Add custom tick to parallel coordinate axis.

        Returns:
            Reference to ParallelCoordinateCustomTick class.
        """
        return ParallelCoordinateCustomTick(self.chart, self)
    
    def set_tick_labels(
        self,
        major_size: int | float | None = None,
        minor_size: int | float | None = None,
        family: str | None = None,
        style: str | None = None,
        weight: str | None = None,
        major_color: ColorInput | None = None,
        minor_color: ColorInput | None = None,
        major_rotation: float | None = None,
        minor_rotation: float | None = None,
        format_type: str = 'standard',
        precision: int | None = None,
        unit: str | None = None,
        scale: float = 1.0,
    ):
        """Style tick labels for this parallel coordinate axis.
        
        Args:
            major_size: Font size for major tick labels in pixels.
            minor_size: Font size for minor tick labels in pixels.
            family: CSS font family for both major and minor tick labels.
            style: CSS font style ('normal', 'italic').
            weight: CSS font weight ('normal', 'bold').
            major_color: Text color for major tick labels.
                Accepts hex string, named color, RGB/RGBA tuple, or Color object.
            minor_color: Text color for minor tick labels.
                Accepts hex string, named color, RGB/RGBA tuple, or Color object.
            major_rotation: Rotation angle in degrees for major tick labels.
            minor_rotation: Rotation angle in degrees for minor tick labels.
            format_type: Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'thousands': Compact notation (K, M, B, T)
                - 'integer': Rounded integer values
            precision: Number of decimal places (None = auto).
            unit: Unit to append (e.g., "kg", "ms", "items").
            scale: Scale factor to multiply value (default: 1.0).
        
        Returns:
            The instance of the axis for fluent interface.
        
        Examples:
            Basic font styling:
            >>> axis.set_tick_labels(major_size=14, minor_size=10, weight='bold')
            
            Rotated labels with color:
            >>> axis.set_tick_labels(
            ...     major_size=12,
            ...     major_rotation=45,
            ...     major_color='darkblue'
            ... )
            
            Using various color formats:
            >>> axis.set_tick_labels(major_color='#FF0000')           # Hex string
            >>> axis.set_tick_labels(major_color='red')               # Named color
            >>> axis.set_tick_labels(major_color=(255, 0, 0))         # RGB tuple
            >>> axis.set_tick_labels(major_color=(255, 0, 0, 128))    # RGBA tuple
            >>> axis.set_tick_labels(major_color=0xFF0000)            # Integer
            
            Formatted with units:
            >>> axis.set_tick_labels(
            ...     major_size=12,
            ...     precision=2,
            ...     unit='Hz',
            ...     scale=1000
            ... )
            
            Percentage formatting:
            >>> axis.set_tick_labels(
            ...     format_type='percentage',
            ...     precision=1
            ... )
        """
        from lightningchart.utils import convert_color_to_hex
        
        config: dict[str, str | int | float] = {}
        
        if family is not None:
            config['family'] = family
        if style is not None:
            config['style'] = style
        if weight is not None:
            config['weight'] = weight
        if major_size is not None:
            config['majorSize'] = major_size
        if minor_size is not None:
            config['minorSize'] = minor_size
        if major_rotation is not None:
            config['majorRotation'] = major_rotation
        if minor_rotation is not None:
            config['minorRotation'] = minor_rotation
        if major_color is not None:
            config['majorColor'] = convert_color_to_hex(major_color)
        if minor_color is not None:
            config['minorColor'] = convert_color_to_hex(minor_color)
        if format_type is not None:
            config['formatType'] = format_type
        if precision is not None:
            config['precision'] = precision
        if unit is not None:
            config['unit'] = unit
        if scale is not None:
            config['scale'] = scale
        
        self.chart.instance.send(
            self.chart.id,
            'setParallelTickLabels',
            {'axisId': self.axis_key, 'config': config}
        )
        return self
    
    def get_custom_ticks(self):
        """Get information about all custom ticks on this axis.
        
        Returns:
            list[dict]: List of custom tick information dictionaries, each containing:
                - id (str): Unique identifier for the tick
                - value (float): Axis value where tick is positioned
                - text (str): Label text displayed on the tick
                - visible (bool): Whether tick is visible
                - allocatesAxisSpace (bool): Whether tick reserves space on axis
                - tickLength (float): Length of tick line in pixels
                - gridStrokeLength (float): Length of grid line
                - tickLabelPadding (float): Padding around label
                - gridStrokeStyle (dict): Grid line style {'thickness': int, 'color': str}
                - tickStrokeStyle (dict): Tick line style {'thickness': int, 'color': str}
                - markerFont (dict): Font settings {'size': int, 'family': str, 'weight': str, 'style': str}
                - markerColor (str): Marker text color (rgba string)
                - textFont (dict): Text font settings
                - textColor (str): Text color (rgba string)
                - backgroundColor (str): Label background color (rgba string)
                - backgroundStrokeStyle (dict): Background border style {'thickness': int, 'color': str}
                - padding (float): Padding value
                - tickLabelRotation (float): Label rotation in degrees
        
        Notes:
            Must be called in live mode and better after opening the chart window, chart.open(live=True).
            
            
        Examples:
            Get all custom ticks with their properties:
            >>> ticks = axis.get_custom_ticks()
            >>> for tick in ticks:
            ...     print(f"Value: {tick['value']}, Text: {tick['text']}")
            ...     print(f"Font: {tick['textFont']}")
            ...     print(f"Color: {tick['textColor']}")
        """
        return self.instance.get(self.id, 'getCustomTicks', {})
    

   

class ParallelCoordinateAxisRangeSelector():
    def __init__(self, chart, axis_key, selector_id):
        """Initialize a range selector for a parallel coordinate axis.

        Args:
            chart (ParallelCoordinateChart): The parent chart.
            axis_key (str): The key or name of the axis.
            selector_id (str): Unique identifier for the selector.
        """
        self.chart = chart
        self.axis_key = axis_key
        self.selector_id = selector_id

    def set_interval(self, a: float, b: float, stop_axis_after: bool = False, animate: bool = False):
        """Set the range interval for the selector.

        Args:
            a (float): Start of the interval.
            b (float): End of the interval.
            stop_axis_after (bool, optional): Stop axis after the range. Defaults to False.
            animate (bool, optional): Animate the range update. Defaults to False.

        Returns:
            The instance of the selector for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'setRangeSelectorInterval',
            {
                'selectorId': self.selector_id,
                'axisId': self.axis_key,
                'start': a,
                'end': b,
                'stop': stop_axis_after,
                'animate': animate,
            },
        )
        return self

    def dispose(self):
        """Remove the range selector permanently.

        Returns:
            The instance of the class for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'disposeRangeSelector',
            {
                'selectorId': self.selector_id,
            },
        )
        return self


class ParallelCoordinateChartDashboard(ParallelCoordinateChart):
    """Class for ParallelCoordinateChart contained in Dashboard."""

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
            'createParallelCoordinateChart',
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


class ParallelCoordinateChartContainer(ParallelCoordinateChart):
    def __init__(self, instance, container, column, row, colspan, rowspan, title, 
                legend):
        Chart.__init__(self, instance)
        
        self.axes = []
        self.series_list = []
        
        legend_config = build_legend_config(legend)
        self.instance.send(
            self.id,
            'createParallelCoordinateChartContainer',
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