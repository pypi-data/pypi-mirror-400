from __future__ import annotations

from typing import Optional, Unpack
import uuid

from lightningchart.series import ComponentWithLinePaletteColoring
from lightningchart.ui import UIEWithTitle, UIElement, UserInteractions
from lightningchart.ui.band import Band
from lightningchart.ui.constant_line import ConstantLine
from lightningchart.ui.custom_tick import CustomTick
from lightningchart.ui.custom_tick import CustomTick3D
from lightningchart.utils import convert_color_to_hex
from lightningchart.utils.utils import LegendOptions, PaddingKwargs


class GenericAxis(UIEWithTitle):
    def __init__(self, chart):
        UIElement.__init__(self, chart)

    def set_title(self, title: str):
        """Specifies an Axis title string

        Args:
            title: Axis title as a string

        Returns:
            Axis itself for fluent interface
        """
        self.instance.send(self.id, 'setTitle', {'title': title})
        return self

    def set_title_color(self, color: any):
        """Set the color of the Chart title.

        Args:
            color (Color): Color of the title. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTitleColor', {'color': color})
        return self

    def set_title_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleEffect', {'enabled': enabled})
        return self

    def set_visible(self, visible: bool = True):
        """Set element visibility.

        Args:
            visible (bool): True when element should be visible and false when element should be hidden.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self

    def set_scroll_strategy(
        self,
        strategy: str = 'scrolling',
        progressive: bool = None,
        realtime: bool | float = None,
        start: bool = None,
        end: bool = None,
        visibleonly: bool = None,
    ):
        """Specify ScrollStrategy of the Axis.
        
        Args:
            strategy (str):
                - "expansion": expand to fit new data without moving view
                - "fitting": resize to fit all data
                - "scrolling" (default): scroll with incoming data
                - "fittingStepped" resize to fit data in larger steps
            progressive (bool, optional): Whether axis should scroll towards higher data value, or lower data value.
            realtime (bool, optional): If set to true axis will automatically scroll according to real time, rather than jumping to latest data point immediately. This is intended for applications where data arrives in chunks (for example, every 1 second). This assumes that Axis interval represents milliseconds!
            start (bool, optional): Whether should affect Axis interval start (left side for X axis, bottom side for Y axis). 
            end (bool, optional): Whether should affect Axis interval end (right side for X axis, top side for Y axis). 
            visibleonly (bool, optional): Whether axis scrolling should only consider data in visible range, rather than entire data set which may be partly outside the view.
        """
        strategies = ('expansion', 'fitting', 'fittingStepped', 'scrolling')
        
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        options = {}
        if start is not None:
            options['start'] = bool(start)
        if end is not None:
            options['end'] = bool(end)
        if visibleonly is not None:
            options['considerVisibleRangeOnly'] = bool(visibleonly)
        if progressive is not None:
            options['progressive'] = bool(progressive)
        if realtime is not None:
            if isinstance(realtime, dict):
                options['realTime'] = realtime
            else:
                options['realTime'] = bool(realtime)

        self.instance.send(self.chart.id, 'setScrollStrategy', {
            'strategy': strategy, 
            'options': options, 
            'axis': self.id
        })
        return self

    def set_interval(
        self,
        start: int | float,
        end: int | float,
        stop_axis_after: bool = True,
        animate: bool = False,
    ):
        """Set axis interval.

        Args:
            start (int): Start of the axis.
            end (int): End of the axis.
            stop_axis_after (bool): If false, the axis won't stop from scrolling.
            animate (bool): Boolean for animation enabled, or number for animation duration in milliseconds.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.chart.id,
            'setAxisInterval',
            {
                'start': start,
                'end': end,
                'axis': self.id,
                'stopAxisAfter': stop_axis_after,
                'animate': animate,
            },
        )
        return self

    def fit(self, animate: int | bool = 0, stop_axis_after: bool = False):
        """Fit axis view to attached series.

        Args:
            animate (int | bool): Boolean for animation enabled, or number for animation duration in milliseconds.
            stop_axis_after (bool): If true, stops Axis after fitting.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'fit', {'animate': animate, 'stopAxisAfter': stop_axis_after})
        return self

    def set_animations_enabled(self, enabled: bool = True):
        """Disable/Enable all animations of the Chart.

        Args:
            enabled (bool): Boolean value to enable or disable animations.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationsEnabled', {'enabled': enabled})
        return self

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set the Axis line stroke.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self
    
    def set_default_interval(
        self,
        start: int | float = None,
        end: int | float = None,
        stop_axis_after: bool = None,
        animate: bool | int = None,
        apply_immediately: bool = None,
        skip_interval_restrictions: bool = None,
    ):
        """Set Axis default interval.

        This does the same as set_interval method, but is also applied again whenever
        fit is triggered, or the "zoom to fit" user interaction is triggered.

        Args:
            start (int | float, optional): Interval start point.
            end (int | float, optional): Interval end point.
            stop_axis_after (bool, optional): Whether to stop axis scrolling after applying interval. Defaults to True.
            animate (bool | int, optional): Animation setting. False for no animation, True for default,
                or milliseconds as int.
            apply_immediately (bool, optional): If False, don't apply the interval immediately,
                only on next fit/restore. Defaults to True.
            skip_interval_restrictions (bool, optional): If False, respect interval restrictions.
                Defaults to True (skip restrictions).

        Returns:
            The instance of the class for fluent interface.

        Examples:
            Set default interval with start and end:

            >>> axis.set_default_interval(start=0, end=100)

            Set only end value:

            >>> axis.set_default_interval(end=5000)

            Set interval with animation:

            >>> axis.set_default_interval(start=0, end=5000, animate=2000)

            Configure default interval without applying immediately:

            >>> axis.set_default_interval(start=0, end=10, apply_immediately=False)

            Respect interval restrictions:

            >>> axis.set_default_interval(start=0, end=10, skip_interval_restrictions=False)
        """
        interval = {}
        if start is not None:
            interval['start'] = start
        if end is not None:
            interval['end'] = end
        if stop_axis_after is not None:
            interval['stopAxisAfter'] = stop_axis_after
        if animate is not None:
            interval['animate'] = animate

        opts = {}
        if apply_immediately is not None:
            opts['applyImmediately'] = apply_immediately
        if skip_interval_restrictions is not None:
            opts['skipIntervalRestrictions'] = skip_interval_restrictions

        self.instance.send(
            self.id,
            'setDefaultInterval',
            {'interval': interval if interval else None, 'opts': opts if opts else None},
        )
        return self

    def set_interval_restrictions(
        self,
        interval_min: int | float = None,
        interval_max: int | float = None,
        start_min: int | float = None,
        start_max: int | float = None,
        end_min: int | float = None,
        end_max: int | float = None,
    ):
        """Set or clear restrictions on Axis interval (start/end).

        These restrictions are not applied immediately but will affect all axis scrolling
        and user interactions afterward.

        Args:
            interval_min (int | float, optional): Minimum interval length.
            interval_max (int | float, optional): Maximum interval length.
            start_min (int | float, optional): Minimum interval start value.
            start_max (int | float, optional): Maximum interval start value.
            end_min (int | float, optional): Minimum interval end value.
            end_max (int | float, optional): Maximum interval end value.

        Usage:
            - `axis.set_interval_restrictions(interval_min=10, interval_max=1000)`
            - `axis.set_interval_restrictions(start_min=0, end_max=5000)`
            - `axis.set_interval_restrictions(None)`  # Clears all restrictions

        Returns:
            The instance of the class for fluent interface.
        """

        if all(
            v is None
            for v in [
                interval_min,
                interval_max,
                start_min,
                start_max,
                end_min,
                end_max,
            ]
        ):
            self.instance.send(self.id, 'setIntervalRestrictions', None)
            return self

        self.instance.send(
            self.id,
            'setIntervalRestrictions',
            {
                'endMax': end_max,
                'endMin': end_min,
                'intervalMax': interval_max,
                'intervalMin': interval_min,
                'startMax': start_max,
                'startMin': start_min,
            },
        )
        return self   

    def set_units(
        self,
        unit: str | None,
        display_on_axis: bool = None,
        display_in_cursor: bool = None,
    ):
        """Set unit that axis measures (e.g., 'Hz', '°C').

        Args:
            unit (str | None): Unit string, or None to clear.
            display_on_axis (bool, optional): Show unit after axis title. Defaults to True.
            display_in_cursor (bool, optional): Show unit in cursor formatters. Defaults to True.

        Returns:
            The instance of the class for fluent interface.

        Examples:
            >>> axis.set_title("Frequency").set_units("Hz")
            >>> axis.set_units("Hz", display_on_axis=False)
        """
        behavior = {}
        if display_on_axis is not None:
            behavior['displayOnAxis'] = display_on_axis
        if display_in_cursor is not None:
            behavior['displayInCursor'] = display_in_cursor

        self.instance.send(self.id, 'setAxisUnits', {
            'unit': unit,
            'behavior': behavior if behavior else None
        })
        return self 
    
    def set_scroll_margins(self, *args, **kwargs):
        """Set scroll margins for the axis.

        Args:
            *args:
                - Single int or float: symmetric scroll margins in pixels.
                - Single bool: if False, disables scroll margins.
                - Single None: clears all scroll margins.
            **kwargs:
                start (int | float, optional): Start margin in pixels.
                end (int | float, optional): End margin in pixels.

        Notes:
            If the axis interval is explicitly configured using
            ``set_interval()`` or ``set_default_interval()``, scroll
            margins are not applied.
        
        Returns:
            The instance of the class for fluent interface.

        Example:
            >>> axis.set_scroll_margins(5)  # Sets symmetric scroll margins as 5 pixels.
            >>> axis.set_scroll_margins(False)  # Disables scroll margins entirely.
            >>> axis.set_scroll_margins(start = 0, end = 10})  # Sets asymmetric scroll margins.
        """
        if args:
            margins = {'arg': args[0]}
            if margins['arg'] is None:
                margins = {}
        elif 'start' in kwargs or 'end' in kwargs:
            margins = {'arg': {'start': kwargs.get('start', 0), 'end': kwargs.get('end', 0)}}

        else:
            raise ValueError("Expected either a valid positional argument or 'start', 'end' as keyword arguments")

        self.instance.send(self.id, 'setScrollMargins', margins)
        return self
    

class GetCustomTicks:
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


class AxisGetMethods:
    def get_interval(self) -> dict:
        """Get the currently applied axis scale interval.

        Returns:
            dict: Object containing the current start and end of Axis with keys:
                - start (float): The start value of the axis interval
                - end (float): The end value of the axis interval

        Examples:
            Get current axis interval:
            >>> interval = axis.get_interval()
            >>> print(f"Start: {interval['start']}, End: {interval['end']}")
        """
        return self.instance.get(self.id, 'getInterval', {})

    def get_default_interval(self) -> dict | None:
        """Get current configuration of default interval (set_default_interval).

        Returns the current default interval configuration, or None if not set.
        When a dynamic interval function was configured on the JS side, returns
        a dict with type='function' indicating a function is configured.

        Returns:
            dict | None: Interval configuration with optional keys:
                - start (float, optional): Interval start value
                - end (float, optional): Interval end value
                - animate (bool | int, optional): Animation setting
                - stopAxisAfter (bool, optional): Whether to stop axis after interval is applied

                Returns None if no default interval is configured.
                Returns {'type': 'function', 'description': '...'} if a dynamic function is configured.

        Examples:
            Get current default interval configuration:

            >>> config = axis.get_default_interval()
            >>> print(f"Default interval: {config.get('start')} to {config.get('end')}")
        """
        return self.instance.get(self.id, 'getDefaultInterval', {})
    
    def get_interval_restrictions(self) -> dict | None:
        """Get current interval restrictions configuration.

        Returns:
            dict | None: Restrictions configuration with optional keys:
                - intervalMin (float, optional): Minimum interval length
                - intervalMax (float, optional): Maximum interval length
                - startMin (float, optional): Minimum interval start value
                - startMax (float, optional): Maximum interval start value
                - endMin (float, optional): Minimum interval end value
                - endMax (float, optional): Maximum interval end value

                Returns None if no restrictions are configured.

        Examples:
            >>> restrictions = axis.get_interval_restrictions()
            >>> if restrictions:
            ...     print(f"Interval min: {restrictions.get('intervalMin')}")
        """
        return self.instance.get(self.id, 'getIntervalRestrictions', {})
    
    def get_keep_tick_labels_in_axis_bounds(self) -> bool:
        """Check whether axis keeps tick labels within its boundaries.

        Returns:
            bool: True if tick labels are kept in bounds, False otherwise.

        Examples:
            >>> is_enabled = axis.get_keep_tick_labels_in_axis_bounds()
            >>> print(f"Keep labels in bounds: {is_enabled}")
        """
        return self.instance.get(self.id, 'getKeepTickLabelsInAxisBounds', {})
    
    def get_margin_after_title(self) -> float:
        """Get padding after Axis title.

        Returns:
            float: Gap between the title and the next axis in pixels.

        Examples:
            >>> margin = axis.get_margin_after_title()
        """
        return self.instance.get(self.id, 'getMarginAfterTitle', {})

    def get_margin_after_ticks(self) -> float:
        """Get padding after axis ticks.

        Returns:
            float: Padding after axis ticks in pixels.

        Examples:
            >>> margin = axis.get_margin_after_ticks()
        """
        return self.instance.get(self.id, 'getMarginAfterTicks', {})

    def get_length(self) -> dict:
        """Get relative or absolute size of axis in its own stack.

        For example, if you have a chart with 2 stacked Y axes, by default they
        will have equal heights. By altering axis relative size, you can adjust
        how the chart height is distributed between these two axes.

        Returns:
            dict: Either {'pixels': number} or {'relative': number}.
                Defaults to {'relative': 1}.

        Examples:
            >>> length = axis.get_length()
            >>> if 'relative' in length:
            ...     print(f"Relative size: {length['relative']}")
            >>> elif 'pixels' in length:
            ...     print(f"Pixel size: {length['pixels']}")
        """
        return self.instance.get(self.id, 'getLength', {})

    def get_margins(self) -> dict:
        """Get axis margins as set with set_margins.

        Returns:
            dict: Object with keys:
                - start (float): Start margin
                - end (float): End margin

        Examples:
            >>> margins = axis.get_margins()
            >>> print(f"Start: {margins['start']}, End: {margins['end']}")
        """
        return self.instance.get(self.id, 'getMargins', {})

    def get_overlay_style(self) -> str | None:
        """Get style of axis overlay (shown only when interacting with mouse/touch).

        Returns:
            str | None: Color as rgba string, or None if transparent.

        Examples:
            >>> color = axis.get_overlay_style()
        """
        return self.instance.get(self.id, 'getOverlayStyle', {})

    def get_parallel_index(self) -> int:
        """Get index of Axis in its own parallel group.

        This retrieves the same value which was used (or defaulted) when the axis was created.

        Returns:
            int: Parallel index of the axis.

        Examples:
            >>> index = axis.get_parallel_index()
        """
        return self.instance.get(self.id, 'getParallelIndex', {})

    def get_scroll_margins(self) -> bool | dict:
        """Get scroll margins configuration.

        Returns:
            bool | dict: Either False (disabled) or a dict with:
                - start (float): Start margin
                - end (float): End margin

        Examples:
            >>> margins = axis.get_scroll_margins()
            >>> if isinstance(margins, dict):
            ...     print(f"Start: {margins['start']}, End: {margins['end']}")
        """
        return self.instance.get(self.id, 'getScrollMargins', {})

    def get_scroll_strategy(self) -> dict | None:
        """Get current axis scroll strategy configuration.

        Returns:
            dict | None: Strategy configuration with keys:
                - id (str): Strategy name ('fitting', 'expansion', 'progressive', etc.)
                - considerVisibleRangeOnly (bool): Whether scrolling only considers visible data range

                Returns None if no strategy is set.

        Examples:
            >>> strategy = axis.get_scroll_strategy()
            >>> if strategy:
            ...     print(f"Strategy: {strategy['id']}")
            ...     print(f"Visible range only: {strategy['considerVisibleRangeOnly']}")
        """
        return self.instance.get(self.id, 'getScrollStrategy', {})

    def get_series_data_range(self) -> dict | None:
        """Get data extents of series attached to the axis.

        Returns:
            dict | None: {'min': number, 'max': number} or None if no data.

        Examples:
            >>> data_range = axis.get_series_data_range()
            >>> if data_range:
            ...     print(f"Data range: {data_range['min']} to {data_range['max']}")
        """
        return self.instance.get(self.id, 'getSeriesDataRange', {})

    def get_stack_index(self) -> int:
        """Get index of Axis in its own stack.

        This retrieves the same value which was used (or defaulted) when the axis was created.

        Returns:
            int: Stack index of the axis.

        Examples:
            >>> index = axis.get_stack_index()
        """
        return self.instance.get(self.id, 'getStackIndex', {})

    def get_stopped(self) -> bool:
        """Get whether the axis is stopped.

        When an Axis is stopped it temporarily prevents the active scroll strategy
        from changing the Axis interval. Axis can be stopped programmatically or
        by built-in interactions such as panning/zooming.

        Returns:
            bool: True if axis is stopped, False otherwise.

        Examples:
            >>> is_stopped = axis.get_stopped()
            >>> print(f"Axis stopped: {is_stopped}")
        """
        return self.instance.get(self.id, 'getStopped', {})
    
    def get_stroke_style(self) -> dict | None:
        """Get axis line stroke style.

        Returns:
            dict | None: Stroke style with keys:
                - thickness (float): Line thickness in pixels
                - color (str): Color as rgba string

        Examples:
            >>> style = axis.get_stroke_style()
            >>> if style:
            ...     print(f"Thickness: {style['thickness']}, Color: {style['color']}")
        """
        return self.instance.get(self.id, 'getStrokeStyle', {})

    def get_thickness(self) -> dict:
        """Get axis thickness min/max limits in pixels.

        For X Axis, this means Axis height.
        For Y Axis, this means Axis width.

        Returns:
            dict: Thickness limits with keys:
                - min (float | None): Minimum thickness, None if not set
                - max (float | None): Maximum thickness, None if not set

        Examples:
            >>> thickness = axis.get_thickness()
            >>> print(f"Min: {thickness['min']}, Max: {thickness['max']}")
        """
        return self.instance.get(self.id, 'getThickness', {})

    def get_tick_strategy(self) -> str:
        """Get the currently used tick strategy.

        Returns:
            str: Tick strategy name - 'Empty', 'Numeric', 'DateTime', or 'Time'

        Examples:
            >>> strategy = axis.get_tick_strategy()
            >>> print(f"Tick strategy: {strategy}")
        """
        return self.instance.get(self.id, 'getTickStrategy', {})

    def get_title_effect(self) -> bool:
        """Get whether theme effect is enabled on axis title.

        A theme can specify an Effect to add extra visual elements to chart
        applications, like Glow effects around data or other components.

        Returns:
            bool: True if theme effect is enabled, False otherwise.

        Examples:
            >>> effect_enabled = axis.get_title_effect()
        """
        return self.instance.get(self.id, 'getTitleEffect', {})

    def get_title_fill_style(self) -> str | None:
        """Get axis title fill style (color).

        Returns:
            str | None: Color as rgba string, or None if transparent.

        Examples:
            >>> color = axis.get_title_fill_style()
        """
        return self.instance.get(self.id, 'getTitleFillStyle', {})

    def get_title_font(self) -> dict:
        """Get font settings of axis title.

        Returns:
            dict: Font settings with keys:
                - size (float): Font size
                - family (str): Font family
                - weight (str): Font weight (e.g., 'normal', 'bold')
                - style (str): Font style (e.g., 'normal', 'italic')

        Examples:
            >>> font = axis.get_title_font()
            >>> print(f"Size: {font['size']}, Family: {font['family']}")
        """
        return self.instance.get(self.id, 'getTitleFont', {})

    def get_title_position(self) -> str:
        """Get axis title position.

        Returns:
            str: Title position - 'center', 'end', 'start', or 'center-chart'

        Examples:
            >>> position = axis.get_title_position()
            >>> print(f"Title position: {position}")
        """
        return self.instance.get(self.id, 'getTitlePosition', {})

    def get_title_rotation(self) -> float:
        """Get rotation of axis title.

        Returns:
            float: Rotation in degrees.

        Examples:
            >>> rotation = axis.get_title_rotation()
            >>> print(f"Title rotation: {rotation} degrees")
        """
        return self.instance.get(self.id, 'getTitleRotation', {})

    def get_units(self) -> str | None:
        """Get unit that axis measures.

        The unit is displayed after the Axis title (if defined), e.g., "Axis title (Hz)".
        Default cursor formatters also place the unit next to axis values.

        Returns:
            str | None: Unit string (e.g., 'Hz', '°C'), or None if not set.

        Examples:
            >>> units = axis.get_units()
            >>> if units:
            ...     print(f"Axis units: {units}")
        """
        return self.instance.get(self.id, 'getUnits', {})

class AxisWithAddEventListener:
    def add_event_listener(
        self,
        event: str,
        handler: callable | None = None,
        throttle_ms: int = 0,
        once: bool = False,
    ) -> str:
        """
        Add event listener to axis.

        Args:
            event: Event name. Common options include:
                - Interaction: 'click', 'pointermove', 'pointerdown', 'pointerup',
                  'pointerenter', 'pointerleave', 'dblclick'
                - Axis-specific: 'intervalchange' (when axis interval changes)
            handler: Python callback receiving event data
            throttle_ms: Minimum delay between callbacks in milliseconds
            once: If True, listener removes itself after first trigger

        Returns:
            callback_id identifying the registered handler

        Examples:
            Listen for axis interval changes:
            >>> def on_interval_change(event):
            ...     print(f"Axis interval: {event['start']} - {event['end']}")
            >>> axis.add_event_listener('intervalchange', handler=on_interval_change)

            Listen for clicks on axis:
            >>> def on_click(event):
            ...     print(f"Axis clicked at: {event}")
            >>> axis.add_event_listener('click', handler=on_click)

            Throttled pointer move events:
            >>> def on_move(event):
            ...     print(f"Pointer at: {event}")
            >>> axis.add_event_listener('pointermove', handler=on_move, throttle_ms=100)
        """
        callback_id = str(uuid.uuid4()).split('-')[0] if handler else ''
        if handler is not None:
            self.instance.event_handlers[callback_id] = handler

        self.instance.send(self.id, 'addEventListener', {
            'event': event,
            'callbackId': callback_id or None,
            'throttleMs': int(throttle_ms) if throttle_ms else 0,
            'options': {'once': bool(once)},
            'target': 'chart',
        })
        return callback_id
    
    def get_title(self) -> str:
        """Get the current axis title text.

        Returns:
            str: The axis title text.

        Examples:
            >>> title = axis.get_title()
            >>> print(f"Axis title: {title}")
        """
        return self.instance.get(self.id, 'getTitle', {})   
    
class Axis(GenericAxis, ComponentWithLinePaletteColoring, UserInteractions, GetCustomTicks, AxisGetMethods, AxisWithAddEventListener):
    def __init__(
        self,
        chart,
        axis: str,
        stack_index: int,
        parallel_index: int,
        opposite: bool,
        type: str,
        base: int,
    ):
        GenericAxis.__init__(self, chart)
        self.instance.send(
            self.id,
            'addAxis',
            {
                'chart': self.chart.id,
                'axis': axis,
                'opposite': opposite,
                'iStack': stack_index,
                'iParallel': parallel_index,
                'type': type,
                'base': base,
            },
        )

    def set_decimal_precision(self, decimals: int):
        """Format the axis ticks to certain number of decimal numbers.

        Args:
            decimals (int): Decimal precision.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickStrategyFormattingRound', {'decimals': decimals})
        return self

    def set_tick_formatting(self, text: str):
        """

        Args:
            text (str):

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickStrategyFormattingText', {'text': text})
        return self

    def set_length(self, length: int | float, relative: bool):
        """Configure length of axis. E.g. height for Y axis, width for X axis.

        Args:
            length (int | float): Length value
            relative (bool): If true, length value is interpreted as relative length across multiple axes. If false,
                length value is interpreted as length in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLength', {'length': length, 'relative': relative})
        return self

    def set_margins(self, start: int | float, end: int | float):
        """Add empty space at either end of the axis, without affecting the relative size of the Axis.

        Args:
            start (int | float): Start margin in pixels.
            end (int | float): End margin in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setMargins', {'start': start, 'end': end})
        return self    

    def add_band(self, on_top: bool = True, legend: Optional[LegendOptions] = None,):
        """Add a highlighter Band to the Axis. A Band can be used to highlight an interval on the Axis.

        Args:
            on_top (bool): Is Band rendered above Series, or below. Default to above.
        
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
            Reference to Band class.
        """
        return Band(self.chart, self, on_top, legend=legend)

    def add_constant_line(self, on_top: bool = True, legend: Optional[LegendOptions] = None):
        """Add a highlighter ConstantLine to the Axis.
        A ConstantLine can be used to highlight a specific value on the Axis.

        Args:
            on_top (bool): Is ConstantLine rendered above Series, or below. Default to above.

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
            Reference to ConstantLine class.
        """
        return ConstantLine(self.chart, self, on_top, legend=legend)

    def add_custom_tick(self, tick_type: str = 'major'):
        """Add custom tick to Axis. Custom ticks can be used to expand on default tick placement,
        or completely override Axis ticks placement with custom logic.

        Args:
            tick_type (str): "major" | "minor" | "box"

        Returns:
            Reference to CustomTick class.
        """
        types = ('major', 'minor', 'box')
        if tick_type not in types:
            raise ValueError(f"Expected tick_type to be one of {types}, but got '{tick_type}'.")

        return CustomTick(self.chart, self, tick_type)

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric" | "DateTime" | "Time"
            time_origin (int | float): Use with "DateTime" or "Time" strategy.
                If a time origin is defined, data points will be interpreted as milliseconds since time_origin.
            utc (bool): Use with DateTime strategy. By default, false, which means that tick placement is applied
                according to clients local time-zone/region and possible daylight saving cycle.
                When true, tick placement is applied in UTC which means no daylight saving adjustments &
                timestamps are displayed as milliseconds without any time-zone region offsets.

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('Empty', 'Numeric', 'DateTime', 'Time')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.instance.send(
            self.chart.id,
            'setTickStrategy',
            {
                'strategy': strategy,
                'axis': self.id,
                'timeOrigin': time_origin,
                'utc': utc,
            },
        )
        return self

    def pan(self, amount: int | float):
        """Pan scale by pixel value delta.

        Args:
            amount (int | float): Amount to shift scale of axis in pixels

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'panAxis', {'amount': amount})
        return self

    def zoom(self, reference_position: int | float, zoom_direction: int | float):
        """Zoom scale from/to a position.

        Args:
            reference_position (int | float): Position to zoom towards or from on axis.
            zoom_direction (int | float): Amount and direction of zoom [-1, 1] as a guideline.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'zoomAxis',
            {'referencePosition': reference_position, 'zoomDirection': zoom_direction},
        )
        return self
    
    def set_tick_labels(
        self,
        major_size: int | float = None,
        minor_size: int | float = None,
        family: str = None,
        style: str = None,
        weight: str = None,
        major_color = None,
        minor_color = None,
        major_rotation: float = None,
        minor_rotation: float = None,
        format_type: str = 'standard',
        operation: str = 'none',
        precision: int = None,
        unit: str = None,
        scale: float = 1.0,
    ):
        """Style tick labels for this axis with comprehensive formatting options.
        
        Args:
            major_size (int | float, optional): Font size for major tick labels in pixels.
            minor_size (int | float, optional): Font size for minor tick labels in pixels.
            family (str, optional): CSS font family for both major and minor tick labels.
            style (str, optional): CSS font style ('normal', 'italic').
            weight (str, optional): CSS font weight ('normal', 'bold').
            major_color (Color, optional): Text color for major tick labels.
            minor_color (Color, optional): Text color for minor tick labels.
            major_rotation (float, optional): Rotation angle in degrees for major tick labels.
            minor_rotation (float, optional): Rotation angle in degrees for minor tick labels.
            format_type (str): Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'compact': Compact notation (K, M, B, T)
                - 'engineering': Engineering notation
                - 'scientific': Scientific notation
                - 'integer': Rounded integer values
            operation (str): Mathematical operation to apply:
                - 'none' - No operation (default)
                - 'round' - Round to nearest integer
                - 'ceil' - Round up to nearest integer
                - 'floor' - Round down to nearest integer
            precision (int, optional): Number of decimal places (None = auto)
            unit (str, optional): Unit to append (e.g., "kg", "ms", "items")
            scale (float): Scale factor to multiply value (default: 1.0)
        
        Returns:
            The instance of the axis for fluent interface.
        
        Examples:
            Basic font styling
            >>> axis.set_tick_labels(major_size=14, minor_size=10, weight='bold')
            
            Rotated labels with color
            >>> axis.set_tick_labels(
            ...     major_size=12,
            ...     major_rotation=45,
            ...     major_color='darkblue'
            ... )
            
            Formatted with units
            >>> axis.set_tick_labels(
            ...     major_size=12,
            ...     precision=2,
            ...     unit='Hz',
            ...     scale=1000
            ... )
            
            Percentage formatting
            >>> axis.set_tick_labels(
            ...     format_type='percentage',
            ...     precision=1
            ... )
            
            Currency with rotation
            >>> axis.set_tick_labels(
            ...     format_type='currency',
            ...     precision=0,
            ...     major_rotation=45
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
        if operation is not None:
            config['operation'] = operation
        if precision is not None:
            config['precision'] = precision
        if unit is not None:
            config['unit'] = unit
        if scale is not None:
            config['scale'] = scale
        
        self.instance.send(
            self.id,
            'setAxisTickLabels',
            config
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

    def set_fallback_to_extreme_ticks(self, enabled: bool = True):
        """Enable or disable automatic fallback to extreme ticks when an axis becomes too small.

        Args:
            enabled (bool): If True, extreme ticks will be automatically displayed when needed.
                            If False, restores the previous behavior (hides extreme ticks).
                            This only applies for Numeric Tick Strategies.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setFallBackToExtremeTicksAutomatically', {'enabled': enabled})
        return self

    def set_great_tick_style(
        self,
        color: any = None,
        size: int | float = None,
        length: int | float = None,
        family: str = None,
        style: str = None,
        weight: str = None,
        disable: bool = False,
    ):
        """Set or disable the style of Great Ticks for a DateTime axis.

        Args:
            color (Color, optional): Tick label color.
            size (int | float, optional): Tick label font size.
            length (int | float, optional): Length of tick lines.
            family (str, optional): Font family.
            style (str, optional): Font style ('normal', 'italic').
            weight (str, optional): Font weight ('normal', 'bold').
            disable (bool, optional): Set to True to disable Great Ticks.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        config = {
            'color': color,
            'fontSize': size,
            'tickLength': length,
            'fontFamily': family,
            'fontStyle': style,
            'fontWeight': weight,
            'disable': disable,
        }
        config = {k: v for k, v in config.items() if v is not None}

        self.instance.send(self.id, 'setGreatTickStyle', config)
        return self  

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Examples:
            # Disable all interactions:
            >>>     axis.set_user_interactions(None)

            # Restore default interactions:
            >>>     axis.set_user_interactions()
            ...     axis.set_user_interactions({})

            # Configure specific interactions:
            >>>     axis.set_user_interactions(
            ...     {
            ...         'pan': {
            ...             'lmb': {'drag': True},
            ...             'rmb': False,
            ...             'mmb': False,
            ...         },
            ...         'rectangleZoom': {
            ...             'lmb': False,
            ...             'rmb': {'drag': True},
            ...             'mmb': False,
            ...         },
            ...     }
            ... )
        """
        return super().set_user_interactions(interactions)
    
    def set_title_position(self, position: str = None):
        """Set axis title position.

        Args:
            position (str): None(default) | "center" | "end" | "start" | "center-chart" 

        Returns:
            The instance of the class for fluent interface.
        """
        title_positions = (
            'center',
            'end',
            'start',
            'center-chart',
        )
        if position not in title_positions:
            raise ValueError(f"Expected position to be one of {title_positions}, but got '{position}'.")

        self.instance.send(self.id, 'setAxisTitlePosition', {'position': position})
        return self
    
    def set_stroke_style(self, style):
        """Set style of Axis line stroke.
        
        Args:
            style: Line style - 'empty', 'solid', 'dashed', or dict with thickness/color
            
        Examples:
            axis.set_stroke_style('empty')  # Hide axis line
            axis.set_stroke_style({'thickness': 0})  # Hide with thickness 0
            axis.set_stroke_style({'thickness': 2, 'color': '#ff0000'})  # Red line
        """
        for item in style:
            if item == 'color':
                style['color'] = convert_color_to_hex(style['color']) if style['color'] is not None else None
        self.instance.send(self.id, 'setAxisStrokeStyle', {'style': style})
        return self
    def set_keep_tick_labels_in_axis_bounds(self, enabled: bool = True):
        """Configure whether axis should keep tick labels within its boundaries.

        When enabled, tick labels are shifted to fit within the axis bounds,
        preventing them from going outside. This may cause labels to overlap
        in edge cases, but generally does not occur in normal scenarios.

        Args:
            enabled (bool): True to keep labels in bounds, False to allow overflow.
                Defaults to True.

        Returns:
            The instance of the class for fluent interface.

        Examples:
            Disable keeping tick labels in bounds:

            >>> axis.set_keep_tick_labels_in_axis_bounds(False)

            Re-enable (default behavior):

            >>> axis.set_keep_tick_labels_in_axis_bounds(True)
        """
        self.instance.send(self.id, 'setKeepTickLabelsInAxisBounds', {'enabled': enabled})
        return self
    
    def set_margin_after_title(self, margin: int | float):
        """Set padding after Axis title.

        This is only applied when the title is visible.

        Args:
            margin (int | float): Gap between the title and the next axis in pixels.
                Can also affect chart margins.

        Returns:
            The instance of the class for fluent interface.

        Examples:
            >>> axis.set_margin_after_title(20)
        """
        self.instance.send(self.id, 'setMarginAfterTitle', {'margin': margin})
        return self

    def set_overlay_style(self, color: any):
        """Set style of axis overlay.

        Args:
            color (Color): Fill color for the overlay. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.

        Examples:
            >>> axis.set_overlay_style((255, 255, 0))
            >>> axis.set_overlay_style('transparent')  # Hide overlay
        """
        color = convert_color_to_hex(color) if color is not None else None
        self.instance.send(self.id, 'setOverlayStyle', {'color': color})
        return self    
    

class DefaultAxis(Axis):
    def __init__(self, chart, axis: str):
        self.chart = chart
        self.dimension = axis
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = chart.instance
        self.instance.send(
            self.chart.id,
            'getDefaultAxisReference',
            {'dimension': self.dimension, 'axisID': self.id},
        )


class DefaultAxis3D(GenericAxis, GetCustomTicks, AxisGetMethods, AxisWithAddEventListener):
    def __init__(self, chart, axis: str):
        self.chart = chart
        self.dimension = axis
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = chart.instance
        self.instance.send(
            self.chart.id,
            'getDefaultAxisReference',
            {'dimension': self.dimension, 'axisID': self.id},
        )

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric" | "DateTime" | "Time"
            time_origin (int | float): Define with time.time(). If a time origin is defined,
                data-points will instead be interpreted as milliseconds since time origin.
            utc (bool): Use with DateTime strategy. By default, false, which means that tick placement is applied
                according to clients local time-zone/region and possible daylight saving cycle.
                When true, tick placement is applied in UTC which means no daylight saving adjustments &
                timestamps are displayed as milliseconds without any time-zone region offsets.

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('Empty', 'Numeric', 'DateTime', 'Time')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.instance.send(
            self.chart.id,
            'setTickStrategy',
            {
                'strategy': strategy,
                'axis': self.id,
                'timeOrigin': time_origin,
                'utc': utc,
            },
        )
        return self

    def add_custom_tick(self, tick_type: str = 'major'):
        """Add a 3D custom tick to the Axis.
        Custom ticks can be used to completely control tick placement, text, and styles in a 3D environment.

        Args:
            tick_type (str): "major" | "minor" | "box"

        Returns:
            Reference to CustomTick3D class.
        """
        types = ('major', 'minor', 'box')
        if tick_type not in types:
            raise ValueError(f"Expected tick_type to be one of {types}, but got '{tick_type}'.")

        return CustomTick3D(self.chart, self, tick_type)

    def set_tick_labels(
        self,
        major_size: int | float = None,
        minor_size: int | float = None,
        family: str = None,
        style: str = None,
        weight: str = None,
        major_color = None,
        minor_color = None,
        major_rotation: float = None,
        minor_rotation: float = None,
        format_type: str = 'standard',
        operation: str = 'none',
        precision: int = None,
        unit: str = None,
        scale: float = 1.0,
    ):
        """Style tick labels for this axis with comprehensive formatting options.
        
        Args:
            major_size (int | float, optional): Font size for major tick labels in pixels.
            minor_size (int | float, optional): Font size for minor tick labels in pixels.
            family (str, optional): CSS font family for both major and minor tick labels.
            style (str, optional): CSS font style ('normal', 'italic').
            weight (str, optional): CSS font weight ('normal', 'bold').
            major_color (Color, optional): Text color for major tick labels.
            minor_color (Color, optional): Text color for minor tick labels.
            major_rotation (float, optional): Rotation angle in degrees for major tick labels.
            minor_rotation (float, optional): Rotation angle in degrees for minor tick labels.
            format_type (str): Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'compact': Compact notation (K, M, B, T)
                - 'engineering': Engineering notation
                - 'scientific': Scientific notation
                - 'integer': Rounded integer values
            operation (str): Mathematical operation to apply:
                - 'none' - No operation (default)
                - 'round' - Round to nearest integer
                - 'ceil' - Round up to nearest integer
                - 'floor' - Round down to nearest integer
            precision (int, optional): Number of decimal places (None = auto)
            unit (str, optional): Unit to append (e.g., "kg", "ms", "items")
            scale (float): Scale factor to multiply value (default: 1.0)
        
        Returns:
            The instance of the axis for fluent interface.
        
        Examples:
            Basic font styling
            >>> axis.set_tick_labels(major_size=14, minor_size=10, weight='bold')
            
            Rotated labels with color
            >>> axis.set_tick_labels(
            ...     major_size=12,
            ...     major_rotation=45,
            ...     major_color='darkblue'
            ... )
            
            Formatted with units
            >>> axis.set_tick_labels(
            ...     major_size=12,
            ...     precision=2,
            ...     unit='Hz',
            ...     scale=1000
            ... )
            
            Percentage formatting
            >>> axis.set_tick_labels(
            ...     format_type='percentage',
            ...     precision=1
            ... )
            
            Currency with rotation
            >>> axis.set_tick_labels(
            ...     format_type='currency',
            ...     precision=0,
            ...     major_rotation=45
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
        if operation is not None:
            config['operation'] = operation
        if precision is not None:
            config['precision'] = precision
        if unit is not None:
            config['unit'] = unit
        if scale is not None:
            config['scale'] = scale
        
        self.instance.send(
            self.id,
            'setAxisTickLabels',
            config
        )
        return self
    
class BarChartAxis(GenericAxis):
    def __init__(self, chart):
        GenericAxis.__init__(self, chart)

    def set_thickness(self, thickness: int | float):
        """Set Axis thickness as pixels.

        Args:
            thickness (int | float): Explicit thickness of Axis as pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setThickness', {'thickness': thickness})
        return self


class CategoryAxis(BarChartAxis):
    def __init__(self, chart):
        BarChartAxis.__init__(self, chart)
        self.instance.send(self.id, 'getCategoryAxisReference', {'chart': self.chart.id})


class ValueAxis(BarChartAxis):
    def __init__(self, chart):
        BarChartAxis.__init__(self, chart)
        self.instance.send(self.id, 'getValueAxisReference', {'chart': self.chart.id})

    def set_tick_strategy(self, strategy: str):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric"

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('Empty', 'Numeric')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.instance.send(
            self.chart.id,
            'setTickStrategy',
            {
                'strategy': strategy,
                'axis': self.id,
            },
        )
        return self

    def set_decimal_precision(self, decimals: int):
        """Format the axis ticks to certain number of decimal numbers.

        Args:
            decimals (int): Decimal precision.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickStrategyFormattingRound', {'decimals': decimals})
        return self


class SpiderChartAxis:
    """A class containing axis-related methods for the SpiderChart."""

    def set_axis_interval(self, start: int | float, end: int | float, stop_axis_after: bool = True):
        """Set interval of Charts Axes

        Args:
            start (int | float): Value at edges of chart.
            end (int | float): Value at center of chart. Defaults to zero.
            stop_axis_after (bool): Stop axis after value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setSpiderAxisInterval',
            {'start': start, 'end': end, 'stop': stop_axis_after},
        )
        return self

    def add_axis(self, tag: str):
        """Add a new axis to Spider Chart.

        Args:
            tag (str): String tag for the axis.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'addSpiderAxis', {'tag': tag})
        return self

    def set_auto_axis_creation(self, enabled: bool):
        """Specifies if auto creation of axis is turned on or not.

        Args:
            enabled (bool): State of automatic axis creation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutoAxis', {'enabled': enabled})
        return self

    def set_axis_label_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAxisLabelEffect', {'enabled': enabled})
        return self

    def set_axis_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of axis labels.

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
            'setAxisLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_axis_label_padding(self, padding: int | float):
        """Set padding of axis labels.

        Args:
            padding (int | float): Padding in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAxisLabelPadding', {'padding': padding})
        return self

    def set_axis_label_color(self, color: any):
        """Set the color of axis labels.

        Args:
            color (Color): Color of the labels. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setAxisLabelStyle', {'color': color})
        return self

    def set_axis_scroll_strategy(
        self, 
        strategy: str,
        start: bool = None,
        end: bool = None,
        visibleonly: bool = None,
    ):
        """Sets the scroll strategy of charts axes.
        
        Args:
            strategy (str):
                - "expansion": expand to fit new data without moving view
                - "fitting": resize to fit all data
                - "scrolling" (default): scroll with incoming data
                - "fittingStepped" resize to fit data in larger steps
            start (bool, optional): Lock scroll to start of data range  
            end (bool, optional): Lock scroll to end of data range
            visibleonly (bool, optional): Limit effect to visible series only
        """
        strategies = ('expansion', 'fitting', 'fittingStepped', 'scrolling')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")
        
        opts = {}
        if start is not None: 
            opts['start'] = start
        if end is not None: 
            opts['end'] = end
        if visibleonly is not None: 
            opts['considerVisibleRangeOnly'] = visibleonly
                
        self.instance.send(self.id, 'setAxisScrollStrategy', {
            'strategy': strategy, 
            'opts': opts if opts else None
        })
        return self

    def set_axis_style(self, thickness: int | float, color: any = None):
        """Set the style of axis line.

        Args:
            thickness (int | float): Thickness of the axis line.
            color (Color): Color of the axis line. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setAxisStyle', {'thickness': thickness, 'color': color})
        return self

    def set_scale_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of scale labels.

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
            'setScaleLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_scale_label_padding(self, padding: int | float):
        """Set padding of scale labels.

        Args:
            padding (int | float): Padding in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setScaleLabelPadding', {'padding': padding})
        return self

    def set_scale_label_color(self, color: any):
        """Set the color of the scale labels.

        Args:
            color (Color): Color of the scale labels. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setScaleLabelStyle', {'color': color})
        return self


