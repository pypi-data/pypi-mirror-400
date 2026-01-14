"""Provides a buffer class to plot values"""


class PlotValueChannel:
    """Class for holding a specific number of values and handling minimum/maximum"""


    def __init__(self, max_value_count: int):

        self._x_data: list[float] = []
        self._y_data: list[float] = []

        self._max_value_count = max_value_count
        self._counter = 0


    def append_value(self, value: float):
        """Appends a value and returns updated minimum and maximum for plot"""
        self._x_data.append(self._counter)
        self._counter += 1
        if len(self._x_data) > self._max_value_count:
            self._x_data.pop(0)

        self._y_data.append(value)
        if len(self._y_data) > self._max_value_count:
            self._y_data.pop(0)


    def update_plot(self):
        """Function to update values to plot"""


    @property
    def data(self) -> tuple[list[float], list[float]]:
        """Returns x and y values"""
        return [self._x_data, self._y_data]


class PlotHelper:
    """Class to handle values for plotting"""


    def __init__(self):
        self._data: dict[int, PlotValueChannel] = {}


    @property
    def data(self) -> dict[int, PlotValueChannel]:
        """Returns data with PlotValueChannels"""
        return self._data


    def append_value(self, channel: int, value: float):
        """Append value to channel buffer"""
        self._data[channel].append_value(value)


    def append_values(self, channel: int, values: list[float]):
        """Append values to channel buffer"""
        for x in values:
            self.append_value(channel, x)


    def update(self):
        """Update plot"""


    def loop(self):
        """Run event loop until plot window closed"""


    def _calc_layout_dimension(self, channel_count: int) -> tuple[int, int]:
        """Calculates layout for a specific number of channels, tries to grow
        equal in both directions"""
        layouts = {1: [1, 1], 2: [2, 1], 3: [3, 1], 4: [2, 2], 5: [3, 2], 6: [3, 2], 7: [4, 2], 8: [4, 2]}
        return layouts[channel_count]
