"""Provides a buffer class to plot values"""

from queue import Empty, Full, Queue
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.backend_bases import CloseEvent

from .plot_base import PlotHelper, PlotValueChannel


class PyPlotValueChannel(PlotValueChannel):
    """Class for holding a specific number of values and handling minimum/maximum specific for PyPlot"""


    def __init__(self, axes: plt.Axes, max_value_count: int, color: str):

        super().__init__(max_value_count)

        # add line with color
        line, = axes.plot(self._x_data, self._y_data, color)
        # enable grid
        axes.grid()

        self._axes = axes
        self._line = line

        self._minimum = None
        self._maximum = None

        # this queue is used to synchronize data between background and main thread
        self._data_queue = Queue(maxsize=0)


    def append_value(self, value: float):
        """Appends a value and updates minimum and maximum for plot. Does run in main thread context"""
        super().append_value(value)

        if self._minimum is None or value < self._minimum:
            self._minimum = value
        if self._maximum is None or value > self._maximum:
            self._maximum = value

        # self._axes.redraw_in_frame()
        try:
            self._data_queue.put_nowait([self._x_data, self._y_data, self._minimum, self._maximum])
        except Full:
            # Queue is full, skip this update
            pass


    def update_plot(self):
        """This function is call in context animation function"""
        super().update_plot()
        try:
            new_x_data, new_y_data, new_minimum, new_maximum = self._data_queue.get_nowait()
            self._line.set_xdata(new_x_data)
            self._line.set_ydata(new_y_data)

            if len(new_x_data) > 1:
                self._axes.set_xlim(new_x_data[0], new_x_data[-1])
                offset = (new_maximum - new_minimum) * 0.1 + 0.1
                self._axes.set_ylim(bottom=new_minimum - offset, top=new_maximum + offset)
        except Empty:
            # No new data in the queue
            pass


class PyPlotHelper(PlotHelper):
    """Class to handle values for plotting"""


    def __init__(self, channels: dict[int, tuple[str, str]], max_value_count: int):
        super().__init__()

        self._window_closed = False
        x_dimension, y_dimension = self._calc_layout_dimension(len(channels))
        self._figure, self._axes = plt.subplots(y_dimension, x_dimension, constrained_layout=True, squeeze=False)
        self._figure.canvas.mpl_connect("close_event", self._on_close)

        for (key, value), sub_plot in zip(channels.items(), self._axes.flat):
            sub_plot.set(xlabel="Samples", ylabel=value[0], title=value[0])
            self._data[key] = PyPlotValueChannel(sub_plot, max_value_count, value[1])

        # interactive mode and show plot
        self._animation_result = animation.FuncAnimation(self._figure, self._animation,
                                                         interval=100, save_count=max_value_count)
        plt.ion()
        plt.show(block=False)
        self.update()


    def update(self):
        """Wait for a short time to process events"""
        plt.pause(0.0001)


    def loop(self):
        """Run event loop until plot window closed"""
        while not self._window_closed:
            self.update()


    def _animation(self, _frame: int, *_fargs: tuple):
        """This function is call in context of main thread"""
        for x in self._data.values():
            x.update_plot()


    def _on_close(self, _event: CloseEvent):
        self._window_closed = True
