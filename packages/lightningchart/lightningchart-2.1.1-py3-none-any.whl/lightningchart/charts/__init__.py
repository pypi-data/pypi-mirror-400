from __future__ import annotations
import datetime
from typing import Unpack
import uuid

from lightningchart.instance import Instance
from lightningchart.ui.axis import DefaultAxis, DefaultAxis3D, Axis
from lightningchart.ui.legend import Legend
from lightningchart.ui.text_box import TextBox
from lightningchart.utils import convert_to_base64, convert_color_to_hex
from lightningchart.utils.utils import ColorInput, LegendOptions, PaddingKwargs


class Chart:
    def __init__(self, instance: Instance):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = instance
        self._legend = None

    @property
    def legend(self):
        """Access to chart's default legend."""
        if self._legend is None:
            self._legend = Legend(self)
        return self._legend

    def open(
        self,
        method: str = None,
        live=False,
        width: int | str = '100%',
        height: int | str = 600,
    ):
        """Open the rendering view.
        Method "browser" will open the chart in your browser.
        Method "notebook" will display the chart in a notebook environment with an IFrame component.
        Method "link" will return a URL of the chart that can be used to embed it in external applications.

        Args:
            method (str): "browser" | "notebook"
            live (bool): Whether to use real-time rendering or not.
            width (int): The width of the IFrame component in pixels.
            height (int): The height of the IFrame component in pixels.

        Returns:
            self | str: Returns a URL string if method is "link", otherwise returns the class instance.
        """
        return self.instance.open(method=method, live=live, width=width, height=height) or self

    def close(self):
        """Close the connection to a chart with real-time display mode.

        Note: This will terminate the current Python instance!
        """
        self.instance.close()
        return self

    def set_data_preservation(self, enabled: bool):
        """Enable or disable server-side data preservation for real-time visualization use cases.

        Enabled by default!

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.set_data_preservation(enabled)
        return self


class GeneralMethods(Chart):
    def save_to_file(
        self,
        file_name: str = None,
        image_format: str = 'image/png',
        image_quality: float = 0.92,
        scale: float = None,
    ):
        """Save the current rendering view as a screenshot.

        Args:
            file_name (str): Name of prompted download file as string. File extension shouldn't be included as it is
                automatically detected from 'type'-argument.
            image_format (str): A DOMString indicating the image format. The default format type is image/png.
            image_quality (float): A Number between 0 and 1 indicating the image quality to use for image formats that
                use lossy compression such as image/jpeg and image/webp. If this argument is anything else,
                the default value for image quality is used. The default value is 0.92.
            scale (float): Convenience output scaling factor. This doesn't actually stretch the result, but instead draws an altered scaled version and captures that.

        Returns:
            The instance of the class for fluent interface.
        """
        if file_name is None:
            file_name = f'LightningChart_Python_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        self.instance.send(
            self.id,
            'saveToFile',
            {
                'fileName': file_name,
                'type': image_format,
                'encoderOptions': image_quality,
                'scale': scale,
            },
        )
        return self

    def dispose(self):
        """Permanently destroy the component."""
        self.instance.send(self.id, 'dispose')

    def set_animations_enabled(self, enabled: bool = True):
        """Disable/Enable all animations of the Chart.

        Args:
            enabled (bool): Boolean value to enable or disable animations.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationsEnabled', {'enabled': enabled})
        return self

    def set_padding(self, *args, **kwargs: Unpack[PaddingKwargs]):
        """Set padding around the chart in pixels.        

        Args:
            *args: A single numeric value (int or float) for uniform padding on all sides.
            **kwargs: Optional named arguments to specify padding for individual sides:
                - `left` (int or float): Padding for the left side.
                - `right` (int or float): Padding for the right side.
                - `top` (int or float): Padding for the top side.
                - `bottom` (int or float): Padding for the bottom side.

        Examples:
            - `set_padding(5)`: Sets uniform padding for all sides (integer or float).
            - `set_padding(left=10, top=15)`: Sets padding for specific sides only.
            - `set_padding(left=10, top=15, right=20, bottom=25)`: Fully define padding for all sides.

        Returns:
            The instance of the class for fluent interface.
        """
        if len(args) == 1 and isinstance(args[0], (int, float)):
            padding = args[0]
        elif kwargs:
            padding = {}
            for key in ['left', 'right', 'bottom', 'top']:
                if key in kwargs:
                    padding[key] = kwargs[key]
        else:
            raise ValueError(
                'Invalid arguments. Use one of the following formats:\n'
                '- set_padding(5): Uniform padding for all sides.\n'
                '- set_padding(left=10, top=15): Specify individual sides.\n'
                '- set_padding(left=10, top=15, right=20, bottom=25): Full padding definition.'
            )

        self.instance.send(self.id, 'setPadding', {'padding': padding})
        return self

    def set_background_color(self, color: ColorInput | None):
        """Set the background color of the chart.

        Args:
            color (Color): Color of the background. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBackgroundFillStyle', {'color': color})
        return self
    
    def get_background_color(self) -> dict:
        """Get chart background color.
        
        Returns:
            dict with 'color', 'colorHex', 'colorRgb'.
        """
        return self.instance.get(self.id, 'getChartBackgroundColor', {})

    def set_background_stroke(self, thickness: int | float, color: ColorInput | None = None):
        """Set the background stroke style of the chart.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): The color of the stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setBackgroundStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self
    
    def add_legend(self, **options:Unpack[LegendOptions]) -> Legend:
        """Add a new user-managed legend to the chart.  

        Args:
            **options: Legend configuration options including:
                visible (bool): Whether legend should be visible (default: True)
                position: Legend position (LegendPosition enum or custom position dict)
                title (str): Legend title
                title_font (dict): Title font settings
                title_fill_style: Title color/fill style
                orientation: Legend orientation (LegendOrientation.Horizontal/Vertical)
                render_on_top (bool): Whether to render legend on top of chart
                background_visible (bool): Whether background should be visible
                background_fill_style: Background fill style
                background_stroke_style: Background stroke style
                padding: Legend content padding
                margin_inner: Margin from chart to legend
                margin_outer: Margin from legend to chart edge
                entry_margin: Margin between legend entries
                auto_hide_threshold (float): Auto-hide threshold (0.0-1.0)
                add_entries_automatically (bool): Whether to add entries automatically (default: False for user legends)
                entries (dict): Default entry options
        
        Returns:
           New user-managed legend instance
        
        Examples:
            Basic user-managed legend
            >>> legend = chart.add_legend(title="Custom Legend")
            
            Positioned legend
            >>> legend = chart.add_legend(
            ...    position='TopRight',
            ...    orientation='Horizontal',
            ...    background_visible=True
            )
        """
        legend = Legend(self, is_user_legend=True)
        legend_id = str(uuid.uuid4())
        legend.id = legend_id
        self.instance.send(
            legend_id, 
            'addLegend', 
            {'chart': self.id}
        )
        if options:
            legend.set_options(**options)            
        return legend           

    def add_textbox(
        self,
        text: str = None,
        x: int = None,
        y: int = None,
        position_scale: str = 'axis',
    ):
        """Add text box to the chart.

        Args:
            text (str): Text of the text box.
            x (int): X position in percentages (0-100).
            y (int): Y position in percentages (0-100).
            position_scale (str): "percentage" | "pixel" | "axis"

        Returns:
            Reference to Text Box class.
        """
        return TextBox(chart=self, text=text, x=x, y=y, position_scale=position_scale)

    textbox = add_textbox   


