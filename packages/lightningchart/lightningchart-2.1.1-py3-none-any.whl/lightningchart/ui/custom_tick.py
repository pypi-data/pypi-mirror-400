from __future__ import annotations
from typing import Unpack

from lightningchart.ui import UIElement
from lightningchart.utils import convert_color_to_hex
from lightningchart.utils.utils import PaddingKwargs


class CustomTick(UIElement):
    def __init__(self, chart, axis, tick_type: str = 'major'):
        UIElement.__init__(self, chart)
        self.instance.send(self.id, 'addCustomTick', {'axis': axis.id, 'tickType': tick_type})

    def set_value(self, value: int | float):
        """Sets the position of this custom tick on its Axis.

        Args:
            value (int | float): Value in the units of main scale.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValue', {'value': value})
        return self

    def set_text(self, text: str):
        """Override the tick label text

        Args:
            text (str): Text to display on the tick.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTextFormatterText', {'text': str(text)})
        return self

    def set_decimal_precision(self, decimals: int):
        """Format the tick label value to certain number of decimal numbers.

        Args:
            decimals (int): Decimal precision.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTextFormatterRound', {'decimals': decimals})
        return self

    def set_allocates_axis_space(self, enabled: bool):
        """Set whether CustomTick should allocate space on its Axis.
        By default, this is true, which means that Axis will always make sure it is big enough to fit the tick.
        By setting to false, this particular CustomTick can be removed from this behaviour,
        which can be useful in applications where some custom ticks are only enabled temporarily.
        Disabling this functionality can prevent the size of the Axis from changing in unwanted ways.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAllocatesAxisSpace', {'enabled': enabled})
        return self

    def set_grid_stroke_length(self, length: int | float):
        """Set length of grid stroke in percents.

        Args:
            length (int | float): Grid line length as a % of viewport size.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setGridStrokeLength', {'length': length})
        return self

    def set_grid_stroke_style(self, thickness: int | float, color: any = None):
        """Set style of grid stroke.

        Args:
            thickness (int | float): Thickness of the grid stroke.
            color (Color): Color of the grid stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setGridStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_marker_color(self, color: any):
        """Set the color of the tick label.

        Args:
            color (Color): Color of the tick label. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setMarkerColor', {'color': color})
        return self

    def set_marker_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of tick label.

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
            'setMarkerFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_marker_visible(self, visible: bool):
        """Set marker visible or not.

        Args:
            visible (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setMarkerVisible', {'visible': visible})
        return self

    def set_tick_label_padding(self, padding: int | float):
        """Set pixel padding between tick line and label.

        Args:
            padding (int | float): Amount of padding in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickLabelPadding', {'padding': padding})
        return self

    def set_tick_label_rotation(self, value: int | float):
        """Set rotation of tick label.

        Args:
            value (int | float): Rotation in degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickLabelRotation', {'value': value})
        return self

    def set_tick_length(self, length: int | float):
        """Set tick length as pixels.

        Args:
            length (int | float): Tick length as pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickLength', {'length': length})
        return self
    
    def set_tick_label_alignment(
        self,
        alignment: float,
        alignment2: float = None,
    ):
        """Set alignment of tick label relative to tick line.
        
        Args:
            alignment: Primary label alignment (-1 to 1)
                -1: After tick line
                0: Center on tick line
                +1: Before tick line
            alignment2: Secondary alignment for XY axes only (-1 to 1)
                Controls alignment along perpendicular dimension
                
        Returns:
            The instance of the class for fluent interface.
            
        Examples:
            Align labels after tick (default for most axes):
            >>> custom_tick.set_tick_label_alignment(-1)
            
            Center labels on tick line:
            >>> custom_tick.set_tick_label_alignment(0)
            
            XY axis with both alignments:
            >>> custom_tick.set_tick_label_alignment(
            ...     alignment=-1,    # Primary dimension
            ...     alignment2=0.5   # Secondary dimension
            ... )
            
            Fine-tune alignment:
            >>> custom_tick.set_tick_label_alignment(-0.8)  # Slightly offset
        """
        params = {'alignment': alignment}
        if alignment2 is not None:
            params['alignment2'] = alignment2
            
        self.instance.send(self.id, 'setTickLabelAlignment', params)
        return self


class CustomTick3D(UIElement):
    def __init__(self, chart, axis, tick_type: str = 'major'):
        UIElement.__init__(self, chart)
        self.instance.send(self.id, 'addCustomTick', {'axis': axis.id, 'tickType': tick_type})

    def set_value(self, value: int | float):
        """Set location of custom tick on its Axis.

        Args:
            value: Location on axis.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValue', {'value': value})
        return self

    def set_text(self, text: str):
        """Override the tick label text

        Args:
            text (str): Text to display on the tick.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTextFormatterText', {'text': str(text)})
        return self

    def set_background_color(self, color: any):
        """Set the background color of the tick.

        Args:
            color: Color value. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBackgroundFillStyle', {'color': color})
        return self

    def set_background_stroke(self, thickness: int | float, color: any = None):
        """Set stroke style of background around ticks label.

        Args:
            thickness: Thickness of the stroke.
            color: Color of the stroke. Use 'transparent' or None to hide.

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

    def set_grid_stroke(self, thickness: int | float, color: any = None):
        """Set style of custom ticks grid line. This line highlights the tick location under the series area.

        Args:
            thickness: Thickness of the stroke.
            color: Color of the stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setGridStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_text_color(self, color: any):
        """Set fill style of custom ticks text.

        Args:
            color: Color value. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTextFillStyle', {'color': color})
        return self

    def set_text_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of custom ticks text.

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
            'setTextFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_tick_length(self, length: int | float):
        """Set tick line length as pixels.

        Args:
            length: Tick line length as pixels

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickLength', {'length': length})
        return self

    def set_tick_style(self, thickness: int | float, color: any = None):
        """Set style of custom ticks tick line.
        This line connects the text to its Axis, generally a very short line (6 pixels, or so).

        Args:
            thickness: Thickness of the stroke.
            color: Color of the stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setTickStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_padding(self, *args, **kwargs: Unpack[PaddingKwargs]):
        """Set padding between tick label text and its background (if any).

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
