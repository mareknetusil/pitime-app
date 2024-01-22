import datetime as dt
import typing as tp

from kivy.logger import Logger
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, MeshLinePlot, exp10, log10, identity

from globals import get_global
from weather import CurrentWeather, Forecast, WEATHER_KEY, InfoType


class ForecastGraph(Graph):
    timestamps: tp.Optional[tp.List[str]] = None

    def _update_labels(self):
        xlabel = self._xlabel
        ylabel = self._ylabel
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        padding = self.padding
        x_next = padding + x
        y_next = padding + y
        xextent = width + x
        yextent = height + y
        ymin = self.ymin
        ymax = self.ymax
        xmin = self.xmin
        precision = self.precision
        x_overlap = False
        y_overlap = False
        # set up x and y axis labels
        if xlabel:
            xlabel.text = self.xlabel
            xlabel.texture_update()
            xlabel.size = xlabel.texture_size
            xlabel.pos = int(
                x + width / 2. - xlabel.width / 2.), int(padding + y)
            y_next += padding + xlabel.height
        if ylabel:
            ylabel.text = self.ylabel
            ylabel.texture_update()
            ylabel.size = ylabel.texture_size
            ylabel.x = padding + x - (ylabel.width / 2. - ylabel.height / 2.)
            x_next += padding + ylabel.height
        xpoints = self._ticks_majorx
        xlabels = self._x_grid_label
        xlabel_grid = self.x_grid_label
        ylabel_grid = self.y_grid_label
        ypoints = self._ticks_majory
        ylabels = self._y_grid_label
        # now x and y tick mark labels
        if len(ylabels) and ylabel_grid:
            # horizontal size of the largest tick label, to have enough room
            funcexp = exp10 if self.ylog else identity
            funclog = log10 if self.ylog else identity
            ylabels[0].text = precision % funcexp(ypoints[0])
            ylabels[0].texture_update()
            y1 = ylabels[0].texture_size
            y_start = y_next + (padding + y1[1] if len(xlabels) and xlabel_grid
                                else 0) + \
                               (padding + y1[1] if not y_next else 0)
            yextent = y + height - padding - y1[1] / 2.

            ymin = funclog(ymin)
            ratio = (yextent - y_start) / float(funclog(ymax) - ymin)
            y_start -= y1[1] / 2.
            y1 = y1[0]
            for k in range(len(ylabels)):
                if k == 0:
                    ylabels[k].text = ''
                else:
                    ylabels[k].text = precision % funcexp(ypoints[k])
                ylabels[k].texture_update()
                ylabels[k].size = ylabels[k].texture_size
                y1 = max(y1, ylabels[k].texture_size[0])
                ylabels[k].pos = (
                    int(x_next),
                    int(y_start + (ypoints[k] - ymin) * ratio))
            if len(ylabels) > 1 and ylabels[0].top > ylabels[1].y:
                y_overlap = True
            else:
                x_next += y1 + padding
        if len(xlabels) and xlabel_grid:
            funcexp = exp10 if self.xlog else identity
            funclog = log10 if self.xlog else identity
            # find the distance from the end that'll fit the last tick label
            if self.timestamps:
                xlabels[0].text = self.timestamps[0]
            else:
                xlabels[0].text = precision % funcexp(xpoints[-1])
            # xlabels[0].text = 'prdel'
            xlabels[0].texture_update()
            xextent = x + width - xlabels[0].texture_size[0] / 2. - padding
            # find the distance from the start that'll fit the first tick label
            if not x_next:
                if self.timestamps:
                    xlabels[0].text = self.timestamps[0 * self.x_ticks_major]
                else:
                    xlabels[0].text = precision % funcexp(xpoints[0])
                xlabels[0].texture_update()
                x_next = padding + xlabels[0].texture_size[0] / 2.
            xmin = funclog(xmin)
            ratio = (xextent - x_next) / float(funclog(self.xmax) - xmin)
            right = -1
            for k in range(len(xlabels)):
                if self.timestamps:
                    xlabels[k].text = self.timestamps[k * self.x_ticks_major]
                else:
                    xlabels[k].text = precision % funcexp(xpoints[k])
                # update the size so we can center the labels on ticks
                xlabels[k].texture_update()
                xlabels[k].size = xlabels[k].texture_size
                half_ts = xlabels[k].texture_size[0] / 2.
                xlabels[k].pos = (
                    int(x_next + (xpoints[k] - xmin) * ratio - half_ts),
                    int(y_next))
                if xlabels[k].x < right:
                    x_overlap = True
                    break
                right = xlabels[k].right
            if not x_overlap:
                y_next += padding + xlabels[0].texture_size[1]
        # now re-center the x and y axis labels
        if xlabel:
            xlabel.x = int(
                x_next + (xextent - x_next) / 2. - xlabel.width / 2.)
        if ylabel:
            ylabel.y = int(
                y_next + (yextent - y_next) / 2. - ylabel.height / 2.)
            ylabel.angle = 90
        if x_overlap:
            for k in range(len(xlabels)):
                xlabels[k].text = ''
        if y_overlap:
            for k in range(len(ylabels)):
                ylabels[k].text = ''
        return x_next - x, y_next - y, xextent - x, yextent - y


class ForecastWidget(BoxLayout):
    temperatures = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.graph = ForecastGraph(
            x_ticks_minor=1, x_ticks_major=2, y_ticks_major=10,
            y_grid_label=True, x_grid_label=True,
            padding=5,
            x_grid=True, y_grid=True,
            xmin=0, xmax=16, ymin=-20, ymax=40,
            label_options={
                'font_family': 'Roboto-Bold'
            },
        )
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])

        self.add_widget(Widget(size_hint=(1, 0.1)))  # padding
        self.add_widget(
            Label(
                text='Předpověď',
                size_hint=(1, 0.1),
                font_name='Roboto-Bold',
                font_size=50,
        ))
        self.add_widget(self.graph)
        self.add_widget(Widget(size_hint=(1, 0.1)))  # padding

        weather_api = get_global(WEATHER_KEY)
        weather_api.add_subscriber({InfoType.Forecast: self.update_forecast})

    @staticmethod
    def get_time_label(timestamp: int) -> str:
        timestamp = dt.datetime.fromtimestamp(timestamp)
        return timestamp.strftime('%H:%M')

    def update_forecast(self, forecast: Forecast):
        self.temperatures = [weather.main.temp for weather in forecast.list]
        self.timestamps = [
            f'{self.get_time_label(weather.dt)}\n{weather.main.temp - 273:.1f}°'
            for weather in forecast.list
        ]
        self.plot.points = [
            (x, temp - 273)
            for x, temp in enumerate(self.temperatures)
        ]
        self.graph.timestamps = self.timestamps
        self.graph.add_plot(self.plot)
