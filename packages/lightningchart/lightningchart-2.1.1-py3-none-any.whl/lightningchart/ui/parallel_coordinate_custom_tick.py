from lightningchart.ui import UIElement
from lightningchart.ui.axis import GetCustomTicks
from lightningchart.utils import convert_color_to_hex
from lightningchart.utils.utils import ColorInput


class ParallelCoordinateCustomTick(UIElement, GetCustomTicks):
    def __init__(self, chart, axis):
        UIElement.__init__(self, chart)
        self.instance.send(self.id, 'addParallelCustomTick', {'axis': axis.id})

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
        self.instance.send(self.id, 'setTextFormatter', {'text': str(text)})
        return self

    def set_text_fill_style(self, color: ColorInput | None):
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

    def set_text_padding(self, padding: int | float):
        """Set padding between CustomTick tickline and text.

        Args:
            padding (int | float): Padding as pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTextPadding', {'padding': padding})
        return self

    def set_text_rotation(self, value: int | float):
        """Set custom tick text rotation as degrees.

        Args:
            value (int | float): Rotation as degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTextRotation', {'rotation': value})
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

    def set_tick_style(self, thickness: int | float, color: ColorInput | None = None):
        """Set style of custom ticks tickline.

        Args:
            thickness (int | float): Thickness of the stroke.
            color: Color of the stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(
            self.id,
            'setTickStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_label_alignment(self, alignment: int | float):
        """Set alignment of Label respective to tick line.
        
        Values: -1 (after), 0 (center), +1 (before)

        Args:
            alignment (int | float): Label alignment [-1, 1].

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelAlignment', {'alignment': alignment})
        return self

    def set_visible(self, visible: bool):
        """Set element visibility.

        Args:
            visible (bool): True when element should be visible and false when hidden.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self

    def dispose(self):
        """Permanently destroy the custom tick.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'dispose')
        return self
    
