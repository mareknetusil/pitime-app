import os
import importlib
import inspect

from kivy.app import App
from kivy.base import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class WidgetList(BoxLayout):
    def __init__(self, app, **kwargs):
        super(WidgetList, self).__init__(**kwargs)
        self.app = app

        self.orientation = 'vertical'
        self.widget_buttons = []

        label = Label(text='Available Widgets')
        self.add_widget(label)

        self.widget_list_layout = BoxLayout(orientation='vertical')
        self.add_widget(self.widget_list_layout)
        self.update_widget_buttons()

    def update_widget_buttons(self):
        for widget_button in self.widget_buttons:
            self.widget_list_layout.remove_widget(widget_button)

        self.widget_buttons = []

        for widget_name in self.app.available_widgets:
            widget_button = Button(text=widget_name)
            widget_button.bind(on_press=self.load_widget)
            self.widget_buttons.append(widget_button)
            self.widget_list_layout.add_widget(widget_button)

    def load_widget(self, instance):
        widget_name = instance.text
        self.app.load_widget(widget_name)


class ViewerViewport(BoxLayout):
    def __init__(self, **kwargs):
        super(ViewerViewport, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.loaded_widget = None

    def load_widget(self, widget):
        if self.loaded_widget:
            self.remove_widget(self.loaded_widget)
        self.loaded_widget = widget
        self.add_widget(widget)


class WidgetLoader:
    @staticmethod
    def locate_class(widget_name, module):
        widget_name = f'{widget_name.lower()}widget'
        for name in dir(module):
            attr = getattr(module, name)
            if inspect.isclass(attr) and name.lower() == widget_name:
                return attr
        return None

    @staticmethod
    def load_widget(widget_module_name):
        try:
            widget_module = importlib.import_module(widget_module_name)
            widget_name = widget_module_name.split('.')[-1]
            widget_class = WidgetLoader.locate_class(
                widget_name,
                widget_module
            )
            if widget_class:
                module_path = widget_module_name.replace('.', '/')
                kivy_file = f'{module_path}.kv'
                if os.path.exists(kivy_file):
                    Builder.load_file(kivy_file)
                return widget_class()
        except ImportError:
            Logger.error(f'Failed to import {widget_module_name}')
            pass
        Logger.error(f'Failed to load {widget_module_name}')
        return None


class ViewerApp(App):
    def build(self):
        self.widgets_directory = 'widgets'  # Your widgets directory
        self.available_widgets = []
        self.schedule_widget_update()

        layout = BoxLayout(orientation='horizontal')

        self.widget_list = WidgetList(self)
        self.viewport = ViewerViewport()

        layout.add_widget(self.widget_list)
        layout.add_widget(self.viewport)

        return layout

    def load_widget(self, widget_name):
        Logger.info(f'Loading {widget_name}')
        widget = WidgetLoader.load_widget(f'widgets.{widget_name}')
        if widget:
            Logger.info(f'Loaded {widget_name}')
            self.viewport.load_widget(widget)

    def schedule_widget_update(self, dt=10):  # Adjust the interval as needed
        self.update_widget_list()
        # self.root.after = self.schedule_widget_update

    def update_widget_list(self):
        widgets = [
            filename.split('.py')[0]
            for filename in os.listdir(self.widgets_directory)
            if filename.endswith('.py')
        ]
        Logger.info(f'Available widgets: {widgets}')
        self.available_widgets = widgets


if __name__ == '__main__':
    ViewerApp().run()
