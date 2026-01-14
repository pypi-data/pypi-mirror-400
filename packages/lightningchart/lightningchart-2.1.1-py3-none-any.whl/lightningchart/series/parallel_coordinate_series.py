from lightningchart.charts import Chart
from lightningchart.series import Series, SeriesWithAddEventListener
from lightningchart.utils import convert_color_to_hex
from lightningchart.utils.utils import ColorInput


class ParallelCoordinateSeries(Series, SeriesWithAddEventListener):
    """Represents a single series within a ParallelCoordinateChart.

    This series is associated with one ParallelCoordinateChart and is used to visualize data across the chart's axes.
    """

    def __init__(
        self,
        chart: Chart
    ):
        """
        Initialize a ParallelCoordinateSeries.

        Args:
            chart (Chart): The parent ParallelCoordinateChart to which this series belongs.
            theme (Themes): The theme of the series, default is `Themes.White`.
            name (str, optional): The name of the series. Defaults to None.
        """

        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'addSeries',
            {'chart': self.chart.id},)

    def set_data(self, data: dict[str, float]):
        """
        Set data points for the series.

        Data is provided as a dictionary mapping axis names to values. Each axis name must match the axes defined
        in the associated ParallelCoordinateChart.

        Args:
            data (dict[str, float]): A dictionary where the keys are axis names and the values are the corresponding data values.

        Returns:
            The instance of the series for fluent interface.
        """
        self.data = data
        self.instance.send(self.id, 'setData', {'data': data})
        return self

    def get_data(self) -> dict[str, float] | None:
        """
        Retrieve the data of the series.

        The data is returned as a dictionary mapping axis names to their corresponding values.

        Returns:
            dict[str, float] | None: A dictionary of axis-value pairs if data is set, otherwise None.
        """
        return self.data

    def set_color(self, color: ColorInput | None):
        """Set a color fill for the series.

        Args:
            color (Color): Color of the series. Use 'transparent' or None to hide.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setColor', {'color': color})
        return self
    
    def get_color(self) -> dict:
        """Get color of the series.
        
        Returns:
            dict: Color as {'r': int, 'g': int, 'b': int, 'a': int}
        
        Notes:
            Call this in live mode, e.g. ``chart.open(live=True)``
        
        Example:
            >>> series = chart.add_series()
            >>> series.set_color((255, 0, 0))
            >>> color = series.get_color()
            >>> print(color)  # {'r': 255, 'g': 0, 'b': 0, 'a': 255}
        """
        return self.instance.get(self.id, 'getColorParallelCoordinateSeries', {})
