"""Provides a buffer class to plot values"""

from queue import Empty, Full, Queue

import numpy as np
import fastplotlib as fpl

from .plot_base import PlotHelper, PlotValueChannel


class FastPlotLibValueChannel(PlotValueChannel):
    """Class for holding a specific number of values specific for FastPlotLib"""


    def __init__(self, sub_plot, max_value_count: int, color: str):
        """sub_plot type is Subplot from fastplotlib"""

        super().__init__(max_value_count)
        self._sub_plot = sub_plot

        # we use an array with zero as start data
        y_data = np.array([0.0] * max_value_count, dtype=np.float32)
        self._line = sub_plot.add_line(y_data, name="values", colors=color)

        # this queue is used to synchronize data between background and main thread
        self._data_queue = Queue(maxsize=0)


    def append_value(self, value: float):
        """Appends a value and returns updated minimum and maximum for plot.
        This function is call in context of background thread"""
        super().append_value(value)

        # because it is not possible to change value count during animation,
        # we fill arrays with "dummy" values
        # for x axis we use values between 0 and 1
        # for y axis we use first real value to fill arrays with that value
        if len(self._x_data) < self._max_value_count:
            self._x_data = [x / self._max_value_count for x in range(self._max_value_count)]
        if len(self._y_data) < self._max_value_count:
            self._y_data = [value] * self._max_value_count

        try:
            self._data_queue.put_nowait([self._x_data, self._y_data])
        except Full:
            # Queue is full, skip this update
            pass


    def update_plot(self):
        """This function is called in context of main thread"""
        super().update_plot()
        try:
            new_x_data, new_y_data = self._data_queue.get_nowait()
            new_x_data = np.array(new_x_data)
            new_y_data = np.array(new_y_data)
            self._line.data[:, 0] = new_x_data
            self._line.data[:, 1] = new_y_data
        except Empty:
            # No new data in the queue
            pass


class FastPlotLibHelper(PlotHelper):
    """Class to handle plots and values for plotting specific for FastPlotLib"""


    def __init__(self, channels: dict[int, tuple[str, str]], max_value_count: int):
        super().__init__()

        # calc layout for sub plots
        x_dimension, y_dimension = self._calc_layout_dimension(len(channels))

        # create figure
        self._figure = fpl.Figure(size=(1024, 768), shape=(y_dimension, x_dimension))

        for (key, value), sub_plot in zip(channels.items(), list(self._figure)):
            sub_plot.title = value[0]
            self._data[key] = FastPlotLibValueChannel(sub_plot, max_value_count, value[1])

        # set animation function that is called regularly to update plots
        self._figure.add_animations(self._animation)
        # show figure
        self._figure.show(maintain_aspect=False)


    def _animation(self, figure: fpl.Figure):
        """This function is called in context of main thread"""
        for x in self._data.values():
            x.update_plot()

        # this keeps the plot in camera view, but prevents any mouse control
        for graph in figure:
            graph.auto_scale()