class TitleMethods(Chart):
    def set_title(self, title: str):
        """Set text of Chart title.

        Args:
            title (str): Chart title as a string.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitle', {'title': title})
        return self

    def hide_title(self):
        """Hide title and remove padding around it.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'hideTitle')
        return self

    def set_title_color(self, color: ColorInput | None):
        """Set color of Chart title.

        Args:
            color (Color): Color of the title. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTitleColor', {'color': color})
        return self

    def set_title_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of Chart title.

        Args:
            size (int | float): CSS font size. For example, 16.
            family (str): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str): CSS font weight. For example, 'bold'.
            style (str): CSS font style. For example, 'italic'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setTitleFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self
    def set_title_margin(self, *args, **kwargs: Unpack[PaddingKwargs]):
        """Specifies padding after chart title.

        Args:
            *args: A single numeric value (int or float) for uniform padding on all sides.
            **kwargs: Optional named arguments to specify padding for individual sides:
                - `left` (int or float): Padding for the left side.
                - `right` (int or float): Padding for the right side.
                - `top` (int or float): Padding for the top side.
                - `bottom` (int or float): Padding for the bottom side.

        Examples:
            - `set_title_margin(5)`: Sets uniform padding for all sides (integer or float).
            - `set_title_margin(left=10, top=15)`: Sets padding for specific sides only.
            - `set_title_margin(left=10, top=15, right=20, bottom=25)`: Fully define padding for all sides.

        Returns:
            The instance of the class for fluent interface.
        """
        if len(args) == 1 and isinstance(args[0], (int, float)):
            padding = args[0]
        elif kwargs:
            padding = {}
            for key in ['left', 'right', 'bottom', 'top']:
                if key in kwargs:
                    padding[key] = kwargs[key]
        else:
            raise ValueError(
                'Invalid arguments. Use one of the following formats:\n'
                '- set_padding(5): Uniform padding for all sides.\n'
                '- set_padding(left=10, top=15): Specify individual sides.\n'
                '- set_padding(left=10, top=15, right=20, bottom=25): Full padding definition.'
            )

        self.instance.send(self.id, 'setTitleMargin', {'margin': padding})
        return self

    def set_title_rotation(self, degrees: int | float):
        """Set rotation of Chart title.

        Args:
            degrees (int | float): Rotation in degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleRotation', {'value': degrees})
        return self

    def set_title_effect(self, enabled: bool = True):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleEffect', {'enabled': enabled})
        return self
    
    def get_title(self)-> str | None:
        """Get text of Chart title.

        Returns:
            The instance of the class for fluent interface.

        Notes:
            Call this in live mode, e.g. ``chart.open(live=True)``
        """
        return self.instance.get(self.id, 'getTitle', {})
         


