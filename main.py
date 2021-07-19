# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

import random
import time
import json
import datetime
from copy import deepcopy

flug_urllib_usual = True
if flug_urllib_usual:
    import urllib.request
else:
    from kivy.network.urlrequest import UrlRequest
    import urllib

from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

resource_add_path('./fonts')
LabelBase.register(DEFAULT_FONT, './ArialCE.ttf')


FILE_PATH = "./params.json"
HOST = "192.168.0.51"
PORT = "8000"

class DataManager():
    def __init__(self):
        try:
            self.dict_params = self.load_params(fpath=FILE_PATH)
            self.user_name = self.dict_params["user_name"]
            self.upload_to = self.dict_params["upload_to"]
            if self.upload_to == "":
                self.upload_to = HOST + ":" + PORT
        except:
            print("failed to load params")
            self.dict_params = dict()
            self.user_name = "user_unknown"
            self.upload_to = HOST + ":" + PORT
        self.dt_start = None
        self.type = "addition"
        self.score_format = {
            "dt_start": None,
            "user_name": None,
            "type": None,
            "duration": None,
            "ans_num": int(0),
            "correct_num": int(0)
        }
        self.init_param()
        self.list_score = list()
        self.is_valid = False
        return None
    
    def init_param(self):
        self.score = deepcopy(self.score_format)
    
    def append_score(self, score):
        self.list_score.append(deepcopy(score))
        self.init_param()
    
    def load_params(self, fpath):
        with open(fpath) as f:
            dict_json = json.load(f)
        return dict_json
    
    def restore_params(self, fpath=FILE_PATH):
        dict_data = {
            "user_name": self.user_name,
            "upload_to": self.upload_to
        }
        with open(fpath, mode="w") as f:
            json.dump(dict_data, f, indent=4)
        return None

    def upload_to_gss(self):
        return None
    
    def upload_to_server(self):
        url = "http://{}/upload".format(self.upload_to)
        print(url)
        headers = {
#            'Content-type': 'application/x-www-form-urlencoded',
#            'Accept': 'text/plain'
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
#        print(len(self.list_score))
        list_keep = list()
        def print_resp(req, result):
            print(result)
            return None
        for score in self.list_score:
            score["user_name"] = deepcopy(self.user_name)
            score["type"] = deepcopy(self.type)
            print(score)

#            req = urllib.request.Request(url, json.dumps(score).encode(), headers)
            time.sleep(0.3)
            try:
                # GET ----------------
                if False:
                    if flug_urllib_usual:
                        req = urllib.request.Request("http://{}/".format(self.upload_to))
                        with urllib.request.urlopen(req) as res:
                            body = res.read()
                        print(body)
                    else:
                        req = UrlRequest(
                            "http://{}/".format(self.upload_to),
                            on_success=print_resp,
                            on_failure=print_resp,
                            timeout=10
                        )
                        print("result: {}".format(req.result))
                        print("error: {}".format(req.error))
                # POST ----------------
                else:
                    if flug_urllib_usual:
                        req = urllib.request.Request(url, json.dumps(score).encode(), headers)
                        with urllib.request.urlopen(req) as res:
                            body = res.read()
                        print(body)
                    else:
                        req = UrlRequest(
                            url, 
                            on_success=print_resp,
                            on_failure=print_resp,
                            req_body=urllib.parse.urlencode(score),
                            req_headers=headers,
                            timeout=10
                        )
                        print("result: {}".format(req.result))
                        print("error: {}".format(req.error))
            except Exception as e:
                print(e)
                list_keep.append(score)
        self.list_score = deepcopy(list_keep)
        if len(self.list_score) == int(0):
            self.is_valid = False

        return None
    

dm = DataManager()


TYPE_CHOICE = ("addition", "division")

class MenuScreen(Screen):
    type_choice = TYPE_CHOICE
    def on_upload_btn(self):
        if dm.is_valid:
            try:
                dm.upload_to_server()
            except Exception as e:
                print(e)
                print("failed to upload, keep data")
        else:
            print("no valid data to upload")
    
    def on_training_btn(self):
        dm.type = self.ids.calc_type.text


class SettingScreen(Screen):
    user_name = StringProperty(dm.user_name)
    upload_to = StringProperty(dm.upload_to)

    def on_save_btn(self):
        if str(self.ids.text_user_name.text) != "":
            dm.user_name = str(self.ids.text_user_name.text)
        if str(self.ids.text_upload_to.text) != "":
            dm.upload_to = str(self.ids.text_upload_to.text)
        dm.restore_params()


class Calculation():
    def __init__(self):
        return None
    
    def get_eq_ans(self, _type="addition"):
        # addition ==========================
        if _type == "addition":
            a = random.randrange(1, 10)
            b = random.randrange(1, 10)
            eq = "{} + {} = {}".format(
                a, 
                b, 
                "?"
            )
            ans = a + b
        # division ==========================
        elif _type == "division":
            a = random.randrange(1, 9)
            b = random.randrange(1, 9)
            eq = "{} ÷ {} = {}".format(
                a * b, 
                a, 
                "?"
            )
            ans = b
        return eq, ans


TIME_MAX_SEC = 30
COUNT_MAX = 10
class CalculatorScreen(Screen):
    eq = StringProperty()
    ans = NumericProperty()
    text = StringProperty()
    text_input = StringProperty()
    time = NumericProperty()
    result = StringProperty()

    def __init__(self, **kwargs):
        super(CalculatorScreen, self).__init__(**kwargs)
        self.calc = Calculation()
#        self.init_params()
    
    def init_params(self):
        self.result = ""
#        self.ids.text_ans.text = ""
        self.count = COUNT_MAX
        self.text_input = ""
        self.eq, self.ans = self.calc.get_eq_ans(_type=dm.type)
        self.score = deepcopy(dm.score_format)
        self.score["duration"] = int(TIME_MAX_SEC)
#        self.timer_start()

    
    def next_eq(self, _):
        if self.time > 0:
            self.result = ""
#            self.ids.text_ans.text = ""
            self.text_input = ""
#            self.eq, self.ans = self.calc.get_eq_ans(_type=dm.type)
            self.eq, self.ans = self.calc.get_eq_ans(_type=dm.type)

    def buttonClicked(self):
        self.text = self.text_handler.get_text()
    
    def timer_start(self):
        self.time = int(TIME_MAX_SEC)
        self.timer = Clock.schedule_interval(self.timer_countdown, 1.0)
    
    def timer_cancel(self):
        try:
            self.timer.cancel()
        except:
            pass
    
    def timer_countdown(self, dt):
        self.time -= int(1)
        if self.time <= 0:
            self.result = ""
#            self.ids.text_ans.text = ""
            self.text_input = ""
            self.eq = "  finished !\npress Quit"
            dm.append_score(self.score)
            dm.is_valid = True
            return False
    
    def set_dt_start(self):
        self.score["dt_start"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def on_keypad(self, input):
        if str(input) in [str(i) for i in range(1, 10)]:
            self.text_input += str(input)
        elif str(input) == "0":
            if len(self.text_input) > int(0):
                self.text_input += str(input)
            else:
                pass
        elif str(input) == "del":
            self.text_input = self.text_input[:-1]
        elif str(input) == "clr":
            self.text_input = ""
        else:
            pass

    
    def check_ans_and_go_next(self):
        if self.time > 0:
            self.score["ans_num"] += int(1)
    #        self.count -= int(1)
            try:
#                ans_input = int(self.ids.text_ans.text)
                ans_input = int(self.text_input)
            except:
                ans_input = str()
            if ans_input == self.ans:
                self.result = "OK"
                self.score["correct_num"] += int(1)
            else:
                self.result = "NG"
            Clock.schedule_once(self.next_eq, 0.5)
        else:
            pass


class CalculatorApp(App):
    def __init__(self, **kwargs):
        super(CalculatorApp, self).__init__(**kwargs)
        self.title = 'Calculator'

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
#        sm.add_widget(CalculatorScreen(name='training'))
        self.calc_screen = CalculatorScreen(name='training')
        sm.add_widget(self.calc_screen)
        self.setting_screen = SettingScreen(name='setting')
        sm.add_widget(self.setting_screen)
        self.dm = dm
        return sm


if __name__ == '__main__':
#    Window.size = (600, 450)
    app = CalculatorApp()
    app.run()