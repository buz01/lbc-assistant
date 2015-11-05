from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from leboncoin_scrapper.processor import get_item_list, get_full_details
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from datetime import datetime
import collections

Builder.load_string('''
<Screen1>:
    BoxLayout:
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.5, 1
            ScrollView:
                size_hint: 1, 1
                do_scroll_x: False
                BoxLayout:
                    orientation: 'vertical'
                    id: item_list
                    size_hint: 1, None
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1, .05
                Button:
                    id: refresh_btn
                    size_hint: 1, 1
                    text: 'Refresh'
                    on_release: root.refresh()
        BoxLayout:
            orientation: 'vertical'
            id: detail_box
            size_hint: 0.5, 1
            spacing: 1

            Carousel:
                orientation: 'vertical'
                direction: 'right'
                size_hint: 1, 1
                id: big_picture_list

            BoxLayout:
                orientation: 'vertical'
                size_hint: 1, 0.2
                spacing: 1
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, 1
                    spacing: 1
                    Label:
                        id: publication_date_lbl
                        markup:True
                        text: '12/12/1200 15:00'
                        size_hint: 0.5, 1
                    Label:
                        id: title_lbl
                        markup:True
                        text: 'title'
                    Label:
                        id: price_lbl
                        markup:True
                        text: 'price'
                        size_hint: 0.5, 1

''')


__version__ = '1.0.0'


class Screen1(Screen):
    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)

        # Item list
        self.item_list = self.ids['item_list']
        self.refresh_btn = self.ids['refresh_btn']

        # Details
        self.publication_date_lbl = self.ids['publication_date_lbl']
        self.title_lbl = self.ids['title_lbl']
        self.price_lbl = self.ids['price_lbl']
        self.big_picture_list = self.ids['big_picture_list']

        self.last_refresh = None
        self.previous_selected_button = None
        pass

    def refresh(self):
        self.get_details()
        self.last_refresh = datetime.today()
        self.refresh_btn.text = 'Refresh (last refresh : ' + self.last_refresh.strftime('%d/%m/%Y %X')

    def get_details(self):
        item_list = get_item_list(self.last_refresh)
        self.item_list.clear_widgets()
        for i in item_list:

            # WHo many hours ago
            item_datetime = datetime.strptime(i.publication_date, "%Y/%m/%d %H:%M")
            date_diff = abs((datetime.now() - item_datetime).seconds) / 60.0
            if date_diff < 60:
                formatted_time_ago = str(int(round(date_diff, 0))) + " min"
            elif date_diff < 24 * 60:
                formatted_time_ago = str(int(round(date_diff / 60, 0))) + " h"
            else:
                formatted_time_ago = str(int(round(date_diff / 60 / 24, 0))) + " j"
            i_time_ago = Label(text=formatted_time_ago, size_hint=[0.1, 1], font_size=9)

            # Price
            i_price = Label(text=i.price, size_hint=[0.1, 1])

            # Title
            formatted_title = i.title
            if i.is_new:
                formatted_title = '[color=#ffcc00]' + i.title + '[/color]'
            i_title = ItemListButton(text=formatted_title, height='100sp', markup=True, size_hint=[1, 1])
            i_title.item = i
            i_title.bind(on_press=self.show_details)

            # Image
            i_picture = AsyncImage(source=i.pictures[0], size_hint=[0.1, 1], pos_hint={'right': 1.0})

            # Layout
            layout = BoxLayout(padding=1)
            layout.add_widget(i_time_ago)
            layout.add_widget(i_price)
            layout.add_widget(i_title)
            layout.add_widget(i_picture)

            self.item_list.add_widget(layout)

        self.item_list.size = (1, len(item_list) * 50)

    def show_details(self, instance):
        """
        Update the big pictures view (right view) by :
        - remove the old pictures
        - get the full details of the new item
        - add the new big pictures to the right view

        Manage the call to coloration function of the buttons (pressed and unpressed).

        :rtype : None
        :type instance: ItemListButton
        """

        self.big_picture_list.clear_widgets()
        i = get_full_details(instance.item)

        for big_pic_url in i.big_pictures:
            big_pic = AsyncImage(source=big_pic_url, size_hint=[1, 1], allow_stretch=True)
            self.big_picture_list.add_widget(big_pic)
        # self.big_picture_list.size = (len(i.big_pictures) * 50, 1)

        # Manage the active ad button color
        if self.previous_selected_button is not None:
            self.previous_selected_button.toggle_color()
        self.previous_selected_button = instance
        instance.toggle_color()


SELECTED_COLOR = (1, 0.5, 0.5, 0.5)
UNSELECTED_COLOR = (1, 1, 1, 1)


class ItemListButton(Button):
    def __init__(self, **kwargs):
        """

        :type kwargs: object
        """
        super(ItemListButton, self).__init__(**kwargs)
        self.item = None

    def toggle_color(self):

        """

        :type self: object
        """
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

        if compare(self.background_color, SELECTED_COLOR):
            self.background_normal = 'atlas://data/images/defaulttheme/button'
            self.background_color = UNSELECTED_COLOR
        else:
            self.background_normal = ''
            self.background_color = SELECTED_COLOR


class ScreenMain(App):
    def build(self):
        return sm


sm = ScreenManager()
sm.add_widget(Screen1(name='Screen1'))


class LoginScreen(GridLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        item_list = get_item_list()

        self.cols = 5

        for i in item_list:
            self.add_widget(Label(text=i.publication_date))
            self.add_widget(Label(text=i.title))
            self.add_widget(Label(text=i.price))
            self.add_widget(Label(text=i.place))
            if len(i.pictures) > 0:
                self.add_widget(AsyncImage(source=i.pictures[0]))
            else:
                self.add_widget(Label(text='-'))


'''
class MyApp(App):

    def build(self):
        root = ScrollView(size_hint=(None, None), size=(400, 400))
        root.add_widget(LoginScreen())
        return root
'''

if __name__ == '__main__':
    ScreenMain().run()