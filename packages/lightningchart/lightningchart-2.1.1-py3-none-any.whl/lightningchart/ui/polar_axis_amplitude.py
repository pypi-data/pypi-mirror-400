from __future__ import annotations

from lightningchart.ui.polar_axis import PolarAxis


class PolarAxisAmplitude(PolarAxis):
    def __init__(self, chart):
        super().__init__(chart)
        self.instance.send(self.id, 'getAmplitudeAxis', {'chart': self.chart.id})

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric" | "DateTime" | "Time"
            time_origin (int | float): Use with "DateTime" or "Time" strategy.
                If a time origin is defined, data points will be interpreted as milliseconds since time_origin.
            utc (bool): Use with DateTime strategy. By default, False, which means that tick placement is applied
                according to client's local time-zone/region and possible daylight saving cycle.
                When True, tick placement is applied in UTC which means no daylight saving adjustments &
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
    
    def set_tick_format(self, decimals: int | None = None, suffix: str | None = None):
        """
        Format amplitude tick labels, e.g. '12.3 dB'.
        
        Args:
            decimals (int | None): Number of decimals to display. If None, default formatting is used.
            suffix (str | None): Optional suffix appended to the value (e.g., ' dB').

        Example:
            >>> radial = chart.get_amplitude_axis()
            >>> radial.set_tick_format(decimals=1, suffix=' dB')  # -> '12.3 dB'
        """
        self.instance.send(self.id, 'setAmplitudeTickFormat', {
            'decimals': decimals,
            'suffix': suffix
        })
        return self

    def style_tick_labels(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
        rotation: float | None = None,
        tick_padding: int | float | None = None,
        label_padding: int | float | None = None,
    ):
        """
        Style amplitude tick labels (font + optional rotation & paddings).

        Args:
            size:
                Font size in CSS pixels (e.g., ``12`` or ``14``).
            family:
                CSS font-family for labels (comma-separated fallback list).
            style:
                CSS font-style (e.g., ``'normal'``, ``'italic'``).
            weight:
                CSS font-weight (e.g., ``'normal'``, ``'600'``, ``'bold'``).
            rotation:
                Optional label rotation in **degrees**. If given, rotates the tick label text.
            tick_padding:
                Optional pixels between the **tick line** and the label.
            label_padding:
                Optional pixels **after** the label (right/below depending on layout).

        Returns:
            self: The axis instance for fluent chaining.

        Examples:
            >>> radial = chart.get_amplitude_axis()
            >>> radial.style_tick_labels(size=11, weight='600', rotation=0, label_padding=2)
        """
        payload = {'family': family, 'size': size, 'weight': weight, 'style': style}
        if rotation is not None: 
            payload['rotation'] = rotation
        if tick_padding is not None: 
            payload['tick_padding'] = tick_padding
        if label_padding is not None: 
            payload['label_padding'] = label_padding
        self.instance.send(self.id, 'styleAmplitudeTickLabels', payload)
        return self

