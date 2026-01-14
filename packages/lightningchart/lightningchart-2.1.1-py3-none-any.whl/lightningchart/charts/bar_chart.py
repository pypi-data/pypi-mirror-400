from __future__ import annotations
from typing import Any, Optional


import lightningchart
from lightningchart import conf, Themes
from lightningchart.charts import ChartsWithAddEventListener, GeneralMethods, TitleMethods, Chart
from lightningchart.instance import Instance
from lightningchart.ui.axis import CategoryAxis, ValueAxis
from lightningchart.utils import convert_to_dict, convert_to_list, convert_color_to_hex
from lightningchart.utils.utils import ColorInput, LegendOptions, apply_post_legend_config, build_legend_config


class BarChart(GeneralMethods, TitleMethods, ChartsWithAddEventListener):
    """Chart type for visualizing categorical data as Bars."""

    def __init__(
        self,
        data: list[dict] = None,
        vertical: bool = True,
        axis_type: str = 'linear',
        axis_base: int = 10,
        title: str = None,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        license: str = None,
        license_information: str = None,
        instance: Instance = None,
        html_text_rendering: bool = True,
        legend: Optional[LegendOptions] = None,
    ):
        """Create a bar chart.

        Args:
        data: List of {category, value} entries.
        vertical (bool): If true, bars are aligned vertically. If false, bars are aligned horizontally.
        axis_type (str): "linear" | "logarithmic"
        axis_base (int): Specification of Logarithmic Base number (e.g. 10, 2, natural log).
        title (str): The title of the chart.
        theme (Themes): The theme of the chart.
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
            BarChart instance.

        Examples:
            Basic chart with simple legend
            >>> chart = lc.BarChart(
            ...     title='My Chart',
            ...     legend={
            ...         'visible': True,
            ...         'position': 'RightCenter',
            ...         'title': "Data Series"
            ...     }
            ... )

            Styled legend with background and custom entries
            >>> chart = lc.BarChart(
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
            >>> chart = lc.BarChart(
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
        Chart.__init__(self, instance)

        legend_config = build_legend_config(legend)
        self.instance.send(
            self.id,
            'barChart',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'vertical': vertical,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'axisType': axis_type,
                'axisBase': axis_base,
                'htmlTextRendering': html_text_rendering,
                'legendConfig': legend_config,
            },
        )
        self.category_axis = CategoryAxis(self)
        self.value_axis = ValueAxis(self)
        if title:
            self.set_title(title)
        if data:
            self.set_data(data)
        apply_post_legend_config(self, legend)      

    
    def set_label_rotation(self, degrees: int):
        """Rotate the category labels.

        Args:
            degrees (int): Degree of the label rotation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarChartLabelRotation', {'degrees': degrees})
        return self

    def set_data(self, data: list[dict]):
        """Set BarChart data, or update existing bars.

        Args:
            data (list[dict]): List of {category, value, color} entries. Color is optional.

        Returns:
            The instance of the class for fluent interface.
        """
        data = convert_to_dict(data)
        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setBarData', {'data': data})
        return self

    def set_data_grouped(self, categories: list[str], data: list[dict]):
        """Set BarChart data, updating the visible bars.
        This method accepts data for a Grouped Bar Chart, displaying it as such.

        Args:
            categories (list[str]): List of categories as strings.
            data: List of { "subCategory": str, "values" list[int | float], "color": str } dictionaries. Color is optional.

        Returns:
            The instance of the class for fluent interface.
        """
        categories = convert_to_list(categories)
        data = convert_to_dict(data)
        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setDataGrouped', {'categories': categories, 'data': data})
        return self

    def set_data_stacked(self, categories: list[str], data: list[dict]):
        """Set BarChart data, updating the visible bars.
        This method accepts data for a Stacked Bar Chart, displaying it as such.

        Args:
            categories (list[str]): List of categories as strings.
            data: List of { "subCategory": str, "values" list[int | float], "color": str } dictionaries. Color is optional.

        Returns:
            The instance of the class for fluent interface.
        """
        categories = convert_to_list(categories)
        data = convert_to_dict(data)
        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setDataStacked', {'categories': categories, 'data': data})
        return self

    def set_value_labels(
        self,
        enabled: bool = True,
        position: str = None,
        color: ColorInput | None = None,
        font_size: int = None,
        font_family: str = None,
        font_weight: str = None,
        font_style: str = None,
        rotation: float = None,
        format_type: str = 'standard',
        precision: int = None,
        unit: str = None,
        scale: float = 1.0,
        currency_symbol: str = None,
        show_category: bool = False,
        display_stacked_sum: bool = None,
        display_stacked_individuals: bool = None,
    ):
        """
        Configure how value labels are displayed in the BarChart.

        Args:
            enabled (bool): Whether to show value labels. If False, hides all labels.
            position (str, optional): Label position: 'after-bar', 'inside-bar', 'inside-bar-centered'
            color (Color, optional): Label text color. Use 'transparent' to hide.
            font_size (int, optional): Font size in pixels
            font_family (str, optional): Font family name
            font_weight (str, optional): Font weight ('normal', 'bold')
            font_style (str, optional): Font style ('normal', 'italic')
            rotation (float, optional): Label rotation in degrees
            format_type (str): Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'thousands': Compact notation (K, M, B, T)
                - 'integer': Rounded integer values
            precision (int, optional): Number of decimal places (None = auto)
            unit (str, optional): Unit to append (e.g., "kg", "ms", "items")
            scale (float): Scale factor to multiply value (default: 1.0)
            currency_symbol (str, optional): Currency symbol for currency format (default: "$")
            show_category (bool): Whether to include category name in label
            display_stacked_sum (bool, optional): Show sum labels for stacked bars
            display_stacked_individuals (bool, optional): Show individual labels for stacked bars

        Examples:
            Rotated labels
            >>> chart.set_value_labels(position='after-bar', rotation=45, format_type='currency', precision=0))

            Stacked bar labels
            >>> chart.set_value_labels(position='inside-bar', display_stacked_individuals=True, display_stacked_sum=True, format_type='currency', precision=2)

            Currency formatting
            >>> chart.set_value_labels(format_type='currency', currency_symbol='€', precision=0)

            Percentage formatting
            >>> chart.set_value_labels(format_type='percentage', precision=1)

        Returns:
            The instance of the class for fluent interface.
        """

        config = {
            'enabled': enabled,
            'position': position,
            'color': convert_color_to_hex(color) if color else None,
            'fontSize': font_size,
            'fontFamily': font_family,
            'fontWeight': font_weight,
            'fontStyle': font_style,
            'rotation': rotation,
            'formatType': format_type,
            'precision': precision,
            'unit': unit,
            'scale': scale,
            'currencySymbol': currency_symbol,
            'showCategory': show_category,
            'displayStackedSum': display_stacked_sum,
            'displayStackedIndividuals': display_stacked_individuals,
        }

        config = {k: v for k, v in config.items() if v is not None}

        self.instance.send(self.id, 'setValueLabels', config)
        return self  

    def set_category_axis_labels(
        self,
        size: int = None,
        family: str = None,
        weight: str = None,
        style: str = None,
        color: str = None,
        rotation: float = None,
        alignment: float = None,
        margin: int = None,
        shadow: str = None,
        tick_length: int = None,
        tick_style: dict = None,
    ):
        """Set font of Chart category axis labels (X-axis labels in vertical bar charts).

        Args:
            size (int | float): CSS font size in pixels. For example, 16.
            family (str, optional): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str, optional): CSS font weight. Options: 'normal', 'bold', 'bolder', 'lighter'.
            style (str, optional): CSS font style. Options: 'normal', 'italic', 'oblique'.
            color (Color, optional): Label text color. Default: None (uses chart theme default). Use 'transparent' to hide.
            rotation (float, optional): Label rotation in degrees. Positive values rotate clockwise.
            alignment: Label alignment (-1 to 1)
            margin: Pixels margin before label
            shadow: Shadow color (hex)
            tick_length: Tick line length (pixels)
            tick_style: {'thickness': int, 'color': str}

        Returns:
            The instance of the class for fluent interface.

        Examples:
            
            Basic usage - set font size
            >>> chart.set_category_axis_labels(size=14)

            Bold labels with custom color
            >>> chart.set_category_axis_labels(
            ...     size=12,
            ...     weight='bold',
            ...     color='darkblue'
            ... )

            Rotated labels for long category names
            >>> chart.set_category_axis_labels(
            ...     size=10,
            ...     rotation=45,
            ...     weight='bold'
            ... )

            Complete customization
            >>> chart.set_category_axis_labels(
            ...     size=16,
            ...     family='Arial',
            ...     style='italic',
            ...     weight='bold',
            ...     color='#ff6600',
            ...     rotation=30,
            ...     tick_style={               
            ...        'thickness': 2,
            ...         'color': '#0000FF'
            ...     }   
            ... )
        """
        config = {}
        if family is not None: 
            config['family'] = family
        if size is not None: 
            config['size'] = size
        if weight is not None: 
            config['weight'] = weight
        if style is not None: 
            config['style'] = style
        if alignment is not None: 
            config['alignment'] = alignment
        if margin is not None: 
            config['margin'] = margin
        if shadow is not None: 
            config['shadow'] = shadow
        if tick_length is not None: 
            config['tickLength'] = tick_length
        if tick_style is not None: 
            config['tickStyle'] = tick_style
        if color is not None: 
            config['color'] = convert_color_to_hex(color)
        if rotation is not None: 
            config['degrees'] = rotation

        self.instance.send(self.id, 'setCategoryAxisLabelFont', config)
        return self
    
    def set_value_axis_labels(
        self,
        major_size: int | float = None,
        minor_size: int | float = None,
        family: str = None,
        style: str = None,
        weight: str = None,
        major_color: lightningchart.Color = None,
        minor_color: lightningchart.Color = None,
        major_rotation: float = None,
        minor_rotation: float = None,
        format_type: str = 'standard',
        precision: int = None,
        unit: str = None,
        scale: float = 1.0,
    ):
        """Set font of value axis tick labels (Y-axis labels in vertical bar charts).

        Args:
            major_size (int | float, optional): Font size for major tick labels in pixels.
            minor_size (int | float, optional): Font size for minor tick labels in pixels.
            family (str, optional): CSS font family for both major and minor tick labels.
            style (str, optional): CSS font style for both major and minor tick labels.
            weight (str, optional): CSS font weight for both major and minor tick labels.
            major_color (Color, optional): Text color for major tick labels. Use 'transparent' or None to hide.
            minor_color (Color, optional): Text color for minor tick labels. Use 'transparent' or None to hide.
            major_rotation (float, optional): Rotation angle in degrees for major tick labels.
                Positive values rotate clockwise. Useful for long numeric formats or units.
            minor_rotation (float, optional): Rotation angle in degrees for minor tick labels.
            format_type (str): Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'thousands': Compact notation (K, M, B, T)
                - 'integer': Rounded integer values
            precision (int, optional): Number of decimal places (None = auto)
            unit (str, optional): Unit to append (e.g., "kg", "ms", "items")
            scale (float): Scale factor to multiply value (default: 1.0)

        Returns:
            The instance of the class for fluent interface.

        Examples:
            Different sizes for major and minor ticks
            >>> chart.set_value_axis_labels(major_size=12, minor_size=10)

            Rotate major tick labels (useful for long numbers/units)
            >>> chart.set_value_axis_labels(
            ...     major_size=12,
            ...     major_rotation=45,
            ...     major_color=('black')
            ... )

            Different rotations for major and minor ticks
            >>> chart.set_value_axis_labels(
            ...     major_size=12,
            ...     minor_size=9,
            ...     major_rotation=30,
            ...     minor_rotation=15,
            ...     major_color='darkblue',
            ...     minor_color='gray'
            ... )

            Professional look with rotated labels
            >>> chart.set_value_axis_labels(
            ...     major_size=12,
            ...     minor_size=9,
            ...     weight='bold',
            ...     major_color='#2c3e50',
            ...     minor_color='#7f8c8d',
            ...     major_rotation=0,    # No rotation for major
            ...     minor_rotation=90    # Vertical minor labels
            ... )

            Rotated labels for currency or percentage values
            >>> chart.set_value_axis_labels(
            ...     major_size=11,
            ...     minor_size=8,
            ...     major_rotation=45,
            ...     minor_rotation=45,
            ...     major_color='darkgreen',
            ...     minor_color='green'
            ... )

            Scientific notation with rotation and formatting parameters
            >>> chart.set_value_axis_labels(
            ...     major_size=10,
            ...     minor_size=8,
            ...     family='monospace',
            ...     major_rotation=30,
            ...     minor_rotation=30,
            ...     major_color='navy',
            ...     minor_color='blue',
            ...     format_type='standard',
            ...     precision=2,
            ...     unit='AA',
            ...     scale=2
            ... )
        """
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

        self.instance.send(self.id, 'setBarValueAxisLabelFont', config)
        return self


    def set_sorting(self, mode: str):
        """Configure automatic sorting of bars.

        Args:
            mode: "disabled" | "ascending" | "descending" | "alphabetical"

        Returns:
            The instance of the class for fluent interface.
        """
        sorting_modes = ('disabled', 'ascending', 'descending', 'alphabetical')
        if mode not in sorting_modes:
            raise ValueError(f"Expected mode to be one of {sorting_modes}, but got '{mode}'.")

        self.instance.send(self.id, 'setSorting', {'mode': mode})
        return self

    def set_label_fitting(self, enabled: bool):
        """Enable or disable automatic label fitting.

        Args:
            enabled (bool): If true, labels will not overlap.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelFitting', {'enabled': enabled})
        return self

    def set_series_background_effect(self, enabled: bool = True):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setSeriesBackgroundEffect', {'enabled': enabled})
        return self

    def set_series_background_color(self, color: ColorInput | None):
        """Set chart series background color.

        Args:
            color (Color): Color of the series background. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSeriesBackgroundFillStyle', {'color': color})
        return self

    def set_animation_category_position(self, enabled: bool):
        """Enable/disable animation of bar category positions. This is enabled by default.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationCategoryPosition', {'enabled': enabled})
        return self

    def set_animation_values(self, enabled: bool):
        """Enable/disable animation of bar values. This is enabled by default.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationValues', {'enabled': enabled})
        return self

    def set_bars_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarsEffect', {'enabled': enabled})
        return self

    def set_bars_margin(self, margin: int | float):
        """Set margin around each bar along category axis as percentage of the bar thickness.
        For example, 0.1 = on both left and right side of bar there is a 10% margin.
        Actual thickness of bar depends on chart size, but for 100 px bar that would be 10 px + 10 px margin.
        Valid value range is between [0, 0.49].

        Args:
            margin (int | float): Margin around each bar along category axis as percentage of bar thickness.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarsMargin', {'margin': margin})
        return self

    def set_bar_color(self, category: str, color: ColorInput | None):
        """Set the color value of a single category bar.

        Args:
            category (str): Category name.
            color (Color): Color value. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBarColor', {'category': category, 'color': color})
        return self

    def set_subcategory_color(self, category: str, subcategory: str, color: ColorInput | None):
        """Set the color value of a single category bar.

        Args:
            category (str): Category name.
            subcategory (str): Subcategory name.
            color (Color): Color value. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setSubCategoryColor',
            {
                'category': category,
                'subCategory': subcategory,
                'color': color,
            },
        )
        return self

    def set_bars_color(self, color: ColorInput | None):
        """Set the color value of all bars.

        Args:
            color: Color value. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBarsColor', {'color': color})
        return self

    def get_bar_color(self, category: str, sub_category: str | None = None) -> dict:
        """Get the fill color of a single bar (BarChart).

        Args:
            category: Bar category name.
            sub_category: Optional sub-category (for grouped/stacked bars).

        Returns:
            dict with 'color', 'colorHex', 'colorRgb'.

        Notes:
            Call this in live mode, e.g. ``chart.open(live=True)``
        """
        payload = {'category': category}
        if sub_category is not None:
            payload['subCategory'] = sub_category
        return self.instance.get(self.id, 'getBarFillStyle', payload)

    def set_palette_colors(
        self,
        steps: list[dict[str, Any]],
        percentage_values: bool = True,
        interpolate: bool = True,
        look_up_property: str = 'y',
    ):
        """Define a palette coloring for the bars.

        Args:
            steps (list[dict]): List of {"value": number, "color": Color, 'label': 'Label'} dictionaries.
            interpolate (bool): Enables automatic linear interpolation between color steps.
            percentage_values (bool): Whether values represent percentages or explicit values.
            look_up_property (str): "value" | "x" | "y"

        Returns:
            The instance of the class for fluent interface.
        """
        for i in steps:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(
            self.id,
            'setPalettedBarColor',
            {
                'steps': steps,
                'lookUpProperty': look_up_property,
                'interpolate': interpolate,
                'percentageValues': percentage_values,
            },
        )
        return self

    def translate_coordinate(self, coordinate: dict, target: str, source: str = None):
        """Translate BarChart coordinates between systems.
        
        Args:
            coordinate: Dict with keys for source system
            target: 'bars' | 'relative' | 'client'
            source: 'bars' | 'relative' | 'client' (auto-detected if None)
        
        Returns:
            Dict with translated coordinates
    
        Examples:
            >>> # Bars to relative (source auto-detected)
            >>> loc = chart.translate_coordinate({'iCategory': 0, 'value': 50}, target='relative', source='bars')
            >>> print(f"Relative: x={loc['x']}, y={loc['y']}")
            
            >>> # Relative to bars
            >>> loc = chart.translate_coordinate({'x': 200, 'y': 300}, target='bars', source='relative')
            >>> print(f"Bars: category={loc['iCategory']}, value={loc['value']}")
            
            >>> # Client to bars (source auto-detected)
            >>> loc = chart.translate_coordinate({'clientX': 500, 'clientY': 400}, target='bars')
            >>> print(f"Bars: category={loc['iCategory']}, value={loc['value']}")
        """
        if source is None:
            source = 'bars' if 'iCategory' in coordinate else 'client' if 'clientX' in coordinate else 'relative'
        
        return self.instance.get(self.id, 'translateCoordinateBar', {
            'coordinate': coordinate,
            'source': source,
            'target': target
        })
