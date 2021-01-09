from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
import matplotlib.pyplot as plt
import csv
import random
from datetime import datetime
import pandas as pd
import seaborn as sns
from libs.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
# from kivy.garden.matplotlib import matplotlib

class Huisgenoot:
    def __init__(self, name, amount_left, amount_drunk):
        self.name = name
        self.amount_left = int(amount_left)
        self.amount_drunk = int(amount_drunk)


class LongPressButton(MDRaisedButton, TouchBehavior):
    def __init__(self, **kwargs):
        super(LongPressButton, self).__init__(**kwargs)
        self.long_pressed = False

    def on_kv_post(self, base_widget):
        self.dropdown = MDDropdownMenu(
            caller=self,
            items=[{"text": "+24"}, {"text": "-24"}, {"text": "+1"}, {"text": "-1"}],
            width_mult=4,
            callback=self.update_amount
        )

    def update_amount(self, instance):
        amount = int(instance.text)
        index = int(self.name[-1]) - 1
        MDApp.get_running_app().root.ids.screen_manager.get_screen("turflist").update(index,amount)

    def on_long_touch(self, *args):
        self.long_pressed = True
        self.dropdown.open()

    def on_release(self):
        if self.long_pressed:
            self.long_pressed = False
            return
        index = int(self.name[-1]) - 1
        MDApp.get_running_app().root.ids.screen_manager.get_screen("turflist").update(index, -1)


class TurfList(Screen):
    p1_left = NumericProperty()
    p2_left = NumericProperty()
    p3_left = NumericProperty()
    p4_left = NumericProperty()

    def __init__(self, **kwargs):
        super(TurfList, self).__init__(**kwargs)
        self.huisgenoten = MDApp.get_running_app().huisgenoten
        self.p1_left = self.huisgenoten[0].amount_left
        self.p2_left = self.huisgenoten[1].amount_left
        self.p3_left = self.huisgenoten[2].amount_left
        self.p4_left = self.huisgenoten[3].amount_left

    def update(self, index, amount):
        # print(self.ids.lpbutton1)
        self.huisgenoten[index].amount_left += amount
        if amount == -1:
            self.huisgenoten[index].amount_drunk += 1

        if index == 0:
            self.p1_left += amount
        elif index == 1:
            self.p2_left += amount
        elif index == 2:
            self.p3_left += amount
        else:
            self.p4_left += amount

        with open("Stats/data.csv", "w") as data_file:
            data_writer = csv.writer(data_file)
            data_writer.writerow(("name", "amount_left", "amount_drunk"))
            for h in self.huisgenoten:
                data_writer.writerow([h.name, h.amount_left, h.amount_drunk])

        with open("Stats/history.csv", "a") as hist_file:
            hist_writer = csv.writer(hist_file)
            now = datetime.now()
            hist_writer.writerow([now.date(), now.time(), self.huisgenoten[index].name, amount, self.huisgenoten[index].amount_left])


class Statistics(Screen):
    def __init__(self, **kwargs):
        super(Statistics, self).__init__(**kwargs)
        self.plot = None
        self.fig = plt.figure()

    def day(self):
        if self.plot:
            self.ids.plot_location.remove_widget(self.plot)
            del self.plot

        with open("Stats/history.csv") as hist:
            df = pd.read_csv(hist)
            df = df[df["amount"] == -1]
            df.index = pd.to_datetime(df["date"])

            df_turf = df.groupby(["name", pd.Grouper(freq="D")]).sum()
            df_turf["amount"] *= -1

            # print(df_turf)
            # print(max(df["date"]))

            self.fig.clear()
            plt.clf()
            plt.close("all")

            sns.lineplot(data=df_turf, x="date", y="amount", hue="name")
            plt.gcf().autofmt_xdate()

        self.plot = FigureCanvasKivyAgg(plt.gcf())
        self.ids.plot_location.add_widget(self.plot)

    def week(self):
        if self.plot:
            self.ids.plot_location.remove_widget(self.plot)
            del self.plot

        with open("Stats/history.csv") as hist:
            df = pd.read_csv(hist)
            df = df[df["amount"] == -1]
            df.index = pd.to_datetime(df["date"])
            df_turf = df.groupby(["name", pd.Grouper(freq="W")]).sum()
            df_turf["amount"] *= -1
            # print(df_turf)
            self.fig.clear()
            plt.clf()
            plt.close("all")

            sns.lineplot(data=df_turf, x="date", y="amount", hue="name")
            plt.gcf().autofmt_xdate()

        self.plot = FigureCanvasKivyAgg(plt.gcf())
        self.ids.plot_location.add_widget(self.plot)

    def month(self):
        if self.plot:
            self.ids.plot_location.remove_widget(self.plot)
            del self.plot

        with open("Stats/history.csv") as hist:
            df = pd.read_csv(hist)
            df = df[df["amount"] == -1]
            df.index = pd.to_datetime(df["date"])
            df_turf = df.groupby(["name", pd.Grouper(freq="M")]).sum()
            df_turf["amount"] *= -1
            # print(df_turf)
            self.fig.clear()
            plt.clf()
            plt.close("all")

            sns.lineplot(data=df_turf, x="date", y="amount", hue="name")
            plt.gcf().autofmt_xdate()

        self.plot = FigureCanvasKivyAgg(plt.gcf())
        self.ids.plot_location.add_widget(self.plot)


class Gerechten(Screen):
    current_food = StringProperty()

    def __init__(self, **kwargs):
        super(Gerechten, self).__init__(**kwargs)
        self.current_food = ""
        with open("resources/gerechten.txt") as f:
            self.foods = [food.strip() for food in f]

    def randomize(self):
        self.current_food = random.choice(self.foods)

    def add(self):
        # print(self.ids.new_dish.text)
        dish = self.ids.new_dish.text
        if dish:
            with open("resources/gerechten.txt", "a") as f:
                f.write(f"{dish}\n")
            with open("resources/gerechten.txt") as f:
                self.foods = [food.strip() for food in f]
            self.ids.new_dish.text = ""

    def remove(self):
        with open("resources/gerechten.txt", "r") as f:
            lines = f.readlines()
        with open("resources/gerechten.txt", "w") as f:
            for line in lines:
                if line.strip() != self.ids.new_dish.text:
                    f.write(line)
                else:
                    self.current_food = f'Deleted "{self.ids.new_dish.text}"'
        with open("resources/gerechten.txt") as f:
            self.foods = [food.strip() for food in f]
        self.ids.new_dish.text = ""


class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Bierlijst"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        super().__init__(**kwargs)

        with open("Stats/data.csv") as data:
            self.huisgenoten = []
            reader = csv.DictReader(data)
            for person in reader:
                self.huisgenoten.append(Huisgenoot(person["name"], person["amount_left"], person["amount_drunk"]))

    def build(self):
        return Builder.load_file("main.kv")


if __name__ == "__main__":
    MainApp().run()

# history.close()
