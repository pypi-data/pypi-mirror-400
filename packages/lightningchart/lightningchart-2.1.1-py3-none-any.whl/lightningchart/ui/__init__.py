from __future__ import annotations
from typing import Unpack
import uuid

from lightningchart.utils.utils import PaddingKwargs


class UIElement:
    def __init__(self, chart):
        self.chart = chart
        self.instance = chart.instance
        self.id = str(uuid.uuid4()).split('-')[0]

    def dispose(self):
        """Permanently destroy the component.

        Returns:
            True
        """
        self.instance.send(self.id, 'dispose')
        return True

    def set_visible(self, visible: bool = True):
        """Set element visibility.

        Args:
            visible (bool): True when element should be visible and false when element should be hidden.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self


class UIEWithPosition(UIElement):
    def set_position(self, x: int | float, y: int | float):
        """Sets the position of this UiElement relative to its origin

        Args:
            x (int): Location in X-dimension.
            y (int): Location in Y-dimension.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setPosition', {'x': x, 'y': y})
        return self

    def set_origin(self, origin: str):
        """Sets the position of this UiElement relative to its origin.

        Args:
            origin (str): "Center" | "CenterBottom" | "CenterTop" | "LeftBottom" | "LeftCenter" |
                "LeftTop" | "RightBottom" | "RightCenter" | "RightTop"

        Returns:
            The instance of the class for fluent interface.
        """
        origins = (
            'Center',
            'CenterBottom',
            'CenterTop',
            'LeftBottom',
            'LeftCenter',
            'LeftTop',
            'RightBottom',
            'RightCenter',
            'RightTop',
        )
        if origin not in origins:
            raise ValueError(f"Expected origin to be one of {origins}, but got '{origin}'.")

        self.instance.send(self.id, 'setOrigin', {'origin': origin})
        return self

    def set_margin(self, *args, **kwargs: Unpack[PaddingKwargs]):
        """Set margin around the object in pixels.

        Usage:
            - `set_margin(5)`: Sets uniform margin for all sides (integer or float).
            - `set_margin(left=10, top=15)`: Sets margin for specific sides only.
            - `set_margin(left=10, top=15, right=20, bottom=25)`: Fully define margin for all sides.

        Args:
            *args: A single numeric value (int or float) for uniform margin on all sides.
            **kwargs: Optional named arguments to specify margin for individual sides:
                - `left` (int or float): Margin for the left side.
                - `right` (int or float): Margin for the right side.
                - `top` (int or float): Margin for the top side.
                - `bottom` (int or float): Margin for the bottom side.

        Returns:
            The instance of the class for fluent interface.
        """
        if len(args) == 1 and isinstance(args[0], (int, float)):
            margin = args[0]
        elif kwargs:
            margin = {}
            for key in ['left', 'right', 'bottom', 'top']:
                if key in kwargs:
                    margin[key] = kwargs[key]
        else:
            raise ValueError(
                'Invalid arguments. Use one of the following formats:\n'
                '- set_margin(5): Uniform margin for all sides.\n'
                '- set_margin(left=10, top=15): Specify individual sides.\n'
                '- set_margin(left=10, top=15, right=20, bottom=25): Full margin definition.'
            )

        self.instance.send(self.id, 'setMargin', {'margin': margin})
        return self
    
class UIEWithTitle(UIElement):
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

    def set_title_rotation(self, degrees: int | float):
        """Set rotation of Chart title.

        Args:
            degrees (int | float): Rotation in degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleRotation', {'value': degrees})
        return self


class UIEWithHighlight(UIElement):
    def set_highlight(self, highlight: bool | int | float):
        """Set state of component highlighting.

        Args:
            highlight (bool | int | float): Boolean or number between 0 and 1, where 1 is fully highlighted.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setHighlight', {'highlight': highlight})
        return self

    def set_highlight_on_hover(self, enabled: bool):
        """Set highlight on mouse hover enabled or disabled.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setHighlightOnHover', {'enabled': enabled})
        return self


class UserInteractions:
    """Mixin class providing user interactions functionality."""

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions
        """
        if interactions is None:
            self.instance.send(self.id, 'setUserInteractions', {})
        elif interactions is ... or not interactions:
            self.instance.send(self.id, 'setUserInteractions', {'config': {}})
        else:
            self.instance.send(self.id, 'setUserInteractions', {'config': interactions})
        return self
    
class UIElementsWithAutoDispose:
    def set_auto_dispose(
        self,
        mode: str,
        threshold: float,
    ):
        """
        Auto-dispose this element when it exceeds a viewport threshold.

        Args:
            mode: "max-width" or "max-height"
            threshold: Fraction of viewport (0–1) at which to dispose.
        """
        if mode not in ('max-width', 'max-height'):
            raise ValueError("mode must be 'max-width' or 'max-height'")
        
        if mode == 'max-width':
            auto_dispose_mode = {'type': 'max-width', 'maxWidth': threshold}
        else:
            auto_dispose_mode = {'type': 'max-height', 'maxHeight': threshold}
        
        self.instance.send(self.id, 'setAutoDispose', {'autoDisposeMode': auto_dispose_mode})
        return self
    
    def set_dragging_mode(self, mode: str):
        """
        Set dragging mode for this UI element.

        Args:
            mode: "draggable", "notDraggable", "onlyHorizontal", or "onlyVertical"
        """
        valid_modes = ('draggable', 'notDraggable', 'onlyHorizontal', 'onlyVertical')
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}")
        
        self.instance.send(self.id, 'setDraggingMode', {'draggingMode': mode})
        return self