class BarChartDashboard(BarChart):
    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        vertical: bool,
        axis_type: str,
        axis_base: int,
        title: str = None,
        legend: Optional[LegendOptions] = None,
    ):
        Chart.__init__(self, instance)
        legend_config = build_legend_config(legend)
        self.instance.send(
            self.id,
            'createBarChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
                'vertical': vertical,
                'axisType': axis_type,
                'axisBase': axis_base,
                'legendConfig': legend_config,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        self.category_axis = CategoryAxis(self)
        self.value_axis = ValueAxis(self)
        apply_post_legend_config(self, legend)


class BarChartContainer(BarChart):
    def __init__(
            self, 
            instance, 
            container, 
            column, 
            row, 
            colspan, 
            rowspan,  
            title,  
            vertical,
            axis_type,
            axis_base,
            legend, 
            ):
        Chart.__init__(self, instance)
        
        legend_config = build_legend_config(legend)
        self.instance.send(
            self.id,
            'createBarChartContainer',
            {
                'containerId': container.id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
                'vertical': vertical,
                'axisType': axis_type,
                'axisBase': axis_base,
                'legendConfig': legend_config,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        self.category_axis = CategoryAxis(self)
        self.value_axis = ValueAxis(self)
        apply_post_legend_config(self, legend)