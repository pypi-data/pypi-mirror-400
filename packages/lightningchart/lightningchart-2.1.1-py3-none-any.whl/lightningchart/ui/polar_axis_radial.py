from __future__ import annotations

from lightningchart.ui.polar_axis import PolarAxis


class PolarAxisRadial(PolarAxis):
    """Class representing the radial axis in a polar chart."""

    def __init__(self, chart):
        super().__init__(chart)
        self.instance.send(self.id, 'addPolarAxisRadial', {'chart': self.chart.id})

    def set_division(self, sections_count: int):
        """Set how many sections the radial axis is divided into by Ticks.

        Args:
            sections_count: Number of sections.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setDivision', {'sectionsCount': sections_count})
        self.sections_count = sections_count
        return self

    def get_division(self) -> int:
        """Get how many sections the radial axis is divided into by Ticks.

        Returns:
            Number of sections.
        """
        return self.sections_count

    def set_clockwise(self, clockwise: bool):
        """Set whether PolarAxisRadial direction is clockwise or counterclockwise.

        Args:
            clockwise: True for clockwise direction, False for counterclockwise.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setClockwise', {'clockwise': clockwise})
        return self

    def set_north(self, angle: int):
        """Set rotation of radial axis by specifying degree angle that is depicted at North position (horizontally centered, vertically highest).

        Args:
            angle: Angle as degrees that will be depicted at North position. Defaults to 90.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setNorth', {'angle': angle})
        return self

    def set_tick_labels(self, labels: list[str]):
        """Replace all default tick labels within the radial axis with a list of custom labels.

        Args:
            labels: A list of strings to display on the ticks. Must match the number of axis divisions.

        Returns:
            The instance of the class for fluent interface.
        """

        self.instance.send(self.id, 'setTickFormattingFunction', {'labels': labels})
        return self

    def set_degrees_format(self, step_degrees: int | None = None, show_degree_symbol: bool = True):
        """
        Configure how tick labels on the **radial (angle)** axis are displayed in degrees.

        Args:
            step_degrees:
                If provided, round displayed degree values to the nearest multiple of this
                step size (e.g., ``30`` results in labels like ``0°, 30°, 60°, …``).
                If ``None`` (default), labels are shown using rounded degrees without step snapping.
            show_degree_symbol:
                If ``True`` (default), append the degree symbol (``°``) to labels.
                If ``False``, labels are shown as plain numbers.

        Returns:
            self: The axis instance for fluent chaining.

        Examples:
            >>> radial = chart.get_radial_axis()
            >>> radial.set_division(12).set_clockwise(True)
            >>> radial.set_degrees_format(step_degrees=30, show_degree_symbol=True)
        """
        self.instance.send(
            self.id,
            'setRadialTickFormat',
            {
                'stepDegrees': step_degrees,
                'showDegreeSymbol': show_degree_symbol,
            },
        )
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
        Style the **radial axis tick labels** (font, rotation, and paddings).

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
            >>> radial = chart.get_radial_axis()
            >>> radial.style_tick_labels(size=11, weight='600', rotation=0, label_padding=2)
        """
        payload = {'family': family, 'size': size, 'weight': weight, 'style': style}
        if rotation is not None:
            payload['rotation'] = rotation
        if tick_padding is not None:
            payload['tick_padding'] = tick_padding
        if label_padding is not None:
            payload['label_padding'] = label_padding

        self.instance.send(self.id, 'styleRadialTickLabels', payload)
        return self

    def set_margin_after_ticks(self, pixels: int | float):
        """Set gap (px) after tick labels toward the plot."""
        self.instance.send(self.id, 'setAxisMarginAfterTicks', {'margin': pixels})
        return self