class ChartWithXYAxis(Chart):
    def __init__(self):
        self.default_x_axis = DefaultAxis(self, 'x')
        self.default_y_axis = DefaultAxis(self, 'y')

    def get_default_x_axis(self) -> Axis:
        """Get the reference to the default x-axis of the chart.

        Returns:
            Reference to Axis class.
        """
        return self.default_x_axis

    def get_default_y_axis(self) -> Axis:
        """Get the reference to the default y-axis of the chart.

        Returns:
            Reference to Axis class.
        """
        return self.default_y_axis

    def synchronize_axis_intervals(self, axis_array: list[Axis]):
        """Convenience function for synchronizing the intervals of n amount of ´Axis´.

        Args:
            axis_array (list[Axis]): List of Axis to synchronize.

        Returns:
            The instance of the class for fluent interface.
        """
        axis_array = [axis.id for axis in axis_array]
        self.instance.send(self.id, 'synchronizeAxes', {'axes': axis_array})
        return self   

class ChartWithXYZAxis(Chart):
    def __init__(self):
        self.default_x_axis = DefaultAxis3D(self, 'x')
        self.default_y_axis = DefaultAxis3D(self, 'y')
        self.default_z_axis = DefaultAxis3D(self, 'z')

    def get_default_x_axis(self) -> DefaultAxis3D:
        """Get the reference to the default x-axis of the chart.

        Returns:
            Reference to Axis3D class.
        """
        return self.default_x_axis

    def get_default_y_axis(self) -> DefaultAxis3D:
        """Get the reference to the default y-axis of the chart.

        Returns:
            Reference to Axis3D class.
        """
        return self.default_y_axis

    def get_default_z_axis(self) -> DefaultAxis3D:
        """Get the reference to the default z-axis of the chart.

        Returns:
            Reference to Axis3D class.
        """
        return self.default_z_axis


class ChartWithSeries(Chart):
    def __init__(self, instance: Instance):
        Chart.__init__(self, instance)
        self.series_list = []
        self._auto_color_index_counter = 0

    def _resolve_auto_color_index(self, automatic_color_index: int | None):
        """Return the user-specified automatic_color_index or generate a new one."""
        if automatic_color_index is not None:
            return automatic_color_index
        idx = self._auto_color_index_counter
        self._auto_color_index_counter += 1
        return idx

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
        """Set the color of chart series background.

        Args:
            color (Color): Color of the series background. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSeriesBackgroundFillStyle', {'color': color})
        return self   
    
    def get_series_background_color(self) -> dict:
        """Get series-background color of the chart.

        Returns:
            dict with 'color' (uint32 RGBA), 'colorHex' (#rrggbbaa), 'colorRgb' (rgb/rgba).

        Notes:
            Call this in live mode, e.g. ``chart.open(live=True)``
        """
        return self.instance.get(self.id, 'getSeriesBackgroundColor', {})

    
    
    def set_series_background_stroke(self, thickness: int | float, color: ColorInput | None = None):
        """
        Set the stroke (border) of the Series Background (plot area).
        Use thickness=0 or color=None/'transparent' to hide it.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(
            self.id,
            'setSeriesBackgroundStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self
    
    def set_engine_background_color(self, color: ColorInput | None):
        """
        Set the background color of the chart's ENGINE (canvas behind the chart). Use 'transparent' or None to hide.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setEngineBackgroundFillStyle', {'color': color})
        return self



class ChartWithLUT(Chart):
    def set_lookup_table(
        self,
        steps: list[dict[str, any]],
        interpolate: bool = True,
        percentage_values: bool = False,
    ):
        """Attach lookup table (LUT) to fill the slices with Colors based on value.

        Args:
            steps (list[dict]): List of {"value": number, "color": Color, 'label': 'Label'} dictionaries.
            interpolate (bool): Whether color interpolation is used
            percentage_values (bool): Whether values represent percentages or explicit values.

        Returns:
            The instance of the class for fluent interface.
        """
        for i in steps:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(
            self.id,
            'setLUT',
            {
                'steps': steps,
                'interpolate': interpolate,
                'percentageValues': percentage_values,
            },
        )
        return self


class ChartWithLabelStyling(Chart):
    def set_label_formatter(self, formatter: str = 'NamePlusValue'):
        """Set formatter of Slice Labels.

        Args:
            formatter: "Name" | "NamePlusValue" | "NamePlusRelativeValue"

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelFormatter', {'formatter': formatter})
        return self

    def set_label_color(self, color: ColorInput | None):
        """Set the color of Slice Labels.

        Args:
            color (Color): Color of the labels. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setLabelColor', {'color': color})
        return self

    def set_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of Slice Labels.

        Args:
            size (int | float): CSS font size. For example, 16.
            family (str): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str): CSS font weight. For example, 'bold'.
            style (str): CSS font style. For example, 'italic'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_label_effect(self, enabled: bool):
        """Set theme effect enabled on label or disabled. A theme can specify an Effect to add extra visual
        oomph to chart applications, like Glow effects around data or other components.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelEffect', {'enabled': enabled})
        return self

    def set_slice_effect(self, enabled: bool):
        """Set theme effect enabled on slice or disabled. A theme can specify an Effect to add extra visual
        oomph to chart applications, like Glow effects around data or other components.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setSliceEffect', {'enabled': enabled})
        return self

    def set_slice_colors(self, color_list: list[any]):
        """Set the colors of all slices at once.

        Args:
            color_list (list[Color]): list of Colors. The length must match the current number of slices! Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        hex_array = []
        for color in color_list:
            hex_array.append(convert_color_to_hex(color))

        self.instance.send(self.id, 'setSliceFuncFillStyle', {'hexArray': hex_array})
        return self

    def set_slice_sorter(self, sorter: str):
        """Define the sorting logic for slices.

        Args:
            sorter (str): "name" | "valueAscending" | "valueDescending" | "none"

        Returns:
            The instance of the class for fluent interface.
        """
        slice_sorters = ('name', 'valueAscending', 'valueDescending', 'none')
        if sorter not in slice_sorters:
            raise ValueError(f"Expected sorter to be one of {slice_sorters}, but got '{sorter}'.")

        self.instance.send(self.id, 'setSliceSorter', {'sorter': sorter})
        return self    

    def set_label_connector_style(self, style: str, thickness: int | float, color: ColorInput | None = None):
        """Set style of Label connector lines.

        Args:
            style (str): "solid" | "dashed" | "empty"
            thickness (int | float): Thickness of the connector line.
            color (Color): Color of the connector line. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        styles = ('solid', 'dashed', 'empty')
        if style not in styles:
            raise ValueError(f"Expected sorter to be one of {styles}, but got '{style}'.")

        self.instance.send(
            self.id,
            'setLabelConnectorStyle',
            {'style': style, 'thickness': thickness, 'color': color},
        )
        return self
    def get_slice_color(self, category: str) -> dict:
        """Get the fill color of a slice (Pie / Funnel / Pyramid).

        Args:
            category: Slice name.

        Returns:
            dict with 'color', 'colorHex', 'colorRgb'.

        Notes:
            Call this in live mode, e.g. ``chart.open(live=True)``
        """
        return self.instance.get(self.id, 'getSliceFillStyle', {'category': category})


class BackgroundChartStyle(Chart):
    def set_chart_background_image(
        self,
        source: str,
        fit_mode: str = 'Stretch',
        surrounding_color=None,
        source_missing_color=None,
    ):
        """
        Set the chart background image.

        Args:
            source (str): The image source. This can be:
                - A URL (remote image).
                - A local file path.
                - An already Base64-encoded image string.
            fit_mode (str, optional): Fit mode for the image. Options:
                - "Stretch" (default)
                - "Fill"
                - "Fit"
                - "Tile"
                - "Center"
            surrounding_color (Color, optional): Color for areas outside the image.
            source_missing_color (Color, optional): Color when the image fails to load.

        Returns:
            self: The instance of the class for method chaining.

        Raises:
            ValueError: If the source is invalid.

        Example:
            >>> chart.set_chart_background_image("D:/path/to/local_image.png")
            >>> chart.set_chart_background_image("https://example.com/image.jpg")
        """

        if not source:
            raise ValueError('Image source is required.')
        if not source.startswith('data:'):
            source = convert_to_base64(source)

        args = {
            'source': source,
            'fitMode': fit_mode,
            'surroundingColor': convert_color_to_hex(surrounding_color) if surrounding_color else None,
            'sourceMissingColor': convert_color_to_hex(source_missing_color) if source_missing_color else None,
        }

        for fit_mode_option in ['Stretch', 'Fill', 'Fit', 'Tile', 'Center']:
            if fit_mode_option.lower() == fit_mode.lower():
                args['fitMode'] = fit_mode_option
                break

        self.instance.send(self.id, 'setChartBackgroundImage', args)
        return self

    def set_chart_background_video(
        self,
        video_source: str,
        fit_mode: str = 'fit',
        surrounding_color: ColorInput | None = None,
        source_missing_color: ColorInput | None = None
    ):
        """
        Sets the chart background to a video.

        Args:
            video_source (str): Path to the video file (MP4 or WEBM).
            fit_mode (str): Fit mode ('Fit', 'Stretch', 'Fill', 'Center', 'Tile').
            surrounding_color (Color, optional): Color for areas outside the video.
            source_missing_color (Color, optional): Color when video fails to load.

        Returns:
            The instance of the class for method chaining.

        Example:
            >>> chart.set_chart_background_video("D:/path/to/local_video.mp4")
            >>> chart.set_chart_background_video("https://example.com/video.mp4")
        """

        if not video_source:
            raise ValueError('Video source is required.')
        video_data_uri = convert_to_base64(video_source)

        surrounding_color = convert_color_to_hex(surrounding_color) if surrounding_color is not None else None
        source_missing_color = convert_color_to_hex(source_missing_color) if source_missing_color is not None else None

        args = {
            'videoSource': video_data_uri,
            'fitMode': fit_mode,
            'surroundingColor': surrounding_color if surrounding_color else None,
            'sourceMissingColor': source_missing_color if source_missing_color else None,
        }

        for fit_mode_option in ['Stretch', 'Fill', 'Fit', 'Tile', 'Center']:
            if fit_mode_option.lower() == fit_mode.lower():
                args['fitMode'] = fit_mode_option
                break
        self.instance.send(self.id, 'setChartBackgroundVideo', args)
        return self

    def set_series_background_image(
        self,
        source: str,
        fit_mode: str = 'Stretch',
        surrounding_color=None,
        source_missing_color=None,
    ):
        """
        Set the series background image.

        Args:
            source (str): The image source. This can be:
                - A URL (remote image).
                - A local file path.
                - An already Base64-encoded image string.
            fit_mode (str, optional): Fit mode for the image. Options:
                - "Stretch" (default)
                - "Fill"
                - "Fit"
                - "Tile"
                - "Center"
            surrounding_color (Color, optional): Color for areas outside the image.
            source_missing_color (Color, optional): Color when the image fails to load.

        Returns:
            self: The instance of the class for method chaining.

        Raises:
            ValueError: If the source is invalid.

        Example:
            >>> chart.set_series_background_image("D:/path/to/local_image.png")
            >>> chart.set_series_background_image("https://example.com/image.jpg")
        """
        if not source:
            raise ValueError('Image source is required.')
        if not source.startswith('data:'):
            source = convert_to_base64(source)

        args = {
            'source': source,
            'fitMode': fit_mode,
            'surroundingColor': convert_color_to_hex(surrounding_color) if surrounding_color else None,
            'sourceMissingColor': convert_color_to_hex(source_missing_color) if source_missing_color else None,
        }

        for fit_mode_option in ['Stretch', 'Fill', 'Fit', 'Tile', 'Center']:
            if fit_mode_option.lower() == fit_mode.lower():
                args['fitMode'] = fit_mode_option
                break  
        self.instance.send(self.id, 'setSeriesBackgroundImage', args)
        return self

    def set_series_background_video(
        self,
        video_source: str,
        fit_mode: str = 'fit',
        surrounding_color: ColorInput | None = None,
        source_missing_color: ColorInput | None = None,
    ):
        """
        Sets the series background to a video.

        Args:
            video_source (str): Path to the video file (MP4 or WEBM).
            fit_mode (str): Fit mode ('Fit', 'Stretch', 'Fill', 'Center', 'Tile').
            surrounding_color (Color, optional): Color for areas outside the video.
            source_missing_color (Color, optional): Color when video fails to load.

        Returns:
            The instance of the class for method chaining.

        Example:
            >>> chart.set_series_background_video("D:/path/to/local_video.mp4")
            >>> chart.set_series_background_video("https://example.com/video.mp4")
        """
        if not video_source:
            raise ValueError('Video source is required.')
        video_data_uri = convert_to_base64(video_source)

        surrounding_color = convert_color_to_hex(surrounding_color) if surrounding_color is not None else None
        source_missing_color = convert_color_to_hex(source_missing_color) if source_missing_color is not None else None

        args = {
            'videoSource': video_data_uri,
            'fitMode': fit_mode,
            'surroundingColor': surrounding_color if surrounding_color else None,
            'sourceMissingColor': source_missing_color if source_missing_color else None,
        }
        for fit_mode_option in ['Stretch', 'Fill', 'Fit', 'Tile', 'Center']:
            if fit_mode_option.lower() == fit_mode.lower():
                args['fitMode'] = fit_mode_option
                break
        self.instance.send(self.id, 'setSeriesBackgroundVideo', args)
        return self
    

class FunnelPyramidLabelConnectorMethods:
    def set_label_connector_gap_before_label(self, gap: int | float):
        """Set gap before label in label connector.
        
        Args:
            gap (int | float): Gap in pixels.
            
        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelConnectorGapBeforeLabel', {'gap': gap})
        return self

    def set_label_connector_gap_before_slice(self, gap: int | float):
        """Set gap before slice in label connector.
        
        Args:
            gap (int | float): Gap in pixels.
            
        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelConnectorGapBeforeSlice', {'gap': gap})
        return self

    def set_label_connector_length_after_slice(self, length: int | float):
        """Set length after slice in label connector.
        
        Args:
            length (int | float): Length in pixels.
            
        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelConnectorLengthAfterSlice', {'length': length})
        return self

    def set_label_connector_min_length_before_slice(self, length: int | float):
        """Set minimum length before slice in label connector.
        
        Args:
            length (int | float): Minimum length in pixels.
            
        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelConnectorMinLengthBeforeSlice', {'length': length})
        return self

class ChartsWithCoordinateTransforms:
    def translate_coordinate(self, coordinate: dict, target: str, source: str = None):
        """Translate coordinates between client (browser) and relative (component) systems.
        
        Args:
            coordinate: Dict with 'x'/'y' (relative) or 'clientX'/'clientY' (client)
            target: 'relative' | 'client'
            source: 'relative' | 'client' (auto-detected if None)

        Returns:
            Dict with translated coordinates
    
    Examples:
        >>> # Client to relative (source auto-detected)
        >>> loc = chart.translate_coordinate({'clientX': 500, 'clientY': 300}, target='relative')
        >>> print(f"Relative: x={loc['x']}, y={loc['y']}")
        
        >>> # Relative to client
        >>> loc = dashboard.translate_coordinate({'x': 400, 'y': 250}, target='client', source='relative')
        >>> print(f"Client: x={loc['clientX']}, y={loc['clientY']}")
        """
        if source is None:
            source = 'client' if 'clientX' in coordinate else 'relative'
        
        return self.instance.get(self.id, 'translateCoordinateGeneral', {
            'coordinate': coordinate,
            'source': source,
            'target': target
        })
    
class ChartsWithAddEventListener:
    def add_event_listener(
        self,
        event: str,
        handler: callable | None = None,
        xy_chart=None,
        throttle_ms: int = 0,
        once: bool = False,
        target: str = 'auto',       
    ) -> str:
        """
        Add event and (optionally) bind a ChartXY overlay to stay
        in sync with a Map/Bar view.

        Args:
            event : str
                Event name emitted by the target. Common options include:
                - Interaction: 'click', 'pointermove', 'pointerdown', 'pointerup',
                'pointerenter', 'pointerleave', 'dblclick'
                - Cursor: 'cursortargetchange' (reports cursor hits / mouse location)
                - Lifecycle/Layout: 'ready', 'layoutchange'
                - Map/Bar view: 'viewchange' (latitude/longitude + margins)
            handler : Python callback receiving event data
            xy_chart : ChartXY | None, keyword-only
                When `event == 'viewchange'`, pass a `ChartXY` here to keep its axes
                and padding bound to the Map/Bar view. Ignored for other events.
            throttle_ms : Minimum delay between callbacks in milliseconds
            once : bool, default False, keyword-only
                If True, listener removes itself after first trigger
            target : {'auto','seriesBackground','background','title','axisXTitle','axisYTitle','chart'}, default 'auto'
                Which LCJS element to attach to:
                - 'auto'            : For mouse/pointer events, uses plot area
                                    (`seriesBackground`) if available, otherwise the chart.
                - 'seriesBackground': Plot area (inside axes) — best for data-space clicks/moves.
                - 'background'      : Chart background (outside axes).
                - 'title'           : Chart title element.
                - 'axisXTitle'      : X-axis title element.
                - 'axisYTitle'      : Y-axis title element.
                - 'axisZTitle'      : Z-axis title element (3D charts only).
                - 'chart'           : Chart object itself (e.g., 'layoutchange', 'ready',
                                    or chart-level cursor events).

        Returns:        
            `callback_id` that identifies the registered handler (empty string if
            no `handler` was supplied).

        Examples:        
            # 1) Clicks in the plot area of a ChartXY
            >>> def on_click(ev): print('[click]', ev)
            >>> xy.add_event_listener('click', handler=on_click, target='seriesBackground')

            # 2) Keep an overlayed XY chart glued to a Map view (pan/zoom/resize)
            >>> map_chart.add_event_listener('viewchange', xy_chart=xy_overlay)

            # 3) Listen cursor hits (hover) at chart level
            >>> def on_cursor(ev): print(ev.get('hits'))
            >>> xy.add_event_listener('cursortargetchange', handler=on_cursor, target='chart', throttle_ms=50)

            # 4) Run code when a chart signals it is ready
            >>> def on_ready(_): print('chart ready')
            >>> map_chart.add_event_listener('ready', handler=on_ready, target='chart')
        """       
        callback_id = str(uuid.uuid4()).split('-')[0] if handler else ''
        if handler is not None:
            self.instance.event_handlers[callback_id] = handler

        self.instance.send(self.id, 'addEventListener', {
            'event': event,
            'callbackId': callback_id or None,
            'xyId': getattr(xy_chart, 'id', None),
            'throttleMs': int(throttle_ms) if throttle_ms else 0,
            'options': {'once': bool(once)},
            'target': target,                 
        })
        return callback_id

class ChartsWithCursorMode:
    def set_cursor_mode(self, mode: str):
        """Set chart Cursor behavior.

        Args:
            mode (str): "disabled" | "show-all" | "show-all-interpolated" | "show-nearest" |
                "show-nearest-interpolated" | "show-pointed" | "show-pointed-interpolated"

        Returns:
            The instance of the class for fluent interface.
        """
        cursor_modes = (
            'disabled',
            'show-all',
            'show-all-interpolated',
            'show-nearest',
            'show-nearest-interpolated',
            'show-pointed',
            'show-pointed-interpolated',
        )
        if mode not in cursor_modes:
            raise ValueError(f"Expected mode to be one of {cursor_modes}, but got '{mode}'.")

        self.instance.send(self.id, 'setCursorMode', {'mode': mode})
        return self
